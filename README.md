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
