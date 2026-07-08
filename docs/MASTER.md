# MASTER — 진행 상태 및 설계 결정

기준: `차트해석엔진_프로젝트스펙.md` §8 개발 우선순위. 이 문서는 **현재 상태**만 유지한다 — 조사 과정·논의 이력은 `docs/HISTORY.md` 참고.

## §8 우선순위 진행 상태

- [x] 1. `pivot.py` — 고점/저점 탐지 + 지지/저항 거리(`price_distance_pct`) + 추세 판단(`determine_trend_direction`)
- [x] 1. `ma_relation.py` — EMA 계산 + 이평선 대비 위치/거리(`ma_position`)
- [x] 2. `summarizer` 1차 템플릿 — `templates.py` + `build_summary.build_partial_summary()`. pivot/ma_relation 두 모듈로 만들 수 있는 추세·위치 문장만 조합 (거래량/패턴/박스권 문장은 3·4번 완료 후 `analyze_and_summarize()`/`ChartAnalysis` 전체 조립 때 추가)
- [x] 3. `range_box.py` — `box_bounds`(직전 확정 window개 봉으로 박스 경계) + `range_compression_pct`(최근 박스 대비 lookback 구간 평균 박스폭 비율) + `determine_range_state`(압축중/이탈/아님 판정)
- [x] 4. `volume_filter.py`(`average_volume`/`volume_ratio`, candles[-1] 진행 중 봉 제외 원칙은 range_box와 동일) + `candle_pattern.py`(`detect_candle_pattern` — candles[-3]/[-2] 몸통 기준 장악형 판정) 구현. 이 두 모듈 완료를 계기로 `summarizer/build_summary.py`의 `build_partial_summary()`를 스펙 §7 진입점 이름 그대로인 `analyze_and_summarize()`로 교체 — pivot/ma_relation/range_box/volume_filter/candle_pattern 5개 core 모듈 전체를 `ChartAnalysis`로 조립하고 스펙 5장 5문장(추세/위치/거래량/패턴/종합)을 모두 생성
- [x] 5. `adapters/bybit_adapter.py`(코단/비단 공용) + `adapters/kiwoom_adapter.py`(주단) 구현 완료. Bybit는 실제 공개 API(`GET /v5/market/kline`, 인증 불필요)로 BTCUSDT 1H/5m 실 데이터를 받아 `analyze_and_summarize()`까지 전체 파이프라인 실행 검증 완료(`tests/fixtures/real/kodan_BTCUSDT_60.json`, `bidan_BTCUSDT_5.json`). **3개 소비 프로젝트 실제 통합(2026-07-08 완료, 상세는 `docs/HISTORY.md` 참고)**: 주단·코단은 `uv add git+https://github.com/xeonix0/chartnun.git`으로 실제 의존성 추가 + 각자 기존 실시간 알림 경로(주단 `TradingEngine._on_bar_closed`→`Notifier.notify`, 코단 `ReboundLiveEngine.on_kline`→`format_rebound_entry_alert`)에 `analyze_and_summarize()`를 연결해 요약 문장을 알림에 덧붙였고, 각 저장소 게이트(ruff/mypy strict/pytest) 전부 통과 확인. 비단은 의존성만 추가(Phase 0 백테스트 전용 상태로 프로젝트 자체가 일시 중단 중이라 실시간 스캐너가 없음) — 어댑터 배선은 비단이 Phase 1(실시간 스캐너 구현)을 재개하는 시점으로 이월. 주단의 REST 과거 조회 부재로 인한 kiwoom_adapter 실 데이터(Bybit 방식) fixture 검증은 여전히 미실시이나, 이번 통합에서 주단 저장소 자체의 실제 `Bar` 데이터로 `analyze_and_summarize()`가 정상 동작함을 통합 테스트로 확인함(STOP GATE 3 취지 충족)

## §10 2차 개발 진행 상태 (스펙 §10-3 우선순위 기준)

- [x] 1. `visualizer/static_chart.py`(`render_chart()`, mplfinance PNG) — §10-1-1 목업 표의 오버레이(이평선/추세선/저항·지지/박스권/거래량/캔들패턴)를 `overlays: list[str]`로 on/off. 이평선/저항·지지/박스권/거래량은 기존 core 모듈 재사용, 추세선만 신규 `core/trendline.py`(§4 `ChartAnalysis` 스키마엔 없음 — visualizer 전용 계산이라 3개 소비 프로젝트 영향 없음) 추가. 색상은 `visualizer/colors.py`에 단일 출처로 고정(스펙 §10-1-1 원칙 3 그대로)
- [ ] 2. Alert 시스템과 이미지 첨부 연동 — 이 저장소 범위 밖(주단/코단/비단 쪽에서 `render_chart()` 호출 후 이미지 경로를 알림에 첨부하는 작업), 착수 시 각 프로젝트에서 진행
- [ ] 3. `interactive_chart.py`(plotly HTML)
- [ ] 4. `pinescript_export`

## 확정된 설계 계약

새 core/summarizer/adapter 모듈을 만들 때 아래를 전제로 삼는다. 근거·논의 과정은 `docs/HISTORY.md` 참고.

| 항목 | 결정 | 위치 |
|---|---|---|
| 패키지 구조 | src-layout (`src/chart_interpreter/`) — 스펙 §7 import문과 맞추고, 소비 프로젝트 패키지명 충돌 회피 | `pyproject.toml` |
| `Candle.timestamp` | UTC epoch **밀리초**(int) 통일. 주단만 adapter에서 KST naive datetime → 변환 필요 | `schema.py` |
| `ChartInput.timeframe` | `VALID_TIMEFRAMES`(`1m`~`1M`, 스펙 5장 표기와 동일한 `1D`/`4H`/`15m` 형태)로 정규화. 원본(주단 `interval_seconds`, Bybit `"D"`/`"240"`)은 adapter가 변환 | `schema.py` |
| `ChartInput.candles` 마지막 원소 | 미확정(진행 중) 캔들일 수 있음 — "현재가"로만 사용. `pivot.py`는 구조상 이미 안전(마지막 `right_bars`개는 pivot 후보 제외). `candle_pattern.py`는 "직전 확정 봉"을 `candles[-2]` 기준으로 판정 | `schema.py` docstring |
| 캔들 수 부족 신호 | 전용 예외 `InsufficientCandlesError(symbol, timeframe, have, need)`, `MIN_CANDLES_REQUIRED=60`. `build_partial_summary()` 진입부에서 이미 raise. 주단은 장 시작 직후 상시 발생 — 3개 소비 프로젝트 모두 try/except로 스캔 스킵 처리 필요 | `errors.py` + `summarizer/build_summary.py` |
| pivot 타이(동률) 처리 | 구간 내 최고/최저가가 2개 이상 캔들에 동시에 나타나면(완전 평탄 구간 등) pivot 후보에서 제외 — 유일한 최댓값/최솟값일 때만 pivot으로 인정 | `core/pivot.py` |
| adapter 함수 시그니처 원칙 | 라이브러리는 소비 프로젝트의 구체 타입(주단 `Bar`, 코단/비단 `pandas.DataFrame`)에 의존하지 않는다 — 확정된 형태: `bybit_adapter.to_chart_input(rows: list[tuple[int,float,float,float,float,float]], ...)`, `kiwoom_adapter.to_chart_input(bars: list[tuple[datetime,int,int,int,int,int]], ...)`. 소비 프로젝트는 `DataFrame`/`Bar` 인스턴스를 이 튜플 형태로 변환해서 넘긴다(`zip(df["timestamp"], df["open"], ...)` 등) | `adapters/*.py` |
| 실 데이터 검증 순서 | STOP GATE 3 검증은 **코단/비단부터** 진행 — Bybit 공개 API(`GET /v5/market/kline`, 인증 불필요)로 BTCUSDT 1H/5m 100봉을 즉시 받아 `analyze_and_summarize()` 전체 파이프라인 실행 후 pivot/volume_ratio 값을 원본 캔들과 재대조해 확인 완료(§8 5번). 주단은 REST 과거 조회 자체가 없어(WS 실시간 집계만 존재) 이 방식의 실 데이터 검증이 불가능 — kiwoom_adapter는 합성 데이터 단위테스트로만 검증된 상태로 남음. 시각적 캔들차트 대조(CLAUDE.md STOP GATE 3 원칙)는 `visualizer/`(스펙 §10, 2차 개발)가 아직 없어 수치 재계산 대조로 대체함 | `tests/fixtures/real/kodan_BTCUSDT_60.json`, `bidan_BTCUSDT_5.json` |
| 타입 배포 | `py.typed` 마커 포함, `uv build` wheel에 포함 확인 완료 — 소비 프로젝트 `mypy --strict`가 stub 누락으로 안 막힘 | `src/chart_interpreter/py.typed` |
| 시각화 색상 | 상승/롱=초록, 하락/숏=빨강, 이평선=파랑, 추세선=주황, 지지/저항=자주색, 박스권=보라 (스펙 §10-1-1 기준으로 확정, CLAUDE.md 표 수정 완료) | `CLAUDE.md` 단일 출처 맵 |
| 실 데이터 검증 fixture | `tests/fixtures/real/{project}_{symbol}_{timeframe}.json` — 정적 스냅샷을 커밋. 코단/비단은 Bybit 공개 API를 1회 호출해 직접 확보(라이브러리 코드 자체는 API를 호출하지 않음, 이 fixture 생성 스크립트는 일회성 개발 도구일 뿐). 주단은 REST 과거 조회가 없어 아직 미생성 | `kodan_BTCUSDT_60.json`, `bidan_BTCUSDT_5.json` 생성 완료. 주단용은 미생성 |
| `range_box.py` 박스 경계 기준 | pivot.py와 동일한 원칙 — `candles[-1]`(진행 중일 수 있는 현재 봉)은 박스 계산에서 제외하고 직전 확정 `window`(기본 20)개 봉으로만 박스 상/하단을 정의. 현재가(`candles[-1].close`)는 이 박스와 비교해 이탈 여부만 판정 | `core/range_box.py` |
| `range_box.py` 압축률 계산 | 최근 박스폭 ÷ 직전 `lookback`(기본 60)개 확정 봉 구간에서 굴린 같은 크기 박스들의 평균폭 × 100. `COMPRESSION_THRESHOLD_PCT=70.0` 이하면 "박스권 압축중". 이탈(현재가가 박스 밖) 체크가 압축 판정보다 우선 | `core/range_box.py` |
| `volume_filter.py` 거래량 배율 계산 | 분자는 `candles[-1].volume`(진행 중일 수 있는 현재 봉 그대로 사용 — range_box처럼 "현재가"를 박스 밖 이탈 판정에 쓰는 것과 동일한 원칙), 분모는 그 직전 확정 `window`(기본 20)개 봉의 평균 거래량. 분모가 0(거래정지 등)이면 중립값 0.0 | `core/volume_filter.py` |
| `candle_pattern.py` 장악형 판정 | `candles[-2]`(직전 확정 봉)와 `candles[-3]`(그 이전 확정 봉)의 시가/종가 몸통만으로 판정 — `candles[-1]`은 진행 중일 수 있어 제외(schema.py 불변식 그대로 적용). 몸통이 완전히 감싸야("상승장악형"/"하락장악형") 인정, 꼬리(고가/저가)는 보지 않음 | `core/candle_pattern.py` |
| `analyze_and_summarize()`의 resistance/support pivot 미탐지 폴백 | `ChartAnalysis.resistance_price`/`support_price`가 스펙상 `float`(Optional 아님)이므로, pivot이 하나도 없으면(완전 평탄 구간 등) 현재가(`candles[-1].close`)를 그대로 채우고 거리는 0.0으로 채운다. `trend_sentence()`는 이 폴백과 별개로 원본 `pivot_high`/`pivot_low`(`None` 가능)를 그대로 받아 "탐지되지 않았습니다"를 명시 — 폴백 때문에 "탐지 안 됨" 사실이 요약 문장에서 가려지지 않게 함 | `summarizer/build_summary.py` |
| 최종 한 줄 요약(`final_summary_sentence`) | 스펙 §6-5 "조건 늘리며 확장" 원칙대로 지금은 규칙 기반 MVP(패턴+고거래량 → 박스권 이탈 → 박스권 압축중 → 상승눌림/하락지속 → 기본 문구 순으로 우선순위 판정). 조건 추가는 항상 이 함수에서만 | `summarizer/templates.py` |
| 소비 프로젝트 의존성 방식 (2026-07-08 확정) | git 의존성 — `uv add git+https://github.com/xeonix0/chartnun.git`. 로컬 경로 의존성은 미니PC 등 다른 머신에서 절대경로가 다르므로 배제. 주단/코단 양쪽에서 Windows Credential Manager 인증으로 비공개 저장소 clone이 실제로 성공함을 확인(별도 PAT/SSH 설정 불필요) | 주단/코단 `pyproject.toml`/`uv.lock` |
| `core/trendline.py` | 스펙 §4 `ChartAnalysis`엔 추세선 필드가 없음(§10-1-1 목업 표에만 등장) — pivot.py의 확정 고점/저점을 그대로 재사용해 `uptrend_line()`(저점끼리), `downtrend_line()`(고점끼리), `trendline_for_direction()`(trend_direction에 맞는 쪽 선택)만 제공하는 **visualizer 전용** 모듈. `ChartAnalysis`/summarizer는 건드리지 않아 3개 소비 프로젝트 영향 없음. 두 pivot 사이만 선형 보간해 좌표 리스트로 반환(연장선 없음 — "저점/고점 연결"이라는 스펙 문구 그대로) | `core/trendline.py` |
| `visualizer/` 의존성 격리 | `mplfinance`(pandas/matplotlib/numpy 포함)를 `[project.dependencies]`가 아니라 `[project.optional-dependencies] visualizer`로만 선언 — 시각화를 안 쓰는 소비 프로젝트가 `uv add git+...`만 하면 이 무거운 의존성을 전혀 받지 않음. 시각화가 필요한 프로젝트는 `uv add "chart-interpreter[visualizer] @ git+..."` 형태로 extra를 명시해야 함(아직 3개 프로젝트 중 실제로 extra를 추가한 곳은 없음) | `pyproject.toml` |
| `mypy` `python_version` 설정 | `[project].requires-python`(런타임 지원 버전, `>=3.11`)과 `[tool.mypy].python_version`(정적 분석 시 stub 파싱 문법 기준)은 별개 — numpy 최신 stub이 PEP 695 `type` 문을 쓰는데 `python_version="3.11"`로 두면 mypy가 이 stub 자체를 SyntaxError로 못 읽어 strict 게이트가 항상 실패함을 실측. 우리 코드는 3.12 전용 문법을 쓰지 않으므로 mypy 설정만 `3.12`로 올려 해결(런타임 호환 범위는 변경 없음) | `pyproject.toml` |
| `render_chart()`의 mplfinance `addplot` kwarg | `overlays`가 선/수평선 계열을 하나도 포함하지 않으면(예: `overlays=["volume"]`, `overlays=["candle_pattern"]`) `add_plots` 리스트가 빈 채로 남는데, 이때 `mpf.plot(..., addplot=None)`처럼 **명시적으로 None을 넘기면 mplfinance validator가 TypeError를 던짐**(실행 중 재현·수정 완료) — kwarg 자체를 아예 안 넘기도록 조건부로 구성해야 함. `tests/test_static_chart.py::test_render_chart_with_no_line_overlays_still_produces_file`로 회귀 방지 | `visualizer/static_chart.py` |
| 한글 폰트 렌더링 | matplotlib 기본 폰트(DejaVu Sans)는 한글 글리프가 없어 범례/캔들패턴 라벨이 침묵 실패(경고만 뜨고 네모로 깨짐)한다 — 실제 PNG를 육안 대조하다가 발견. `plt.rcParams["font.family"]`를 직접 바꿔도 mplfinance가 스타일 적용 시 내부적으로 되돌리므로 무시됨(실측 확인) — 반드시 `mpf.make_mpf_style(rc={"font.family": ...})`로 넘겨야 실제 반영됨. Windows 개발 환경은 `Malgun Gothic`으로 확인, 설치된 한글 폰트가 없으면 `warnings.warn()`으로 명시(침묵 실패 금지 원칙) | `visualizer/static_chart.py::_korean_font_rc` |
| matplotlib 백엔드 고정 | `render_chart()`는 항상 `savefig()`만 하고 화면에 띄우지 않는데, matplotlib이 GUI 백엔드(TkAgg)를 자동 선택하면 Tcl 설치 상태에 따라 간헐적으로 `TclError`가 나는 걸 반복 게이트 실행 중 실제로 재현(5회 중 1회) — `static_chart.py` 최상단에서 `pyplot` import 전에 `matplotlib.use("Agg")`를 강제해 해결. `interactive_chart.py`(plotly, §10-3 3번)는 렌더링 방식 자체가 달라 이 이슈와 무관 | `visualizer/static_chart.py` |

## 소비 프로젝트 실제 데이터 포맷 (2026-07-08 조사)

| | 주단 (Kiwoom) | 코단 (Bybit linear) | 비단 (Bybit 무기한) |
|---|---|---|---|
| 캔들 소스 | REST 과거 조회 없음 — WS 틱을 `app/core/bar_aggregator.py`가 실시간 집계 | REST `get_kline()` (`app/adapters/bybit.py:401`) → `pandas.DataFrame` | 코단과 거의 동일 (`app/adapters/bybit.py:71`), 코단에서 포팅 |
| OHLCV 타입 | `int` (원 단위) | `float64` | `float64` |
| timestamp | naive `datetime` (tz 없음, KST 벽시계로 추정) | `int64` epoch 밀리초, UTC | `int64` epoch 밀리초, UTC |
| timeframe 표기 | `interval_seconds: int` (기본 300) | Bybit 원본 문자열(`"5"`,`"15"`,`"60"`,`"D"`) | Bybit 원본 문자열, 동일 |
| 최소 캔들 개수 | 메모리 상한 100봉, 장 시작 직후 60봉 미만 **상시 발생** | 함수별 산발적 체크, 공용 게이트 없음 | 코단과 동일 |
| 무기한선물 특이 필드 | 해당 없음 | funding rate 별도 함수 — kline에 안 섞임 | funding/OI 모두 별도 함수 — kline에 안 섞임 |

## 알려진 단순화 (의도적으로 미룸)

| 단순화 | 트리거(언제 다룰지) |
|---|---|
| `ma_position()`의 `"이평선 위 눌림"` 라벨은 이평선 대비 위/아래만 반영, 실제 눌림목 판단엔 추세 컨텍스트 필요 | `final_summary_sentence()`가 `trend_direction`과 `ma_position`을 함께 받아 "상승 추세 + 이평선 위 눌림"일 때만 눌림목으로 조합 — §8 4번 완료 시 반영됨 |
| ~~`ma_position()`이 캔들 부족 시 스펙 §4 enum에 없는 `"판단불가"`/`0.0`을 반환~~ | **해소(§8 4번)**: `analyze_and_summarize()` 진입점이 `MIN_CANDLES_REQUIRED=60 > ma_relation.DEFAULT_MA_PERIOD=20`이라 이 경로에서는 `"판단불가"`가 발생할 수 없음을 확인. `ma_position()` 자체는 여전히 반환 가능(단위테스트용) — 진입점 보장일 뿐 함수 시그니처 변경 아님 |
| `range_compression_pct()`가 baseline 확정 봉이 `window`개 미만이면(비교 불가) 중립값 100.0(압축 아님으로 처리)을 반환 | 실 데이터 검증(§8 5번) 시 60봉 근처 종목에서 실제로 발생하는지 확인, 필요하면 폴백 값 재검토 |
| `analyze_and_summarize()`의 resistance/support pivot 미탐지 시 현재가로 폴백 | 실 데이터 검증(§8 5번) 시 실제로 자주 발생하는지 확인 — 자주 발생하면 스펙 §4 필드를 `float`에서 `float \| None`으로 바꿀지 3개 소비 프로젝트와 논의 필요(현재는 스펙 원문이 `float`이므로 폴백으로 대응) |

## 다음 액션

1. 주단 실 데이터 검증 — WS 틱을 일정 시간 실제로 수집해 60봉 이상을 쌓은 뒤 `tests/fixtures/real/judan_*.json` 확보(REST 과거 조회가 없어 코단/비단과 달리 즉시 확보 불가). 이번 세션의 통합 테스트(주단 저장소 `tests/test_state_machine.py::test_chart_summary_attached_once_60_bars_accumulated`)로 실제 `Bar`→`kiwoom_adapter`→`analyze_and_summarize()` 경로 자체는 검증됐으나, 정적 fixture 커밋은 여전히 미생성
2. 비단 어댑터 배선 — 비단이 Phase 1(실시간 스캐너 구현)을 재개하면 `chart_interpreter.adapters.bybit_adapter`를 코단과 동일한 패턴으로 연결(의존성은 2026-07-08에 이미 추가됨, `d:\www\비단_비트코인단타\docs\HISTORY.md` 참고)
3. §10 2차 개발 계속 — `interactive_chart.py`(plotly HTML, §10-3 3번) 또는 Alert 이미지 첨부 연동(주단/코단/비단 쪽 작업, §10-3 2번) 중 다음에 진행할 항목 선택 필요
4. 미니PC(`unrules-nucbox-g2`) 배포 시 설치 방식 재확인 — git 의존성(`uv add git+https://github.com/xeonix0/chartnun.git`) 방식이 주단/코단 양쪽에서 실제로 동작함을 확인(Windows Credential Manager 인증으로 비공개 저장소 clone 성공) — 미니PC(리눅스, 별도 인증 수단)에서도 동일하게 동작하는지는 실제 배포 시점에 재확인 필요. `visualizer` extra(mplfinance)를 쓰는 프로젝트가 생기면 리눅스에 한글 폰트(`fonts-noto-cjk` 등)가 설치돼 있는지도 그때 같이 확인할 것(`_KOREAN_FONT_CANDIDATES`에 `Noto Sans CJK KR` 포함해둠)
