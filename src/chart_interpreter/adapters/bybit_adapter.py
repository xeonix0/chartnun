from chart_interpreter.schema import Candle, ChartInput

# 코단/비단 공용 bybit.py get_kline()의 반환 컬럼(timestamp, open, high, low, close, volume,
# turnover) 중 turnover를 제외한 한 행. 라이브러리가 pandas.DataFrame에 의존하지 않도록
# (adapter 함수 시그니처 원칙, docs/MASTER.md) 원시 튜플로만 받는다.
BybitKlineRow = tuple[int, float, float, float, float, float]

# Bybit kline interval 원본 문자열 → schema.VALID_TIMEFRAMES 정규화 표기.
BYBIT_INTERVAL_TO_TIMEFRAME = {
    "1": "1m",
    "3": "3m",
    "5": "5m",
    "15": "15m",
    "30": "30m",
    "60": "1H",
    "120": "2H",
    "240": "4H",
    "360": "6H",
    "720": "12H",
    "D": "1D",
    "W": "1W",
    "M": "1M",
}


def bybit_interval_to_timeframe(interval: str) -> str:
    timeframe = BYBIT_INTERVAL_TO_TIMEFRAME.get(interval)
    if timeframe is None:
        raise ValueError(f"알 수 없는 Bybit interval: {interval!r}")
    return timeframe


def to_chart_input(rows: list[BybitKlineRow], symbol: str, interval: str) -> ChartInput:
    """코단/비단 bybit.py get_kline()의 DataFrame을 튜플 리스트로 변환한 rows를 받는다.
    예: `list(zip(df["timestamp"], df["open"], df["high"], df["low"], df["close"], df["volume"]))`.
    get_kline()이 이미 시간 오름차순 정렬을 보장하지만, schema.py의 ChartInput.candles 불변식
    (오름차순 정렬)을 라이브러리 경계에서도 명시적으로 보장하기 위해 여기서 다시 정렬한다.
    """
    candles = [
        Candle(
            timestamp=int(timestamp),
            open=float(open_),
            high=float(high),
            low=float(low),
            close=float(close),
            volume=float(volume),
        )
        for timestamp, open_, high, low, close, volume in rows
    ]
    candles.sort(key=lambda c: c.timestamp)
    timeframe = bybit_interval_to_timeframe(interval)
    return ChartInput(symbol=symbol, timeframe=timeframe, candles=candles)
