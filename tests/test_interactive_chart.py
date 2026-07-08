import os

import pytest

from chart_interpreter.schema import Candle, ChartInput
from chart_interpreter.summarizer.build_summary import analyze_and_summarize
from chart_interpreter.visualizer.interactive_chart import build_figure, render_interactive_chart


def make_uptrend_candles(n: int) -> list[Candle]:
    prices = []
    for i in range(n):
        leg = i // 12
        pos = i % 12
        amplitude = 10 + leg * 8
        base = 100 + leg * 25
        if pos <= 6:
            price = base + pos * (amplitude / 6)
        else:
            price = base + amplitude - (pos - 6) * (amplitude / 6)
        prices.append(float(price))
    return [
        Candle(timestamp=i, open=p, high=p, low=p, close=p, volume=100.0)
        for i, p in enumerate(prices)
    ]


def make_engulfing_chart_input() -> ChartInput:
    candles = [
        Candle(timestamp=i, open=100.0, high=100.0, low=100.0, close=100.0, volume=100.0)
        for i in range(60)
    ] + [
        Candle(timestamp=60, open=110.0, high=111.0, low=99.0, close=100.0, volume=100.0),
        Candle(timestamp=61, open=95.0, high=116.0, low=94.0, close=115.0, volume=300.0),
        Candle(timestamp=62, open=115.0, high=116.0, low=114.0, close=115.0, volume=50.0),
    ]
    return ChartInput(symbol="BTCUSDT", timeframe="4H", candles=candles)


def test_render_interactive_chart_with_default_overlays_creates_html_file(
    tmp_path: object,
) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_interactive_chart(chart_input, analysis, save_dir=str(tmp_path))

    assert os.path.exists(save_path)
    assert os.path.getsize(save_path) > 0
    assert save_path.endswith(".html")


def test_render_interactive_chart_filename_matches_symbol_timeframe_and_last_timestamp(
    tmp_path: object,
) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_interactive_chart(chart_input, analysis, save_dir=str(tmp_path))

    expected_name = f"005930_1D_{chart_input.candles[-1].timestamp}.html"
    assert os.path.basename(save_path) == expected_name


def test_render_interactive_chart_rejects_unknown_overlay(tmp_path: object) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    with pytest.raises(ValueError):
        render_interactive_chart(
            chart_input, analysis, save_dir=str(tmp_path), overlays=["존재하지않음"]
        )


def test_render_interactive_chart_with_no_line_overlays_still_produces_file(
    tmp_path: object,
) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_interactive_chart(
        chart_input, analysis, save_dir=str(tmp_path), overlays=["volume"]
    )

    assert os.path.exists(save_path)


def test_render_interactive_chart_candle_pattern_overlay_only_produces_file(
    tmp_path: object,
) -> None:
    chart_input = make_engulfing_chart_input()
    analysis, _ = analyze_and_summarize(chart_input)
    assert analysis.candle_pattern == "상승장악형"

    save_path = render_interactive_chart(
        chart_input, analysis, save_dir=str(tmp_path), overlays=["candle_pattern"]
    )

    assert os.path.exists(save_path)


def test_build_figure_returns_figure_without_writing_file(tmp_path: object) -> None:
    """render_interactive_chart()와 달리 파일을 저장하지 않고 Figure 객체를 바로 반환해야
    한다 — Streamlit 등 소비 프로젝트 자체 UI에 st.plotly_chart(fig)로 직접 임베드하는
    용도(디스크 I/O 없이)."""
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    fig = build_figure(chart_input, analysis)

    assert fig.data
    assert os.listdir(str(tmp_path)) == []


def test_build_figure_rejects_unknown_overlay() -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    with pytest.raises(ValueError):
        build_figure(chart_input, analysis, overlays=["존재하지않음"])


def test_render_interactive_chart_all_overlays_together_produces_file(tmp_path: object) -> None:
    chart_input = make_engulfing_chart_input()
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_interactive_chart(
        chart_input,
        analysis,
        save_dir=str(tmp_path),
        overlays=["ma", "trendline", "support_resistance", "range_box", "candle_pattern", "volume"],
    )

    assert os.path.exists(save_path)
