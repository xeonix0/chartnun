import os
from datetime import datetime, timezone

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from chart_interpreter.core import ma_relation, range_box, trendline
from chart_interpreter.schema import ChartAnalysis, ChartInput
from chart_interpreter.visualizer.colors import (
    DOWN_COLOR,
    MA_COLOR,
    RANGE_BOX_COLOR,
    SUPPORT_RESISTANCE_COLOR,
    TRENDLINE_COLOR,
    UP_COLOR,
)
from chart_interpreter.visualizer.static_chart import DEFAULT_OVERLAYS, VALID_OVERLAYS


def build_figure(
    chart_input: ChartInput,
    analysis: ChartAnalysis,
    overlays: list[str] | None = None,
) -> go.Figure:
    """core 모듈이 계산한 이평선/추세선/저항·지지/박스권/거래량을 캔들차트 위에 오버레이한
    plotly Figure를 파일로 저장하지 않고 그대로 반환한다.

    소비 프로젝트가 자체 UI(예: Streamlit `st.plotly_chart()`)에 직접 임베드하고 싶을 때
    쓴다 — `render_interactive_chart()`는 이 함수로 만든 Figure를 HTML로 저장하는 얇은
    래퍼일 뿐이라, 파일 저장이 필요 없는 소비처는 이 함수를 바로 써야 한다(디스크 I/O·
    임시 파일 경로 관리가 불필요해짐).

    overlays 계약(VALID_OVERLAYS/DEFAULT_OVERLAYS)은 static_chart.render_chart()와 공유한다 —
    "확대해서 보고 싶을 때" 선택적으로 쓰는 대체 렌더러일 뿐(스펙 §10-3 3번), 어떤 요소를
    켤 수 있는지·기본값이 무엇인지가 두 렌더러에서 갈라지면 안 되기 때문이다.
    """
    selected = set(overlays) if overlays is not None else set(DEFAULT_OVERLAYS)
    unknown = selected - VALID_OVERLAYS
    if unknown:
        raise ValueError(f"알 수 없는 overlay: {sorted(unknown)}")

    candles = chart_input.candles
    n = len(candles)
    x = [datetime.fromtimestamp(c.timestamp / 1000, tz=timezone.utc) for c in candles]

    show_volume = "volume" in selected
    if show_volume:
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03
        )
    else:
        fig = make_subplots(rows=1, cols=1)

    fig.add_trace(
        go.Candlestick(
            x=x,
            open=[c.open for c in candles],
            high=[c.high for c in candles],
            low=[c.low for c in candles],
            close=[c.close for c in candles],
            increasing_line_color=UP_COLOR,
            decreasing_line_color=DOWN_COLOR,
            name="가격",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    if "ma" in selected:
        ema_values = ma_relation.calculate_ema(candles)
        if ema_values:
            padded: list[float | None] = [None] * (n - len(ema_values)) + list(ema_values)
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=padded,
                    mode="lines",
                    line={"color": MA_COLOR, "width": 1.5},
                    name=f"EMA{ma_relation.DEFAULT_MA_PERIOD}",
                ),
                row=1,
                col=1,
            )

    if "trendline" in selected:
        line = trendline.trendline_for_direction(candles, analysis.trend_direction)
        if line is not None:
            point1, point2 = line
            fig.add_trace(
                go.Scatter(
                    x=[x[point1[0]], x[point2[0]]],
                    y=[point1[1], point2[1]],
                    mode="lines+markers",
                    line={"color": TRENDLINE_COLOR, "width": 1.5, "dash": "dash"},
                    marker={"color": TRENDLINE_COLOR, "size": 8},
                    name="추세선",
                ),
                row=1,
                col=1,
            )

    if "support_resistance" in selected:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=[analysis.resistance_price] * n,
                mode="lines",
                line={"color": SUPPORT_RESISTANCE_COLOR, "width": 1, "dash": "dot"},
                name="저항선",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=[analysis.support_price] * n,
                mode="lines",
                line={"color": SUPPORT_RESISTANCE_COLOR, "width": 1, "dash": "dot"},
                name="지지선",
            ),
            row=1,
            col=1,
        )

    if "range_box" in selected:
        box_high, box_low = range_box.box_bounds(candles)
        fig.add_trace(
            go.Scatter(
                x=x,
                y=[box_high] * n,
                mode="lines",
                line={"color": RANGE_BOX_COLOR, "width": 1, "dash": "dashdot"},
                name="박스 상단",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=x,
                y=[box_low] * n,
                mode="lines",
                line={"color": RANGE_BOX_COLOR, "width": 1, "dash": "dashdot"},
                name="박스 하단",
            ),
            row=1,
            col=1,
        )

    if "candle_pattern" in selected and analysis.candle_pattern is not None and n >= 2:
        pattern_index = n - 2
        pattern_candle = candles[pattern_index]
        marker_color = UP_COLOR if analysis.candle_pattern == "상승장악형" else DOWN_COLOR
        fig.add_annotation(
            x=x[pattern_index],
            y=pattern_candle.high,
            text=analysis.candle_pattern,
            showarrow=False,
            yshift=12,
            font={"color": marker_color, "size": 11},
            row=1,
            col=1,
        )

    if show_volume:
        volume_colors = [UP_COLOR if c.close >= c.open else DOWN_COLOR for c in candles]
        fig.add_trace(
            go.Bar(
                x=x,
                y=[c.volume for c in candles],
                marker_color=volume_colors,
                name="거래량",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        title=f"{chart_input.symbol} {chart_input.timeframe}",
        xaxis_rangeslider_visible=False,
        legend={"orientation": "h"},
    )

    return fig


def render_interactive_chart(
    chart_input: ChartInput,
    analysis: ChartAnalysis,
    save_dir: str,
    overlays: list[str] | None = None,
) -> str:
    """build_figure()로 만든 Figure를 plotly HTML로 저장하고 저장 경로를 반환한다."""
    fig = build_figure(chart_input, analysis, overlays)

    os.makedirs(save_dir, exist_ok=True)
    filename = (
        f"{chart_input.symbol}_{chart_input.timeframe}_{chart_input.candles[-1].timestamp}.html"
    )
    save_path = os.path.join(save_dir, filename)
    fig.write_html(save_path)
    return save_path
