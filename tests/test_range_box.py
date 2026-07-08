from chart_interpreter.core.range_box import (
    box_bounds,
    determine_range_state,
    range_compression_pct,
)
from chart_interpreter.schema import Candle


def make_candles(bars: list[tuple[float, float, float]]) -> list[Candle]:
    """(high, low, close) 튜플 리스트로 캔들 생성. open은 close와 동일하게 채운다."""
    return [
        Candle(timestamp=i, open=c, high=h, low=low, close=c, volume=100.0)
        for i, (h, low, c) in enumerate(bars)
    ]


def test_box_bounds_excludes_last_unconfirmed_candle() -> None:
    bars = [
        (110.0, 90.0, 100.0),  # window 밖(오래된 봉)
        (105.0, 95.0, 100.0),
        (108.0, 92.0, 100.0),
        (106.0, 94.0, 100.0),  # 마지막 확정 봉
        (200.0, 10.0, 100.0),  # 진행 중(미확정) 봉 — 박스 계산에서 제외되어야 함
    ]
    candles = make_candles(bars)

    assert box_bounds(candles, window=3) == (108.0, 92.0)


WIDE_BAR = (120.0, 80.0, 100.0)
NARROW_BAR = (102.0, 98.0, 100.0)


def test_range_compression_pct_low_when_recent_box_narrower_than_baseline() -> None:
    candles = make_candles([WIDE_BAR] * 60 + [NARROW_BAR] * 20 + [NARROW_BAR])

    compression = range_compression_pct(candles, window=20, lookback=60)

    assert compression < 70.0


def test_range_compression_pct_neutral_when_baseline_insufficient() -> None:
    candles = make_candles([WIDE_BAR] * 5 + [WIDE_BAR])

    assert range_compression_pct(candles, window=20, lookback=60) == 100.0


def test_determine_range_state_compressed() -> None:
    candles = make_candles([WIDE_BAR] * 60 + [NARROW_BAR] * 20 + [(100.0, 100.0, 100.0)])

    assert determine_range_state(candles, window=20, lookback=60) == "박스권 압축중"


def test_determine_range_state_breakout_above_box_high() -> None:
    candles = make_candles([WIDE_BAR] * 60 + [NARROW_BAR] * 20 + [(110.0, 110.0, 110.0)])

    assert determine_range_state(candles, window=20, lookback=60) == "박스권 이탈"


def test_determine_range_state_breakout_below_box_low() -> None:
    candles = make_candles([WIDE_BAR] * 60 + [NARROW_BAR] * 20 + [(90.0, 90.0, 90.0)])

    assert determine_range_state(candles, window=20, lookback=60) == "박스권 이탈"


def test_determine_range_state_not_compressed_when_range_matches_baseline() -> None:
    candles = make_candles([WIDE_BAR] * 81)

    assert determine_range_state(candles, window=20, lookback=60) == "박스권 아님"
