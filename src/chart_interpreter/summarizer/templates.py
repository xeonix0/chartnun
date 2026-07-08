def ma_position_sentence(ma_position: str, ma_distance_pct: float) -> str:
    direction = "위" if ma_distance_pct >= 0 else "아래"
    return (
        f"현재가는 이평선 대비 {abs(ma_distance_pct):.2f}% {direction}에서 "
        f"{ma_position} 상태입니다."
    )


def support_resistance_sentence(
    resistance_price: float,
    resistance_distance_pct: float,
    support_price: float,
    support_distance_pct: float,
) -> str:
    return (
        f"저항선({resistance_price:,})까지 {resistance_distance_pct:+.2f}%, "
        f"지지선({support_price:,})까지 {support_distance_pct:+.2f}% 남았습니다."
    )


def trend_sentence(
    trend_direction: str, pivot_high: float | None, pivot_low: float | None
) -> str:
    if pivot_high is None or pivot_low is None:
        return f"추세는 {trend_direction}이며, 확정 고점/저점은 아직 탐지되지 않았습니다."
    return (
        f"최근 확정 고점은 {pivot_high:,}, 확정 저점은 {pivot_low:,}이며 "
        f"추세는 {trend_direction}입니다."
    )


VOLUME_HIGH_THRESHOLD = 1.2
VOLUME_LOW_THRESHOLD = 0.8


def volume_sentence(volume_ratio: float) -> str:
    if volume_ratio >= VOLUME_HIGH_THRESHOLD:
        qualifier = "평소보다 많은 편"
    elif volume_ratio <= VOLUME_LOW_THRESHOLD:
        qualifier = "평소보다 적은 편"
    else:
        qualifier = "평소와 비슷한 수준"
    return f"최근 거래량은 20봉 평균 대비 {volume_ratio:.2f}배로 {qualifier}입니다."


def candle_pattern_sentence(pattern: str | None) -> str:
    if pattern is None:
        return "뚜렷한 캔들 패턴은 감지되지 않았습니다."
    return f"직전 봉에서 {pattern} 패턴이 확인되었습니다."


def final_summary_sentence(
    trend_direction: str,
    ma_position: str,
    range_state: str,
    volume_ratio: float,
    candle_pattern: str | None,
) -> str:
    """스펙 §6-5의 "최종 한 줄 요약". 조건 4가지(추세/위치/거래량/패턴)를 조합한 규칙 기반
    MVP — 추후 조건을 늘리며 확장 예정(스펙 §6 원칙 그대로).
    """
    if candle_pattern is not None and volume_ratio >= VOLUME_HIGH_THRESHOLD:
        return f"→ 요약: {candle_pattern} 발생, 거래량 동반 확인 — 방향성 확인 필요"
    if range_state == "박스권 이탈":
        if volume_ratio >= VOLUME_HIGH_THRESHOLD:
            volume_phrase = "거래량 증가 동반"
        else:
            volume_phrase = "거래량 뚜렷한 동반 없음"
        return f"→ 요약: 박스권 이탈 발생, {volume_phrase} — 추세 전환 여부 확인 필요"
    if range_state == "박스권 압축중":
        return "→ 요약: 박스권 압축 진행 중 — 돌파 시 거래량 동반 여부 확인 필요"
    if trend_direction == "상승" and ma_position == "이평선 위 눌림":
        if volume_ratio < VOLUME_HIGH_THRESHOLD:
            return "→ 요약: 상승 추세 내 정상 눌림 구간, 거래량 동반 없이 관망 구간으로 판단"
        return "→ 요약: 상승 추세 내 눌림 구간, 거래량 증가 동반 — 반등 시도 가능성"
    if trend_direction == "하락" and ma_position == "이평선 아래":
        return "→ 요약: 하락 추세 지속, 반등 신호 뚜렷하지 않음"
    return f"→ 요약: {trend_direction} 추세, 거래량 {volume_ratio:.2f}배 — 뚜렷한 신호 없음"
