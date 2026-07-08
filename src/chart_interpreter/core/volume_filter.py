from chart_interpreter.schema import Candle

DEFAULT_VOLUME_WINDOW = 20


def average_volume(candles: list[Candle], window: int = DEFAULT_VOLUME_WINDOW) -> float:
    """직전 확정 window개 봉의 평균 거래량. candles[-1]은 진행 중일 수 있는 현재 봉이므로
    (schema.py 불변식) 평균 계산에서 제외한다 — range_box.box_bounds와 동일한 원칙.
    비교할 확정 봉이 하나도 없으면 0.0을 반환한다.
    """
    confirmed = candles[:-1]
    window_candles = confirmed[-window:]
    if not window_candles:
        return 0.0
    return sum(c.volume for c in window_candles) / len(window_candles)


def volume_ratio(candles: list[Candle], window: int = DEFAULT_VOLUME_WINDOW) -> float:
    """최근 거래량(candles[-1], 진행 중일 수 있음) / 직전 확정 window개 평균 거래량.
    평균이 0이면(거래정지 등으로 비교 불가) 중립값 0.0을 반환한다.
    """
    avg = average_volume(candles, window)
    if avg == 0:
        return 0.0
    return candles[-1].volume / avg
