> **후속 결정:** ADR-0034에서 기본안(Qwen3.5-2B/4B + Kanana-2-3B, baseline 3개)을 채택했습니다. 아래 제안 당시의 대안은 자동 채택되지 않았으며 Gemini·9B 등은 보류입니다.

# 소형 로컬 모델 중심 비교군 재검토 — 2026-09-24

**상태: 조사 기반 제안. 실행 모델 교체·예산 집행·담당 변경은 아직 확정하지 않음.** 기존 담당자에게 본 실험을 새로 시작하라는 지시가 아니다. 사용자는 API 비용과 일정 때문에 최신 연구를 참고한 작은 로컬 모델 후보 재선정을 요청했다.

## 권장안

GPU 사양을 모르는 현재의 기본 제안은 **Qwen3.5-2B + Qwen3.5-4B + Kanana-2-3B-Instruct**, 기존 Presidio·ko-pii·OpenMed 유지다. 3개 LLM × 두 문맥 조건 + 3 baseline = **6시스템·9조건**. Gemini는 비용을 계측한 뒤 추가 여부를 결정할 선택 API 기준점이다. 추가 시 기존처럼 7시스템·11조건이다. API 결과 없이도 규제 기반 taxonomy/변형 benchmark 및 로컬 탐지기의 문맥 효과를 연구할 수 있지만, 폐쇄형 frontier 모델까지 일반화하지 않는다.

| 우선순위 | 정확한 후보 ID | 역할 | 공식 문맥 한도 | 결정 시 확인 |
|---|---|---|---|---|
| 기본 | `Qwen/Qwen3.5-2B` | 작은 범용 모델 | 262,144 | 한국어 taxonomy 지시·JSON 준수, 실제 dtype/서버 지원 |
| 기본 | `Qwen/Qwen3.5-4B` | 같은 계열의 규모 비교 | 262,144 | 비추론 모드 고정, 2B와 동일 출력 protocol |
| 기본·capacity 조건부 | `kakaocorp/kanana-2-3b-instruct` | 한국어 중심 소형 모델 | 32,768 | 긴 문서+taxonomy+출력 예산의 실제 토큰 합계 |
| GPU 여유 시 교체 후보 | `Qwen/Qwen3.5-9B` | 더 강한 로컬 비교점 | 공식 카드 참조 | 2B/4B/9B를 모두 늘리기보다 **4B+9B** 쌍으로 대체 고려 |
| 한국어 대안 | `LGAI-EXAONE/EXAONE-4.0-1.2B` | 더 작은 한국어 모델 | 65,536 | 36개 label 추출과 strict JSON의 실용성, 라이선스 확인 |
| 타 계열 대안 | `google/gemma-4-E4B-it` | 계열 다양성 | 128K | effective 4.5B, embeddings 포함 약 8B로 메모리를 단순 4B로 계산하지 않음 |

Qwen3.5는 2026년 모델군이고 Kanana-2 SLM은 공식 카드상 2026-07-27 공개다. Qwen의 더 최신 대형 버전 숫자를 택하는 것보다 소형 공식 checkpoint를 비교하는 것이 이번 비용/일정 목적에 부합한다. 정확한 가중치 commit은 배포 시 고정한다.

모델명 속 B는 실측 VRAM이 아니다. FP16/BF16 저장 가중치의 단순 계산은 전체 파라미터당 약 2바이트이며 KV cache, runtime workspace, 멀티모달 모듈 등이 별도로 필요하다. 이전 30/35B-A3B MoE는 active 3B라도 전체 가중치를 올려야 하므로 3B dense와 같은 메모리 모델이 아니다. Qwen3.5는 텍스트 입력만 사용해도 멀티모달 checkpoint의 실제 로드 범위를 확인해야 한다.

GPU 사양 확인 전에는 ‘몇 GB면 반드시 가능’ 또는 완료 시간을 약속하지 않는다. 모델을 한 번에 하나씩 서빙하고, 단일 요청에서 최장 입력을 통과시킨 뒤 동시성을 늘린다. 16/24GB급이면 우선 2B/4B/Kanana-3B를 시험할 대상으로 삼고, 9B는 긴 입력 여유를 직접 확인한 뒤 채택한다. 이는 용량 보증이 아니다.

## 논문이 뒷받침하는 선정 원칙

| 1차 출처 | 확인한 내용 | 우리 선정에 대한 해석 / 전이 한계 |
|---|---|---|
| [Thunder-DeID, Findings EMNLP 2025](https://aclanthology.org/2025.findings-emnlp.682/) / [본문](https://aclanthology.org/2025.findings-emnlp.682.pdf) | 한국어 법원 문서 비식별화; 소형 encoder 및 Polyglot-ko 1.3B·EXAONE 2.4B 비교 | 한국어 민감정보 연구에서 소형 비교군은 타당하다. 과업/학습/라벨/지표가 다르므로 논문 점수를 우리 zero-shot 36-category F1의 예상치로 쓰지 않는다. |
| [CAPID, EACL SRW 2026](https://aclanthology.org/2026.eacl-srw.23/) | 로컬 SLM을 fine-tune해 QA에서 문맥상 필요한 PII를 구분하는 접근 | 로컬 모델과 문맥의 실용적 의미를 뒷받침한다. 우리는 QA utility나 같은 fine-tuning을 재현하지 않으며 benchmark 학습 금지를 유지한다. |
| [REDACT, 2026-06 preprint](https://arxiv.org/abs/2606.19881) | 규칙, GLiNER, privacy filter, API LLM의 서로 다른 탐지 계열 비교 | 대형 LLM 개수를 늘리기보다 탐지 방식·변형별 실패를 설명하는 구성이 유용하다. 이 논문이 Qwen/Kanana 소형의 우수성을 입증한 것은 아니다. |
| [PIIBench, 2026-04 preprint](https://arxiv.org/abs/2604.15776) | Presidio, 범용 NER, PII 전용 및 금융 NER 등 8개 시스템 비교 | 규칙/전용 탐지기를 유지할 근거. 금융 NER의 label space를 우리 PII taxonomy와 동일하다고 보지 않는다. |

논문은 **비교 설계의 근거**, 최신 공식 모델 카드는 **실제 checkpoint·한도·서빙의 근거**로 구분한다. ‘논문에서 검증된 Kiii² 성능 순위’는 아직 없다. Qwen 2B/4B 차이도 순수 파라미터 수의 인과 효과로 단정하지 않고, 같은 계열의 두 배포 모델 비교로 표현한다. Kanana 대 Qwen 비교만으로 한국어 학습의 인과적 효과를 주장하지 않는다.

## 실행 전 넘어야 할 조건

1. **공통 capacity:** Kanana 32K는 특히 확인한다. 원래 corpus의 16k bucket은 해당 모델의 실제 prompt 토큰 수가 아니다. taxonomy·TARGET 반복·chat framing·출력 한도를 모두 포함하여 모든 모델/두 조건의 공통 eligible 집합을 고정한다. 제외가 많으면 조용히 긴 문서를 버리지 말고, 이 모델의 유지/대안 선택과 benchmark coverage 손실을 결정 전에 공유한다.
2. **설정:** Qwen3.5-4B 등은 기본 thinking 동작을 확인한다. 추출 과제의 기본 제안은 공식 chat-template의 비추론 모드로 고정하고 요청/계측에 똑같이 적용하는 것이다. provider/모델이 지원하지 않는 설정을 임의 주입하지 않는다. FP16 API 서빙 선호는 유지하되 공식 카드의 BF16 예시와 실제 backend 지원을 확인하고 fallback은 명시한다.
3. **평가 무결성:** 별도 pilot에서 출력 형식/잘림/offset/지연/메모리를 검증한다. test 성능을 보고 모델/프롬프트를 고르지 않는다. 새 모델이라도 full/local core·halo·출력 한도·실패 처리 기준은 동일하다.
4. **시간:** 작은 모델은 호출 수를 줄이지 않는다. 현재 partition이라면 3 LLM × 2조건 = **82,338 요청**으로 API 3개를 쓸 때와 같다. 캐시/서빙 처리량을 별도 pilot에서 재고 GPU 시간을 추정한다. 모델 축소만으로 마감 내 완료를 보장하지 않는다.
5. **선정 후:** 새 accepted ADR, README/AGENTS/STATUS/배정표/config matrix/사라 brief를 함께 갱신한다. 사라의 문맥 분석 질문은 유지한다. 현재 운영 roster를 이 제안만으로 바꾸지는 않는다.

## 제외·후순위

- Claude/대형 MoE는 비용·시간 제약상 우선순위를 낮춘다. 이미 실행된 실험이 있다면 그 결과를 폐기하지 않는다.
- Gemini는 선택 기준점이며 무료 또는 충분히 저렴하다고 전제하지 않는다. 전체 두 조건의 실측 견적과 배정 예산이 필요하다.
- GLiNER 추가는 선행연구와의 연결성은 있으나 새 label mapping/어댑터 검증이 필요하므로 제출 직전 기본 목록에 늘리지 않는다.
- 한국어 모델 여러 개, 별도 thinking ablation, 양자화별 비교는 이번 4페이지 범위에서 보류한다.
- Presidio·ko-pii·OpenMed는 기존 구현을 활용한다. OpenMed의 GPU 모델 호환성/decoder 변형/coverage 한계는 기존 문서대로 남긴다.

## 공식 모델 출처 (2026-09-24 확인)

- [Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B)
- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B)
- [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B)
- [Kanana-2-3B-Instruct](https://huggingface.co/kakaocorp/kanana-2-3b-instruct)
- [EXAONE-4.0-1.2B](https://huggingface.co/LGAI-EXAONE/EXAONE-4.0-1.2B)
- [Gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it)

이 문서는 모델 조사이며 신규 inference, 모델 다운로드, GPU 가용성·FP16 호환성 실측을 수행한 결과가 아니다.
