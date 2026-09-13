# src — 코드

```
src/
├── generate/    ← 합성 코퍼스 생성 (택소노미 yaml → 문서). 식별자 포맷/체크섬 유틸 포함
├── eval/        ← 평가. metrics.py의 지표 이름 = 결과 json의 metrics 키
└── prompts/     ← 프롬프트 파일. 버전 붙여서 (span_p1.txt, deid_p1.txt …). 고치면 새 버전 파일
```

## 생성 파이프라인 (`src/generate`) — 설계는 `docs/generation_design.md`

```
taxonomy.py    taxonomy.yaml 로더 (카테고리·op·문서유형)
identifiers.py 식별자 값 생성 + 체크섬 (rrn·brn·crn·Luhn)
variation.py   표면형 변형 op (T1·T2 + T3 조각화), 합성 규칙·순서
compose.py     문서 계획 → 프롬프트 → LLM (OpenAI 호환; 로컬 vLLM 동일)
fill.py        {{슬롯}}·[[태그]] 파싱 → 값 채움 → gold 스팬(오프셋·entity·op)
negatives.py   hard negative 삽입 ({{NEG}})
validate.py    오프셋·체크섬·누출·태그·길이 검증
run.py         CLI: plan / compose / fill / dryrun
```

```bash
python -m pytest tests -q                                   # 9 tests
python -m src.generate.run dryrun --text sample.txt --level T2   # LLM 없이 fill+validate 확인
python -m src.generate.run plan --n 100 --out data/corpus/pilot-0.1/plan.jsonl
python -m src.generate.run compose --plan … --model gpt-5.5 --out …/raw.jsonl      # API 키 필요
python -m src.generate.run fill --raw …/raw.jsonl --out …/docs.jsonl
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
