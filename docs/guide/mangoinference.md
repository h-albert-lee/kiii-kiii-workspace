# MangoInference 연결 및 생성기 비교

2026-09-18 · API 주생성기 변경 여부를 판단하기 위한 소규모 시험

완료된 첫 시험의 건수·비용·실패 사유는 [시험 보고서](../pilot-mangoinference-comparison.md)에 기록했다. 아래 명령은 유료 호출 예시이며, 이번 출력 파일에는 한도 종료 응답이 있어 그대로 재개하면 거부된다. 재시험할 때는 수정한 프롬프트 버전과 별도 출력 경로를 사용한다.

후속 `compose_v3` 4건 시험에서는 GLM 4/4 자동 검증 통과, DeepSeek 503 일시 사용 불가를 확인했다. 내용 검토 이슈와 결과는 [재시험 보고서](../pilot-mangoinference-retest.md)에 있다. GLM은 `--prompt-version compose_v3`로 실행할 수 있으며 주생성기 변경은 아직 결정하지 않았다.

## 연결

공식 API 주소는 `https://api.mangoboost.io/v1`이다. `.env`의 `MANGOINFERENCE_API_KEY`를 사용하며 기존 `OPENAI_API_KEY`와 분리한다. `.env`는 Git에서 제외하고 파일 권한을 0600으로 유지한다. 소스 코드·실행 보고서에 키를 넣지 않는다.

2026-09-18 제공된 키로 `GET /v1/models` 연결 성공. 실제 반환된 모델 ID:

- `deepseek-ai/DeepSeek-V4-Pro-0813`
- `zai-org/GLM-5.2-FP8`
- `zai-org/GLM-5.2-MXFP4`
- `minimax/MiniMax-M3`

화면의 표시 이름과 API ID가 다르므로 목록에서 반환된 ID를 그대로 사용한다.

```bash
set -a
source .env
set +a
.venv/bin/python -m src.generate.run compose \
  --plan data/corpus/mango-comparison-2026-09-18/plan.jsonl \
  --generator-slice api-main \
  --model deepseek-ai/DeepSeek-V4-Pro-0813 \
  --base-url "$MANGOINFERENCE_BASE_URL" \
  --prompt-version compose_v2 --workers 2 \
  --out data/corpus/mango-comparison-2026-09-18/raw.deepseek.jsonl
```

GLM은 모델을 `zai-org/GLM-5.2-FP8`, 출력 파일을 `raw.glm.jsonl`로 바꾼다. 기존 완료 응답은 재개 시 건너뛰고, 모델/계획/프롬프트 불일치는 거부한다. 실패 후 재개는 먼저 원문과 오류를 확인한다. 완료 여부가 불명확한 요청은 중복 과금될 수 있어 무조건 재실행하지 않는다.

## 호출 설정

MangoInference 도메인에는 별도 제공자 설정을 사용한다. `temperature=0.8`, `top_p=1.0`, `max_tokens=32000`으로 지정하며, 문서화되지 않은 `seed`나 `reasoning_effort`는 보내지 않는다. 추론은 서버 기본 동작이다. 자동 재시도는 끄고 요청별 시간 제한은 1,200초로 둔다. 코드로 식별자 값을 채울 때에는 기존 계획 seed가 적용된다.

최종 본문은 `message.content`만 사용한다. 응답 모델 ID, `metadata.weight_version` 등 서버 메타데이터, 요청 옵션, 사용 토큰, 응답 시간은 원문 레코드의 `completion`에 기록한다. 추론 원문은 별도 저장하지 않는다. `usage.reasoning_tokens`와 OpenAI 형식의 중첩 필드를 모두 지원하며 추론 토큰을 출력 토큰에 다시 더하지 않는다.

MangoInference의 Batch 호환성은 확인하지 않았다. 현재 `batch-*`는 OpenAI 공식 API 전용이므로 MangoInference에는 위의 `compose` 경로를 사용한다.

## 비교 범위

기존 Astra v2 사전 시험과 같은 문서 계획 10건을 각 모델에 적용한다. 문서 유형 10종, T0~T3, 고객 1/3/8명, 길이 1k/4k/16k를 포함한다. 프롬프트는 `compose_v2`를 그대로 사용한다. 모델별 토크나이저, 생성 날짜, 추론 설정까지 동일한 통제 실험은 아니다.

본문 생성에 성공했어도 태그 형식·은행 옵션·주체 연결·속성 경계가 맞는지는 별도 검증한다. 현재 프롬프트에는 지원 은행 전체 목록과 subtype 태그 예시가 충분히 설명되지 않은 부분이 있어, 실패 원인을 모델 능력만으로 돌리지 않는다.

```bash
.venv/bin/python scripts/report_generator_comparison.py \
  --directory data/corpus/mango-comparison-2026-09-18
```

결과는 모델별 `audit.*.json`, `docs.*.jsonl`, `docs.*.rejects.jsonl`, `comparison-summary.json`에 저장된다. 원문은 보존한다. 요약은 저장된 응답에 한정하므로 실행 중에는 부분 결과다. 비용은 사용자가 제공한 콘솔 화면의 단가로 환산한 추정치이며 실제 크레딧 차감액이 아니다. 반환되지 않은 응답·중단 요청·계정별 요금 조건은 포함하지 않는다.

이 시험만으로 Astra 교체 또는 Qwen 비교군 삭제를 결정하지 않는다. Qwen 20% 비교군 계획은 유지한다.

## 공식 참고

- [Quickstart](https://inference.mangoboost.io/docs/getting-started/quickstart/)
- [Chat Completions](https://inference.mangoboost.io/docs/reference/chat-completions/)
- [모델 ID와 요금](https://inference.mangoboost.io/docs/reference/models-and-pricing/)
- [추론과 사용량](https://inference.mangoboost.io/docs/guides/reasoning/)
