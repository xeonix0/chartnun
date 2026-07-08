from chart_interpreter.schema import Candle

DEFAULT_BOX_WINDOW = 20
DEFAULT_LOOKBACK = 60
COMPRESSION_THRESHOLD_PCT = 70.0


def box_bounds(candles: list[Candle], window: int = DEFAULT_BOX_WINDOW) -> tuple[float, float]:
    """박스 상단/하단. candles[-1]은 진행 중일 수 있는 현재 봉이므로(schema.py의
    ChartInput.candles 불변식) 박스 정의에서 제외하고, 그 직전 확정 window개 봉만으로
    박스 경계를 그린다. 현재가는 이 박스 경계를 기준으로 이탈 여부를 판정한다.
    """
    confirmed = candles[:-1]
    box_candles = confirmed[-window:]
    box_high = max(c.high for c in box_candles)
    box_low = min(c.low for c in box_candles)
    return box_high, box_low


def range_compression_pct(
    candles: list[Candle],
    window: int = DEFAULT_BOX_WINDOW,
    lookback: int = DEFAULT_LOOKBACK,
) -> float:
    """최근 박스(직전 확정 window개 봉)의 고가-저가 변동폭이, 그 이전 lookback개 확정 봉
    구간에서 굴려본 같은 크기 박스들의 평균 변동폭 대비 몇 %인지. 값이 작을수록 변동성이
    압축된 상태. 비교할 과거 구간이 window개 미만이면(데이터 부족) 압축 여부를 판단할
    근거가 없으므로 압축 아님(100.0)으로 처리한다.
    """
    confirmed = candles[:-1]
    box_high, box_low = box_bounds(candles, window)
    recent_range = box_high - box_low

    baseline = confirmed[-lookback:]
    window_ranges = [
        max(c.high for c in baseline[i : i + window]) - min(c.low for c in baseline[i : i + window])
        for i in range(len(baseline) - window + 1)
    ]
    if not window_ranges:
        return 100.0

    avg_range = sum(window_ranges) / len(window_ranges)
    if avg_range == 0:
        return 0.0
    return recent_range / avg_range * 100


def determine_range_state(
    candles: list[Candle],
    window: int = DEFAULT_BOX_WINDOW,
    lookback: int = DEFAULT_LOOKBACK,
) -> str:
    box_high, box_low = box_bounds(candles, window)
    current_price = candles[-1].close

    if current_price > box_high or current_price < box_low:
        return "박스권 이탈"

    if range_compression_pct(candles, window, lookback) <= COMPRESSION_THRESHOLD_PCT:
        return "박스권 압축중"
    return "박스권 아님"
