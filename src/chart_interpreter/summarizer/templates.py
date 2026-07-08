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
