# src — 코드

```
src/
├── generate/    ← 합성 코퍼스 생성 (택소노미 yaml → 문서). 식별자 포맷/체크섬 유틸 포함
├── eval/        ← 평가. metrics.py의 지표 이름 = 결과 json의 metrics 키
└── prompts/     ← 프롬프트 파일. 버전 붙여서 (span_p1.txt, deid_p1.txt …). 고치면 새 버전 파일
```

## 규칙

- 택소노미는 `taxonomy/taxonomy.yaml`을 읽어서 씁니다. 코드에 카테고리를 하드코딩하지 않습니다.
- 프롬프트는 파일로. 코드 문자열 안에 넣지 않습니다. 결과 json의 `prompt_version`이 파일명을 가리킵니다.
- API 키는 `.env` (gitignore됨). 예시는 `.env.example`.
- 실행 진입점은 `python -m src.eval.run --config experiments/configs/<run_id>.yaml` 형태로 통일 (예정).

## 환경

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
