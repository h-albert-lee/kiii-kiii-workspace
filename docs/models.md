# 리더보드 모델 선정 (ADR-0005)

*조사일 2026-09-13. 근거: 선행 PII 벤치마크 12편의 평가 모델 목록 + 2026-09 기준 한국어·오픈 모델 현황 (`literature/notes/evaluated-models.md`). 모델 ID·라이선스는 실험 직전 재확인 필요 — `[?]` 표시.*

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

### Frontier API (4)
| # | 모델 | 이유 | 비용 메모 |
|---|---|---|---|
| 1 | GPT-5.5 (+ GPT-5.4-mini 저비용 행) | PII-Bench·AmBench·REDACT의 GPT 행 연속 | 16k 문서 다수 → mini로 전량, 5.5는 서브셋 [?] |
| 2 | Claude Sonnet 5 (Opus 5는 서브셋) | REDACT Sonnet 4.6 연속 | |
| 3 | Gemini 3.5 Flash (+ 3.1 Pro 서브셋) | AmBench Gemini 행; 저비용 대량 실행 | |
| 4 | HyperCLOVA X HCX-007 | **한국어 우선 frontier API 유일**. 한국어 네이티브 학습이 주민번호·계좌 포맷·한글 숫자에 도움 되는지 검증 | CLOVA Studio |

### 오픈 범용 대형 (4) — 80GB 1장
| # | 모델 | 이유 |
|---|---|---|
| 5 | Qwen3.5-35B-A3B-Instruct (Apache-2.0) | Qwen2.5 행의 후속; 3B active로 빠름 |
| 6 | gpt-oss-120b (Apache-2.0, MXFP4 ~63GB) | 오픈 OpenAI 행; AmBench·Albanese에 20B 등장 |
| 7 | Gemma 4 31B-it (Apache-2.0) | 140개 언어 사전학습에 한국어 포함 |
| 8 | Llama-3.1-8B-Instruct | 선행 5편의 공통 행 — **연속성 앵커**. Llama 4 Scout는 한국어 공식 미지원이라 "미지원 대조군"으로 서브셋만 |

### 한국어 개발 오픈 (4)
| # | 모델 | 이유 | 라이선스 |
|---|---|---|---|
| 9 | Kanana-2-30B-A3B-Instruct-2601 (Kakao) | 한국어 토크나이저 효율 +30%; 3B active | Kanana Open License (custom) [?] 재배포 조건 |
| 10 | HyperCLOVAX-SEED-Think-14B (Naver) | 오픈 가중치 + reasoning 토글 → CoT 효과 측정 | SEED custom |
| 11 | EXAONE-4.0-32B (LG) | Thunder-DeID 베이스라인(3.5) 계열; 텍스트 플래그십 | **NC (연구 전용)** — 논문에 명시 |
| 12 | A.X-4.0-Light 7B vs A.X-3.1-Light 7B (SKT) | Qwen 파생 vs 자체 토크나이저 — 같은 회사 두 모델로 토크나이저 효과 ablation | Qwen / Apache-2.0 |

### 오픈 소형 ≤10B (2)
| # | 모델 | 이유 |
|---|---|---|
| 13 | Qwen3.5-9B (+4B) | 소형 스케일링 행 |
| 14 | Mi:dm-2.0-Mini 2.3B (KT, MIT) 또는 Kanana-2-3B | 온디바이스 한국어 행. MIT 라이선스가 배포 실험에 유리 |

### 규칙·NER 베이스라인 (4) — regex 상한선과 실무 도구
| # | 도구 | 이유 |
|---|---|---|
| B1 | **Presidio 2.2.364** + `ko` recognizer 5종 활성화 (RRN·FRN·BRN·운전면허·여권; 기본 비활성) | 선행 6편의 공통 베이스라인. 계좌·카드 한국형 recognizer 없음 → 우리가 추가한 regex 버전도 함께 |
| B2 | **ko-pii 1.16** | 한국어 금융 규칙 커버리지 최강 (카드 Luhn, 계좌 앵커, 주민번호 체크섬). T3 anchor_missing이 정확히 이걸 깨뜨림 |
| B3 | **OpenAI Privacy Filter** (영어, 대조군) + **OpenMed/privacy-filter-multilingual** (한국어 포함 fine-tune) | REDACT·OPF-eval 이후 표준 행 |
| B4 | **KLUE-RoBERTa-large 토큰 분류기** (우리 train split으로 fine-tune) | in-domain 상한선. Thunder-DeID·K-LegalDeID 관행. GLiNER2-PII는 한국어 미지원 음성 대조군으로 서브셋 |

## 3. 실행 프로토콜 (요약)

- 스팬 추출: 동일 프롬프트(`src/prompts/span_p1.txt`), temperature 0, JSON 출력. reasoning 모델은 thinking on/off 두 행.
- 비식별화: 동일 문서, surrogate 규칙 프롬프트. 일관성은 entity_id 기준.
- 3 seed 평균 (API는 1 seed + temperature 0).
- 결과 파일 `model_type ∈ {api, local, rule, generator}`; 생성기(GPT-5.5 또는 Claude Sonnet 5, Qwen3.5-35B-A3B)는 `generator`로 표기하고 헤드라인 순위에서 제외 (ADR-0002).
- 80GB 1장 가능: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 전부. A.X-4.0 72B·Llama 4 Scout는 4-bit. Solar Open 100B/250B, A.X K2, K-EXAONE, Motif-3는 단일 GPU 불가 → 포함 시 hosted API [?].

## 4. 제외한 후보와 이유

- Solar Open 100B / Open 2 250B, A.X K1/K2, K-EXAONE 236B/750B, Motif-3 314B — 단일 GPU 불가, 4페이지 논문 범위 밖. 후속에서 API로.
- Llama 4 Maverick, DeepSeek V3/V4, GLM-5.1, Kimi K2/K3 — 한국어 검증 부족 + 규모. DeepSeek는 선행 4편에 등장하므로 hosted API 서브셋 후보 [?].
- Piiranha — CC-BY-NC-ND, 유럽어만.
- 42dot, VARCO 텍스트, KONI — 구형.

## 5. 논문 표 구성 제안

Table 1 (main): 18행 × {L-id F1, L-attr F1, I F1, T0/T1/T2/T3 F1, de-id risk-weighted recall, consistency}. 
Figure 2: T-level별 F1 곡선 — 규칙(B1·B2) / 국제 오픈 / 한국어 오픈 / API 4군 평균선 + 개별 점.
Table 2 (analysis): op별 recall 상위·하위 5개 (hangul_digits, chunk_split, partial_mask, agent_readback 포함).
