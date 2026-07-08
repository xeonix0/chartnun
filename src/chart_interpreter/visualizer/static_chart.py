import math
import os
import warnings
from datetime import datetime, timezone

import matplotlib

# render_chart()는 항상 savefig()로 PNG를 저장할 뿐 화면에 띄우지 않는다(스펙 §10-1 "정적
# 이미지"). 그런데 matplotlib이 GUI 백엔드(TkAgg 등)를 자동 선택하면 Tcl/Tk 설치 여부에 따라
# savefig만 하는 이 경로에서도 간헐적으로 TclError가 나는 것을 실제로 겪었다 — pyplot을
# import하기 전에 헤드리스 백엔드로 고정해 이 환경 의존성을 원천 차단한다.
matplotlib.use("Agg")

import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import mplfinance as mpf  # noqa: E402
import pandas as pd  # noqa: E402

from chart_interpreter.core import ma_relation, range_box, trendline
from chart_interpreter.schema import Candle, ChartAnalysis, ChartInput
from chart_interpreter.visualizer.colors import (
    DOWN_COLOR,
    MA_COLOR,
    RANGE_BOX_COLOR,
    SUPPORT_RESISTANCE_COLOR,
    TRENDLINE_COLOR,
    UP_COLOR,
)

# 스펙 §10-1-1 표에 나열된, on/off 가능한 오버레이 요소.
VALID_OVERLAYS = frozenset(
    {"ma", "trendline", "support_resistance", "range_box", "candle_pattern", "volume"}
)
DEFAULT_OVERLAYS: tuple[str, ...] = ("ma", "trendline", "support_resistance")

# matplotlib 기본 폰트(DejaVu Sans)는 한글 글리프가 없어 범례/라벨이 네모(tofu)로 깨진다.
# 요약 문장과 차트가 같은 언어로 연결되어야 한다는 §10-1-1 원칙 2를 지키려면 필수.
# 개발 환경(Windows)마다 설치된 한글 폰트가 다를 수 있어 후보를 순서대로 탐색한다.
_KOREAN_FONT_CANDIDATES = (
    "Malgun Gothic",
    "NanumGothic",
    "AppleGothic",
    "Noto Sans CJK KR",
    "Noto Sans KR",
)


def _korean_font_rc() -> dict[str, object]:
    """mplfinance는 style을 통해 렌더링할 때 rcParams를 자체적으로 적용하므로(내부적으로
    'sans-serif'로 되돌림), 호출부에서 plt.rcParams를 직접 바꿔도 무시된다 — 반드시
    make_mpf_style(rc=...)로 넘겨야 실제로 반영된다(실측 확인 완료)."""
    available = {f.name for f in fm.fontManager.ttflist}
    for name in _KOREAN_FONT_CANDIDATES:
        if name in available:
            return {"font.family": name, "axes.unicode_minus": False}
    warnings.warn(
        "설치된 한글 폰트를 찾지 못했습니다 — 범례/패턴 라벨이 네모(tofu)로 깨질 수 있습니다. "
        f"후보: {_KOREAN_FONT_CANDIDATES}",
        stacklevel=2,
    )
    return {"axes.unicode_minus": False}


def _to_dataframe(candles: list[Candle]) -> pd.DataFrame:
    index = pd.DatetimeIndex(
        [datetime.fromtimestamp(c.timestamp / 1000, tz=timezone.utc) for c in candles],
        name="Date",
    )
    return pd.DataFrame(
        {
            "Open": [c.open for c in candles],
            "High": [c.high for c in candles],
            "Low": [c.low for c in candles],
            "Close": [c.close for c in candles],
            "Volume": [c.volume for c in candles],
        },
        index=index,
    )


def _connecting_line(
    length: int, point1: tuple[int, float], point2: tuple[int, float]
) -> list[float]:
    """point1→point2 두 pivot을 잇는 직선을 그 구간(index i1..i2)에만 채우고 나머지는
    NaN으로 둔다 — mplfinance/matplotlib는 NaN 구간에서 선을 끊으므로, 두 점만 값을 넣으면
    (사이가 전부 NaN) 연결선이 아니라 고립된 점 두 개만 찍힌다. 스펙이 요구하는 "저점/고점을
    연결한" 추세선을 실제로 그리려면 두 인덱스 사이를 직접 보간해야 한다."""
    (i1, p1), (i2, p2) = point1, point2
    series = [math.nan] * length
    if i1 == i2:
        series[i1] = p1
        return series
    slope = (p2 - p1) / (i2 - i1)
    for idx in range(i1, i2 + 1):
        series[idx] = p1 + slope * (idx - i1)
    return series


def _marker_points(length: int, indices: list[int], values: list[float]) -> list[float]:
    series = [math.nan] * length
    for i, v in zip(indices, values):
        series[i] = v
    return series


def render_chart(
    chart_input: ChartInput,
    analysis: ChartAnalysis,
    save_dir: str,
    overlays: list[str] | None = None,
) -> str:
    """core 모듈이 계산한 이평선/추세선/저항·지지/박스권/거래량을 캔들차트 위에 오버레이해
    PNG로 저장하고 저장 경로를 반환한다.

    overlays로 표시할 요소만 선택한다(§10-1-1 원칙 1: 기법 하나당 관련 요소만 켠다).
    생략 시 DEFAULT_OVERLAYS(이평선/추세선/저항·지지)를 사용한다.
    """
    selected = set(overlays) if overlays is not None else set(DEFAULT_OVERLAYS)
    unknown = selected - VALID_OVERLAYS
    if unknown:
        raise ValueError(f"알 수 없는 overlay: {sorted(unknown)}")

    candles = chart_input.candles
    n = len(candles)
    df = _to_dataframe(candles)

    add_plots = []

    if "ma" in selected:
        ema_values = ma_relation.calculate_ema(candles)
        if ema_values:
            padded = [math.nan] * (n - len(ema_values)) + ema_values
            add_plots.append(
                mpf.make_addplot(
                    padded, color=MA_COLOR, width=1.0, label=f"EMA{ma_relation.DEFAULT_MA_PERIOD}"
                )
            )

    if "trendline" in selected:
        line = trendline.trendline_for_direction(candles, analysis.trend_direction)
        if line is not None:
            point1, point2 = line
            add_plots.append(
                mpf.make_addplot(
                    _connecting_line(n, point1, point2),
                    color=TRENDLINE_COLOR,
                    linestyle="dashed",
                    label="추세선",
                )
            )
            add_plots.append(
                mpf.make_addplot(
                    _marker_points(n, [point1[0], point2[0]], [point1[1], point2[1]]),
                    type="scatter",
                    markersize=40,
                    marker="o",
                    color=TRENDLINE_COLOR,
                )
            )

    if "support_resistance" in selected:
        add_plots.append(
            mpf.make_addplot(
                [analysis.resistance_price] * n,
                color=SUPPORT_RESISTANCE_COLOR,
                linestyle="dotted",
                label="저항선",
            )
        )
        add_plots.append(
            mpf.make_addplot(
                [analysis.support_price] * n,
                color=SUPPORT_RESISTANCE_COLOR,
                linestyle="dotted",
                label="지지선",
            )
        )

    if "range_box" in selected:
        box_high, box_low = range_box.box_bounds(candles)
        add_plots.append(
            mpf.make_addplot(
                [box_high] * n, color=RANGE_BOX_COLOR, linestyle="dashdot", label="박스 상단"
            )
        )
        add_plots.append(
            mpf.make_addplot(
                [box_low] * n, color=RANGE_BOX_COLOR, linestyle="dashdot", label="박스 하단"
            )
        )

    marketcolors = mpf.make_marketcolors(up=UP_COLOR, down=DOWN_COLOR, inherit=True)
    style = mpf.make_mpf_style(marketcolors=marketcolors, rc=_korean_font_rc())

    plot_kwargs: dict[str, object] = {
        "type": "candle",
        "style": style,
        "volume": "volume" in selected,
        "returnfig": True,
    }
    if add_plots:
        plot_kwargs["addplot"] = add_plots

    fig, axlist = mpf.plot(df, **plot_kwargs)

    if "candle_pattern" in selected and analysis.candle_pattern is not None and n >= 2:
        pattern_index = n - 2
        pattern_candle = candles[pattern_index]
        marker_color = UP_COLOR if analysis.candle_pattern == "상승장악형" else DOWN_COLOR
        axlist[0].annotate(
            analysis.candle_pattern,
            xy=(pattern_index, pattern_candle.high),
            xytext=(pattern_index, pattern_candle.high),
            textcoords="data",
            color=marker_color,
            fontsize=9,
            ha="center",
            va="bottom",
        )

    if any(ap.get("label") for ap in add_plots):
        axlist[0].legend(loc="upper left", fontsize=8)

    os.makedirs(save_dir, exist_ok=True)
    filename = f"{chart_input.symbol}_{chart_input.timeframe}_{candles[-1].timestamp}.png"
    save_path = os.path.join(save_dir, filename)
    fig.savefig(save_path)
    plt.close(fig)
    return save_path
