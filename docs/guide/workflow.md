# Git 워크플로 가이드

5분이면 읽습니다. 규칙은 최소로 두고, 대신 꼭 지킵니다.

## 브랜치

- `main`: 항상 "다른 사람이 봐도 되는" 상태. 직접 push 금지.
- 작업 브랜치: `이름/짧은-주제` — 예: `hanwool/taxonomy-v1`, `sh/gen-pipeline`
- 작업이 끝나면 PR → 리뷰 1명 → squash merge.
- 문서만 고치는 작은 변경(오타, STATUS 갱신)은 `main`에 바로 커밋해도 됩니다. 단, 남의 문서를 크게 고칠 때는 PR.

## 커밋 메시지

`영역: 무엇을 했는지` 한 줄. 필요하면 빈 줄 후 본문.

```
taxonomy: Legal tier 초안 (신용정보법 시행령 §2 매핑)
lit: Thunder-DeID 노트 추가, bib 갱신
exp: EXAONE-3.5-7.8B 스팬 추출 결과 (run 0912-03)
fig: Figure 2 subject 수별 F1 곡선
docs: ADR-0002 생성 모델 결정
status: 9/15 주간 갱신
paper: Overleaf 포인터 갱신 (intro 수정 반영)
```

영역 태그: `taxonomy` `lit` `exp` `fig` `docs` `status` `src` `paper` `owners`

## 무엇을 커밋하고 무엇을 안 하나

커밋 **함**: 문서, 설정, 결과 요약(csv/json, 수 MB 이하), figure pdf/png, 코드, bib
커밋 **안 함**: 원본 데이터 대용량 파일, 모델 가중치, API 키, 개인 노트북 체크포인트, `.env`

대용량은 `data/` 아래에 두고 `.gitignore`에 걸려 있습니다. 공유가 필요하면 위치(드라이브/S3 경로)를 `data/README.md`에 적습니다.

## PR 체크리스트

- [ ] 결과 파일에 config + 커밋 해시가 있는가 (실험일 때)
- [ ] 결정이 포함되면 ADR을 만들었는가
- [ ] STATUS.md가 바뀌어야 하면 바꿨는가
- [ ] 논문에 들어갈 수치면 `leaderboard.csv`에 반영했는가

## 자주 쓰는 명령

```bash
git switch -c hanwool/taxonomy-v1          # 브랜치 만들기
git add -p                                 # 조각 단위로 담기 (뭘 커밋하는지 보면서)
git commit -m "taxonomy: Legal tier 초안"
git push -u origin hanwool/taxonomy-v1
git submodule update --remote paper        # Overleaf 최신 반영 (docs/guide/overleaf.md 참고)
```
