# Experiment artifacts

Current execution instructions: [experiment-runbook.md](experiment-runbook.md). Native output is `result.json` from `src.eval.execute finalize` or `src.eval.baselines`, with `manifest`, `execution`, `metrics`, category/axis tables and `per_document`. Source/data/config hashes and native raw responses are retained alongside it. `src.eval.export` produces one CSV row per model/condition; use `src.eval.run compare` for paired document bootstrap.

The following older schema is historical and is not the implemented API. ADR-0029 supersedes its multi-seed CSV/flat metadata assumptions. Do not invent absent metrics to satisfy this example.

# 실험 결과 수합 가이드

여러 사람이 각자 돌린 결과를 한 표로 모으는 방법입니다. 핵심은 **파일 하나 = 실행 하나**, **표 하나 = 논문 표 하나**.

2026-09-20: 새 오프라인 평가 CLI와 실제 출력 스키마는 [evaluation.md](evaluation.md), 실험 조건은 ADR-0020 참조. 아래 JSON은 과거 수합 예시이며 아직 구현되지 않은 지표를 포함한다. 현재 구현은 `metrics.exact_micro`, `category_character_micro`, `entity_all_mentions_exact_recall`, `hard_negative_false_positive_rate`, `non_pii_character_mask_rate`, `by_category`, `by_axis`, `tier_kind_tlevel`, `op_exact_recall`, `subject_role_exact_recall`, `per_document`, `reliability`를 출력한다. TAB risk-weighted recall과 모델의 entity linking 일관성은 아직 구현하지 않았다.

## 실행 ID

`MMDD-NN` 형식. 예: `0912-03` = 9월 12일 세 번째 실행. 결과 파일, config, 커밋 메시지에 모두 이 ID를 씁니다.

## 디렉토리

```
experiments/
├── configs/
│   └── 0912-03.yaml            ← 이 실행의 설정 (모델, 프롬프트 버전, 데이터 버전, 시드)
└── results/
    ├── 0912-03.json            ← 요약 지표 (아래 스키마)
    ├── 0912-03.preds.jsonl.gz  ← 예측 원본 (작으면 커밋, 크면 data/로)
    └── leaderboard.csv         ← 마스터 표. 논문 Table 1의 원천
```

## 결과 파일 스키마 (`results/<run_id>.json`)

```json
{
  "run_id": "0912-03",
  "task": "span_extraction",          // span_extraction | deidentification
  "model": "EXAONE-3.5-7.8B-Instruct",
  "model_type": "local",              // api | local | rule
  "data_version": "v0.3",
  "prompt_version": "p2",
  "seed": 0,
  "git_commit": "a1b2c3d",
  "run_by": "hanwool",
  "date": "2026-09-12",
  "metrics": {
    "f1_micro": 0.712,
    "f1_legal": 0.801,
    "f1_identifiability": 0.534,
    "consistency": 0.66
  },
  "by_num_subjects": {"1": 0.85, "3": 0.74, "8": 0.58},
  "by_context_len": {"1k": 0.83, "4k": 0.72, "16k": 0.55},
  "notes": "16k에서 후반부 엔티티 누락 두드러짐"
}
```

`metrics` 키 이름은 `src/eval/metrics.py`의 이름과 같아야 합니다. 새 지표를 추가하면 그 파일과 이 문서를 같이 고칩니다.

## leaderboard.csv 규칙

- 한 줄 = 한 (task, model, data_version, prompt_version) 조합의 **대표 결과**. 시드 여러 개면 평균과 표준편차.
- 새 실행이 기존 줄을 대체하면 기존 줄을 지우고, 커밋 메시지에 `replaces 0910-01`을 적습니다.
- 논문에 들어가는 수치는 이 파일에서만 가져갑니다. 개인 노트북 수치는 안 씁니다.

## 하지 말 것

- config 없는 결과 파일 커밋
- 결과 json을 손으로 고치기 (다시 돌리거나 `notes`에 사유 기록)
- 데이터 생성에 쓴 모델을 리더보드에 무표기로 올리기 → `model_type`에 `generator` 표기 (ADR-0002 참고)
