from chart_interpreter.core.ma_relation import calculate_ema, ma_position
from chart_interpreter.schema import Candle


def make_candles(closes: list[float]) -> list[Candle]:
    return [
        Candle(timestamp=i, open=c, high=c, low=c, close=c, volume=100.0)
        for i, c in enumerate(closes)
    ]


def test_calculate_ema_returns_empty_when_not_enough_candles() -> None:
    candles = make_candles([10.0, 11.0, 12.0])

    assert calculate_ema(candles, period=5) == []


def test_calculate_ema_seeds_with_sma_then_applies_smoothing() -> None:
    closes = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0]
    candles = make_candles(closes)

    ema_values = calculate_ema(candles, period=5)

    assert len(ema_values) == len(closes) - 5 + 1
    assert ema_values[0] == 12.0
    assert round(ema_values[1], 4) == 13.0
    assert round(ema_values[2], 4) == 14.0


def test_ma_position_above_ma_beyond_threshold() -> None:
    closes = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 20.0]
    candles = make_candles(closes)

    label, distance_pct = ma_position(candles, period=5)

    assert label == "이평선 위 눌림"
    assert distance_pct > 0.5


def test_ma_position_below_ma_beyond_threshold() -> None:
    closes = [20.0, 19.0, 18.0, 17.0, 16.0, 15.0, 10.0]
    candles = make_candles(closes)

    label, distance_pct = ma_position(candles, period=5)

    assert label == "이평선 아래"
    assert distance_pct < -0.5


def test_ma_position_near_ma_within_threshold() -> None:
    closes = [10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.02]
    candles = make_candles(closes)

    label, distance_pct = ma_position(candles, period=5)

    assert label == "이평선 근접"
    assert abs(distance_pct) <= 0.5


def test_ma_position_returns_undecidable_when_not_enough_candles() -> None:
    candles = make_candles([10.0, 11.0, 12.0])

    label, distance_pct = ma_position(candles, period=5)

    assert label == "판단불가"
    assert distance_pct == 0.0
