from chart_interpreter.core.candle_pattern import detect_candle_pattern
from chart_interpreter.schema import Candle


def make_candles(bars: list[tuple[float, float]]) -> list[Candle]:
    """(open, close) 튜플 리스트로 캔들 생성. high/low는 open/close 범위를 넉넉히 감싼다."""
    return [
        Candle(
            timestamp=i,
            open=o,
            high=max(o, c) + 1.0,
            low=min(o, c) - 1.0,
            close=c,
            volume=100.0,
        )
        for i, (o, c) in enumerate(bars)
    ]


def test_detect_candle_pattern_bullish_engulfing_uses_last_two_confirmed_candles() -> None:
    bars = [
        (110.0, 100.0),  # 직전 확정 이전 봉(bearish) — candles[-3]
        (95.0, 115.0),  # 직전 확정 봉(bullish, 위 봉 몸통을 감쌈) — candles[-2]
        (200.0, 1.0),  # 진행 중(미확정) 봉 — 판정에서 제외되어야 함
    ]
    candles = make_candles(bars)

    assert detect_candle_pattern(candles) == "상승장악형"


def test_detect_candle_pattern_bearish_engulfing() -> None:
    bars = [
        (100.0, 110.0),  # bullish — candles[-3]
        (115.0, 95.0),  # bearish, 위 봉 몸통을 감쌈 — candles[-2]
        (1.0, 200.0),  # 진행 중 봉 — 판정에서 제외
    ]
    candles = make_candles(bars)

    assert detect_candle_pattern(candles) == "하락장악형"


def test_detect_candle_pattern_none_when_no_engulfing() -> None:
    bars = [
        (100.0, 105.0),
        (106.0, 110.0),
        (111.0, 115.0),
    ]
    candles = make_candles(bars)

    assert detect_candle_pattern(candles) is None


def test_detect_candle_pattern_none_when_not_enough_candles() -> None:
    candles = make_candles([(100.0, 105.0), (106.0, 110.0)])

    assert detect_candle_pattern(candles) is None
