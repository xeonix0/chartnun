from chart_interpreter.summarizer.templates import (
    candle_pattern_sentence,
    final_summary_sentence,
    ma_position_sentence,
    support_resistance_sentence,
    trend_sentence,
    volume_sentence,
)


def test_ma_position_sentence_includes_direction_and_number() -> None:
    sentence = ma_position_sentence("이평선 위 눌림", 1.34)

    assert "1.34" in sentence
    assert "위" in sentence
    assert "이평선 위 눌림" in sentence


def test_ma_position_sentence_below_uses_negative_distance() -> None:
    sentence = ma_position_sentence("이평선 아래", -2.5)

    assert "2.50" in sentence
    assert "아래" in sentence


def test_support_resistance_sentence_includes_all_numbers() -> None:
    sentence = support_resistance_sentence(74500.0, 3.9, 69800.0, -2.1)

    assert "74,500" in sentence
    assert "+3.90%" in sentence
    assert "69,800" in sentence
    assert "-2.10%" in sentence


def test_trend_sentence_with_pivots_includes_numbers() -> None:
    sentence = trend_sentence("상승", 242.0, 207.0)

    assert "242" in sentence
    assert "207" in sentence
    assert "상승" in sentence


def test_trend_sentence_without_pivots_states_undetected_explicitly() -> None:
    sentence = trend_sentence("횡보", None, None)

    assert "탐지되지 않았습니다" in sentence
    assert "횡보" in sentence


def test_volume_sentence_high_ratio_says_above_average() -> None:
    sentence = volume_sentence(1.9)

    assert "1.90" in sentence
    assert "많은 편" in sentence


def test_volume_sentence_low_ratio_says_below_average() -> None:
    sentence = volume_sentence(0.8)

    assert "0.80" in sentence
    assert "적은 편" in sentence


def test_candle_pattern_sentence_with_pattern_names_it() -> None:
    sentence = candle_pattern_sentence("상승장악형")

    assert "상승장악형" in sentence


def test_candle_pattern_sentence_none_states_no_pattern_explicitly() -> None:
    sentence = candle_pattern_sentence(None)

    assert "감지되지 않았습니다" in sentence


def test_final_summary_sentence_pattern_with_high_volume_takes_priority() -> None:
    sentence = final_summary_sentence(
        trend_direction="상승",
        ma_position="이평선 위 눌림",
        range_state="박스권 아님",
        volume_ratio=1.9,
        candle_pattern="상승장악형",
    )

    assert "상승장악형" in sentence
    assert "거래량 동반" in sentence


def test_final_summary_sentence_uptrend_pullback_low_volume() -> None:
    sentence = final_summary_sentence(
        trend_direction="상승",
        ma_position="이평선 위 눌림",
        range_state="박스권 아님",
        volume_ratio=0.8,
        candle_pattern=None,
    )

    assert "눌림" in sentence
    assert "관망" in sentence


def test_final_summary_sentence_range_breakout() -> None:
    sentence = final_summary_sentence(
        trend_direction="횡보",
        ma_position="이평선 근접",
        range_state="박스권 이탈",
        volume_ratio=1.4,
        candle_pattern=None,
    )

    assert "박스권 이탈" in sentence
