from chart_interpreter.schema import Candle

DEFAULT_MA_PERIOD = 20
NEAR_MA_THRESHOLD_PCT = 0.5


def calculate_ema(candles: list[Candle], period: int = DEFAULT_MA_PERIOD) -> list[float]:
    if len(candles) < period:
        return []

    closes = [c.close for c in candles]
    multiplier = 2 / (period + 1)
    ema_values = [sum(closes[:period]) / period]
    for close in closes[period:]:
        ema_values.append((close - ema_values[-1]) * multiplier + ema_values[-1])
    return ema_values


def latest_ema(candles: list[Candle], period: int = DEFAULT_MA_PERIOD) -> float | None:
    ema_values = calculate_ema(candles, period)
    return ema_values[-1] if ema_values else None


def ma_position(
    candles: list[Candle], period: int = DEFAULT_MA_PERIOD
) -> tuple[str, float]:
    ema = latest_ema(candles, period)
    if ema is None or not candles:
        return "판단불가", 0.0

    current_price = candles[-1].close
    distance_pct = (current_price - ema) / ema * 100

    if abs(distance_pct) <= NEAR_MA_THRESHOLD_PCT:
        return "이평선 근접", distance_pct
    if distance_pct > 0:
        return "이평선 위 눌림", distance_pct
    return "이평선 아래", distance_pct
