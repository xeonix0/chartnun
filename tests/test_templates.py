from chart_interpreter.summarizer.templates import (
    ma_position_sentence,
    support_resistance_sentence,
    trend_sentence,
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
