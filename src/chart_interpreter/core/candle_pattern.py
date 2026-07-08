from chart_interpreter.schema import Candle


def _is_bullish(candle: Candle) -> bool:
    return candle.close > candle.open


def _is_bearish(candle: Candle) -> bool:
    return candle.close < candle.open


def detect_candle_pattern(candles: list[Candle]) -> str | None:
    """직전 확정 봉(candles[-2])과 그 이전 확정 봉(candles[-3])을 비교해 장악형 패턴을 판정한다.
    candles[-1]은 진행 중일 수 있는 미확정 봉이므로(schema.py의 ChartInput.candles 불변식)
    candles[-2]를 "직전 확정 봉"으로 삼는다 — pivot.py/range_box.py와 동일한 원칙.
    몸통(시가-종가) 기준 장악만 판정하며, 캔들이 3개 미만이면 None을 반환한다.
    """
    if len(candles) < 3:
        return None

    prev, curr = candles[-3], candles[-2]

    if (
        _is_bearish(prev)
        and _is_bullish(curr)
        and curr.open <= prev.close
        and curr.close >= prev.open
    ):
        return "상승장악형"
    if (
        _is_bullish(prev)
        and _is_bearish(curr)
        and curr.open >= prev.close
        and curr.close <= prev.open
    ):
        return "하락장악형"
    return None
