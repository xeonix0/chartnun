import pytest

from chart_interpreter.pinescript_export.generate import export_pine_script


def test_export_pine_script_trendline_substitutes_params() -> None:
    code = export_pine_script(strategy="trendline", params={"leftBars": 5, "rightBars": 5})

    assert "//@version=6" in code
    assert "leftBars = input.int(5" in code
    assert "rightBars = input.int(5" in code
    assert "$" not in code


def test_export_pine_script_range_box_substitutes_params() -> None:
    code = export_pine_script(
        strategy="range_box",
        params={"window": 20, "lookback": 60, "compressionThresholdPct": 70.0},
    )

    assert "boxWindow = input.int(20" in code
    assert "lookback = input.int(60" in code
    assert "compressionThresholdPct = input.float(70.0" in code


def test_export_pine_script_pullback_substitutes_params() -> None:
    code = export_pine_script(strategy="pullback", params={"period": 20, "nearThresholdPct": 0.5})

    assert "period = input.int(20" in code
    assert "nearThresholdPct = input.float(0.5" in code


def test_export_pine_script_unknown_strategy_raises() -> None:
    with pytest.raises(ValueError, match="알 수 없는 strategy"):
        export_pine_script(strategy="not_a_strategy", params={})


def test_export_pine_script_missing_param_raises() -> None:
    with pytest.raises(ValueError, match="누락"):
        export_pine_script(strategy="trendline", params={"leftBars": 5})
