# ADR-0019: 총 1,440건과 축소 평가 세트

- 날짜: 2026-09-20
- 상태: accepted (1,440건 목표와 모델 수 축소); 구체 모델 4+3은 실행 준비안
- 대체: 720건 후 2160건 확대안, ADR-0005의 14+4 전체 실행 범위

사용자가 “720*2로 하자” 및 실험 모델군 축소를 지시했다. 이는 총 1,440개 독립 문서이며 동일 문서의 복제나 모델별 720개 재작성으로 해석하지 않는다. 현재 720건 실행은 수정하지 않고 이어간다.

추가 720개 계획은 `data/corpus/main-1440-v1/stage2-plan.jsonl`, 전체 계획은 동 디렉터리 `plan.jsonl`이다. 계획 생성 seed=20260920. 기존과 doc_id·개별 생성 seed가 겹치지 않음을 확인했다. 계획상 10종 문서 × T0~T3 × 주체 수 1/3/8 × 길이 1k/4k/16k = 360개 셀에 각 4건이다. 실제 통과·길이 분포와 별개이며 최종 coverage를 다시 확인해야 한다.

추가 계획은 아직 API에 제출하지 않았다. 현 OpenAI $100, Mango 과거 비용 포함 $150 상한을 늘리지 않는다. 1차 생성 수율·비용에 따라 남은 예산 안에서 2차 생성기를 배정하고, 초과분은 수치화해 사용자에게 알린다.

## 축소 실행안: LLM 4 + 베이스라인 3

| 역할 | 후보 | 선택 이유 |
|---|---|---|
| API 비교 A | Claude Sonnet 5 | 생성에 사용하지 않은 공급자의 대표 API |
| API 비교 B | Gemini 3.8 Flash | 별도 공급자 API 비교 |
| 범용 오픈 | Qwen3.6-35B-A3B | 범용 공개 가중치 대표 |
| 한국어 오픈 | Kanana-2-30B-A3B-Instruct-2601 | 한국어 개발 공개 가중치 대표 |
| 규칙 도구 | Presidio + 한국형 recognizer | 범용 도구와 한국형 규칙 결합 |
| 한국어 규칙 | ko-pii | 한국어 규칙 기반 비교 |
| 학습된 PII 탐지 | OpenMed/privacy-filter-multilingual | 규칙과 다른 기존 탐지 모델 비교 |

정확한 가중치 revision, 실행 접근성, 라이선스, 입력+출력 컨텍스트 예산은 실험 전 고정한다. 모델 카드가 존재한다는 것은 로컬 서버/계정 접근이 준비됐다는 뜻이 아니다. 특히 Kanana 문맥 한도 내에 실제 토큰화 입력·출력이 들어오는지 확인하고 조용히 잘라내지 않는다.

Sol/Luna·Opus·Pro·Solar·gpt-oss·Gemma·Llama·SEED·EXAONE·A.X·소형 모델 추가 행 및 KLUE fine-tune은 이번 핵심 실행 범위에서 제외한다. Astra와 GLM은 생성기이므로 헤드라인 평가에서 제외하며 별도 자기평가를 필수로 추가하지 않는다.

## 실험 범위

우선 동일한 스팬 추출 과업과 문서 집합으로 7개를 비교한다. 생성기별 분리 성능과 문서 단위 paired bootstrap 구간을 보고한다. 지원하지 않는 카테고리는 공통 범위 점수와 전체 택소노미 점수로 구분하여 해석한다. 생성 모델마다 문서 조건이 다르므로 생성기 효과를 인과적으로 단정하지 않는다.

fine-tune을 제외하므로 새 train split 구축을 핵심 일정에 넣지 않는다. 프롬프트 개발에 사용한 문서/파일럿은 최종 test와 구분하며, 최종 평가 전 split과 프롬프트를 고정한다. 1,440건 전체가 자동으로 test가 되는 것은 아니다. 별도 de-id 생성 호출과 thinking on/off·다중 seed 실험은 후순위로 둔다. 스팬으로 유도한 마스킹 지표를 직접 de-id 성능이라고 부르지 않는다.

조합당 4건으로 세부 효과의 유의미함을 보장하지 않는다. 전체, tier×kind, T-level, 문서 유형별 분석을 우선하며 사람 경계/주체 검수를 별도 완료한다.

확인 원천: [Claude](https://platform.claude.com/docs/en/models/sonnet-5/whats-new-sonnet-5), [Gemini](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash), [Qwen](https://huggingface.co/Qwen/Qwen3.6-35B-A3B), [Kanana](https://huggingface.co/kakaocorp/kanana-2-30b-a3b-instruct-2601). 베이스라인 후보는 기존 선정 목록에서 유지하며 버전·지원 범위 재검증 필요.
