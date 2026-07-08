import pytest

from chart_interpreter.adapters.bybit_adapter import (
    bybit_interval_to_timeframe,
    to_chart_input,
)


def test_to_chart_input_converts_fields_and_timeframe() -> None:
    rows = [
        (1700000000000, 100.0, 110.0, 90.0, 105.0, 50.0),
        (1700000060000, 105.0, 115.0, 100.0, 112.0, 80.0),
    ]

    chart_input = to_chart_input(rows, symbol="BTCUSDT", interval="60")

    assert chart_input.symbol == "BTCUSDT"
    assert chart_input.timeframe == "1H"
    assert len(chart_input.candles) == 2
    assert chart_input.candles[0].timestamp == 1700000000000
    assert chart_input.candles[0].close == 105.0
    assert chart_input.candles[1].volume == 80.0


def test_to_chart_input_sorts_by_timestamp_ascending() -> None:
    rows = [
        (1700000060000, 105.0, 115.0, 100.0, 112.0, 80.0),
        (1700000000000, 100.0, 110.0, 90.0, 105.0, 50.0),
    ]

    chart_input = to_chart_input(rows, symbol="BTCUSDT", interval="D")

    timestamps = [c.timestamp for c in chart_input.candles]
    assert timestamps == sorted(timestamps)


def test_bybit_interval_to_timeframe_maps_known_intervals() -> None:
    assert bybit_interval_to_timeframe("240") == "4H"
    assert bybit_interval_to_timeframe("D") == "1D"


def test_bybit_interval_to_timeframe_raises_on_unknown_interval() -> None:
    with pytest.raises(ValueError, match="알 수 없는 Bybit interval"):
        bybit_interval_to_timeframe("999")
