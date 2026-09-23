# 리더보드 모델 선정 (ADR-0005)

*조사일 2026-09-13, 모델 ID·접근성 1차 출처로 재검증 (같은 날, `literature/notes/evaluated-models.md` §E). `[?]` = 미확인. 가격은 변동이 잦으니 실험 직전 다시 볼 것.*

## 현재 실행 범위 (2026-09-20, ADR-0019)

목표 코퍼스는 총 1,440건이다. 평가 준비안은 **LLM 4개 + 베이스라인 3개**: Claude Sonnet 5, Gemini 3.8 Flash, Qwen3.6-35B-A3B, Kanana-2-30B-A3B-Instruct-2601; Presidio(한국형 규칙 포함), ko-pii, OpenMed/privacy-filter-multilingual. 아래 14+4는 과거 전체 후보 목록으로 보존하며 이번 실행 범위가 아니다. KLUE fine-tuning 등 본 벤치마크 데이터로 학습·튜닝하는 베이스라인은 제외한다(ADR-0026). Presidio·ko-pii·OpenMed는 기존 규칙/사전학습 가중치를 그대로 사용하는 추론 전용 조건으로만 포함한다. 추가 모델군·thinking ablation은 후순위. Astra/GLM 생성기는 헤드라인 평가에서 제외한다. 실행 ID·revision·접근성·토큰 한도는 평가 전 고정한다. 자세한 범위와 제한은 [ADR-0019](decisions/0019-corpus-1440-compact-evaluation.md).

## 1. 선행 논문이 무엇을 평가했나

| 모델/도구 | 등장 논문 수 (12편 중) | 비고 |
|---|---|---|
| Microsoft Presidio | 6 | REDACT, OPF-eval, Mind the Gap, RAT-Bench, Albanese, Staab |
| GPT-4 계열 (4 / 4o / 4.1) | 6 | 사실상 필수 행 |
| Llama-3.1-8B-Instruct | 5 | 가장 많이 쓰인 오픈 SLM |
| Claude (3 Opus / 3.5 / Sonnet 4.6) | 4 | REDACT는 Sonnet 4.6 |
| DeepSeek (V3 / R1 / distill) | 4 | |
| Qwen2.5 (3B/7B/72B) | 3 (+Qwen1.5 1) | |
| GLiNER 계열 | 3 | REDACT, OPF-eval, GLiNER2-PII |
| OpenAI Privacy Filter | 3 | 2026-04 공개 후 표준 행이 됨 |
| gpt-oss-20B | 2 | AmBench, Albanese |
| Gemini 2.5 | 1 (+judge) | |
| **한국어 평가된 모델** | Thunder-DeID만 | EXAONE-3.5-2.4B, Polyglot-Ko-1.3B (디코더 베이스라인), 자체 DeBERTa 360M/800M/1.5B. KDPII는 모델명 미확인 [?] |

결론: 국제 표준 세트는 {GPT-4급 API, Claude, Llama-3.1-8B, Qwen2.5-7B, DeepSeek, Presidio, GLiNER, OPF}. 이 중 한국어로 평가된 것은 없다. 우리 리더보드는 이 세트와의 **연속성**(리뷰어가 아는 행)과 **한국어 로컬 LLM**(우리 기여)을 함께 갖춰야 한다.

## 2. 리더보드 (14 모델 + 4 베이스라인)

> 접근성 원칙 (2026-09-13, 한울): **가입·심사가 필요한 한국 모델은 제외.** 한국어 모델은 OpenRouter에서 호출 가능한 것 또는 HF 공개 오픈 가중치만. HCX-007(NCP 가입+서비스앱 심사) 제외.

### Frontier API (4) — ID는 2026-09-13 공식 문서 기준
| # | 모델 | 정확한 API ID | 가격 in/out per 1M | ctx | 이유 |
|---|---|---|---|---|---|
| 1 | GPT-5.6 Sol (플래그십) + Luna (저비용 전량) | `gpt-5.6-sol`, `gpt-5.6-luna` | Sol $4/$20 (프로모 $2/$10 ~2026-11-21 ⚠ 두 페이지 불일치), Luna $0.20/$1.20 | 1.05M / out 128K | PII-Bench·AmBench·REDACT GPT 행 연속. gpt-5.4/5.5 ID는 문서에서 사라짐 |
| 2 | Claude Sonnet 5 (전량) + Opus 5 (서브셋) | `claude-sonnet-5`, `claude-opus-5` | $2/$10, $5/$25 (batch 반값) | 1M 정가 | REDACT Sonnet 4.6 연속 |
| 3 | Gemini 3.8 Flash (stable, 전량) + 3.1 Pro (preview, 서브셋) | `gemini-3.8-flash`, `gemini-3.1-pro-preview` | $0.75/$3.75 (~2026-12-31, 이후 2배); Pro $2/$12 | 1,048,576 / out 65,536 | AmBench Gemini 행. **GA 3.x Pro 없음** — Pro는 preview 표기 |
| 4 | **Solar Pro 4** (Upstage) | OpenRouter `upstage/solar-pro4` (`api.upstage.ai/v1`도 OpenAI 호환) | $0.30/$1.20 (프로모 $0.09/$0.36 ~2026-10-10) | 524K [?] 384K~524K 보고 상이 | **한국어 우선 API 유일 채택** — 3rd-party 게이트웨이(OpenRouter)에서 호출 가능한 유일한 한국 모델 |

### 오픈 범용 대형 (4) — 80GB 1장
| # | 모델 | 이유 |
|---|---|---|
| 5 | **Qwen3.6-35B-A3B** (`Qwen/Qwen3.6-35B-A3B`, Apache-2.0, 262K) | Qwen2.5 행의 후속. 3.5 → 3.6으로 교체 (A3B 크기에 3.8은 없음; 3.8-27B dense는 옵션) |
| 6 | gpt-oss-120b (`openai/gpt-oss-120b`, Apache-2.0, MXFP4 ~63GB) | 오픈 OpenAI 행. gpt-oss-2 없음 (safeguard는 분류기 전용) |
| 7 | Gemma 4 31B-it (`google/gemma-4-31B-it`, Apache-2.0, 256K, 2026-04) 또는 26B-A4B | 140+ 언어 사전학습. 게이트 없음 |
| 8 | Llama-3.1-8B-Instruct | 선행 5편의 공통 행 — **연속성 앵커**. Llama 4.x/5는 2026-09 기준 미확인(추측 기사만). Llama 4 Scout는 한국어 미지원 대조군 서브셋 |

### 한국어 개발 오픈 (4)
| # | 모델 | 이유 | 라이선스 |
|---|---|---|---|
| 9 | Kanana-2-30B-A3B-Instruct (`kakaocorp/kanana-2-30b-a3b-instruct`, 2601 refresh) | 한국어 토크나이저 효율 +30%; 3B active | Kanana License — 게이트 없음, 출력물은 파생물 아님, "Powered by Kanana" 표기 |
| 10 | HyperCLOVAX-SEED-Think-14B (`naver-hyperclovax/…`) | 오픈 가중치 + reasoning 토글 → CoT 효과 측정 | SEED License — 게이트 없음, "Powered by HyperCLOVA X" 표기 |
| 11 | EXAONE-4.0-32B (`LGAI-EXAONE/EXAONE-4.0-32B`, 131K) | Thunder-DeID 베이스라인(3.5) 계열 | **License 1.2-NC** — 연구 전용이나 **§2.1b가 논문 발표를 명시 허용**. 논문에 명시 |
| 12 | A.X-4.0-Light 7B (Apache-2.0, Qwen2.5 base) vs A.X-3.1-Light 7B (Apache-2.0, from-scratch) | 같은 회사·크기, 토크나이저 ablation | 게이트 없음. **외부 API 없음** → 로컬만 |

### 오픈 소형 ≤10B (2)
| # | 모델 | 이유 |
|---|---|---|
| 13 | Qwen3.6-9B 급 소형 (3.6 라인업 확인 후; 없으면 Qwen3.5-9B) [?] | 소형 스케일링 행 |
| 14 | Mi:dm-2.0-Mini 2.3B (`K-intelligence/Midm-2.0-Mini-Instruct`, MIT) + Kanana-2-3B (2026-07) | 온디바이스 한국어 행. Mi:dm K 2.5 Pro는 HF·API 모두 없음 |

### 규칙·NER 베이스라인 (4) — regex 상한선과 실무 도구
| # | 도구 | 이유 |
|---|---|---|
| B1 | **Presidio 2.2.364** + `ko` recognizer 5종 활성화 (RRN·FRN·BRN·운전면허·여권; 기본 비활성) | 선행 6편의 공통 베이스라인. 계좌·카드 한국형 recognizer 없음 → 우리가 추가한 regex 버전도 함께 |
| B2 | **ko-pii 1.16** | 한국어 금융 규칙 커버리지 최강 (카드 Luhn, 계좌 앵커, 주민번호 체크섬). T3 anchor_missing이 정확히 이걸 깨뜨림 |
| B3 | **OpenAI Privacy Filter** (영어, 대조군) + **OpenMed/privacy-filter-multilingual** (한국어 포함 fine-tune) | REDACT·OPF-eval 이후 표준 행 |
| B4 | **KLUE-RoBERTa-large 토큰 분류기** (우리 train split으로 fine-tune) | in-domain 상한선. Thunder-DeID·K-LegalDeID 관행. GLiNER2-PII는 한국어 미지원 음성 대조군으로 서브셋 |

### 2b. 한국어 모델 접근성 (2026-09-13 확인)

| 모델 | 접근 경로 | 게이트 | 라이선스 | 논문 발표 | 3rd-party 호스팅 | 제약 |
|---|---|---|---|---|---|---|
| Solar Pro 4 | console.upstage.ai 셀프 가입, `api.upstage.ai/v1` OpenAI 호환; OpenRouter | 없음 | 상용 API | 제한 없음 | **OpenRouter** | VAT 10% |
| HyperCLOVAX-SEED | HF 직접 | 없음 | SEED License (10M MAU 이상·경쟁 서비스 시 별도) | OK | Friendli dedicated만 | 표기 의무 |
| Kanana-2 | HF 직접 | 없음 | Kanana License | OK | 없음 | 표기 의무 |
| EXAONE-4.0 | HF 직접 | 없음 | 1.2-NC | **명시 허용** | Friendli dedicated만 (K-EXAONE serverless는 2026-09-06 종료) | 상용 불가 |
| A.X | HF 직접 | 없음 | Apache-2.0 / Qwen | OK | 없음 | **공개 API 없음** (K1 API는 정부 선정 3개 스타트업만) |
| Mi:dm 2.0 | HF 직접 | 없음 | MIT | OK | Friendli dedicated | 2.5 Pro 미공개 |

**결론:** 한국어 API 행은 Solar Pro 4(OpenRouter) 하나. HCX-007은 NCP 가입·서비스앱 심사가 필요해 제외(§4). 나머지 한국어 모델은 HF 오픈 가중치를 로컬 80GB로. 논문 acknowledgement에 "Powered by HyperCLOVA X", "Powered by Kanana" 표기.

## 3. 실행 프로토콜 (요약)

- **생성기 확정 (2026-09-15):** 한울 선택으로 API 주 생성기는 `gpt-6-astra`. 생성기 전용 행으로 별도 보고하며 위 14+4 평가 후보군의 일괄 변경을 뜻하지 않습니다. 공식 문서상 입력/출력 $10/$50 per 1M tokens. Astra는 `temperature`를 지원하지 않아 생략하고 `reasoning_effort=low`로 파일럿을 시작합니다. [모델 문서](https://developers.openai.com/api/docs/models/gpt-6-astra), [호환성 안내](https://developers.openai.com/api/docs/guides/latest-model).

- 스팬 추출: 동일 프롬프트(`src/prompts/span_p1.txt`), temperature 0, JSON 출력. reasoning 모델은 thinking on/off 두 행.
- 비식별화: 동일 문서, surrogate 규칙 프롬프트. 일관성은 entity_id 기준.
- 3 seed 평균 (API는 1 seed + temperature 0).
- 결과 파일 `model_type ∈ {api, local, rule, generator}`; 생성기(GPT-6 Astra, Qwen3.6-35B-A3B)는 `generator`로 표기하고 헤드라인 순위에서 제외 (ADR-0002).
- 80GB 1장 가능: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 전부. A.X-4.0 72B·Llama 4 Scout는 4-bit. Solar Open 100B/250B, A.X K2, K-EXAONE, Motif-3는 단일 GPU 불가 → 포함 시 hosted API [?].

## 4. 제외한 후보와 이유

- **HCX-007 (Naver CLOVA Studio)** — 호출은 가능하지만 NCP 가입 + 테스트 키 60 QPM/60K TPM + 서비스 앱 심사(기간 미명시)가 필요. 접근성 원칙에 따라 제외. Limitations에 "가입형 한국어 API 미평가"로 명시.

- Solar Open 100B / Open 2 250B, A.X K1/K2, K-EXAONE 236B/750B, Motif-3 314B — 단일 GPU 불가, 4페이지 논문 범위 밖. 후속에서 API로.
- Llama 4 Maverick, DeepSeek V3/V4, GLM-5.1, Kimi K2/K3 — 한국어 검증 부족 + 규모. DeepSeek는 선행 4편에 등장하므로 hosted API 서브셋 후보 [?].
- Piiranha — CC-BY-NC-ND, 유럽어만.
- 42dot, VARCO 텍스트, KONI — 구형.

## 4b. 표기 의무 체크리스트 (논문·레포)
- HyperCLOVAX-SEED: "Powered by HyperCLOVA X" · Kanana: "Powered by Kanana" · Solar Open 사용 시: "Built with Solar" · EXAONE: NC 라이선스 명시.

## 5. 논문 표 구성 제안

Table 1 (main): 18행 × {L-id F1, L-attr F1, I F1, T0/T1/T2/T3 F1, de-id risk-weighted recall, consistency}. 
Figure 2: T-level별 F1 곡선 — 규칙(B1·B2) / 국제 오픈 / 한국어 오픈 / API 4군 평균선 + 개별 점.
Table 2 (analysis): op별 recall 상위·하위 5개 (hangul_digits, chunk_split, partial_mask, agent_readback 포함).
