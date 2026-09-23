# 파일럿 0.1 사전 점검 — 2026-09-14

> 후속 상태 (2026-09-15): Astra API 80건 생성·자동 검증을 완료했습니다. 결과는 `docs/pilot-0.1-astra-run.md`에 있습니다. 아래는 9/14 시점의 기록이며, 신규 실행은 `src/README.md`의 `--prompt-version compose_v2` 명령을 따릅니다. API·로컬 슬라이스 모두 같은 프롬프트 버전을 명시합니다.

상태: **100건 계획과 프롬프트 준비 완료. 실제 LLM 호출·코퍼스 생성·사람 검수는 미실행.** API 키와 엔드포인트가 현재 실행 환경에 없으며 `.env` 파일도 없습니다. 로컬 20건은 별도 로컬 모델 연결이 필요합니다.

## 준비 결과

- `.venv`: Python 3.12.13, `requirements.txt` 설치 완료.
- `python -m pytest tests -q`: **16 passed** (기존 9개 + 파일럿 회귀 7개).
- 기존 테스트의 합성 샘플로 T2 `dryrun`: fill·오프셋·검증 통과. 이 샘플은 구조 슬롯도 포함하는 파서 점검용이며 T2 분포 적합성 검증 자료는 아닙니다.
- 프롬프트 템플릿의 `str.format`이 `{{슬롯}}`을 `{슬롯}`으로 축약하던 오류 수정. 단일 중괄호 템플릿 필드만 치환합니다.
- YAML의 `multi-subject: person_name`이 사전으로 파싱돼 내부 메모의 plan·validate가 실패하던 오류 수정. 유형별 필수 카테고리 추출을 공통화했습니다.
- 계획은 문서유형을 균등 배정하고 유형별 셀을 비복원 추출합니다. API/로컬 배정은 80/20입니다.
- `compose`는 슬라이스 선택을 필수로 받고 별도 원문 파일을 사용합니다. 재개 시 계획·모델·프롬프트 버전이 다르거나 출력에 중복 ID가 있으면 호출 전에 중단합니다. `plan`은 기존 파일을 덮어쓰지 않습니다.

## 로컬 산출물

`data/`는 gitignore 대상입니다. 아래 파일은 이 작업 공간에 저장되어 있으며 Git으로 배포되지 않습니다.

- `data/corpus/pilot-0.1/plan.jsonl`: seed 0, 100건.
- `plan.api-main.jsonl` / `plan.local-check.jsonl`: 80건 / 20건.
- `prompts/kf-00001.txt` … `prompts/kf-00100.txt`: 각 계획의 완성 프롬프트.
- `plan-summary.json`: 분포·버전·계획 SHA-256.
- `smoke-input.txt`: 기존 단위 테스트에서 가져온 합성 파서 점검 입력.

계획 SHA-256: `537ee31fcd43dcf1325f32c03bb9620561afa0f23cc0f8b28ffde30a34c3413b`.

| 축 | 실현 분포 |
|---|---|
| 문서유형 | 10종 × 각 10건 |
| 고유 셀 | 100개, 중복 없음 |
| T-level | T0 37 / T1 27 / T2 21 / T3 15 |
| 고객 수 | 1명 28 / 3명 42 / 8명 30 |
| 길이 목표 | 1k 42 / 4k 33 / 16k 25 |
| 생성기 슬라이스 | api-main 80 / local-check 20 |

T-level 가중치 25/30/25/20은 추출 선호도로 사용하며 정확한 최종 할당량은 아닙니다. 현재 실현 분포는 T0 비중이 높습니다. 본 코퍼스의 정확한 주변 분포 할당은 별도 검토가 필요합니다. 길이는 여전히 문자 수 기반 토큰 근삿값을 사용합니다.

## 재개

프로젝트 루트에서 실행합니다. 실제 사용할 API 모델 ID·엔드포인트는 호출 직전에 확인합니다. `ANTHROPIC_API_KEY`만 설정해도 현재 OpenAI 호환 클라이언트가 직접 Anthropic API를 호출할 수 있는 것은 아닙니다.

```bash
source .venv/bin/activate
# 직접 작성한 .env를 사용할 경우에만 실행 (.env는 자동 로드하지 않음).
set -a
source .env
set +a

# OPENAI_API_KEY, 필요 시 OPENAI_BASE_URL을 설정하고 API_MODEL에 확인된 ID를 지정.
python -m src.generate.run compose \
  --plan data/corpus/pilot-0.1/plan.jsonl \
  --generator-slice api-main --model "$API_MODEL" \
  --out data/corpus/pilot-0.1/raw.api.jsonl
python -m src.generate.run fill \
  --raw data/corpus/pilot-0.1/raw.api.jsonl \
  --out data/corpus/pilot-0.1/docs.api.jsonl

# 로컬 서버용 키·LOCAL_MODEL·LOCAL_BASE_URL을 설정한 별도 실행 환경에서 진행.
python -m src.generate.run compose \
  --plan data/corpus/pilot-0.1/plan.jsonl \
  --generator-slice local-check --model "$LOCAL_MODEL" --base-url "$LOCAL_BASE_URL" \
  --out data/corpus/pilot-0.1/raw.local.jsonl
python -m src.generate.run fill \
  --raw data/corpus/pilot-0.1/raw.local.jsonl \
  --out data/corpus/pilot-0.1/docs.local.jsonl
```

실제 호출 전에는 소수 계획으로 응답 길이·API 파라미터 호환성·슬롯 준수를 확인합니다. 호출 후에는 각 `docs.*.jsonl.rejects.jsonl`을 검토합니다. 자동 재생성 3회, 실제 토크나이저 기반 길이 측정, T3 구조 지시 준수율 검사는 아직 구현되지 않았습니다. 프롬프트 문체·태그 경계·consultation_content IAA 30건은 실제 생성 후 검수할 항목입니다.
