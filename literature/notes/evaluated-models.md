# 선행 PII 벤치마크의 평가 모델 + 2026-09 한국어·오픈 모델 현황

- 조사일 2026-09-13. `docs/models.md`(리더보드 선정)와 ADR-0005의 근거. **[?]** = 미확인.

## A. 논문 × 평가 모델

| 논문 | LLM | 규칙·NER·소형 베이스라인 | 실행 방식 | 언어 |
|---|---|---|---|---|
| PII-Bench (arXiv 2502.18545) | GPT-4o-2024-08-06, Claude-3.5-Sonnet, DeepSeek-Chat(V3); Llama-3.1-70B/8B-Instruct, Qwen2.5-72B/7B-Instruct, 0.5~3B SLM | BiLSTM-CRF | zero-shot (naive/CoT/SC/plan-and-solve), temp 0 | EN |
| REDACT (arXiv 2606.19881) | GPT-4.1, Claude Sonnet 4.6 (judge: GPT-5.2, Sonnet 4.6, Gemini 2.5 Pro) | Presidio, GLiNER-multi, OpenAI Privacy Filter | zero-shot | 25개 언어 (한국어 포함 여부 [?]) |
| OPF cross-lingual eval (arXiv 2608.02616) | GPT-4o | OPF 1.5B, Presidio 2.2, GLiNER multitask-large, XLM-R NER (+fine-tune) | zero-shot + light FT | 14개 언어, **한국어 없음** |
| PRvL (arXiv 2508.05545) | LoRA: Llama-3.1-8B, 3.2-3B, DeepSeek distill [?], Mixtral, T5; RAG: GPT-4, o3; FalconMamba | BERT-NER | PEFT / instruction / RAG | en/es/it |
| Mind the Gap (arXiv 2609.03464) | Qwen2.5-3B-Instruct | spaCy, Presidio | zero-shot OOD | EN |
| RAT-Bench (arXiv 2602.12806) | 12 anonymizers: Anthropic PII-purifier prompt, Clio, Rescriber(Llama-3.1-8B), Staab식 iterative, GPT-3.5/4 clinical prompts | Presidio, Azure PII, Scrubadub, spaCy, Flair | off-the-shelf + LLM re-ID attacker | en/es/zh |
| **Thunder-DeID** (Findings EMNLP 2025) | 자체 DeBERTa-v3 스타일 Ko/En 인코더 360M / 800M / 1.5B (full FT) | **Polyglot-Ko 1.3B, EXAONE-3.5 2.4B** (디코더 베이스라인); 법원 규칙 시스템(8~15%) | token classification | **KO** |
| KDPII (IEEE Access 2024) | "representative language models available on the market" — 목록 [?] | — | fine-tune [?] | **KO** |
| Advanced Anonymizers (ICLR 2025) | GPT-4-1106, GPT-3.5-16k, Llama-3.1-70B/8B, Yi-34B, Qwen1.5 4B~72B, Mistral-7B, Mixtral 8x7B/8x22B, Claude 3 Opus, Gemma; FT Llama-2-7B | Azure Language, Presidio, Dou et al. span model, Dipper | adversarial loop | EN |
| AmBench (arXiv 2505.14549) | GPT-5, GPT-5-mini, Gemini 2.5 Pro, DeepSeek R1; GPT-4o, Gemini 2.5 Flash, 1.5 Pro, DeepSeek V3; gpt-oss-20B, Gemma 2 9B, Qwen2.5 7B, Llama 3.1 8B | Flair NER, PrivateAI | zero-shot temp 0 | EN |
| Anonymous-by-Construction (arXiv 2603.17217) | gpt-oss-20B, DeepSeek-R1-Distill 7B | Presidio, Google DLP, ZSTS | temp 0 | EN |
| GLiNER2-PII (arXiv 2605.09973) | — | OPF, nvidia/gliner-PII, urchade/gliner_multi_pii-v1, knowledgator/gliner-pii-base | zero-shot span | 7 유럽어 |
| (참고) K-LegalDeID (EACL 2026) | — | KLUE-BERT-CRF F1 0.9923 | FT | KO 법률 |
| (참고) MDPI Appl.Sci 15(24):12977 | Claude Sonnet 4.5, GPT-5, Gemini 2.5 Pro — 한국어 이름 인식 | — | prompting | KO |

빈도: Presidio 6, GPT-4계열 6, Llama-3.1-8B 5, Claude 4, DeepSeek 4, Qwen2.5 3(+Qwen1.5), GLiNER 3, OPF 3, gpt-oss-20B 2.

### OpenAI Privacy Filter
1.5B total / 50M active MoE, banded attention 토큰 분류기, Viterbi-CRF, 33 BIOES, 128k ctx, Apache-2.0, 8 카테고리, "primarily English" (2026-04). 한국어 fine-tune: OpenMed/privacy-filter-multilingual (16개 언어, 54 타입, Apache-2.0) — https://huggingface.co/openai/privacy-filter , https://huggingface.co/OpenMed/privacy-filter-multilingual

## B. 후보 모델 (2026-09)

### Frontier API
GPT-5.5 (2026-04-24) / GPT-5.4-mini·nano (2026-03) · Claude Opus 5 (2026-07-24) / Sonnet 5 (2026-06-30) [?] ID 확인 · Gemini 3.1 Pro / 3.5 Flash GA / 3.8 Flash (2026-09-02) [?] · **HyperCLOVA X HCX-007** (hybrid reasoning, 128k; CLOVA Studio) · **Solar Pro 4** (2026-08, 524k, en/ko/ja) · A.X(SKT)·Mi:dm(KT) API [?] 외부 접근.

### 오픈 범용 대형
Qwen3.5-35B-A3B / 27B / 122B-A10B / 397B-A17B (Apache-2.0, 256k, 2026-02~03); Qwen3.6·3.8 (2026-04·08) · gpt-oss-120b/20b (Apache-2.0) · Gemma 4 31B / 26B-A4B / 12B / E4B / E2B (**Apache-2.0**, 2026-07) · Llama 4 Scout/Maverick (Llama 4 Community; **한국어 공식 미지원**) · Mistral Small 4 119B-A6.5B (Apache-2.0, 한국어 명시) · DeepSeek V3.x/R1 (MIT), V4 [?] · GLM-5.1 754B-A40B (MIT), Kimi K2/K3 · Phi-4-reasoning 14B (MIT).

### 한국어 개발 오픈
| 모델 | 크기 | 라이선스 | 비고 |
|---|---|---|---|
| HyperCLOVAX-SEED-Text-Instruct 0.5B/1.5B; Think-14B (2025-06); Think-32B(VLM); Omni-8B | | SEED custom (상용 허용 [?]) | Naver |
| EXAONE 3.5 (2.4/7.8/32B), Deep, **4.0 (1.2B/32B, 128k)**, 4.5-33B(VLM) | | **NC (연구 전용)** | LG. Thunder-DeID 베이스라인 계열 |
| K-EXAONE-236B-A23B, **K-EXAONE-2.0-750B-A37B** (2026-08) | MoE | Apache-2.0 | 정예팀 |
| Kanana-1.5 (2.1B/8B, Apache-2.0); **Kanana-2-30B-A3B** (2026-01); Kanana-2 3B/1.3B | | Kanana Open License | Kakao. 한국어 토크나이저 +30% |
| A.X 3.1 (34B, from scratch, Apache-2.0) + 3.1-Light 7B; A.X 4.0 (72B, Qwen2.5 base) + 4.0-Light 7B; A.X K1 519B; **A.X K2 688B-A33B** (Apache-2.0, 2026-07) | | | SKT. `skt/A.X-Encoder-base` 0.1B 인코더도 있음 |
| Mi:dm 2.0 Base-Instruct 11.5B / Mini 2.3B | | **MIT** | KT |
| Solar Open 100B-A12B (2025-12); **Solar Open 2 250B-A15B** (2026-07, 1M) | | Upstage Solar License | 단일 GPU 불가 |
| Motif-2-12.7B (Apache-2.0); **Motif-3 314B-A13B** (MIT, 2026-08) | | | 법률·금융 데이터 강조 |
| Tri-7B/21B/70B (custom); Gravity-16B-A3B / 30B-A5B (Apache-2.0) | | | Trillion Labs |
| Llama-VARCO-8B (NC AI, 2024), 42dot 1.3B, KONI-Llama3.1-8B (KISTI) | | | 구형 |

독자 AI 파운데이션 모델 (국가대표): 1차 5팀 → 2차(2026-08-18) Upstage·SKT·LG 진출, Motif 탈락. 오픈 공개: Solar Open 2, A.X K2, K-EXAONE 2.0, Motif 3.

### 규칙·NER·PII 전용 (한국어 관련)
- **Presidio 2.2.364** (2026-07, repo `data-privacy-stack/presidio`): `ko` recognizer 5종 (KrRrn·KrFrn·KrBrn·KrDriverLicense·KrPassport) — **기본 비활성**. 계좌·카드 한국형 없음. 이름용 한국어 spaCy NER 없음.
- **ko-pii 1.16.0** (2026-09-09, MIT): 33 타입, RRN/FRN/BRN/CRN 체크섬, 카드 Luhn+BIN, 계좌 앵커(은행명 60+).
- OpenMed/privacy-filter-multilingual (KO 포함), openai/privacy-filter (EN).
- GLiNER2-PII 0.3B (CC-BY-4.0, 한국어 없음), nvidia/gliner-PII, urchade/gliner_multi_pii-v1 (mDeBERTa, 한국어 미검증).
- Piiranha-v1 (CC-BY-NC-ND, 유럽어).
- alphagyuu/Korean-PII-Masking-BertForTokenClassification (kcbert, 17 BIO, Apache-2.0); skan0779/korean-pii (KoELECTRA + regex + Presidio).
- KLUE-RoBERTa-large, KoELECTRA, KLUE-BERT-CRF (K-LegalDeID).
- Microsoft Purview SIT: 한국 3종만 (RRN·여권·운전면허). 한국형 계좌·카드 SIT 없음.

## C. 80GB GPU 1장 가능 여부
가능: ≤10B 전부, Kanana-2-30B-A3B (~60GB), Qwen3.5-35B-A3B (~70GB), Qwen3.6/3.8-27B, Gemma 4 31B/26B-A4B, HyperCLOVAX-Think-14B/32B, EXAONE 4.0/4.5 32~33B (~64GB, 짧은 ctx), A.X-3.1 34B, Motif-2-12.7B, Mi:dm 12B, gpt-oss-120b (MXFP4 ~63GB), Tri-21B, Gravity-30B-A5B.
4-bit 필요: A.X-4.0 72B, Tri-70B, Llama 4 Scout.
불가: Solar Open 100B/250B, A.X K1/K2, K-EXAONE, Motif-3, DeepSeek V3/V4, GLM-5.1, Kimi, Llama 4 Maverick, Qwen3.5-397B.

## D. 미확인 [?]
KDPII 모델 목록(IEEE 접근 불가); REDACT 25개 언어에 한국어 포함 여부; Claude/Gemini 2026-09 정확한 모델 ID; Kanana-2 SLM 출시일; DeepSeek V4 라이선스; ETRI·Samsung 오픈 가중치(없음으로 보임).


## E. 2026-09-13 재검증 — 정확한 API ID·접근성 (1차 출처)

### 표준 세트 ID
| 벤더 | 현행 ID | 가격 in/out /1M | ctx | 출처 |
|---|---|---|---|---|
| OpenAI | `gpt-5.6-sol` (=`gpt-5.6`), `gpt-5.6-terra`, `gpt-5.6-luna`; open `gpt-oss-120b`/`20b` | Sol $4/$20 (프로모 $2/$10 ~11/21 ⚠), Terra $2/$12, Luna $0.20/$1.20 | 1.05M / out 128K | developers.openai.com/api/docs/models |
| Anthropic | `claude-fable-5-1`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001` | $10/$50, $5/$25, $2/$10, $1/$5 | 1M (Haiku 200K) | platform.claude.com/docs/en/about-claude/models/overview |
| Google | `gemini-3.8-flash` (stable), `gemini-3.7/3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-pro-preview` (preview), `gemini-2.5-pro` (유일 stable Pro) | 3.8 Flash $0.75/$3.75 (~12/31), 3.1 Pro $2/$12 | 1,048,576 / out 65,536 | ai.google.dev/gemini-api/docs/models |
| Qwen | `Qwen/Qwen3.6-35B-A3B` (Apache, 262K→1M), `Qwen/Qwen3.8-27B` (dense, 2026-08). **Qwen3.8 A3B 없음** | — | | huggingface.co/Qwen |
| Meta | Llama 4 Scout/Maverick 이후 신규 없음 (Llama 5 기사는 추측) | | | huggingface.co/meta-llama |
| Google open | Gemma 4 (2026-04-02): E2B/E4B/26B-A4B/31B, Apache-2.0, 게이트 없음 | | 128K/256K | blog.google …/gemma-4/ |
| DeepSeek | `DeepSeek-V4-Pro` (1.6T/49B), `DeepSeek-V4-Flash` (284B/13B), MIT, 1M. R2 없음 | | | huggingface.co/deepseek-ai |
| Mistral | `Mistral-Small-4-119B-2603` (Apache, 256K); Ministral 3 3B/8B/14B | | | |

### 한국어 모델 접근성
- **CLOVA Studio (HCX-007/005/DASH-002)**: NCP 콘솔 이용 신청(셀프서브) → 테스트 API 키 → 서비스 앱 심사(AI 윤리·오남용 모니터링 계획 요구, 기간 미명시). 네이티브 `POST https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-007`; **OpenAI 호환 `https://clovastudio.stream.ntruss.com/v1/openai`** (기본 max_tokens 512, response_format 미지원). Rate limit (2025-07-17 기준): 테스트 HCX-007 60 QPM/60K TPM, 서비스 180 QPM/300K TPM. ctx 128K, out 4,096. 가격 KRW/1K 토큰 — 콘솔 JS 렌더로 미추출 [?]. 출처 guide.ncloud-docs.com/docs/clovastudio-ratelimiting, api.ncloud-docs.com/docs/clovastudio-openaicompatibility
- **Solar Pro 4**: `api.upstage.ai/v1` `solar-pro4`, OpenRouter `upstage/solar-pro4`; $0.30/$1.20 (프로모 $0.09/$0.36 ~10/10); ctx 384K~524K 보고 상이.
- **HF 게이트**: HyperCLOVAX-SEED·Kanana-2·EXAONE-4.x·A.X·Mi:dm 전부 `gated: false`.
- **라이선스 핵심**: SEED — 10M MAU/경쟁 서비스 시 별도, "Powered by HyperCLOVA X"; Kanana — 출력물은 파생물 아님, "Powered by Kanana"; EXAONE 1.2-NC — 연구 전용, **§2.1b 논문 발표 명시 허용**; A.X-4.0-Light·3.1-Light Apache-2.0, A.X-4.0 72B Qwen license; Mi:dm 2.0 MIT.
- **외부 API 없음**: A.X (K1 API는 중기부 챌린지 3개사 한정, a.x@sk.com), Mi:dm (K 2.5 Pro 미공개).
- **3rd-party 호스팅**: OpenRouter에 `upstage/solar-pro4`만. Friendli는 EXAONE·SEED·Mi:dm dedicated endpoint만 (K-EXAONE-2.0 serverless 2026-08-06~09-06 후 종료). Bedrock·Azure Foundry·Together·Fireworks에 한국 모델 없음.
