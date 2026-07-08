from dataclasses import dataclass

# 캔들 주기 표기 규약(단일 출처). adapters/*.py는 거래소별 원본 표기(예: Bybit "60"/"D",
# 주단 interval_seconds 정수)를 이 값들로 변환해서 ChartInput.timeframe에 채워야 한다.
VALID_TIMEFRAMES = frozenset(
    {"1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "12H", "1D", "1W", "1M"}
)


@dataclass
class Candle:
    """timestamp는 UTC epoch 밀리초(int)로 통일한다.
    주단(naive datetime, KST 벽시계)·코단/비단(Bybit epoch ms UTC)이 서로 다른 원본 포맷을
    쓰므로, 이 변환은 반드시 adapters/*.py 경계에서 끝내고 core/summarizer는 항상 epoch ms UTC로
    가정한다.
    """

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class ChartInput:
    """candles는 timestamp 오름차순으로 정렬되어 있어야 하며, 최소 1개 이상이어야 한다.
    마지막 캔들(candles[-1])은 아직 마감되지 않은 진행 중 캔들일 수 있다 — 이 라이브러리는
    이를 "현재가"로만 취급하고(예: ma_relation.ma_position의 현재가), pivot 탐지처럼 확정된
    고점/저점이 필요한 계산에서는 절대 마지막 right_bars개 캔들을 pivot으로 반환하지 않는다
    (core/pivot.py의 find_pivot_highs/lows 참고). 새 core 모듈을 추가할 때도 이 불변식을
    깨지 않아야 한다 — 예: candle_pattern.py가 "직전 확정 봉"을 판정할 때는 candles[-1]이
    아니라 진행 중 캔들 여부를 adapter가 명시하기 전까지는 candles[-2]를 기준으로 삼는 것이 안전.
    """

    symbol: str
    timeframe: str
    candles: list[Candle]


@dataclass
class ChartAnalysis:
    symbol: str
    timeframe: str
    trend_direction: str
    ma_position: str
    ma_distance_pct: float
    resistance_price: float
    resistance_distance_pct: float
    support_price: float
    support_distance_pct: float
    range_state: str
    volume_ratio: float
    candle_pattern: str | None
    pivot_high_recent: float
    pivot_low_recent: float
