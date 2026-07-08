import os

import pytest

from chart_interpreter.schema import Candle, ChartInput
from chart_interpreter.summarizer.build_summary import analyze_and_summarize
from chart_interpreter.visualizer.static_chart import render_chart


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


def test_render_chart_with_default_overlays_creates_png_file(tmp_path: object) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_chart(chart_input, analysis, save_dir=str(tmp_path))

    assert os.path.exists(save_path)
    assert os.path.getsize(save_path) > 0
    assert save_path.endswith(".png")


def test_render_chart_filename_matches_symbol_timeframe_and_last_timestamp(
    tmp_path: object,
) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_chart(chart_input, analysis, save_dir=str(tmp_path))

    expected_name = f"005930_1D_{chart_input.candles[-1].timestamp}.png"
    assert os.path.basename(save_path) == expected_name


def test_render_chart_rejects_unknown_overlay(tmp_path: object) -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    with pytest.raises(ValueError):
        render_chart(chart_input, analysis, save_dir=str(tmp_path), overlays=["존재하지않음"])


def test_render_chart_with_no_line_overlays_still_produces_file(tmp_path: object) -> None:
    """overlays=[]는 addplot 없이(캔들+거래량만) 렌더링해야 한다 — mplfinance의 addplot
    kwarg는 값을 아예 안 넘기거나 dict/list여야 하고 None을 명시적으로 넘기면 검증 실패로
    죽는다는 실제 버그를 여기서 재현 확인했으므로 회귀 방지용으로 남긴다."""
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_chart(chart_input, analysis, save_dir=str(tmp_path), overlays=["volume"])

    assert os.path.exists(save_path)


def test_render_chart_candle_pattern_overlay_only_produces_file(tmp_path: object) -> None:
    chart_input = make_engulfing_chart_input()
    analysis, _ = analyze_and_summarize(chart_input)
    assert analysis.candle_pattern == "상승장악형"

    save_path = render_chart(
        chart_input, analysis, save_dir=str(tmp_path), overlays=["candle_pattern"]
    )

    assert os.path.exists(save_path)


def test_render_chart_all_overlays_together_produces_file(tmp_path: object) -> None:
    chart_input = make_engulfing_chart_input()
    analysis, _ = analyze_and_summarize(chart_input)

    save_path = render_chart(
        chart_input,
        analysis,
        save_dir=str(tmp_path),
        overlays=["ma", "trendline", "support_resistance", "range_box", "candle_pattern", "volume"],
    )

    assert os.path.exists(save_path)
