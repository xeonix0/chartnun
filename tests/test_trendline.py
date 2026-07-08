from chart_interpreter.core.trendline import (
    downtrend_line,
    trendline_for_direction,
    uptrend_line,
)
from chart_interpreter.schema import Candle

UPTREND_ZIGZAG = [
    100, 105, 110, 104, 98, 90, 95, 100, 120, 110, 100,
    95, 105, 115, 140, 130, 120, 115, 120, 125, 130,
]


def make_candles(prices: list[float]) -> list[Candle]:
    return [
        Candle(timestamp=i, open=p, high=p, low=p, close=p, volume=100.0)
        for i, p in enumerate(prices)
    ]


def test_uptrend_line_connects_last_two_pivot_lows() -> None:
    candles = make_candles([float(p) for p in UPTREND_ZIGZAG])

    line = uptrend_line(candles, left_bars=2, right_bars=2)

    assert line is not None
    (i1, p1), (i2, p2) = line
    assert i1 < i2
    assert p2 > p1


def test_uptrend_line_none_when_fewer_than_two_pivot_lows() -> None:
    candles = make_candles([100.0, 101.0, 100.0, 99.0, 100.0])

    assert uptrend_line(candles, left_bars=2, right_bars=2) is None


def test_downtrend_line_connects_last_two_pivot_highs() -> None:
    candles = make_candles([float(p) for p in reversed(UPTREND_ZIGZAG)])

    line = downtrend_line(candles, left_bars=2, right_bars=2)

    assert line is not None
    (i1, p1), (i2, p2) = line
    assert i1 < i2
    assert p2 < p1


def test_downtrend_line_none_when_fewer_than_two_pivot_highs() -> None:
    candles = make_candles([100.0, 101.0, 100.0, 99.0, 100.0])

    assert downtrend_line(candles, left_bars=2, right_bars=2) is None


def test_trendline_for_direction_picks_matching_line() -> None:
    up_candles = make_candles([float(p) for p in UPTREND_ZIGZAG])
    down_candles = make_candles([float(p) for p in reversed(UPTREND_ZIGZAG)])

    assert trendline_for_direction(up_candles, "상승", left_bars=2, right_bars=2) == uptrend_line(
        up_candles, left_bars=2, right_bars=2
    )
    assert trendline_for_direction(
        down_candles, "하락", left_bars=2, right_bars=2
    ) == downtrend_line(down_candles, left_bars=2, right_bars=2)


def test_trendline_for_direction_none_for_sideways() -> None:
    candles = make_candles([float(p) for p in UPTREND_ZIGZAG])

    assert trendline_for_direction(candles, "횡보", left_bars=2, right_bars=2) is None
