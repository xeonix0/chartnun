from chart_interpreter.core import candle_pattern, ma_relation, pivot, range_box, volume_filter
from chart_interpreter.errors import MIN_CANDLES_REQUIRED, InsufficientCandlesError
from chart_interpreter.schema import ChartAnalysis, ChartInput
from chart_interpreter.summarizer import templates


def analyze_and_summarize(chart_input: ChartInput) -> tuple[ChartAnalysis, str]:
    """스펙 §7의 연동 진입점. pivot/ma_relation/range_box/volume_filter/candle_pattern
    5개 core 모듈 결과를 ChartAnalysis로 조립하고, 스펙 5장 5문장(추세/위치/거래량/패턴/종합)
    형식의 자연어 요약을 함께 반환한다.

    캔들이 MIN_CANDLES_REQUIRED(60)개 미만이면 InsufficientCandlesError를 raise한다.
    resistance/support pivot이 하나도 탐지되지 않으면(완전 평탄 구간 등) 현재가를 기준선으로
    쓰고 거리는 0.0으로 채운다 — schema.py의 ChartAnalysis 필드가 float(Optional 아님)라서
    필요한 폴백. MIN_CANDLES_REQUIRED(60)가 ma_relation.DEFAULT_MA_PERIOD(20)보다 크므로
    이 진입점에서는 ma_position()의 "판단불가" 폴백 자체가 발생하지 않는다(docs/MASTER.md
    "알려진 단순화" 항목 해소).
    """
    if len(chart_input.candles) < MIN_CANDLES_REQUIRED:
        raise InsufficientCandlesError(
            chart_input.symbol, chart_input.timeframe, len(chart_input.candles)
        )

    candles = chart_input.candles
    current_price = candles[-1].close

    trend_direction = pivot.determine_trend_direction(candles)
    ma_label, ma_distance_pct = ma_relation.ma_position(candles)

    pivot_high = pivot.most_recent_pivot_high(candles)
    pivot_low = pivot.most_recent_pivot_low(candles)
    resistance_price = pivot_high if pivot_high is not None else current_price
    support_price = pivot_low if pivot_low is not None else current_price
    resistance_distance_pct = (
        pivot.price_distance_pct(current_price, pivot_high) if pivot_high is not None else 0.0
    )
    support_distance_pct = (
        pivot.price_distance_pct(current_price, pivot_low) if pivot_low is not None else 0.0
    )

    range_state = range_box.determine_range_state(candles)
    ratio = volume_filter.volume_ratio(candles)
    pattern = candle_pattern.detect_candle_pattern(candles)

    analysis = ChartAnalysis(
        symbol=chart_input.symbol,
        timeframe=chart_input.timeframe,
        trend_direction=trend_direction,
        ma_position=ma_label,
        ma_distance_pct=ma_distance_pct,
        resistance_price=resistance_price,
        resistance_distance_pct=resistance_distance_pct,
        support_price=support_price,
        support_distance_pct=support_distance_pct,
        range_state=range_state,
        volume_ratio=ratio,
        candle_pattern=pattern,
        pivot_high_recent=resistance_price,
        pivot_low_recent=support_price,
    )

    lines = [
        f"[{chart_input.symbol}, {chart_input.timeframe}]",
        templates.trend_sentence(trend_direction, pivot_high, pivot_low),
        templates.ma_position_sentence(ma_label, ma_distance_pct),
        templates.support_resistance_sentence(
            resistance_price, resistance_distance_pct, support_price, support_distance_pct
        ),
        templates.volume_sentence(ratio),
        templates.candle_pattern_sentence(pattern),
        templates.final_summary_sentence(trend_direction, ma_label, range_state, ratio, pattern),
    ]
    return analysis, "\n".join(lines)
