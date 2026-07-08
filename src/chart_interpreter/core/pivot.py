from chart_interpreter.schema import Candle

DEFAULT_LEFT_BARS = 5
DEFAULT_RIGHT_BARS = 5


def find_pivot_highs(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> list[tuple[int, float]]:
    pivots: list[tuple[int, float]] = []
    n = len(candles)
    for i in range(left_bars, n - right_bars):
        window = candles[i - left_bars : i + right_bars + 1]
        window_highs = [c.high for c in window]
        max_high = max(window_highs)
        if candles[i].high == max_high and window_highs.count(max_high) == 1:
            pivots.append((i, candles[i].high))
    return pivots


def find_pivot_lows(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> list[tuple[int, float]]:
    pivots: list[tuple[int, float]] = []
    n = len(candles)
    for i in range(left_bars, n - right_bars):
        window = candles[i - left_bars : i + right_bars + 1]
        window_lows = [c.low for c in window]
        min_low = min(window_lows)
        if candles[i].low == min_low and window_lows.count(min_low) == 1:
            pivots.append((i, candles[i].low))
    return pivots


def most_recent_pivot_high(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> float | None:
    pivots = find_pivot_highs(candles, left_bars, right_bars)
    return pivots[-1][1] if pivots else None


def most_recent_pivot_low(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> float | None:
    pivots = find_pivot_lows(candles, left_bars, right_bars)
    return pivots[-1][1] if pivots else None


def price_distance_pct(current_price: float, target_price: float) -> float:
    return (target_price - current_price) / current_price * 100


def determine_trend_direction(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> str:
    highs = find_pivot_highs(candles, left_bars, right_bars)
    lows = find_pivot_lows(candles, left_bars, right_bars)
    if len(highs) < 2 or len(lows) < 2:
        return "횡보"

    higher_high = highs[-1][1] > highs[-2][1]
    higher_low = lows[-1][1] > lows[-2][1]
    lower_high = highs[-1][1] < highs[-2][1]
    lower_low = lows[-1][1] < lows[-2][1]

    if higher_high and higher_low:
        return "상승"
    if lower_high and lower_low:
        return "하락"
    return "횡보"
