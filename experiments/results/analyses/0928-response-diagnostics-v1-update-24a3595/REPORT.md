# 은빈 추가 결과 검토 — 24a3595

2026-09-28. `feat/exp-eb@24a359542ffadc311e0e5ffe6803ff092e728f70`의 새 확장 결과 **Qwen3.5-9B full/local, Kanana-1.5-8B full/local**를 검토했습니다. 직전 `ac25513` 이후 두 커밋이 추가됐습니다. 원격 브랜치·원본 결과·실행 코드는 보존했으며 추가 추론은 없습니다. 아래는 모델별 완료 실행의 기술적 재현과 탐색적 진단이며 통합 헤드라인 순위가 아닙니다.

## 재현과 데이터 범위

- **4조건 모두 완료**: Qwen 각 1,440문서 / 13,723요청 / gold 218,664스팬, Kanana 각 1,438문서 / 13,653요청 / gold 218,197스팬.
- 응답 SHA, 고유 요청 ID, 재구성된 요청 SHA, 데이터·택소노미·scorer SHA를 확인했고 **모든 strict 지표·세부 집계·문서별 점수·실패 기록이 원본과 일치**합니다. manifest/run/progress가 result와 일치합니다.
- 총 **54,752개 응답**의 provider JSON과 completion 전문이 존재하고 서로 일치합니다. 예약/완료 이벤트와 응답도 일치하며 누락·중복이 없습니다. 모든 status 실패는 length 종료(Qwen full/local 239/84, Kanana full/local 873/176)입니다. 기록상 transport 실패는 관측되지 않았습니다. 이는 실제 저장된 필드를 검증한 것으로 서버 내부의 미전달 정보까지 보존했다는 뜻은 아닙니다.
- REPORT에 기재된 모든 파일 SHA(압축/해제 파일 포함)와 실행 소스 SHA를 확인했습니다. [감사 결과](audit.json), [입력 해시와 고정 원본 링크](INPUTS.json).
- Kanana 제외 ID는 `kiii-main-v2-00311`, `kiii-main-v2-01050`입니다. 공유된 full/local preflight summary의 공통 ID 교집합이 eligible-1438과 일치하며, 기존 gold에서 해당 집합을 바이트 그대로 추출한 SHA도 manifest와 일치합니다. 길이 초과 68요청이라는 설명은 담당자 기록이며 원본 토큰 계측으로 독립 확인하지 못했습니다. 두 문서 제거로 평가 요청은 총 70개 줄었습니다.
- **preflight summary는 요청별 native count 및 최종 gate 원본을 대체하지 않습니다.** 실제 counts, `cohort-q9.json`, `cohort-1438.json`은 아직 업로드/링크가 없습니다. 기존 핵심 gate, Qwen 9B gate, Kanana 8B gate는 서로 다르므로 현재 exporter를 우회하거나 점수를 바로 통합하지 않습니다.

## 점수

모든 F1은 0–100 척도입니다. ADR-0036의 고정된 항목별 검사와 전체 JSON 코드펜스 제거를 그대로 적용했습니다. 유효하지 않은 파싱 항목은 각각 exact FP 1개로 계산하고 모든 gold를 유지합니다. 문자 지표는 별도 보조 분석입니다.

| 모델 | 조건 | 문서 수 | 공식 strict F1 | 항목별 F1 | 펜스+항목별 F1 | strict 요청 실패율 |
|---|---|---:|---:|---:|---:|---:|
| Qwen3.5-9B | full | 1,440 | 3.2686 | 13.0016 | 14.4432 | 75.74% |
| Qwen3.5-9B | local | 1,440 | 3.6618 | 16.1108 | 18.0520 | 74.86% |
| Kanana-1.5-8B | full | 1,438 | 0.3337 | 5.5500 | 5.5536 | 98.70% |
| Kanana-1.5-8B | local | 1,438 | 0.8429 | 8.3535 | 8.3522 | 97.53% |

실패율은 평가 규칙상 빈 예측으로 처리된 요청 비율이며 서비스 장애율이 아닙니다. 형식/스키마, 정확 인용문 부재, 대상 core 밖 항목 등이 섞여 있습니다. `quote_not_found`는 occurrence 범위 초과도 포함하므로 전부 환각으로 해석하지 않습니다.

같은 모델 내에서는 local 점수가 full보다 높습니다(공식 F1 차이 Qwen +0.3932, Kanana +0.5092점). 통계적 유의성이나 일반적인 문맥 효과는 아직 주장하지 않습니다. Qwen 9B가 기존 소형 모델 업로드보다 높은 관측 점수를 보이지만 gate가 다르고 핵심 조건도 미완료여서 통합 순위/크기 효과 결론은 보류합니다. Kanana 1.5 8B와 Kanana 2 3B는 세대까지 다르므로 크기만의 효과로 해석할 수 없습니다.

펜스+항목별 exact precision/recall은 Qwen full 18.58/11.81%, local 22.62/15.02%, Kanana full 5.11/6.09%, local 12.01/6.40%입니다. 따라서 형식 처리 이후에도 누락·오탐이 상당합니다. Kanana local은 펜스 처리로 오답도 추가되어 F1이 소폭 낮아집니다. 보조 처리는 점수를 반드시 올리는 보정이 아닙니다.

| 모델·조건 | 펜스+항목별 문자 F1 | 앵커 불가 등을 포함한 invalid-item exact FP |
|---|---:|---:|
| Qwen 9B full | 10.4066 | 96,349 |
| Qwen 9B local | 13.1238 | 87,614 |
| Kanana 8B full | 6.5447 | 235,147 |
| Kanana 8B local | 8.1178 | 83,701 |

문자 점수는 유효하게 앵커된 예측과 모든 gold로 계산합니다. 앵커할 수 없는 항목에는 문자 단위 FP를 부여할 수 없으므로 위 exact precision 및 invalid-item 수와 함께 해석해야 합니다. [1,720행 분해 CSV](tables/breakdowns.csv)는 카테고리·tier×kind×T·문서 유형·길이·정보주체 수·생성기 등을 제공합니다.

## JSON 중복 키: 두 모델 모두 관측

REPORT의 중복 키 이슈를 확인했습니다. 완전한 JSON 파싱에 성공한 본문(별도로 전체 펜스만 해제한 본문 포함)에서 동일 object 내 같은 key가 반복되는지를 검사했습니다. JSON 문법이 끝까지 성립하지 않는 응답의 중복 키는 이 수치에 포함하지 않습니다.

| 조건 | raw JSON 중복 키 요청 | 펜스 안 중복 키 요청 | 그중 공식 strict에서 실패 처리되지 않은 요청 |
|---|---:|---:|---:|
| Qwen 9B full | 72 | 7 | 30 |
| Qwen 9B local | 56 | 0 | 20 |
| Kanana 8B full | 43 | 0 | 4 |
| Kanana 8B local | 28 | 0 | 10 |

기존 Python JSON parser는 중복 키의 **마지막 값**을 사용합니다. 반복된 `spans` 앞쪽 내용 등이 유효성 검사 전에 사라질 수 있어 공식 strict와 ADR-0036 보조 분석 모두 이 한계를 상속합니다. 통과 요청 수는 영향받는 예측/점수 변화량과 같지 않습니다. 이번 검토에서 평가 규칙이나 점수를 바꾸지 않았습니다. 정책을 바꾸려면 별도 ADR·버전과 모든 완료 모델의 저장 응답에 대한 일관된 재분석이 필요하며, 새 추론은 필요하지 않습니다. 중복 키 사례 ID/키별 빈도는 audit.json에 있습니다.

## 운영 기록과 남은 일

새 REPORT는 모델 revision, BF16·양자화 없음, A100 GPU 구성, vLLM/Transformers/torch 버전, sampling/reasoning 설정과 실행 시각을 기재했습니다. 이는 담당자 배포 기록 확인이며 실제 서버 독립 검증은 아닙니다. FP16 권장 대신 BF16 원래 가중치 정밀도를 따랐다는 사유가 있습니다. Qwen 생성/계측은 `enable_thinking: false`이며 네 실행 모두 저장된 reasoning 필드는 비어 있습니다.

1. **native 계측 및 최종 gate 원본 공유**: summary만으로 실제 prompt/chat framing과 출력 예약을 검증할 수 없습니다. 최종 공통 1,438건으로 맞추기로 결정할 경우 원본 실행/각 gate를 보존한 별도 재집계 절차를 검토해야 합니다. 기존 1,440건 응답을 재추론할 이유는 없습니다.
2. **별도 pilot 보정의 실제 범위 확인**: REPORT는 합성 30요청 호환성 점검을 설명하지만 core/halo/output은 “pilot 보정 전 초안값”이라고 명시합니다. 이 자료로 대표성 있는 pilot calibration이 완료됐다고 주장하지 않습니다. 설정 때문에 실패가 많았다는 인과도 확인되지 않았습니다. 이미 본 benchmark 결과를 근거로 프롬프트를 튜닝하지 않습니다.
3. **기록 링크와 run ID 보완**: REPORT가 참조하는 `docs/reviews/2026-09-26-issue-*.md`는 해당 commit에 없습니다. Qwen local 디렉토리 0926-02의 config run_id는 0926-01, Kanana local 0926-04는 0926-03입니다. 과거 설정/해시를 고치지 말고 대응 관계를 설명해야 합니다.
4. **남은 완료 결과**: Qwen 2B local / Qwen 4B full은 여전히 10문서 pilot 업로드이고 OpenMed는 REPORT만 있습니다. 미업로드를 미실행으로 단정하지 않습니다. 이번 4개가 추가되어 완료 검토는 LLM 8조건 + CPU baseline 2조건 = 10조건이며, 전체 계획 13조건의 완료는 아닙니다.
5. 큰 응답/저널은 앞으로 기존 공유 규칙대로 압축 Release asset + SHA로 전달합니다. 이번에는 원본 git 이력을 재작성하거나 raw를 main에 중복 복사하지 않았습니다.

## 재현

기존 `src.analysis.response_diagnostics` 및 `src.analysis.export_diagnostics`를 변경 없이 사용했습니다. 각 하위 analysis.json에 strict replay 확인, 입력·분석 소스·scorer SHA와 recorded gate가 있습니다. [실행 가이드](../../../../docs/guide/response-diagnostics.md)를 따라 INPUTS.json의 고정 commit에서 result/responses를 읽고 같은 SHA의 gold를 사용하면 재현할 수 있습니다. Kanana gold는 frozen 전체 gold에서 eligible-1438 ID만 원래 순서·바이트 그대로 유지해 생성합니다. 분석 소스 기준 main `2206dc4`; 네이티브 API/GPU 테스트나 유료 호출은 수행하지 않았습니다.
