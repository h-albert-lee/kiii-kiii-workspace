# ADR-0003: 타겟 venue — ICAIF'26 Workshop on Financial AI Security, Privacy, and Safety

- 상태: accepted
- 날짜: 2026-09-13
- 결정자: 한울
- 관련: ADR-0001, `paper/` (submodule → github.com/h-albert-lee/ICAIF-workshop, Overleaf 연동)

## 배경

한울이 ICAIF 워크샵용 Overleaf 프로젝트(ACM acmart)를 이미 만들어 GitHub에 연동해 둠. ICAIF'26 (Milan, Nov 14–17) 워크샵 CFP를 조사한 결과 4페이지 short paper에 맞는 트랙이 있음.

## 결정

**1순위: Workshop on Financial AI Security, Privacy, and Safety** (ICAIF'26, Nov 14 또는 15)
- 마감 **2026-10-08** (시간대 미명시 → AoE로 가정, 실제로는 10/7 KST 자정 전 제출 목표), 통보 10/15, 카메라레디 10/24 (expected)
- **4페이지, 참고문헌·부록 제외**, ACM sigconf 2단, **double-blind**, rebuttal 없음, OpenReview
- non-archival (제목·저자만 공개, 논문 비공개) → 이후 FinNLP / ACL / NeurIPS D&B 풀버전에 제약 없음
- 주최: 금융보안원(FSI), KFTC, 카카오뱅크, UNIST, Google, BlackRock, Intesa — 한국 금융 PII 벤치마크의 이상적 청중

**2순위(병행 검토): AI4F — 3rd Workshop on LLMs and Generative AI for Finance** — 10/7 AoE, 길이 제한 없음, single-blind, non-archival, "New datasets, evaluation benchmarks" 토픽 명시. 두 워크샵 모두 non-archival이지만 이중 제출 정책 미명시 [?] → 1순위 결과 후 결정.

**제외:** RAIOps4Fin (10/1, 6p, CEUR 옵션은 ≥5p) — 마감이 너무 이르고 프레이밍이 운영 쪽. 메인 트랙 short paper 없음.

## 이유

- 4페이지 excl. refs = ADR-0001의 분량 계획과 정확히 일치.
- 청중이 곧 잠재 사용자(금융보안원·KFTC·카카오뱅크)라 AIM 비즈니스 측면에서도 최적.
- non-archival이라 벤치마크 공개 후 풀페이퍼 확장 여지 유지.

## 영향 — 일정이 빠듯함

오늘(9/13)부터 **25일**. 역산:
| 날짜 | 마일스톤 |
|---|---|
| 9/15 | 파일럿 100건 생성·검수, 프롬프트 튜닝 |
| 9/18 | 본 코퍼스 생성 완료 (2~3k), 이름·주소 사전 확장 |
| 9/22 | `src/eval` 완성, 규칙 베이스라인 + API 4종 결과 |
| 9/27 | 로컬 10종 결과 (GPU 확보 전제) |
| 10/1 | figure·표 확정, 초고 완성 |
| 10/5 | 내부 리뷰 반영, 익명화 점검 |
| 10/7 KST | 제출 |

- `paper/main.tex`는 `\documentclass[sigconf,anonymous,review]{acmart}`, 4페이지 본문 + refs.
- 익명화: 레포 URL·AIM·토스증권·"Powered by …" 표기는 카메라레디에만. 초고에는 `\anon{}` 매크로.
- Figure는 단일 컬럼 3.3in 기준 (`figures/src/_style.py` 그대로).
