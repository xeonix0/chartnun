from datetime import datetime, timedelta, timezone

from chart_interpreter.schema import Candle, ChartInput

KST = timezone(timedelta(hours=9))

# 주단 BarAggregator.feed()/flush()가 반환하는 Bar(ticker, bar_time, open, high, low, close,
# volume)를 튜플로 변환한 한 행. 라이브러리가 주단의 구체 타입 app.core.bar_aggregator.Bar에
# 의존하지 않도록(adapter 함수 시그니처 원칙, docs/MASTER.md) 원시 튜플로만 받는다.
# bar_time은 naive datetime(KST 벽시계, tzinfo 없음)이라고 가정한다.
KiwoomBarRow = tuple[datetime, int, int, int, int, int]

# 주단 interval_seconds(정수) → schema.VALID_TIMEFRAMES 정규화 표기.
KIWOOM_INTERVAL_SECONDS_TO_TIMEFRAME = {
    60: "1m",
    180: "3m",
    300: "5m",
    900: "15m",
    1800: "30m",
    3600: "1H",
    14400: "4H",
    86400: "1D",
}


def kiwoom_interval_to_timeframe(interval_seconds: int) -> str:
    timeframe = KIWOOM_INTERVAL_SECONDS_TO_TIMEFRAME.get(interval_seconds)
    if timeframe is None:
        raise ValueError(f"알 수 없는 주단 interval_seconds: {interval_seconds!r}")
    return timeframe


def _to_epoch_ms_utc(bar_time: datetime) -> int:
    """주단 bar_time은 naive datetime(KST 벽시계)이므로, KST tzinfo를 붙인 뒤
    UTC epoch 밀리초로 변환한다(schema.py의 Candle.timestamp 불변식).
    """
    aware = bar_time.replace(tzinfo=KST)
    return int(aware.timestamp() * 1000)


def to_chart_input(
    bars: list[KiwoomBarRow], symbol: str, interval_seconds: int
) -> ChartInput:
    """주단 Bar 시퀀스를 튜플 리스트로 변환한 bars를 받는다.
    예: `[(bar.bar_time, bar.open, bar.high, bar.low, bar.close, bar.volume) for bar in bars]`.
    BarAggregator.feed()는 시간 오름차순으로 봉을 완성시키지만, schema.py의 ChartInput.candles
    불변식(오름차순 정렬)을 라이브러리 경계에서도 명시적으로 보장하기 위해 여기서 다시 정렬한다.
    """
    candles = [
        Candle(
            timestamp=_to_epoch_ms_utc(bar_time),
            open=float(open_),
            high=float(high),
            low=float(low),
            close=float(close),
            volume=float(volume),
        )
        for bar_time, open_, high, low, close, volume in bars
    ]
    candles.sort(key=lambda c: c.timestamp)
    timeframe = kiwoom_interval_to_timeframe(interval_seconds)
    return ChartInput(symbol=symbol, timeframe=timeframe, candles=candles)
