# OpenAI Batch로 문서 생성

2026-09-16 · ADR-0007

Batch는 같은 문서 계획·프롬프트·호출 설정을 묶어서 비동기로 실행한다. `api-main`만 처리하며, Qwen `local-check`는 기존 `compose`를 사용한다. 식별자 값 채우기와 검증 코드는 동일하다.

공식 OpenAI 문서 기준 Batch는 일반 호출 대비 50% 할인, 처리 창은 `24h`이다. 만료·취소 시 일부 요청만 완료될 수 있다. 계정별 대기 입력 토큰 한도가 있으므로 전체 요청 수가 파일 제한 이하여도 제출이 거절될 수 있다. [Batch 가이드](https://developers.openai.com/api/docs/guides/batch), [Astra 가격](https://developers.openai.com/api/docs/models/gpt-6-astra)

## 준비 → 제출 → 조회 → 수집

아래는 **새로 확정한 본 생성 계획**에 사용하는 예시다. 이미 생성한 파일럿 80건 계획을 그대로 제출하면 다시 과금된다. 준비 단계는 기존 코퍼스를 자동 검색하지 않는다. 품질 보완과 계획 확정 후 새 작업 디렉터리를 사용한다.

```bash
# 1. 오프라인 준비. API 키 불필요. 기존 폴더 덮어쓰기 금지.
.venv/bin/python -m src.generate.run batch-prepare \
  --plan data/corpus/main-0.1/plan.jsonl \
  --model gpt-6-astra --prompt-version compose_v2 \
  --batch-dir data/corpus/main-0.1/batch-api-01

# 2. 작성한 .env를 로드하고 제출. 이 단계가 실제 생성 비용을 발생시킨다.
set -a
source .env
set +a
.venv/bin/python -m src.generate.run batch-submit \
  --batch-dir data/corpus/main-0.1/batch-api-01

# 3. 상태만 조회. 명령을 종료해도 서버 작업은 계속된다.
.venv/bin/python -m src.generate.run batch-status \
  --batch-dir data/corpus/main-0.1/batch-api-01

# 4. 종료된 작업의 원문·오류를 수집. 아직 실행 중이면 상태만 반환한다.
.venv/bin/python -m src.generate.run batch-collect \
  --batch-dir data/corpus/main-0.1/batch-api-01

# 5. 기존 슬롯 채우기·검증 및 상세 검수와 연결.
.venv/bin/python -m src.generate.run fill \
  --raw data/corpus/main-0.1/batch-api-01/raw.jsonl \
  --out data/corpus/main-0.1/docs.api.jsonl
.venv/bin/python -m src.generate.audit \
  --raw data/corpus/main-0.1/batch-api-01/raw.jsonl \
  --out data/corpus/main-0.1/audit.api.json
```

`compose_v2`는 현재 파일럿과 Qwen 비교에 사용하는 버전이다. 본 생성용 규칙을 바꾸면 새 프롬프트 파일과 버전명을 명시한다. 준비 이후에는 저장된 요청을 그대로 제출하므로 프롬프트 파일을 수정해도 준비된 작업 내용은 바뀌지 않는다.

## 저장 파일

| 파일 | 내용 |
|---|---|
| `requests.jsonl` | 실제 프롬프트·모델·호출 설정. 문서 ID를 `custom_id`로 사용 |
| `manifest.json` | 계획·모델·프롬프트 버전·택소노미 버전·요청 파일 해시 |
| `state.json` | 업로드 파일 ID, Batch ID, 제출 시도 상태, 서버 상태, 수집 파일 해시 |
| `batch-output.jsonl`, `batch-errors.jsonl` | 서버에서 받은 원문 그대로 |
| `raw.jsonl` | 기존 compose와 호환되는 원문. 잘린 응답도 사용량과 함께 보존 |
| `errors.jsonl` | API 오류·출력 잘림/빈 응답·누락 결과 |
| `summary.json` | 성공·실패 건수, 사용량, 재시도할 문서 ID |
| `retry-plan.jsonl` | API 실패·잘림·누락 요청의 계획 |

수집의 `succeeded`는 완전한 API 응답이라는 뜻이다. 슬롯 검증 통과나 사람 검수 완료를 뜻하지 않는다. `fill`과 `audit`를 별도로 실행한다. 사용량 합계에는 잘린 응답도 포함되며 비용은 자동 추정하지 않는다.

## 일부 실패 시

실패 요청만 별도 작업으로 준비한다. 원래 프롬프트와 설정을 그대로 복사하며 준비 명령 자체는 API를 호출하지 않는다.

```bash
.venv/bin/python -m src.generate.run batch-retry \
  --batch-dir data/corpus/main-0.1/batch-api-01 \
  --out-dir data/corpus/main-0.1/batch-api-01-retry1

.venv/bin/python -m src.generate.run batch-submit \
  --batch-dir data/corpus/main-0.1/batch-api-01-retry1
# 이후 batch-status / batch-collect를 재시도 폴더에 실행한다.

# 원 작업부터 재시도 순서로 지정. 모든 문서에 완전한 응답이 있어야 합쳐진다.
.venv/bin/python -m src.generate.run batch-merge \
  --batch-dirs data/corpus/main-0.1/batch-api-01 data/corpus/main-0.1/batch-api-01-retry1 \
  --out data/corpus/main-0.1/raw.api.merged.jsonl
```

이후 합친 파일에 `fill`/`audit`를 실행한다. 성공 응답이 서로 충돌하면 임의 선택하지 않는다. 원 응답과 재시도를 단순히 이어 붙이면 같은 문서 ID가 중복되므로 `batch-merge`를 사용한다. 내용·슬롯 품질 문제로 `fill`에서 탈락한 문서는 API 실패와 구분해 검토하며 자동 재시도 대상이 아니다.

## 중복 제출과 복구

- 같은 작업 폴더에서 `batch-submit`을 다시 실행하면 저장된 Batch ID를 반환한다. 같은 폴더의 동시 명령은 잠금으로 차단한다.
- 제출 요청 전에 시도 사실을 저장하고 SDK의 자동 재시도를 끈다. 서버가 접수했는지 불명확하면 재제출하지 않는다.
- 이때 OpenAI 대시보드 또는 Batch 목록에서 `manifest.json`의 `job_id`와 같은 `metadata.kiii_job_id`를 찾아 연결한다. 입력 파일과 작업 ID가 일치해야 한다.

```bash
.venv/bin/python -m src.generate.run batch-submit \
  --batch-dir data/corpus/main-0.1/batch-api-01 \
  --recover-batch-id batch_실제ID
```

서버에 작업이 없음을 확인하기 전에는 새 폴더를 만들어 같은 요청을 재제출하지 않는다. 확실한 입력 오류로 제출 자체가 거절되었다면 오류를 수정해 새 작업을 준비한다. 업로드 중 연결이 끊긴 경우 재실행으로 사용하지 않는 입력 파일이 추가 업로드될 수 있지만 문서 생성 작업은 중복 생성하지 않는다.

수집 완료 후 재수집은 로컬 파일 해시를 확인하고 같은 결과를 반환한다. 파일·요청 수 상한(50,000건/200 MB)은 준비 단계에서 검사한다. 계정별 토큰 대기 한도에 따른 자동 분할이나 자동 폴링은 구현하지 않았다.

## 키와 Qwen

Batch는 공식 `https://api.openai.com/v1`만 사용하며 로컬 서버용 `OPENAI_BASE_URL`에 영향을 받지 않는다. API 키는 파일에 기록하지 않는다.

Qwen은 별도 `compose --generator-slice local-check --base-url ...` 경로다. 로컬 서버에 연결할 때는 해당 서버의 키를 따로 사용한다. Astra용 키를 로컬/제3자 서버로 보내지 않는다. Qwen이 아직 준비되지 않아도 Batch와 `fill`은 독립적으로 동작한다.

## 검증 상태

추가 21개를 포함한 전체 42개 오프라인 테스트 통과. 실제 SDK의 메서드와 공식 API 문서를 확인하고 모의 응답으로 실패·복구·중복 방지·기존 fill 연결을 검증했다. 실제 서버에 Batch를 제출한 통합 검증은 아직 수행하지 않았다.
