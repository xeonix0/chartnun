from datetime import datetime, timezone

import pytest

from chart_interpreter.adapters.kiwoom_adapter import (
    kiwoom_interval_to_timeframe,
    to_chart_input,
)


def test_to_chart_input_converts_kst_naive_datetime_to_utc_epoch_ms() -> None:
    bars = [
        (datetime(2026, 7, 8, 9, 5, 0), 71000, 71500, 70800, 71200, 12345),
    ]

    chart_input = to_chart_input(bars, symbol="005930", interval_seconds=300)

    # KST 09:05 == UTC 00:05 (같은 날)
    expected_utc = datetime(2026, 7, 8, 0, 5, 0, tzinfo=timezone.utc)
    assert chart_input.candles[0].timestamp == int(expected_utc.timestamp() * 1000)
    assert chart_input.candles[0].close == 71200.0
    assert chart_input.timeframe == "5m"


def test_to_chart_input_sorts_by_bar_time_ascending() -> None:
    bars = [
        (datetime(2026, 7, 8, 9, 10, 0), 100, 100, 100, 100, 1),
        (datetime(2026, 7, 8, 9, 5, 0), 100, 100, 100, 100, 1),
    ]

    chart_input = to_chart_input(bars, symbol="005930", interval_seconds=300)

    timestamps = [c.timestamp for c in chart_input.candles]
    assert timestamps == sorted(timestamps)


def test_kiwoom_interval_to_timeframe_maps_known_intervals() -> None:
    assert kiwoom_interval_to_timeframe(300) == "5m"
    assert kiwoom_interval_to_timeframe(86400) == "1D"


def test_kiwoom_interval_to_timeframe_raises_on_unknown_interval() -> None:
    with pytest.raises(ValueError, match="알 수 없는 주단 interval_seconds"):
        kiwoom_interval_to_timeframe(123)
