"""tests/fixtures/real/의 실 데이터로 analyze_and_summarize() → render_chart()/
render_interactive_chart() 전체 파이프라인을 단독 실행해 PNG/HTML을 실제로 생성한다.

찰눈은 소비 프로젝트(주단/코단/비단) 없이도 라이브러리 자체로 차트를 볼 수 있는지 확인하기
위한 데모 스크립트 — 라이브러리 코드(src/chart_interpreter)는 건드리지 않고 사용법만 보여준다.

실행: uv run python scripts/demo_render_chart.py
"""

import io
import json
import os
import sys

from chart_interpreter.adapters.bybit_adapter import to_chart_input
from chart_interpreter.summarizer.build_summary import analyze_and_summarize
from chart_interpreter.visualizer.interactive_chart import render_interactive_chart
from chart_interpreter.visualizer.static_chart import render_chart

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "tests", "fixtures", "real", "kodan_BTCUSDT_60.json"
)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "demo")


def main() -> None:
    # Windows 콘솔 기본 코드페이지(cp949)는 한글 요약 문장의 일부 문자(em dash 등)를 인코딩하지
    # 못해 UnicodeEncodeError로 죽는다 — 실행 환경 의존성을 이 스크립트 안에서 흡수한다.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")

    with open(FIXTURE_PATH, encoding="utf-8") as f:
        fixture = json.load(f)

    rows = [
        (int(ts), float(o), float(h), float(low), float(c), float(v))
        for ts, o, h, low, c, v, _turnover in fixture["rows"]
    ]
    chart_input = to_chart_input(rows, symbol=fixture["symbol"], interval=fixture["interval"])

    analysis, summary_text = analyze_and_summarize(chart_input)
    print(summary_text)
    print()

    overlays = ["ma", "trendline", "support_resistance", "range_box", "volume", "candle_pattern"]
    png_path = render_chart(chart_input, analysis, save_dir=OUTPUT_DIR, overlays=overlays)
    html_path = render_interactive_chart(
        chart_input, analysis, save_dir=OUTPUT_DIR, overlays=overlays
    )

    print(f"PNG:  {png_path}")
    print(f"HTML: {html_path}")


if __name__ == "__main__":
    main()
