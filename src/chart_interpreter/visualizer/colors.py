# 시각화 색상 의미 고정 (차트해석엔진_프로젝트스펙.md §10-1-1 원칙 3, CLAUDE.md 단일 출처 맵).
# 주단/코단/비단 어느 프로젝트 결과를 보더라도 동일 색상 = 동일 의미가 되도록
# visualizer/ 내부 모든 렌더러(static_chart.py, 추후 interactive_chart.py)가 이 상수만 참조한다.
UP_COLOR = "#2E7D32"  # 양봉/상승/롱
DOWN_COLOR = "#C62828"  # 음봉/하락/숏
MA_COLOR = "#1565C0"  # 이평선
TRENDLINE_COLOR = "#EF6C00"  # 추세선
SUPPORT_RESISTANCE_COLOR = "#8E24AA"  # 저항/지지 (자주색)
RANGE_BOX_COLOR = "#7E57C2"  # 박스권 (보라색)
