from chart_interpreter.core import ma_relation, pivot
from chart_interpreter.errors import MIN_CANDLES_REQUIRED, InsufficientCandlesError
from chart_interpreter.schema import ChartInput
from chart_interpreter.summarizer import templates


def build_partial_summary(chart_input: ChartInput) -> str:
    """pivot.py + ma_relation.py 결과만으로 만드는 1차 요약(§8 우선순위 2).

    volume_filter.py/candle_pattern.py/range_box.py가 아직 없어 스펙 5장의 5문장
    완전판이 아니다. ChartAnalysis 전체 조립과 analyze_and_summarize()는 그 모듈들이
    갖춰진 뒤(§8 우선순위 4 완료 시)로 미룬다 — 지금 만들면 volume_ratio/candle_pattern/
    range_state를 가짜 값으로 채우게 된다.
    """
    if len(chart_input.candles) < MIN_CANDLES_REQUIRED:
        raise InsufficientCandlesError(
            chart_input.symbol, chart_input.timeframe, len(chart_input.candles)
        )

    candles = chart_input.candles
    current_price = candles[-1].close

    trend_direction = pivot.determine_trend_direction(candles)
    pivot_high = pivot.most_recent_pivot_high(candles)
    pivot_low = pivot.most_recent_pivot_low(candles)
    ma_label, ma_distance_pct = ma_relation.ma_position(candles)

    lines = [
        f"[{chart_input.symbol}, {chart_input.timeframe}]",
        templates.ma_position_sentence(ma_label, ma_distance_pct),
    ]
    if pivot_high is not None and pivot_low is not None:
        lines.append(
            templates.support_resistance_sentence(
                pivot_high,
                pivot.price_distance_pct(current_price, pivot_high),
                pivot_low,
                pivot.price_distance_pct(current_price, pivot_low),
            )
        )
    lines.append(templates.trend_sentence(trend_direction, pivot_high, pivot_low))
    return "\n".join(lines)
