import pytest

from chart_interpreter.errors import InsufficientCandlesError
from chart_interpreter.schema import Candle, ChartInput
from chart_interpreter.summarizer.build_summary import build_partial_summary


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


def test_build_partial_summary_raises_when_not_enough_candles() -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_flat_candles(10))

    with pytest.raises(InsufficientCandlesError) as exc_info:
        build_partial_summary(chart_input)

    assert exc_info.value.symbol == "005930"
    assert exc_info.value.have == 10


def test_build_partial_summary_includes_header_and_ma_sentence() -> None:
    chart_input = ChartInput(symbol="005930", timeframe="1D", candles=make_uptrend_candles(65))

    summary = build_partial_summary(chart_input)

    assert "[005930, 1D]" in summary
    assert "이평선" in summary


def test_build_partial_summary_includes_support_resistance_when_pivots_found() -> None:
    chart_input = ChartInput(symbol="BTCUSDT", timeframe="4H", candles=make_uptrend_candles(65))

    summary = build_partial_summary(chart_input)

    assert "저항선" in summary
    assert "지지선" in summary
    assert "상승" in summary


def test_build_partial_summary_omits_support_resistance_when_no_pivots() -> None:
    chart_input = ChartInput(symbol="FLAT", timeframe="1D", candles=make_flat_candles(65))

    summary = build_partial_summary(chart_input)

    assert "저항선" not in summary
    assert "탐지되지 않았습니다" in summary
