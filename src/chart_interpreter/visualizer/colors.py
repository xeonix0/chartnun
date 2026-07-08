# 시각화 색상 의미 고정 (차트해석엔진_프로젝트스펙.md §10-1-1 원칙 3, CLAUDE.md 단일 출처 맵).
# 주단/코단/비단 어느 프로젝트 결과를 보더라도 동일 색상 = 동일 의미가 되도록
# visualizer/ 내부 모든 렌더러(static_chart.py, interactive_chart.py)가 이 상수만 참조한다.
#
# 2026-07-08: 트레이딩뷰 다크 모드를 벤치마킹해 전면 개편 — 기존 값(Material Design 700대
# 다크 톤: #2E7D32/#C62828/#1565C0/#EF6C00/#8E24AA/#7E57C2)은 흰 배경을 전제로 고른 색이라
# 어두운 배경(코단 대시보드 등)에서 대비가 부족해 "선이 잘 안 보인다"는 실사용 피드백이
# 있었다. 색상 계열(초록=상승/빨강=하락/파랑=이평선/주황=추세선/자주=저항지지/보라=박스권)은
# 스펙 §10-1-1 그대로 유지하고, 명도만 다크 배경에서 잘 보이는 밝은 톤으로 교체.
UP_COLOR = "#26A69A"  # 양봉/상승/롱 (트레이딩뷰 기본 다크 테마와 동일한 teal 계열 초록)
DOWN_COLOR = "#EF5350"  # 음봉/하락/숏 (트레이딩뷰 기본 다크 테마와 동일한 coral 계열 빨강)
MA_COLOR = "#42A5F5"  # 이평선 (밝은 파랑)
TRENDLINE_COLOR = "#FFA726"  # 추세선 (밝은 주황)
SUPPORT_RESISTANCE_COLOR = "#EA80FC"  # 저항/지지 (밝은 자주/마젠타 — 박스권 보라와 구분되게)
RANGE_BOX_COLOR = "#B388FF"  # 박스권 (밝은 보라/라벤더)

# 차트 배경/그리드/텍스트 (다크 모드 고정). static_chart.py(mplfinance)·interactive_chart.py
# (plotly) 둘 다 이 3개만 참조 — 렌더러마다 배경색이 갈라지지 않게 한다.
CHART_BACKGROUND_COLOR = "#131722"  # 트레이딩뷰 기본 다크 배경(거의 검정에 가까운 남색)
CHART_GRID_COLOR = "#2A2E39"  # 그리드/보더 (은은하게, 배경과 명도 차이만 살짝)
CHART_TEXT_COLOR = "#D1D4DC"  # 축/범례/라벨 텍스트 (어두운 배경에서 읽히는 밝은 회색)

# 선 굵기 — 어두운 배경에서는 얇은 선(1px대)이 묻히기 쉬워 기존보다 굵게(요청: "굵기도 수정").
MA_LINE_WIDTH = 2.0
TRENDLINE_WIDTH = 2.5
SUPPORT_RESISTANCE_WIDTH = 1.5
RANGE_BOX_WIDTH = 1.5
