from chart_interpreter.core.pivot import (
    DEFAULT_LEFT_BARS,
    DEFAULT_RIGHT_BARS,
    find_pivot_highs,
    find_pivot_lows,
)
from chart_interpreter.schema import Candle

TrendlinePoint = tuple[int, float]
Trendline = tuple[TrendlinePoint, TrendlinePoint]


def uptrend_line(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> Trendline | None:
    """직전 두 확정 저점을 연결한 상승 추세선의 두 끝점((index, price) 쌍)을 반환한다.
    확정 저점이 2개 미만이면 추세선을 그릴 수 없으므로 None."""
    lows = find_pivot_lows(candles, left_bars, right_bars)
    if len(lows) < 2:
        return None
    return lows[-2], lows[-1]


def downtrend_line(
    candles: list[Candle],
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> Trendline | None:
    """직전 두 확정 고점을 연결한 하락 추세선의 두 끝점((index, price) 쌍)을 반환한다.
    확정 고점이 2개 미만이면 추세선을 그릴 수 없으므로 None."""
    highs = find_pivot_highs(candles, left_bars, right_bars)
    if len(highs) < 2:
        return None
    return highs[-2], highs[-1]


def trendline_for_direction(
    candles: list[Candle],
    trend_direction: str,
    left_bars: int = DEFAULT_LEFT_BARS,
    right_bars: int = DEFAULT_RIGHT_BARS,
) -> Trendline | None:
    """determine_trend_direction()이 반환하는 값("상승"/"하락"/"횡보")에 맞는 추세선을 고른다.
    상승이면 저점끼리, 하락이면 고점끼리 연결 — 횡보이거나 해당 pivot이 부족하면 None."""
    if trend_direction == "상승":
        return uptrend_line(candles, left_bars, right_bars)
    if trend_direction == "하락":
        return downtrend_line(candles, left_bars, right_bars)
    return None
