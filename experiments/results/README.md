# 실험 결과는 GitHub로 공유

**각 담당자는 실행 결과와 진행 기록을 이 저장소에 커밋·푸시합니다.** 로컬 파일이나 채팅 전달만으로 완료 처리하지 않습니다. 담당자와 상태의 원본은 [배정표](../ASSIGNMENTS.md)입니다. 실행 절차는 [runbook](../../docs/guide/experiment-runbook.md)을 따릅니다.

## 경로

```text
experiments/results/
  README.md
  runs/<run-id>/
    REPORT.md                 # 담당자, 모델/조건, 상태, 비용, 장애, artifact 링크
    progress.json             # 진행/중단 상태; 부분 성능 수치 없음
    result.json               # finalize 또는 baseline 전체 완료 후에만
    run.json                  # 키·민감한 접속 정보가 없는 실행 메타데이터
    manifest.json             # 원본 plan 해시/프로토콜/데이터 provenance
    ARTIFACTS.sha256           # 공유 파일 및 대용량 원본의 SHA-256
  cohorts/<cohort-id>/
    cohort.json               # 전 모델 × 양 조건 capacity gate
    REPORT.md                 # 설정/버전, 제외 ID와 사유, 계측 파일 위치
  comparisons/<comparison-id>.json
  leaderboard-<date>.csv
```

`experiments/runs/`는 실행 중 예약·재개를 위한 로컬 작업 공간으로 계속 gitignore 처리합니다. **공유본은 별도로 `experiments/results/`에 복사합니다.** 실행 도중 원본 저널을 수정하거나 git 추적으로 재개 상태를 바꾸지 않습니다. 키를 포함하는 `.env`/`.local.json`은 복사하지 않습니다.

## 언제 올리나

- 착수: 배정표 담당자/run ID, REPORT의 환경·조건·배정 예산을 푸시합니다.
- 계측 완료: count 파일과 설정/버전 기록을 GitHub로 전달하고 취합 담당자에게 링크를 남깁니다.
- 중단·장애 또는 작업 인계: REPORT와 progress를 갱신하고 푸시합니다. 부분 점수는 업로드하지 않습니다.
- **모델/조건 하나가 전체 완료될 때마다:** result·실행 메타데이터·재현 자료를 푸시합니다. 다른 모델의 완료를 기다릴 필요는 없습니다. 아직 전체 비교군이 완료되지 않았다는 사실은 REPORT에 남깁니다.
- 최종 취합: 검증된 result들로 CSV와 bootstrap을 만들고 푸시합니다. smoke/pilot 점수는 본 결과 경로·리더보드에 올리지 않습니다.

## 무엇을 보관하나

완료한 result.json 전체(문서별·카테고리·T/길이/생성기별 분석 포함), 모델/토크나이저/서버 revision, 코드 commit 및 source SHA, dependency inventory, 실제 실행 설정, 데이터 pin/해시, manifest, 계측 파일, cohort gate, 제외 내역, raw 응답/예측, 예약·비용 저널을 보관합니다. API 키·인증 헤더·토큰을 포함한 URL은 제외합니다. 공유를 위해 메타데이터의 민감한 접속 정보를 가린 경우 REPORT에 가린 필드를 표시하고 원본은 실행자에게 보관합니다. 원본 request/data/config 해시를 새로 계산해 덮어쓰지 않습니다.

작은 JSON/CSV/Markdown은 git으로 추적합니다. raw 응답/저널/계측 묶음이 큰 경우 gzip으로 압축하고 **같은 GitHub 레포의 Release asset**으로 올린 뒤 REPORT에 다운로드 링크·SHA-256·포함 파일·원본 해시를 남깁니다. 팀 운영 기준으로 파일이 20 MiB를 넘으면 이 경로를 사용합니다. 데이터셋 본문과 반복 프롬프트는 HF pin + 요청 생성 설정/해시로 재현하므로 git에 중복 저장할 필요가 없습니다. 압축 파일에도 동일한 비밀정보 점검을 적용합니다.

## 제출 예시

아래는 완료된 Claude/full 실행의 예입니다. 실제 run ID로 경로를 바꿉니다. 먼저 finalize를 수행하고, REPORT는 [템플릿](../../docs/templates/experiment-report.md)을 채웁니다. 복사한 메타데이터에 키·민감한 endpoint가 없는지 확인합니다.

```bash
mkdir -p experiments/results/runs/0924-01-claude-full
cp experiments/runs/claude-full/result.json experiments/results/runs/0924-01-claude-full/
cp experiments/runs/claude-full/run.json experiments/results/runs/0924-01-claude-full/
cp experiments/runs/claude-full/progress.json experiments/results/runs/0924-01-claude-full/
cp experiments/prepared/full_context_targeted/manifest.json experiments/results/runs/0924-01-claude-full/
cp docs/templates/experiment-report.md experiments/results/runs/0924-01-claude-full/REPORT.md
```

REPORT와 artifact 목록/해시를 채운 다음, **자신의 결과 경로만** stage합니다. `git add .`로 로컬 작업물을 일괄 포함하지 않습니다.

```bash
git add experiments/results/runs/0924-01-claude-full experiments/ASSIGNMENTS.md
git diff --cached --check
git diff --cached --stat
git commit -m "exp: share 0924-01 claude full results"
git push origin HEAD
```

팀 레포의 main에서 작업 중이면 main에 푸시합니다. 별도 브랜치라면 `codex/<작업명>` 등을 사용하고 PR 링크를 배정표에 기록합니다. 원격 업데이트로 push가 거부되면 변경을 가져와 충돌을 해결한 뒤 다시 푸시하며 force push하지 않습니다. 다른 담당자의 결과 디렉토리·과거 결과는 덮어쓰지 않습니다. 재실행은 새 run ID와 사유를 기록하고 실패했던 실행도 보존합니다.

공유 완료 기준: GitHub에서 결과/REPORT/artifact 링크를 열 수 있고, 배정표에 담당자·상태·결과 링크가 반영되어 있어야 합니다. 연구책임자에게는 그 링크를 전달합니다.
