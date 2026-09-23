"""생성 실행기.

  python -m src.generate.run plan   --n 100 --out data/corpus/pilot-0.1/plan.jsonl [--seed 0]
  python -m src.generate.run compose --plan ... --generator-slice api-main --model MODEL [--base-url URL] --out .../raw.api.jsonl
  python -m src.generate.run fill    --raw .../raw.jsonl --out .../docs.jsonl
  python -m src.generate.run dryrun  --text sample.txt --doc-type cs_transcript --level T2   (LLM 없이 fill+validate 확인)
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import product
from pathlib import Path

from .compose import LLMClient, Plan, build_prompt, make_plan, plan_to_dict
from .fill import Filler
from .negatives import fill_negatives
from .schema import Document
from .taxonomy import Taxonomy
from .validate import bucket_for, validate
from .profiles import make_profiles, profile_errors, VERSION as PROFILE_VERSION, REFERENCE_DATE

LEVELS_W = {"T0": 25, "T1": 30, "T2": 25, "T3": 20}
SUBJ_W = {1: 40, 3: 35, 8: 25}
BUCKET_W = {"1k": 40, "4k": 40, "16k": 20}
STT_TYPES = {"cs_transcript", "phishing_report"}


def _approx_tokens(text: str) -> int:
    # 한국어 대략 1 토큰 ≈ 1.6자 (Qwen/GPT 계열 평균 근사). 실측 토크나이저로 교체 가능.
    return int(len(text) / 1.6)


def make_plans(tax: Taxonomy, n: int, seed: int) -> list[Plan]:
    if n < 1:
        raise ValueError("n must be positive")
    rng = random.Random(seed)
    types = list(tax.document_types)
    # Balance document types; sample the remaining cells without replacement
    # within each type. A complete 360-cell round covers every cell once.
    cells = list(product(LEVELS_W, SUBJ_W, BUCKET_W))
    available = {dt: list(cells) for dt in types}
    local_n = (n + 2) // 5
    slices = ["api-main"] * (n - local_n) + ["local-check"] * local_n
    rng.shuffle(slices)
    plans = []
    for i in range(n):
        if i % len(types) == 0:
            rng.shuffle(types)
        dt = types[i % len(types)]
        if not available[dt]:
            available[dt] = list(cells)
        subj_w = dict(SUBJ_W)
        if dt in ("internal_memo", "complaint_case"):
            subj_w = {1: 15, 3: 45, 8: 40}
        weights = [LEVELS_W[lvl] * subj_w[ns] * BUCKET_W[bk] for lvl, ns, bk in available[dt]]
        cell = rng.choices(available[dt], weights=weights)[0]
        available[dt].remove(cell)
        lvl, ns, bk = cell
        plans.append(make_plan(tax, rng, dt, lvl, ns, bk, slices[i], i + 1))
    return plans


def cmd_plan(a):
    plans = make_plans(Taxonomy(), a.n, a.seed)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "x", encoding="utf-8") as f:
        for p in plans:
            f.write(json.dumps(plan_to_dict(p), ensure_ascii=False) + "\n")
    print(f"{len(plans)} plans → {a.out}")
    print(Counter(p.variation_level for p in plans), Counter(p.num_subjects for p in plans), Counter(p.context_len_bucket for p in plans))
    print(Counter(p.generator_slice for p in plans))


def cmd_compose(a):
    tax = Taxonomy()
    with open(a.plan, encoding="utf-8") as f:
        plans = [Plan(**json.loads(l)) for l in f]
    plans = [p for p in plans if p.generator_slice == a.generator_slice]
    if not plans:
        raise ValueError(f"no plans for generator slice {a.generator_slice}")
    if len({p.doc_id for p in plans}) != len(plans):
        raise ValueError("duplicate doc_id in selected plans")
    selected = {p.doc_id: plan_to_dict(p) for p in plans}
    done = set()
    if Path(a.out).exists():
        with open(a.out, encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                doc_id = record["doc_id"]
                if doc_id in done:
                    raise ValueError(f"duplicate output doc_id: {doc_id}")
                if (record.get("plan") != selected.get(doc_id) or doc_id not in selected
                        or record.get("model") != a.model or record.get("prompt_version") != a.prompt_version):
                    raise ValueError(f"output metadata mismatch for {doc_id}; use a separate output file")
                if record.get("completion", {}).get("finish_reason", "stop") != "stop":
                    raise ValueError(f"incomplete response for {doc_id}; regenerate in a separate output file")
                done.add(doc_id)
    pending = [p for p in plans if p.doc_id not in done]
    if not pending:
        print(f"all {len(plans)} plans already composed")
        return
    # A client per request keeps response metadata isolated across workers.
    def compose_record(p):
        client = LLMClient(a.model, base_url=a.base_url)
        prompt = build_prompt(tax, p, a.prompt_version)
        raw = client.complete(prompt, seed=p.seed)
        return {"doc_id": p.doc_id, "plan": plan_to_dict(p), "model": a.model,
                "prompt_version": a.prompt_version, "raw": raw,
                "completion": getattr(client, "last_metadata", {})}

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    pool = ThreadPoolExecutor(max_workers=a.workers)
    futures = [pool.submit(compose_record, p) for p in pending]
    failures = []
    try:
        with open(a.out, "a", encoding="utf-8") as f:
            for future in as_completed(futures):
                try:
                    record = future.result()
                except Exception as exc:
                    failures.append(type(exc).__name__)
                    for queued in futures:
                        queued.cancel()
                    continue
                completion = record["completion"]
                raw = record["raw"]
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
                print(record["doc_id"], len(raw), completion.get("finish_reason", "stop"), flush=True)
                if completion.get("finish_reason", "stop") != "stop" or not raw.strip():
                    failures.append(f"incomplete/empty response for {record['doc_id']}; raw response saved")
                    for queued in futures:
                        queued.cancel()
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    if failures:
        raise ValueError("compose failed: " + "; ".join(failures))


def fill_one(tax: Taxonomy, plan: Plan, raw: str, model: str, prompt_version: str) -> tuple[Document | None, list[str]]:
    rng = random.Random(plan.seed)
    profiles = make_profiles(plan.seed, plan.num_subjects) if prompt_version in {"compose_v4", "compose_v5", "compose_v6", "compose_v7"} else None
    filler = Filler(tax, plan.variation_level, rng, plan.doc_type, stt=plan.doc_type in STT_TYPES,
                    profiles=profiles, profile_seed=plan.seed)
    try:
        text, spans, subjects = filler.fill(raw)
    except (ValueError, AssertionError, KeyError) as e:
        return None, [f"fill error: {e}"]
    text, negs = fill_negatives(text, spans, rng, tax.hard_negative_types)
    n_tok = _approx_tokens(text)
    doc = Document(
        doc_id=plan.doc_id, doc_type=plan.doc_type, variation_level=plan.variation_level, num_subjects=plan.num_subjects,
        context_len_bucket=bucket_for(n_tok), n_tokens=n_tok,
        generator={"model": model, "prompt_version": prompt_version, "slice": plan.generator_slice},
        taxonomy_version=tax.version, text=text, spans=spans, hard_negatives=negs, subjects=subjects,
    )
    errs = validate(doc, tax)
    if profiles is not None:
        doc.generator.update(profile_version=PROFILE_VERSION, reference_date=REFERENCE_DATE.isoformat())
        errs.extend(profile_errors(doc, profiles, tax))
    # bucket 은 실측으로 재배정했으므로 bucket mismatch 는 계획 대비 2단계 이상 어긋날 때만 오류
    errs = [e for e in errs if not e.startswith("length bucket")]
    order = ["1k", "4k", "16k"]
    if abs(order.index(doc.context_len_bucket) - order.index(plan.context_len_bucket)) >= 2:
        errs.append(f"length bucket drift: planned {plan.context_len_bucket}, actual {doc.context_len_bucket}")
    if prompt_version == "compose_v7" and plan.context_len_bucket == "16k" and doc.context_len_bucket != "16k":
        errs.append(f"long-document minimum not met: {doc.n_tokens} < 9000 approximate tokens")
    return doc, errs


def cmd_fill(a):
    tax = Taxonomy()
    ok = bad = 0
    with open(a.out, "w", encoding="utf-8") as fo, open(a.out + ".rejects.jsonl", "w", encoding="utf-8") as fr:
        for l in open(a.raw, encoding="utf-8"):
            r = json.loads(l); plan = Plan(**r["plan"])
            if r.get("completion", {}).get("finish_reason", "stop") != "stop" or not r["raw"].strip():
                doc, errs = None, ["incomplete/empty model response"]
            else:
                doc, errs = fill_one(tax, plan, r["raw"], r["model"], r["prompt_version"])
            if doc and not errs:
                fo.write(json.dumps(doc.to_json(), ensure_ascii=False) + "\n"); ok += 1
            else:
                fr.write(json.dumps({"doc_id": plan.doc_id, "errors": errs}, ensure_ascii=False) + "\n"); bad += 1
    print(f"ok={ok} rejected={bad} → {a.out}")


def cmd_dryrun(a):
    tax = Taxonomy()
    raw = Path(a.text).read_text(encoding="utf-8")
    rng = random.Random(a.seed)
    plan = make_plan(tax, rng, a.doc_type, a.level, a.num_subjects, "1k", "api-main", 0)
    doc, errs = fill_one(tax, plan, raw, "dryrun", "compose_v1")
    if doc:
        print(doc.text)
        print("---- spans ----")
        for s in doc.spans:
            print(f"[{s.category:22s}] {s.surface!r:40s} canon={s.canonical!r} ops={s.applied_ops} regex={s.regex_catchable} subj={s.subject_id}/{s.subject_role}" + (f" frag={s.fragment.index}/{s.fragment.of}" if s.fragment else ""))
        print("---- negatives ----")
        for n in doc.hard_negatives:
            print(f"[{n.type}] {n.surface!r}")
    print("---- validation ----")
    print("OK" if not errs else "\n".join(errs))
    return 0 if not errs else 1


def main(argv=None):
    from .batch import register_commands

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    register_commands(sub)
    p = sub.add_parser("plan"); p.add_argument("--n", type=int, default=100); p.add_argument("--out", required=True); p.add_argument("--seed", type=int, default=0); p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("compose"); p.add_argument("--plan", required=True); p.add_argument("--model", required=True); p.add_argument("--base-url"); p.add_argument("--generator-slice", choices=["api-main", "local-check"], required=True); p.add_argument("--prompt-version", choices=["compose_v1", "compose_v2", "compose_v3", "compose_v4", "compose_v5", "compose_v6", "compose_v7"], default="compose_v1"); p.add_argument("--workers", type=int, choices=range(1, 9), default=1); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_compose)
    p = sub.add_parser("fill"); p.add_argument("--raw", required=True); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_fill)
    p = sub.add_parser("dryrun"); p.add_argument("--text", required=True); p.add_argument("--doc-type", default="cs_transcript"); p.add_argument("--level", default="T2"); p.add_argument("--num-subjects", type=int, default=1); p.add_argument("--seed", type=int, default=0); p.set_defaults(fn=cmd_dryrun)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main() or 0)
