import pytest

from chart_interpreter.errors import InsufficientCandlesError
from chart_interpreter.schema import Candle, ChartInput
from chart_interpreter.summarizer.build_summary import analyze_and_summarize


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


def make_flat_candles(n: int) -> list[Candle]:
    return [
        Candle(timestamp=i, open=100.0, high=100.0, low=100.0, close=100.0, volume=100.0)
        for i in range(n)
    ]


def test_analyze_and_summarize_raises_when_not_enough_candles() -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_flat_candles(10))

    with pytest.raises(InsufficientCandlesError) as exc_info:
        analyze_and_summarize(chart_input)

    assert exc_info.value.symbol == "005930"
    assert exc_info.value.have == 10


def test_analyze_and_summarize_uptrend_fills_pivots_and_all_sentence_categories() -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))

    analysis, summary = analyze_and_summarize(chart_input)

    assert analysis.symbol == "005930"
    assert analysis.trend_direction == "상승"
    assert analysis.resistance_price > analysis.support_price
    assert "[005930, 1D]" in summary
    assert "상승" in summary
    assert "이평선" in summary
    assert "저항선" in summary
    assert "지지선" in summary
    assert "거래량" in summary
    assert "요약" in summary


def test_analyze_and_summarize_flat_data_falls_back_pivots_to_current_price() -> None:
    chart_input = ChartInput(symbol="FLAT", timeframe="1D", candles=make_flat_candles(65))

    analysis, summary = analyze_and_summarize(chart_input)

    assert analysis.resistance_price == 100.0
    assert analysis.support_price == 100.0
    assert analysis.resistance_distance_pct == 0.0
    assert analysis.support_distance_pct == 0.0
    assert analysis.pivot_high_recent == analysis.resistance_price
    assert analysis.pivot_low_recent == analysis.support_price
    assert analysis.candle_pattern is None
    assert "탐지되지 않았습니다" in summary
    assert "감지되지 않았습니다" in summary


def test_analyze_and_summarize_detects_engulfing_pattern_in_final_candles() -> None:
    candles = make_flat_candles(60) + [
        Candle(timestamp=60, open=110.0, high=111.0, low=99.0, close=100.0, volume=100.0),
        Candle(timestamp=61, open=95.0, high=116.0, low=94.0, close=115.0, volume=300.0),
        Candle(timestamp=62, open=115.0, high=116.0, low=114.0, close=115.0, volume=50.0),
    ]
    chart_input = ChartInput(symbol="BTCUSDT", timeframe="4H", candles=candles)

    analysis, summary = analyze_and_summarize(chart_input)

    assert analysis.candle_pattern == "상승장악형"
    assert "상승장악형" in summary
