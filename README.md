# 찰눈 (차트보는눈)

차트를 안 봐도, 지금 상태를 구체적인 자연어 문장으로 판단할 수 있게 하는 차트 해석·요약 독립 라이브러리.
주단(주식) / 코단(코인) / 비단(비트코인) 3개 프로젝트가 공용으로 import한다.

기준 문서: [`차트해석엔진_프로젝트스펙.md`](./차트해석엔진_프로젝트스펙.md)
규율/절차: [`CLAUDE.md`](./CLAUDE.md)
현재 진행 상태: [`docs/MASTER.md`](./docs/MASTER.md)

## 개발 환경

```bash
uv sync
uv run ruff check .
uv run mypy . --strict
uv run pytest
```

## 소비 프로젝트 연동

```python
from chart_interpreter.adapters.kiwoom_adapter import to_chart_input
from chart_interpreter.summarizer.build_summary import analyze_and_summarize

chart_input = to_chart_input(kiwoom_ohlcv_data, symbol="005930", timeframe="1D")
analysis, summary_text = analyze_and_summarize(chart_input)
```

## 단독 실행 데모

소비 프로젝트(주단/코단/비단) 없이 이 저장소 안에서 실 데이터로 요약 문장 + 차트 이미지를 바로 확인할 수 있다.

```bash
uv sync
uv run python scripts/demo_render_chart.py
```

`tests/fixtures/real/kodan_BTCUSDT_60.json`을 읽어 `analyze_and_summarize()` → `render_chart()`/`render_interactive_chart()`를 실행하고, 생성된 PNG/HTML 경로를 출력한다(`output/demo/`, git 추적 제외).
