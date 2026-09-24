# 본 실험 실행 가이드

2026-09-24. 저장소 루트에서 실행합니다. 이 문서는 새 담당자가 환경을 준비하고 실제 실험을 수행하는 순서입니다. 연구 결정은 ADR-0020/0026/0029/0034를 따릅니다.

먼저 [담당 배정표](../../experiments/ASSIGNMENTS.md)에 담당자와 run ID를 기록합니다. **완료 결과는 [공유 규칙](../../experiments/results/README.md)에 따라 이 GitHub 저장소에 커밋·푸시**합니다. 로컬 저장만으로 작업을 완료하지 않습니다.

## 1. 환경과 담당자 입력

README의 Python 3.12 설치·전체 테스트를 먼저 수행합니다. API 실행에는 GPU가 필요 없습니다. ko-pii 1.16.0, presidio-analyzer 2.2.364를 고정했습니다. 모델 서버는 다른 환경에서 운영해도 됩니다.

담당자가 채울 내용:

| 항목 | 기록 방법 |
|---|---|
| 실제 서비스 모델 ID / 가중치 revision | 모델별 `.local.json`; 이동하는 alias라면 실행 시 제공 버전도 별도 기록 |
| tokenizer/chat template revision | hosted API 버전 또는 서버 tokenizer 커밋·템플릿 SHA |
| 입력/출력/합산 한도 | 실제 배포 endpoint 기준, 추측 금지 |
| 가격·확인일·예산 | 요청 상한에 사용할 보수적 단가; 조건별 예산 배분 |
| sampling / reasoning | `generation`, 기본값을 포함해 공급자 문서와 별도 파일럿으로 확인 |
| operator / run_id | 담당자 식별자, `MMDD-NN` |
| 서버·API 키 | `base_url` 또는 `base_url_env`; 키 자체는 환경변수에만 |

템플릿을 복사합니다. `REPLACE`, null, `settings_frozen: false`는 의도적인 실행 차단입니다.

```bash
cp experiments/configs/evaluation/qwen-2b.example.json experiments/configs/evaluation/qwen-2b.local.json
cp experiments/configs/evaluation/qwen-4b.example.json experiments/configs/evaluation/qwen-4b.local.json
cp experiments/configs/evaluation/kanana.example.json experiments/configs/evaluation/kanana.local.json
```

기본 실행 모델은 Qwen3.5-2B/4B와 Kanana-2-3B입니다. 환경변수: `QWEN_API_KEY`, `KANANA_API_KEY`. Claude/Gemini 템플릿은 보관용이며 기본 matrix에 포함하지 않습니다. 인증 없는 로컬 서버는 해당 `api_key_env` 항목을 삭제합니다. `.env`를 자동으로 읽지 않으므로 셸/비밀 관리 도구로 주입하세요. 키를 커맨드 인자나 문서에 붙이지 않습니다.

**담당: 성현(API 보류), 은빈(GPU Qwen3.5-2B/4B·Kanana-2-3B·OpenMed), 한울(CPU Presidio/ko-pii).** Qwen/Kanana는 **FP16으로 vLLM 등에서 서빙하고 평가 실행기를 API로 연결하는 방식**을 권장합니다. 실제 가중치·GPU·서버 버전의 FP16 지원/안정성·메모리 요구량을 pilot에서 확인합니다. dtype을 자동 결정하거나 양자화로 묵시적으로 바꾸지 않으며, 대안이 필요하면 사유와 실제 정밀도를 공유하고 고정합니다. 서버 실행 명령·버전·dtype·tensor parallel 설정을 결과 REPORT에 보관합니다.

Qwen/Kanana는 OpenAI-compatible **vLLM 서버 + 네이티브 `/tokenize`**를 전제로 합니다. `/chat/completions`만 제공하는 서비스는 정확한 계측 어댑터 없이 사용하지 않습니다. 서버가 사용하는 모델·tokenizer·chat template·추론 설정을 고정하고 서버 로그와 실행 명령을 보관합니다. `/v1` inference 주소와 같은 origin의 `/tokenize`를 사용합니다. private HTTP는 필요할 때만 `allow_private_http: true`를 명시합니다. `chat_template_kwargs`를 쓰면 generation과 tokenize_options에 동일하게 넣습니다. 토큰 수가 생성 요청의 실제 framing과 일치하는지 별도 파일럿에서 확인합니다.

## 2. 데이터 고정 / 파일럿

공개 test만 다운로드할 수 있으므로 paper submodule이나 생성 API 키가 없어도 됩니다.

```bash
python -m src.eval.dataset --repo nmixx-fin/kiii-kiii \
  --revision 2df0589d695c18665fd83d4ca5512e03ca0767f6 \
  --directory experiments/prepared/full_context_targeted
python -m src.eval.dataset --repo nmixx-fin/kiii-kiii \
  --revision 2df0589d695c18665fd83d4ca5512e03ca0767f6 \
  --mode local_window --directory experiments/prepared/local_window
```

다운로드 파일은 release-manifest 체크섬을 검증합니다. 로컬 배포본이 있다면 `--repo … --revision …` 대신 `--local data/releases/kiii-v1`을 사용합니다. 각 준비 폴더에 gold, 요청, 해시 manifest, 경계 표현 가능성 audit가 저장됩니다. 전체 요청은 반복된 긴 본문을 포함하므로 충분한 RAM·디스크(수 GB 이상)를 확보합니다.

최초 연결 점검은 별도 경로와 `--smoke-limit 2`를 사용하세요. 이 결과는 본 리더보드로 내보낼 수 없습니다. **출력 크기·prompt·reasoning 보정은 1,440건과 겹치지 않는 별도 합성 pilot**에서 합니다. pilot JSONL은 본 데이터와 같은 문서 스키마로 준비하고 `python -m src.eval.run prepare --corpus … --directory …`로 만듭니다. 테스트의 작은 fixture는 코드 검증용으로, 대표성 있는 pilot을 대신하지 않습니다. 생성용 과거 pilot을 쓰면 본 평가 문서와 중복되지 않는지 먼저 확인합니다.

확인할 것은 최장 입력 처리, JSON 형식, 반복 인용의 occurrence, 한글·이모지 offset, 빽빽한 TARGET의 출력 잘림, reasoning의 출력 예산 포함 여부입니다. 현재 기본값 core=1200 / halo=1200 문자, output=4096 토큰은 **파일럿에서 확정할 초안**입니다. 바꾸면 두 조건·모든 LLM에 동일 적용하고 새 준비 경로를 사용합니다. CLI 옵션 `--core-chars`, `--halo-chars`, `--max-output-tokens`를 지원합니다. `settings_frozen`은 별도 pilot 검증을 마친 뒤 true로 바꿉니다. 본 실험 결과를 보고 재조정하지 않습니다.

## 3. 정확한 토큰 계측과 공통 평가 집합

기본 세 로컬 LLM은 vLLM native tokenize로 계측합니다. 보관된 API 어댑터는 Claude count_tokens / Gemini countTokens를 지원하지만 이번 기본 실행 범위에는 포함하지 않습니다. 계측은 생성 호출을 하지 않지만 endpoint에 프롬프트를 전송하므로 제공자의 계측 과금/쿼터 정책을 확인합니다. 개별 요청을 순차 계측하며 기존 계측 파일로 재개할 수 있습니다.

아래를 **세 모델 × 두 조건**에 대해 수행합니다 (`qwen-2b`/`full_context_targeted`를 바꿉니다).

```bash
python -m src.eval.execute doctor --config experiments/configs/evaluation/qwen-2b.local.json
python -m src.eval.execute count \
  --config experiments/configs/evaluation/qwen-2b.local.json \
  --directory experiments/prepared/full_context_targeted \
  --output experiments/runs/counts/qwen-2b-full_context_targeted.jsonl
python -m src.eval.execute estimate \
  --config experiments/configs/evaluation/qwen-2b.local.json \
  --directory experiments/prepared/full_context_targeted \
  --measurements experiments/runs/counts/qwen-2b-full_context_targeted.jsonl
```

`doctor`는 오프라인 설정 확인이며 endpoint 연결 성공을 뜻하지 않습니다. 단가는 입력 캐시 할인을 가정하지 않는 상한을 사용합니다. reasoning 포함 최대 출력 비용을 예약하며 도구 사용 비용 등 추가 과금 기능은 사용하지 않습니다. 예산은 **run 폴더별**이므로 같은 budget을 6개 실행에 복제하면 총 예산도 6배가 됩니다. GPU 시간·서버 임대 비용은 토큰 과금 장부에 포함되지 않습니다.

모든 입력이 각 endpoint의 한도에 들어가면:

```bash
cp experiments/configs/evaluation/matrix.example.json experiments/configs/evaluation/matrix.local.json
python -m src.eval.cohort --matrix experiments/configs/evaluation/matrix.local.json \
  --output experiments/runs/cohort.json
```

matrix 기본 목록은 qwen-2b/qwen-4b/kanana × 두 조건입니다. 각 config/plan/counts 경로를 실제 경로에 맞춥니다. Kanana의 공식 한도는 32,768이며 실제 배포 한도와 전체 prompt+출력 토큰 합계를 확인합니다. GPU 사양 미확인 상태에서 concurrency나 최대 문맥을 임의로 크게 잡지 않습니다. 모델을 줄이기로 결정하면 **양 조건에서 같은 모델 목록**으로 수정하고 ADR에 남깁니다. gate는 동일 데이터, 출력 partition, 모든 계측의 capacity/config/hash를 검사합니다. 기준 미달 문서가 하나라도 있으면 본 실행을 거부합니다.

한도 초과가 있는 경우 해당 조건의 모델별 count JSONL을 합쳐 `src.eval.run preflight`를 실행하면 모델별 제외 ID와 common_eligible_doc_ids가 나옵니다. **양 조건의 eligible ID 교집합**을 JSON 배열로 저장하고 두 dataset 준비 명령 모두 `--doc-ids eligible.json`으로 새로 만듭니다. 모든 모델의 새 요청을 다시 계측하고 matrix 경로를 갱신합니다. 제외 사유/원래 모수/최종 모수를 결과와 함께 보관합니다. gold 내용이나 검출 성능에 따른 제외는 금지합니다. 각 모델마다 가능한 문서만 따로 쓰면 안 됩니다.

## 4. 실행·중단·재개

담당자에게 확정 설정, 전체 예상 비용, 모델·조건별 배정 예산을 공유한 뒤 승인된 배정으로 실행합니다. 아래 명령은 **유료 추론을 실제 수행**합니다.

```bash
python -m src.eval.execute run --execute \
  --config experiments/configs/evaluation/qwen-2b.local.json \
  --directory experiments/prepared/full_context_targeted \
  --measurements experiments/runs/counts/qwen-2b-full_context_targeted.jsonl \
  --cohort experiments/runs/cohort.json \
  --output experiments/runs/qwen-2b-full
```

- 같은 명령·같은 폴더로 재개합니다. `progress.json`에서 finished/planned, complete, spent_or_reserved, stop_reason을 확인합니다. `--max-new N`은 이번 실행의 호출 수만 제한합니다.
- 실행 폴더의 lock으로 중복 프로세스를 막습니다. 요청은 전송 전에 최대 비용을 디스크에 기록합니다. 정상 완료된 요청과 실패한 요청은 재전송하지 않습니다.
- 네트워크 오류/강제 종료로 과금 여부가 불명확하면 예약을 유지합니다. 재개 시 미완료 요청은 uncertain 실패로 기록합니다. 자동 재시도·출력 보정은 없으며, 오류도 평가에 포함됩니다.
- transport/API 예외가 발생하면 현재 동시 batch의 응답을 기록한 뒤 실행을 멈춥니다. endpoint를 조사한 뒤 재개하세요. 현재 실행기는 오류별 자동 backoff/retry를 하지 않습니다. 같은 조건의 결과를 선택적으로 재생성하지 않습니다.
- 같은 run의 코드·모델·프롬프트·단가·토크나이저 변경은 막습니다. 예산, 동시성(1–32), timeout만 재개 중 변경할 수 있습니다. 예산 증액은 담당자 승인 범위 내에서만 합니다. 서버 버전 변경도 새 실험으로 기록합니다.
- run.json(설정·코드 SHA·dependency inventory), events.jsonl(예약·raw 응답), responses.jsonl, progress.json을 별도로 백업합니다. 실험은 노트북보다 지속 실행 가능한 서버에서 수행하는 편이 좋습니다.

완료 후:

```bash
python -m src.eval.execute finalize \
  --config experiments/configs/evaluation/qwen-2b.local.json \
  --directory experiments/prepared/full_context_targeted \
  --output experiments/runs/qwen-2b-full
```

## 5. 베이스라인

[라벨 매핑/한계](../../experiments/label_maps/README.md)를 읽고 별도 pilot에서 고정합니다. LLM 두 조건과 동일한 최종 문서 집합을 쓰되, 규칙은 문서 전체를 한 번 처리하며 OpenMed는 명시적인 겹침 토큰 창을 씁니다. 이를 full-context LLM 조건과 동일한 구조라고 주장하지 않습니다. 각 baseline은 한 번만 실행합니다.

```bash
python -m src.eval.baselines --name presidio --directory experiments/prepared/full_context_targeted --output experiments/runs/presidio
python -m src.eval.baselines --name ko-pii --directory experiments/prepared/full_context_targeted --output experiments/runs/ko-pii
```

**OpenMed 담당도 은빈입니다.** OpenMed는 chat LLM이 아닌 토큰 분류 모델이므로 현재 구현의 Transformers 경로로 실행합니다. FP16 vLLM chat 서빙 지침을 그대로 적용하지 않습니다.

OpenMed는 호스트에 맞는 torch/CUDA와 `requirements-eval-openmed.txt`를 별도 환경에 설치합니다. native `OpenAIPrivacyFilterForTokenClassification`을 제공하는 transformers가 필요합니다. 설정만 맞춰 놓은 상태이며 **이 저장소 준비 세션에서 실제 GPU 모델을 로드/검증한 것은 아닙니다**. 설치 버전·모델 config 호환을 연결 점검에서 확인하고 고정하세요.

```bash
python -m src.eval.baselines --name openmed \
  --revision f914f18d909d541d288dfda44a4d0b6bdb638d57 \
  --device cuda --window 1024 --overlap 128 \
  --directory experiments/prepared/full_context_targeted --output experiments/runs/openmed
```

OpenMed 구현은 토큰 logits argmax + BIOES grouping이며 OpenMed wrapper의 Viterbi decoding 결과와 동일하다고 주장하지 않습니다. 창 설정은 별도 pilot에서 고정합니다. 모든 창을 처리하고 정확히 중복된 span만 제거합니다. 경계의 충돌/조각은 gold로 고치지 않습니다. 오류가 나면 현재 문서 기록 전에 중단하므로 같은 명령으로 재개할 수 있습니다. 원본 source label도 보관합니다.

## 6. 결과 제출

각 모델·조건이 전체 완료되면 result와 재현 자료를 `experiments/results/runs/<run-id>/`에 정리하여 커밋·푸시하고 배정표에 링크를 남깁니다. 큰 원본 응답·계측·저널은 같은 GitHub 레포의 Release asset으로 올립니다. 구체적인 파일 목록·명령·중단 시 공유 방식은 [결과 공유 가이드](../../experiments/results/README.md)를 따릅니다.

```bash
python -m src.eval.run compare --first experiments/runs/qwen-2b-full/result.json \
  --second experiments/runs/qwen-2b-local/result.json --output experiments/runs/qwen-2b-context-comparison.json
python -m src.eval.export --results experiments/runs/qwen-2b-full/result.json \
  experiments/runs/qwen-2b-local/result.json experiments/runs/presidio/result.json \
  --output experiments/results/leaderboard-0923-01.csv
```

모든 최종 result를 명시적으로 나열합니다. export는 기존 파일을 덮어쓰지 않으며 pilot, 미완료 LLM run, 생성기, 서로 다른 평가 집합을 거부합니다. 산출물을 검토한 뒤에만 기존 헤더뿐인 leaderboard.csv를 최종 CSV로 교체합니다. 이 CSV 스키마는 모델·조건별 한 행으로, 옛 다중 seed 스키마를 대체합니다.

제출 묶음: 사용 git commit + 코드 SHA, frozen config(키 제외), 데이터 revision/해시, 모델·tokenizer/server revision, dependency inventory, count 파일, cohort gate, 제외 내역, raw 응답 저널, result JSON, leaderboard, paired bootstrap JSON, 실제 청구와 장부의 차이 설명. rule baseline에는 token 비용 대신 환경·wall-clock 기록을 첨부합니다. 모델별 실패율과 길이·T·생성기별 성능도 result에서 보고합니다. bootstrap은 문서 단위 2,000회 seed 0이며 차이 방향은 first − second입니다.

API/모델 호출, 토큰 비용, 검출 성능은 실행 전에는 알려져 있지 않습니다. `experiments/preflight/0923-inventory.json`의 문자 수를 토큰 수나 비용으로 인용하지 마세요.
