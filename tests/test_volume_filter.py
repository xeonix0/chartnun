from chart_interpreter.core.volume_filter import average_volume, volume_ratio
from chart_interpreter.schema import Candle


def make_candles(volumes: list[float]) -> list[Candle]:
    return [
        Candle(timestamp=i, open=100.0, high=100.0, low=100.0, close=100.0, volume=v)
        for i, v in enumerate(volumes)
    ]


def test_average_volume_excludes_last_unconfirmed_candle() -> None:
    volumes = [100.0] * 20 + [9999.0]  # 마지막 봉은 진행 중 — 평균에서 제외되어야 함
    candles = make_candles(volumes)

    assert average_volume(candles, window=20) == 100.0


def test_average_volume_zero_when_no_confirmed_candles() -> None:
    candles = make_candles([100.0])

    assert average_volume(candles, window=20) == 0.0


def test_volume_ratio_uses_last_candle_over_confirmed_average() -> None:
    volumes = [100.0] * 20 + [150.0]
    candles = make_candles(volumes)

    assert volume_ratio(candles, window=20) == 1.5


def test_volume_ratio_neutral_when_average_is_zero() -> None:
    candles = make_candles([0.0] * 20 + [150.0])

    assert volume_ratio(candles, window=20) == 0.0
