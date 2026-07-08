from chart_interpreter.core.pivot import (
    determine_trend_direction,
    find_pivot_highs,
    find_pivot_lows,
    most_recent_pivot_high,
    most_recent_pivot_low,
    price_distance_pct,
)
from chart_interpreter.schema import Candle


def make_candles(prices: list[float]) -> list[Candle]:
    return [
        Candle(timestamp=i, open=p, high=p, low=p, close=p, volume=100.0)
        for i, p in enumerate(prices)
    ]


def test_find_pivot_highs_detects_local_maxima() -> None:
    prices = [10, 11, 12, 20, 12, 11, 10, 11, 12, 20, 12, 11, 10]
    candles = make_candles([float(p) for p in prices])

    pivots = find_pivot_highs(candles, left_bars=2, right_bars=2)

    assert pivots == [(3, 20.0), (9, 20.0)]


def test_find_pivot_lows_detects_local_minima() -> None:
    prices = [20, 19, 18, 10, 18, 19, 20, 19, 18, 10, 18, 19, 20]
    candles = make_candles([float(p) for p in prices])

    pivots = find_pivot_lows(candles, left_bars=2, right_bars=2)

    assert pivots == [(3, 10.0), (9, 10.0)]


def test_most_recent_pivot_high_and_low_return_last_value() -> None:
    prices = [10, 11, 12, 20, 12, 11, 10, 11, 12, 20, 12, 11, 10]
    candles = make_candles([float(p) for p in prices])

    assert most_recent_pivot_high(candles, left_bars=2, right_bars=2) == 20.0

    low_prices = [20, 19, 18, 10, 18, 19, 20, 19, 18, 10, 18, 19, 20]
    low_candles = make_candles([float(p) for p in low_prices])
    assert most_recent_pivot_low(low_candles, left_bars=2, right_bars=2) == 10.0


def test_most_recent_pivot_returns_none_when_no_pivots_found() -> None:
    candles = make_candles([100.0, 100.0, 100.0])

    assert most_recent_pivot_high(candles, left_bars=2, right_bars=2) is None
    assert most_recent_pivot_low(candles, left_bars=2, right_bars=2) is None


def test_price_distance_pct_sign_matches_direction() -> None:
    assert round(price_distance_pct(current_price=100.0, target_price=103.9), 4) == 3.9
    assert round(price_distance_pct(current_price=100.0, target_price=97.9), 4) == -2.1


UPTREND_ZIGZAG = [
    100, 105, 110, 104, 98, 90, 95, 100, 120, 110, 100,
    95, 105, 115, 140, 130, 120, 115, 120, 125, 130,
]


def test_determine_trend_direction_up_for_higher_highs_and_lows() -> None:
    candles = make_candles([float(p) for p in UPTREND_ZIGZAG])

    assert determine_trend_direction(candles, left_bars=2, right_bars=2) == "상승"


def test_determine_trend_direction_down_for_lower_highs_and_lows() -> None:
    candles = make_candles([float(p) for p in reversed(UPTREND_ZIGZAG)])

    assert determine_trend_direction(candles, left_bars=2, right_bars=2) == "하락"


def test_determine_trend_direction_sideways_when_not_enough_pivots() -> None:
    candles = make_candles([100.0, 101.0, 100.0, 99.0, 100.0])

    assert determine_trend_direction(candles, left_bars=2, right_bars=2) == "횡보"
