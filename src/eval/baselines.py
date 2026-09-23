"""Frozen baseline extraction over raw Unicode text, resumable per document."""
import argparse
from collections import Counter
import importlib.metadata
import json
from pathlib import Path
import re
from .execute import append, digest, lock, rows, source_hashes
from .metrics import score_corpus
from .protocol import sha
from .run import load_plan, unique, validate_spans, write_json


def mapped(raw, mapping):
    output = set()
    for s in raw:
        if s['label'] not in mapping: raise ValueError('unknown source label; freeze an updated mapping before running')
        if mapping[s['label']] is not None:
            output.add((s['start'], s['end'], mapping[s['label']]))
    return [dict(start=a,end=b,category=c) for a,b,c in sorted(output)]


class Rules:
    def __init__(self, name):
        self.name = name
        if name == 'presidio':
            from presidio_analyzer.predefined_recognizers import (KrBrnRecognizer, KrDriverLicenseRecognizer,
                KrFrnRecognizer, KrPassportRecognizer, KrRrnRecognizer, EmailRecognizer, PhoneRecognizer)
            self.recognizers = [cls(supported_language='ko') for cls in (KrBrnRecognizer,KrDriverLicenseRecognizer,
                KrFrnRecognizer,KrPassportRecognizer,KrRrnRecognizer)]
            import tldextract
            email=EmailRecognizer(supported_language="ko")
            suffixes=tldextract.TLDExtract(suffix_list_urls=(),cache_dir=None)
            email.validate_result=lambda text: bool(suffixes(text).fqdn)
            self.recognizers.extend([email,PhoneRecognizer(supported_language="ko",supported_regions=("KR",))])

    def __call__(self, text):
        if self.name == 'ko-pii':
            from ko_pii import detect_all
            return [dict(start=s.start,end=s.end,label=s.label) for s in detect_all(text,normalize=False)]
        spans = [dict(start=s.start,end=s.end,label=s.entity_type) for r in self.recognizers
                 for s in r.analyze(text,entities=r.supported_entities,nlp_artifacts=None) if s.score >= 0.3]
        # Frozen surface rules; account prefix is not included in the predicted span.
        for m in re.finditer(r'(?:계좌(?:번호)?\s*[:：]?\s*)(\d{2,6}(?:-\d{2,6}){1,3})(?!\d)', text):
            spans.append(dict(start=m.start(1),end=m.end(1),label='KI_BANK_ACCOUNT'))
        for m in re.finditer(r'(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)',text):
            digits=[int(c) for c in m.group() if c.isdigit()]
            total=sum((2*d-9 if 2*d>9 else 2*d) if i%2 else d for i,d in enumerate(reversed(digits)))
            if 13<=len(digits)<=19 and total%10==0:
                spans.append(dict(start=m.start(),end=m.end(),label='KI_CARD'))
        return spans


def decode_bioes(labels, offsets):
    """Argmax BIOES grouping, no learned transitions or gold boundary repair."""
    result=[]; current=None
    def finish():
        nonlocal current
        if current: result.append(current); current=None
    for label,(start,end) in zip(labels,offsets):
        if end<=start: continue
        if label=='O': finish(); continue
        prefix,kind=label.split('-',1)
        if prefix in {'B','S'} or not current or current['label']!=kind:
            finish(); current=dict(start=start,end=end,label=kind)
        else: current['end']=end
        if prefix in {'E','S'}: finish()
    finish(); return result


class OpenMed:
    def __init__(self, revision, device, window, overlap):
        if not re.fullmatch('[0-9a-f]{40}',revision): raise ValueError('pin OpenMed revision')
        if not 0 <= overlap < window-2: raise ValueError('invalid token window overlap')
        import torch
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        self.torch=torch;self.window=window;self.overlap=overlap;self.device=device
        model='OpenMed/privacy-filter-multilingual'
        self.tokenizer=AutoTokenizer.from_pretrained(model,revision=revision,trust_remote_code=False)
        self.model=AutoModelForTokenClassification.from_pretrained(model,revision=revision,trust_remote_code=False).to(device).eval()
        self.labels=self.model.config.id2label

    def __call__(self,text):
        # Explicit overlapping windows cover all tokens. Never truncate a document.
        encoding=self.tokenizer(text,return_offsets_mapping=True,return_overflowing_tokens=True,
            truncation=True,max_length=self.window,stride=self.overlap,padding=False)
        spans=[]
        for i,offsets in enumerate(encoding['offset_mapping']):
            batch={k:self.torch.tensor([v[i]],device=self.device) for k,v in encoding.items()
                   if k in self.tokenizer.model_input_names}
            with self.torch.inference_mode():
                ids=self.model(**batch).logits[0].argmax(-1).tolist()
            spans.extend(decode_bioes([self.labels[k] for k in ids],offsets))
        # Conflicting overlapping-window predictions are retained; exact duplicates deduplicated downstream.
        return spans


def run(directory, output, name, revision=None, device='cpu', window=1024, overlap=128, detector=None):
    manifest,docs,_,taxonomy=load_plan(directory)
    root=Path(output);root.mkdir(parents=True,exist_ok=True)
    mapping_path=Path('experiments/label_maps')/f'{name}.json'
    mapping=json.loads(mapping_path.read_text())['mapping']
    package={'ko-pii':'ko-pii','presidio':'presidio-analyzer','openmed':'transformers'}[name]
    stamp={'dependencies':{d.metadata['Name']:d.version for d in importlib.metadata.distributions()},'model':name,'package_version':importlib.metadata.version(package),
           'model_revision':revision,'device':device,'window_tokens':window,'overlap_tokens':overlap,
           'data_sha256':manifest['data_sha256'],'taxonomy_sha256':manifest['taxonomy_sha256'],
           'mapping_sha256':sha(mapping_path.read_text()),'source_sha256':source_hashes(),
           'decoder':'argmax_bioes' if name=='openmed' else 'native_rules_raw_text'}
    with lock(root/'run.lock'):
        meta=root/'run.json'
        if meta.exists() and json.loads(meta.read_text())!=stamp: raise ValueError('baseline settings changed')
        if not meta.exists(): write_json(meta,stamp)
        path=root/'predictions.jsonl';done=unique(rows(path),'doc_id')
        if set(done)-{d['doc_id'] for d in docs}: raise ValueError('unknown baseline document')
        if detector is None:
            detector=OpenMed(revision,device,window,overlap) if name=='openmed' else Rules(name)
        for d in docs:
            if d['doc_id'] in done: continue
            raw=detector(d['text']);pred=mapped(raw,mapping);validate_spans(pred,d['text'],taxonomy)
            row={'doc_id':d['doc_id'],'spans':pred,'source_label_counts':dict(Counter(s['label'] for s in raw)), 'raw':raw}
            append(path,row);done[d['doc_id']]=row
        result=score_corpus(docs,{k:v['spans'] for k,v in done.items()},taxonomy)
        result.update(model=name,task='span_extraction',manifest=manifest,execution=stamp,
                      baseline_context='whole_document_rules' if name!='openmed' else 'overlapping_token_windows',
                      predictions_sha256=sha(path.read_text()))
        if not (root/'result.json').exists(): write_json(root/'result.json',result)
        return {'result':str(root/'result.json'),'documents':len(done),'f1_micro':result['metrics']['f1_micro']}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory',required=True);p.add_argument('--output',required=True)
    p.add_argument('--name',choices=['presidio','ko-pii','openmed'],required=True)
    p.add_argument('--revision');p.add_argument('--device',default='cpu')
    p.add_argument('--window',type=int,default=1024);p.add_argument('--overlap',type=int,default=128)
    a=p.parse_args();print(json.dumps(run(a.directory,a.output,a.name,a.revision,a.device,a.window,a.overlap)))
