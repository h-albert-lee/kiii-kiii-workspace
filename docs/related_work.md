# K-Financial PII Benchmark — Related Work & Positioning

*Working notes, 2026-09-08. Target: short paper (4 pages + refs), workshop-tier (PrivateNLP / TrustNLP / FinNLP / SafeGenAI) or Findings.*
*Venues verified against ACL Anthology / OpenReview / arXiv pages where possible; items flagged `[arXiv]` had no accepted-venue record at survey time.*

---

## 0. One-paragraph verdict

**No public benchmark exists for Korean financial-domain PII detection or de-identification.** Korean PII work is conversational (KDPII, Jang et al. 2024) or legal (Thunder-DeID, Findings EMNLP 2025); financial PII work is English-only and mostly general NER (FiNER-ORD) or synthetic datasets without papers (Gretel finance PII). Every academic multilingual PII benchmark found (REDACT, RECAP, DialogPII, Centific) excludes Korean. Long-context / multi-subject PII handling is essentially unstudied — PII-Bench's multi-subject split is the only direct evidence, and it shows LLMs degrade there. The gap is real, but it is a **domain + language + setting** gap, not a **task** gap: span extraction and de-identification are mature tasks. The paper therefore has to earn its novelty through (a) the regulation-grounded taxonomy (개인정보보호법 + 신용정보법 + FSC 가명·익명처리 안내서), (b) the long-context multi-subject setting with consistency metrics, and (c) findings that generic PII systems fail on Korean financial identifiers. Adversarial misuse (hyper-personalized phishing) is best kept as motivation plus a small probe, not the main contribution — a 4-page paper cannot carry two benchmarks.

---

## 1. Related work, organized by axis

### 1.1 PII detection / extraction benchmarks (LLM era)

| Paper | Venue | Lang / Domain | What it does | Relevance to us |
|---|---|---|---|---|
| **PII-Bench** (Shen et al.) | `[arXiv]` 2502.18545, 2025 | EN, general | 2,842 samples, 55 PII subcategories; query-aware masking; **single- vs multi-subject** split. LLMs detect PII fine but fail relevance judgments in multi-subject text. | Only direct evidence that multi-entity settings hurt LLMs. Fudan Fintech group — cite for multi-subject framing. |
| **REDACT** (Vats et al., ServiceNow) | `[arXiv]` 2606.19881, 2026 | 25 langs, general | 13.4k records, 51 types, sensitivity-tier stratification; Presidio / GLiNER / OpenAI Privacy Filter / GPT-4.1 / Claude Sonnet 4.6. Aggregate F1 hides tier-specific failures. | Closest methodological template (stratified recall by sensitivity). **Korean not included** — check v-latest. |
| **OpenAI Privacy Filter eval** (Uppala) | `[arXiv]` 2608.02616, 2026 | 14 langs incl. CJK; finance/med/legal | 32 benchmarks incl. Gretel finance docs; OPF strong on Latin-script synthetic PII, degrades on non-Latin scripts. | Direct evidence that off-the-shelf PII filters degrade on CJK → motivates Korean-specific eval. |
| **PIIBench** (Jha) | `[arXiv]` 2604.15776, 2026 | multi, incl. finance | Unifies 10 datasets → 48 types; all systems span-F1 < 0.14 due to schema heterogeneity. | Cite for "taxonomy heterogeneity" problem; our contribution is a *single* legally-grounded schema. Single-author preprint — cite cautiously. |
| **Mind the Gap** (Zafar & Nowaczyk) | `[arXiv]` 2609.03464, 2026 | EN | 660-example OOD stress test (typos, code-switching, overlapping entities). | Robustness-shift framing; we can borrow shift categories. |
| **SPY** (Savkin et al.) | NAACL-SRW 2025 | EN, med/legal | Synthetic PII dataset + generation pipeline. | Precedent for LLM-synthesized PII benchmark accepted at a workshop. |
| **RECAP** (Rajgarhia et al.) | NeurIPS 2025 WS | 13 low-res locales | Regex + LLM hybrid, 300+ entity types. | Hybrid baseline design; no Korean. |
| **PRvL** (Garza et al.) | `[arXiv]` 2508.05545, 2025 | EN/ES/IT | Systematic LLM redaction study across architectures/training regimes; SPriV privacy-violation score. | Metric idea (privacy-violation score); baseline suite. |
| **AmBench** (Pham et al.) | FAccT 2026 | EN | Ambiguous-name recognition failures; 12 LLMs lose 20–40% recall. | Korean names are highly ambiguous (common surnames, homonyms) — analogous failure mode worth a probe. |
| **CAPID** (Ponomarenko et al.) | `[arXiv]` 2602.10074, 2026 | EN | Context-aware selective PII detection for QA. | Selective/contextual detection line — adjacent, not core. |
| **Adaptive PII Mitigation** (Asthana et al., IBM) | AAAI-25 PPAI WS | EN | GDPR/CCPA policy-driven masking. | Regulation-driven taxonomy precedent, but Western law only. |
| **PII-Scope** (Nakka et al.) | IJCNLP-AACL 2025 | EN | Training-data PII *extraction attack* benchmark (memorization). | Different threat model — cite to distinguish inference-time detection from memorization leakage. |

Datasets without papers: **ai4privacy pii-masking-300k / openpii-1m** (no Korean; 3M APAC release lists Korean but financial pack is commercial), **Gretel synthetic_pii_finance_multilingual** (55.9k rows, 7 EU langs, ~60 financial doc types, IBAN/SSN/customer IDs — the most finance-relevant public PII resource; **no Korean**), **OpenMed privacy-filter-multilingual** (model card: CJK "remain the main bottleneck").

### 1.2 De-identification / anonymization with LLMs

| Paper | Venue | Lang / Domain | What it does | Relevance |
|---|---|---|---|---|
| **TAB** (Pilán et al.) | Computational Linguistics 2022 | EN legal | 1,268 ECHR cases; direct vs quasi identifiers; re-identification-risk-weighted recall + information-loss metrics. | **The** metric reference for de-identification. Adopt its direct/quasi split and risk-weighted recall. |
| **Neural Text Sanitization** (Papadopoulou et al.) | AACL 2022 | EN legal | Entity recognition → risk scoring → span selection minimizing info loss. | Pipeline baseline structure. |
| **LLMs are Advanced Anonymizers** (Staab et al.) | ICLR 2025 | EN online | Adversarial anonymization: LLM attacker infers attributes, LLM anonymizer rewrites iteratively; 13 LLMs. | Attribute-inference evaluation paradigm; relevant if we add an "identifiability" probe. |
| **RUPTA** (Yang, Zhu, Gurevych) | ACL 2025 | EN | Privacy evaluator + utility evaluator + optimizer; distillation to small models. | Privacy–utility trade-off framing. |
| **RAT-Bench** (Krčo et al.) | `[arXiv]` 2602.12806, 2026 | multi | Population-level re-identification risk from LLM-inferable attributes; LLM anonymizers fail on non-standard identifier spellings and indirect identifiers. | Closest "anonymization benchmark" in 2026; we differ on language, domain, long-context. |
| **AURA** (Li, Wen, Li) | `[arXiv]` 2605.30848, 2026 | EN interviews | Anonymization vs web-search-enabled agentic re-identification. | Agentic re-ID threat model — cite in future-work. |
| **NAP²** (Huang et al.) | Findings EMNLP 2025 | EN dialogue | Naturalness + privacy rewriting; PRIVACY_NLI metric. | Rewriting-based de-ID (vs. tag masking). |
| **Pasch & Cha** | PrivateNLP 2025 | EN | Masking vs pseudonymization with **back-mapping** for personal writing. | Consistent pseudonymization across mentions — our long-context consistency metric builds on this. |
| **Anonymous-by-Construction** (Albanese et al., Veritran) | `[arXiv]` 2603.17217, 2026 | EN banking dialogues | On-prem LLM replaces PII with type-consistent surrogates on ABCD customer-service data; PII recall 0.99, utility retained. | **Closest financial-services LLM de-ID paper.** English only, industry-authored, no regulatory taxonomy. |
| **Clinical de-ID line** — DeID-GPT `[arXiv]`; Pissarra et al. `[arXiv]`; Panchal et al. BMJ HCI 2026; Kim, Hahm, Lee EMNLP 2024; Baroud et al. PrivateNLP 2025 | mixed | EN clinical | GPT-4 zero-shot de-ID; SFT small models beat ICL LLMs; indirect-identifier schema (9 categories). | HIPAA is the mature analogue of what we do for Korean finance. Baroud's *indirect identifier* schema maps onto 성현's "behavioral quasi-identifiers". |
| **Deußer et al. survey** | IEEE DSAA 2025 | — | Text anonymization survey incl. finance sector. | Single survey cite. |

### 1.3 Korean PII / de-identification

| Paper | Venue | Domain | What it does | Relevance |
|---|---|---|---|---|
| **KDPII** (Fei, Kang, …, Kim; Yonsei) | IEEE Access 2024; Zenodo v2 Dec 2024 | KO dialogue | Korean PII classification framework + ~4.9k synthetic/crowdsourced dialogues dense with PII. Models recognize universal PII (email, phone) far better than **Korean-specific PII (주민등록번호 formats, Korean addresses)**. | De-facto Korean PII eval set. Their finding is our motivation in miniature. Not finance; no 신용정보법. |
| **Jang et al.** | Applied Sciences (MDPI) 2024 | KO SNS/chat | 33-tag Korean PII set (incl. credit card, bank account); KoBERT/ELECTRA F1 0.943. | Tag set overlaps ours; no financial *context*. |
| **Thunder-DeID** (Hahm et al., SNU) | **Findings EMNLP 2025** | KO court judgments | 6,700 judgments, 48k annotations, 3-tier taxonomy (16 → 80 → 729 labels) **including 계좌번호, card numbers, financial institutions, financial products**; DNN pipeline token micro-F1 0.91. | **Most reusable prior art and the paper reviewers will compare us to.** Must clearly differentiate: their domain is legal, corpus is real judgments, taxonomy is court-driven; ours is finance, synthetic long-context, 신용정보법-driven. |
| **최혜지 et al.** | 한국콘텐츠학회논문지 2024 | KO dialogue | General NE vs PII-NE divergence; location/org/date need context to be judged PII. | Supports "context-dependent identifiability" axis. |
| **ko-pii** (Marker-Inc-Korea) | GitHub, 2026 | KO | Rule/checksum-based detector, 33 categories; F1 0.66 on KDPII. | Free rule-based baseline; also validates 주민등록번호/사업자등록번호 checksums for synthetic data. |
| **GenON blog**; **지란지교 IDFILTER** | industry | KO finance | KcBERT-CRF PII masker for financial customer text; had to **synthesize** data from AI Hub 민원 seeds because none existed. | Market evidence of the gap. Blog-level cite only. |
| **KFinEval-Pilot** (Hwang et al., KB) | `[arXiv]` 2504.13216, 2025 | KO finance | Korean financial knowledge/legal/toxicity QA. **No PII task.** | Shows Korean-finance LLM eval interest; we fill the privacy slot. |

Regulatory sources (define the label space; cite as grey literature): 개인정보보호법 (고유식별정보 §24, 민감정보 §23), 신용정보법 (개인신용정보, 2020 데이터3법), **금융분야 가명·익명처리 안내서** (금융위·금감원, rev. 2022-01), 생성형 AI 개발·활용을 위한 개인정보 처리 안내서 (개인정보위, 2025-08). Note: no AI Hub text de-identification dataset was found.

### 1.4 Financial-domain NER / privacy

FiNER-ORD (`[arXiv]` 2023, PER/LOC/ORG only) and Lu & Huo (FinNLP@COLING 2025, LLMs on FiNER-ORD) are general NER, not PII. Mishra et al. (Sci. Rep. 2025) do hybrid PII anonymization on English invoices/audit reports with Faker data. CNFinBench (KDD 2026) evaluates Chinese financial agents incl. unauthorized-disclosure scenarios but is not span-level. **No financial PII benchmark grounded in any jurisdiction's financial privacy statute (GLBA, PCI-DSS, 신용정보법…) was found.**

### 1.5 Contextual privacy, inference attacks, and misuse (for the motivation / optional track)

| Paper | Venue | Relevance |
|---|---|---|
| **ConfAIde** (Mireshghallah et al.) | ICLR 2024 | CI-theory benchmark; GPT-4 leaks in 39% of contexts. Cite for "legal-but-harmful information flows". |
| **PrivacyLens** (Shao et al.) | NeurIPS 2024 D&B | Norm awareness vs. action gap in agents. |
| **GoldCoin** (Fan et al.) | EMNLP 2024 (Outstanding) | Grounds LLMs in privacy *law* (HIPAA) via CI → synthetic scenarios. **Precedent for statute-grounded synthetic data.** |
| **PrivaCI-Bench** (Li et al.) | ACL 2025 | HIPAA/GDPR/EU AI Act compliance; no finance statute. |
| **Beyond Memorization** (Staab et al.) | ICLR 2024 | LLM attribute inference from text, 85% top-1. The threat behind 성현's "behavioral info → profiling". |
| **AutoProfiler** (Du et al.) | Findings ACL 2026 | Agentic profile aggregation / de-anonymization from post history. |
| **Heiding et al.** spear-phishing series | IEEE Access 2024; `[arXiv]` 2412.00586; `[arXiv]` 2511.11759 | Fully automated OSINT → personalized phishing matches human experts (54% click). **The empirical anchor for "hyper-personalized phishing".** |
| **Engineered Persuasion** (Francia et al.) | `[arXiv]` 2609.04410, 2026 | Click-intent odds +28% per personalization level; *accuracy* of personal details matters. Directly supports why behavioral/quasi-identifiers matter. |
| **InjecAgent** (ACL 2024 Findings), **AgentDojo** (NeurIPS 2024 D&B; banking suite), **AgentLeak** (IEEE Access 2026; finance scenarios) | — | Financial-scenario PII exfiltration exists, but with ad hoc PII schemas. |
| **The Good and The Bad** (Zeng et al.) | Findings ACL 2024 | RAG datastore PII extraction. Future-work cite for RAG deployments in banks. |

**Combined-gap check:** no paper combines a jurisdiction-grounded PII taxonomy with adversarial misuse evaluation in finance. That is attractive, but see §3 on why it should not be the short paper's spine.

---

## 2. Gap analysis

| Dimension | State of the art | Our position |
|---|---|---|
| Language | Korean PII: KDPII (dialogue), Thunder-DeID (legal). All multilingual PII benchmarks exclude Korean. | Korean, first in finance. |
| Domain | Finance PII: English only (Gretel, Mishra, Albanese). | Korean finance: 계좌/카드/증권계좌, 고객번호, 거래내역, 투자성향, 상담기록. |
| Taxonomy grounding | Health (HIPAA: GoldCoin, clinical de-ID), EU (GDPR: PrivaCI). Thunder-DeID is court-practice-driven. | 개인정보보호법 + 신용정보법 + FSC 안내서 → **Legal PII** tier; plus an **Identifiability** tier (quasi/behavioral) inspired by TAB's quasi-identifiers and Baroud's indirect identifiers. |
| Setting | Sentence/short-passage; PII-Bench multi-subject is the only multi-entity split. | **Long-context (multi-page), multi-subject, coreferent mentions**; consistency-of-pseudonymization metric. |
| Tasks | Span extraction (F1); anonymization (TAB risk-weighted recall, utility). | Both, on the same documents; plus cross-mention consistency and format-validity (checksum-valid 주민번호/계좌번호 → distinguishes rule vs. model failure). |
| Evaluated systems | Presidio, GLiNER, OPF, GPT/Claude, small SFT models. | Same (API frontier models included) plus **Korean local LLMs** (HyperCLOVA X, EXAONE, Kanana, etc.). The API-vs-local gap is a headline analysis because Korean financial firms often cannot send PII to external APIs. |

---

## 3. Candidate contribution framings for a short paper

**Framing A — "Kiii Kiii: a regulation-grounded Korean financial PII benchmark for long-context extraction and de-identification."** *(ADOPTED 2026-09-08.)*
Decision notes: corpus generation and span-extraction systems are **not** restricted to local models — use whatever generator gives the best data (API or local; the Toss-side constraint only applies to Toss-internal augmentation), and evaluate API models alongside local ones. The leaderboard must include Korean local LLMs, and the paper's 4 pages are budgeted as taxonomy + corpus + leaderboard + analysis.
Contributions: (1) two-tier taxonomy (Legal PII per 개인정보보호법/신용정보법; Identifiability tier of quasi/behavioral attributes) with a mapping table to statutes; (2) synthetic long-context multi-subject corpus (bank/securities documents, KYC forms, complaint/consultation transcripts, transaction statements), with format-valid identifiers; (3) two tasks and metrics: span extraction (entity-level F1 stratified by tier, per KDPII/REDACT) and de-identification (TAB-style risk-weighted recall + information-loss utility + **cross-mention consistency**); (4) leaderboard of ~10–15 systems incl. Korean LLMs and rule baselines; (5) headline findings, e.g., "universal PII ≈ solved, Korean financial identifiers and quasi-identifiers are not; performance collapses with number of subjects / context length; local models X vs API models Y."
Why it fits 4 pages: one dataset, two closely related tasks, one leaderboard, three findings. Reviewers' comparison target is Thunder-DeID + KDPII — differentiation is explicit (domain, setting, statute).

**Framing B — "Legal but dangerous: benchmarking identifiability of Korean financial customers beyond statutory PII."**
Make the Identifiability tier the star: show that even after statutory PII is removed, LLM attackers (Staab-style attribute inference / AutoProfiler-style aggregation) can re-identify or profile customers from consultation/behavioral text, and that this enables personalized phishing (Heiding, Francia). Strong story, higher novelty, but requires a second evaluation apparatus (attacker LLMs, re-ID protocol, possibly human-subject or judge-based phishing-quality eval) — hard in 4 pages and 2–3 weeks. Also carries dual-use reviewer risk. **Better as the follow-up long paper.**

**Framing C — "Do PII filters work in Korean finance? An audit."**
Pure evaluation of existing tools (Presidio, ko-pii, OPF, GLiNER, GPT/Claude, Korean LLMs) on our data, no new taxonomy claims. Cheapest, but weakest novelty and it forfeits the taxonomy contribution that differentiates us from Thunder-DeID.

**Recommended combination:** A as the spine; borrow one paragraph and one small table from B as "identifiability probe" (e.g., attribute-inference accuracy on de-identified outputs, or an LLM-judge rating of how targetable a customer remains), explicitly framed as motivation and future work. This keeps 성현's phishing angle in the paper without making it a second benchmark.

---

## 4. Risks and how to pre-empt them

1. **"Thunder-DeID already has financial entities."** — Answer in related work with a side-by-side: their financial labels are incidental (mentioned in judgments), not financial *documents*; no 신용정보법 alignment; no multi-subject long-context; no de-ID consistency metric.
2. **Synthetic-only data.** — Precedent: SPY (NAACL-SRW), CI-Bench, GoldCoin, PrivacyLens all synthetic; KDPII partially synthetic. Mitigate with (a) format-valid identifiers via checksums, (b) template + LLM paraphrase diversity stats, (c) a small human-verified subset (e.g., 200 docs), (d) a realism check by a domain partner (Toss Securities) — even a sentence about practitioner review helps.
3. **Taxonomy reproducibility.** — Publish the statute → category mapping table; state that the Identifiability tier is *not* a legal claim.
4. **Contamination / leakage of evaluated models.** — Synthetic data generated by local models; report which generator was used and exclude it from the leaderboard or flag it.
5. **Long-context claims.** — Control length and subject count explicitly (e.g., 1 / 3 / 8 subjects × 1k / 4k / 16k tokens) so the degradation curve is a clean figure, not an anecdote.
6. **Dual-use.** — Keep misuse content as a probe on *outputs of de-ID systems*, not as a released attack prompt set.

---

## 5. What to read next (priority order)

1. Thunder-DeID (Findings EMNLP 2025) — taxonomy tiers, annotation guideline, metrics. Reuse label naming where compatible.
2. KDPII paper + Zenodo v2 — Korean-specific PII findings; consider using as an out-of-domain transfer test.
3. TAB (CL 2022) — de-ID metrics to adopt verbatim.
4. PII-Bench — multi-subject protocol.
5. REDACT — stratification and reporting template.
6. Pasch & Cha (PrivateNLP 2025) — pseudonymization back-mapping → consistency metric.
7. 금융분야 가명·익명처리 안내서 + 신용정보법 시행령 — identifier list for the Legal tier.
8. Albanese et al. (Anonymous-by-Construction) — closest financial de-ID paper; surrogate-generation design.

---

## Appendix — full citation index (survey agents' verified URLs)

- PII-Bench — https://arxiv.org/abs/2502.18545
- PIIBench (Jha) — https://arxiv.org/abs/2604.15776
- REDACT — https://arxiv.org/abs/2606.19881
- OpenAI Privacy Filter eval — https://arxiv.org/abs/2608.02616
- Mind the Gap — https://arxiv.org/abs/2609.03464
- SPY — https://aclanthology.org/2025.naacl-srw.23/
- GLiNER2-PII — https://arxiv.org/abs/2605.09973
- RECAP — https://arxiv.org/abs/2510.07551
- PRvL — https://arxiv.org/abs/2508.05545
- Unmasking PII maskers — https://arxiv.org/abs/2504.12308
- AmBench — https://arxiv.org/abs/2505.14549
- CAPID — https://arxiv.org/abs/2602.10074
- Adaptive PII Mitigation — https://arxiv.org/abs/2501.12465
- PII-Scope — https://aclanthology.org/2025.ijcnlp-long.195/
- TAB — https://aclanthology.org/2022.cl-4.19/
- Neural Text Sanitization — https://aclanthology.org/2022.aacl-main.18/
- LLMs are Advanced Anonymizers — https://arxiv.org/abs/2402.13846
- RUPTA — https://aclanthology.org/2025.acl-long.1404/
- IncogniText — https://arxiv.org/abs/2407.02956
- RAT-Bench — https://arxiv.org/abs/2602.12806
- AURA — https://arxiv.org/abs/2605.30848
- NAP² — https://aclanthology.org/2025.findings-emnlp.476/
- Pasch & Cha — https://aclanthology.org/2025.privatenlp-main.3/
- Anonymous-by-Construction — https://arxiv.org/abs/2603.17217
- DeID-GPT — https://arxiv.org/abs/2303.11032 ; Pissarra et al. — https://arxiv.org/abs/2406.00062 ; Panchal et al. — https://pmc.ncbi.nlm.nih.gov/articles/PMC13410914/ ; Kim, Hahm, Lee — https://aclanthology.org/2024.emnlp-main.1181/ ; Baroud et al. — https://arxiv.org/abs/2502.13342
- Deußer survey — https://arxiv.org/abs/2508.21587
- KDPII — https://ieeexplore.ieee.org/document/10681073/ ; https://zenodo.org/records/16759166
- Jang et al. — https://www.mdpi.com/2076-3417/14/13/5682
- Thunder-DeID — https://aclanthology.org/2025.findings-emnlp.682/ ; https://arxiv.org/abs/2506.15266
- 최혜지 et al. — https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART003142051
- ko-pii — https://github.com/Marker-Inc-Korea/ko-pii
- GenON blog — https://www.genon.ai/en/resources/blog/genon-privacy-masking-bert-crf-financial-data-security
- KFinEval-Pilot — https://arxiv.org/abs/2504.13216
- 금융분야 가명·익명처리 안내서 — https://www.fsc.go.kr/po010101/77193
- FiNER-ORD — https://arxiv.org/abs/2302.11157 ; Lu & Huo — https://aclanthology.org/2025.finnlp-1.15/
- Mishra et al. — https://www.nature.com/articles/s41598-025-04971-9
- CNFinBench — https://arxiv.org/abs/2512.09506
- Gretel finance PII — https://huggingface.co/datasets/gretelai/synthetic_pii_finance_multilingual ; ai4privacy — https://huggingface.co/datasets/ai4privacy/pii-masking-300k ; https://www.ai4privacy.com/datasets/pii-masking-3m-asia-pacific/ ; OpenMed — https://huggingface.co/OpenMed/privacy-filter-multilingual
- Centific multilingual PII — https://arxiv.org/abs/2510.06250 ; DialogPII — https://arxiv.org/abs/2606.30312 ; PII-VisBench — https://arxiv.org/abs/2601.05739
- ConfAIde — https://arxiv.org/abs/2310.17884 ; PrivacyLens — https://arxiv.org/abs/2409.00138 ; CI-Bench — https://arxiv.org/abs/2409.13903 ; Operationalizing CI — https://arxiv.org/abs/2408.02373 ; GoldCoin — https://aclanthology.org/2024.emnlp-main.195/ ; PrivaCI-Bench — https://aclanthology.org/2025.acl-long.518/ ; PrivQA — https://arxiv.org/abs/2310.02224 ; IDP-Bench — https://arxiv.org/abs/2606.09908 ; Trust No Bot — https://arxiv.org/abs/2407.11438
- Beyond Memorization — https://arxiv.org/abs/2310.07298 ; AutoProfiler — https://aclanthology.org/2026.findings-acl.485/ ; AgentHarm — https://arxiv.org/abs/2410.09024
- Heiding et al. — https://ieeexplore.ieee.org/document/10466545/ ; https://arxiv.org/abs/2412.00586 ; https://arxiv.org/abs/2511.11759 ; Francia et al. — https://arxiv.org/abs/2406.13049 ; https://arxiv.org/abs/2609.04410
- The Good and The Bad (RAG) — https://aclanthology.org/2024.findings-acl.267/ ; Spill the Beans — https://arxiv.org/abs/2402.17840 ; InjecAgent — https://aclanthology.org/2024.findings-acl.624/ ; AgentDojo — https://arxiv.org/abs/2406.13352 ; AgentDAM — https://arxiv.org/abs/2503.09780 ; Scammer4U — https://arxiv.org/abs/2606.00497 ; AgentLeak — https://arxiv.org/abs/2602.11510 ; PLeak — https://arxiv.org/abs/2405.06823

## Korean financial evaluation (2026-09-23 update)

The paper now cites TWICE / KorFinMTEB (`hwang2025twice`) and NMIXX / KorFinSTS (`lee2025nmixx`), together with KFinEval-Pilot (`hwang2025kfineval`) and KRX Bench (`son2024krx`). They motivate language- and domain-specific evaluation; Kiii² targets typed PII extraction and controlled surface variation rather than embedding similarity or company/financial knowledge. Verified sources and venue notes: `literature/notes/korean-financial-evaluation.md`.
