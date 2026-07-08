from importlib import resources
from string import Template

# 스펙 §10-2: core 모듈(pivot/trendline/range_box)의 분석 로직을 Pine Script v6 문법으로
# 번역한 템플릿. 파라미터 키는 각 core 모듈의 실제 함수 시그니처와 동일하게 맞춘다
# (leftBars/rightBars → pivot.py·trendline.py, window/lookback/compressionThresholdPct →
# range_box.py, period/nearThresholdPct → ma_relation.py) — Python 로직과 다른 파라미터
# 이름을 쓰면 "이미 검증된 로직과 동일한 파라미터"라는 스펙 의도가 깨진다.
VALID_STRATEGIES = frozenset({"pullback", "range_box", "trendline"})


def export_pine_script(strategy: str, params: dict[str, int | float]) -> str:
    """strategy에 대응하는 .pine 템플릿에 params를 주입해 Pine Script v6 소스 코드
    문자열을 반환한다. 템플릿이 요구하는 파라미터가 params에 없으면 조용히 넘어가지
    않고 ValueError로 실패한다(adapter 함수들과 동일한 명시적 실패 원칙).
    """
    if strategy not in VALID_STRATEGIES:
        raise ValueError(
            f"알 수 없는 strategy입니다: {strategy!r} (지원: {sorted(VALID_STRATEGIES)})"
        )

    template_text = (
        resources.files("chart_interpreter.pinescript_export")
        .joinpath("templates", f"{strategy}.pine")
        .read_text(encoding="utf-8")
    )
    try:
        return Template(template_text).substitute(**params)
    except KeyError as exc:
        raise ValueError(
            f"{strategy} 템플릿에 필요한 파라미터가 누락되었습니다: {exc}"
        ) from exc
