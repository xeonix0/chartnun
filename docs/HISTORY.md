# HISTORY

## 2026-07-08

- 프로젝트 스캐폴딩 초기화: git init, `.gitignore`, `pyproject.toml`(uv + mypy strict + ruff + pytest), `src/chart_interpreter/` src-layout(core/summarizer/adapters/schema.py), `tests/`, `docs/MASTER.md`, `README.md`
- 스펙 §2(폴더 구조)와 §7(import 문) 간 불일치를 src-layout으로 해소 — 근거는 `docs/MASTER.md` 참고
- `schema.py`: `Candle`/`ChartInput`/`ChartAnalysis` 스펙 §3~§4 그대로 구현
- `core/pivot.py`: `find_pivot_highs`/`find_pivot_lows`(좌우 N봉 비교), `most_recent_pivot_high`/`_low`, `price_distance_pct`, `determine_trend_direction`(상승/하락/횡보) 구현 + 테스트 9건
- `core/ma_relation.py`: `calculate_ema`(SMA 시드 후 EMA 재귀), `ma_position`(이평선 위/아래/근접 + 거리%) 구현 + 테스트 6건. 데이터 부족 시 `"판단불가"` 명시적 폴백
- 게이트 통과: `ruff check .` 0 errors / `mypy . --strict` 0 errors / `pytest` 14 passed
- 합성(단위테스트) 데이터로만 검증됨 — STOP GATE 3 기준 실 데이터 육안 대조는 아직 미실시(다음 세션 과제로 `docs/MASTER.md`에 기록)

## 2026-07-08 (설계 검토 2회차)

- 주단/코단/비단 3곳의 실제 캔들 데이터 코드 조사(subagent, 코드 수정 없이 읽기 전용) — 주단은 REST 과거 조회 없이 WS 틱 실시간 집계(`int` OHLCV, naive KST datetime, `interval_seconds` 정수), 코단/비단은 Bybit `get_kline()` → `pandas.DataFrame`(`float64`, epoch ms UTC, Bybit 원본 interval 문자열). funding/OI는 코단·비단 모두 kline과 분리되어 있음을 확인(CLAUDE.md 경계 원칙 준수 확인)
- 조사 결과를 `schema.py`에 반영: `Candle.timestamp`를 UTC epoch 밀리초로 명시, `VALID_TIMEFRAMES` 정규화 표기 집합 추가, `ChartInput.candles`의 마지막 원소가 미확정 캔들일 수 있다는 불변식을 docstring으로 명시
- `py.typed` 마커 추가 + `uv build`로 wheel 포함 확인 (소비 프로젝트의 `mypy --strict`가 "missing library stubs"로 막히지 않게 하기 위함)
- 설계 충돌 2건 발견 후 사용자 확인 거쳐 확정:
  1. 시각화 색상표 — CLAUDE.md(이평선=노랑/지지저항=하늘색) vs 스펙 §10-1-1(이평선=파랑/지지저항=자주색) 불일치 발견, 근거 없는 CLAUDE.md 쪽을 스펙에 맞춰 수정
  2. 캔들 수 부족 신호 방식 — 전용 예외로 확정, `errors.py`에 `InsufficientCandlesError`/`MIN_CANDLES_REQUIRED=60` 구현(아직 `build_summary.py`에 연결 안 됨, §8 우선순위 2번 작업 시 연결 예정)
- xeonix0/chartnun GitHub 저장소는 이 환경에서 인증 수단(gh CLI 미설치) 없이 접근 불가 — 비공개 저장소로 확인, 참고 못 함
- 게이트 재확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (14 tests, 신규 파일 3개 추가 후에도 회귀 없음)

## 2026-07-08 (gh CLI 설치·인증, GitHub 연결)

- winget으로 `gh` CLI 설치 후 device-code 로그인으로 `xeonix0` 계정 인증 완료. `xeonix0/chartnun`은 실제로는 완전히 빈 저장소였음(브랜치 없음) — 이전 세션의 "접근 불가"는 권한 문제가 아니라 인증 수단 자체가 없었던 것으로 확인
- 저장소 로컬 git 아이덴티티(user.name/user.email, --global 아님) 설정 후 초기 스캐폴딩+pivot/ma_relation 커밋을 `origin main`에 push

## 2026-07-08 (설계 검토 3회차 — MASTER.md 정리 + summarizer 1차 구현)

- `docs/MASTER.md`를 "조사 이력 나열" 구조에서 "현재 확정된 설계 계약" 표 하나로 재구성. 이력 서술은 `docs/HISTORY.md`로 완전히 이관
- 남아있던 유일한 미확정 항목(실 데이터 검증 fixture 전략)을 `tests/fixtures/real/{project}_{symbol}_{timeframe}.json` 정적 스냅샷 커밋 방식으로 확정
- `summarizer/templates.py` + `summarizer/build_summary.py` 구현: `build_partial_summary()` — pivot.py/ma_relation.py 두 모듈만으로 만들 수 있는 추세·위치 문장만 조합. `analyze_and_summarize()`/`ChartAnalysis` 전체 조립은 range_box/volume_filter/candle_pattern이 갖춰진 뒤(§8 4번 완료)로 의도적으로 미룸 — 지금 만들면 volume_ratio/candle_pattern/range_state를 가짜 값으로 채우게 되므로
- 테스트 작성 중 `core/pivot.py`의 실제 버그 발견 및 수정: 완전 평탄(고가/저가가 전부 동일한) 구간에서 `==` 비교만으로는 구간 내 모든 캔들이 pivot으로 잡히던 문제 — 유일한 최댓값/최솟값일 때만 pivot으로 인정하도록 수정(`window_highs.count(max_high) == 1`). 기존에 "이론적 우려"로만 적어뒀던 알려진 단순화가 합성 테스트로 실제로 재현됨
- adapter 함수 시그니처 원칙 확정: 라이브러리는 소비 프로젝트의 구체 타입(주단 `Bar`, Bybit `DataFrame`)에 의존하지 않고 원시 값만 받는다 — 세부 시그니처는 §8 5번 실제 착수 시점에 확정
- 실 데이터 검증 순서 확정: 코단/비단부터(Bybit REST로 60봉 즉시 확보 가능), 주단은 실시간 집계라 시간이 걸려 별도 트랙으로 나중에 — 스펙 §8-5의 "연동은 주단 먼저" 순서와는 별개
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (23 tests)

## 2026-07-08 (§8 3번 — range_box.py 구현)

- `core/range_box.py` 구현: `box_bounds()`(직전 확정 `window`개 봉으로 박스 상/하단, `candles[-1]`은 pivot.py와 동일한 원칙으로 제외), `range_compression_pct()`(최근 박스폭 ÷ 직전 `lookback`개 확정 봉에서 굴린 같은 크기 박스들의 평균폭 × 100 — 스펙 §5 예시2의 "62% 수준으로 압축" 문구와 동일한 정의), `determine_range_state()`(현재가가 박스 밖이면 "박스권 이탈"을 압축 판정보다 우선 확인, 그 다음 `COMPRESSION_THRESHOLD_PCT=70.0` 이하면 "박스권 압축중", 아니면 "박스권 아님")
- baseline 확정 봉이 `window`개 미만이면(비교 불가) 압축률을 중립값 100.0으로 반환 — 침묵 실패 대신 "압축 아님"으로 명시적 처리(`docs/MASTER.md` 알려진 단순화 표에 §8 5번 실 데이터 검증 시 재검토 트리거로 기록)
- summarizer(`build_partial_summary`) 연동은 하지 않음 — pivot.py/ma_relation.py가 §8 1번에서 그랬듯, volume_filter/candle_pattern까지 갖춰진 뒤(§8 4번 완료) `analyze_and_summarize()`/`ChartAnalysis` 전체 조립 시 한 번에 연결하기로 한 기존 결정 유지
- 테스트 7건 추가(`tests/test_range_box.py`) — 박스 경계가 미확정 마지막 봉을 제외하는지, 압축/이탈(상단·하단)/비압축 3가지 상태 판정, baseline 부족 시 중립값 반환. 합성 데이터만 사용 — STOP GATE 3 실 데이터 육안 대조는 여전히 미실시
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (30 tests)

## 2026-07-08 (§8 4번 — volume_filter.py + candle_pattern.py, ChartAnalysis 전체 조립)

- `core/volume_filter.py` 구현: `average_volume()`(직전 확정 `window`개 봉 평균, `candles[-1]` 제외 — range_box와 동일 원칙), `volume_ratio()`(분자는 `candles[-1].volume` 그대로 사용, 분모가 0이면 중립값 0.0)
- `core/candle_pattern.py` 구현: `detect_candle_pattern()` — `candles[-2]`(직전 확정 봉)와 `candles[-3]`을 몸통(시가/종가) 기준으로만 비교해 "상승장악형"/"하락장악형"/`None` 판정. `candles[-1]`은 진행 중일 수 있어 제외(schema.py 불변식이 candle_pattern.py에 명시적으로 요구하던 사항을 그대로 구현)
- `summarizer/templates.py`에 `volume_sentence()`/`candle_pattern_sentence()`/`final_summary_sentence()` 추가. `final_summary_sentence()`는 스펙 §6-5 "조건 늘리며 확장" 원칙대로 규칙 기반 MVP(패턴+고거래량 → 박스권 이탈 → 박스권 압축중 → 상승눌림/하락지속 → 기본 문구 우선순위)로 구현
- `summarizer/build_summary.py`의 `build_partial_summary()`를 제거하고 스펙 §7 진입점 이름 그대로인 `analyze_and_summarize(chart_input) -> tuple[ChartAnalysis, str]`로 교체 — pivot/ma_relation/range_box/volume_filter/candle_pattern 5개 core 모듈 결과를 `ChartAnalysis`로 전부 조립하고, 스펙 5장 5문장(추세/위치/거래량/패턴/종합)을 모두 생성하는 최초 버전. `build_partial_summary`는 실제로는 3개 소비 프로젝트 어디서도 아직 import하지 않는 상태였으므로(§8 5번 미착수) 교체가 아니라 완성으로 처리
- pivot/support 미탐지 폴백 확정: `ChartAnalysis.resistance_price`/`support_price`가 스펙 원문상 `float`(Optional 아님)이라 pivot이 하나도 없으면 현재가로 채우고 거리 0.0 처리. `trend_sentence()`는 원본 `pivot_high`/`pivot_low`(`None` 가능)를 그대로 받으므로 이 폴백과 무관하게 "탐지되지 않았습니다"를 계속 명시함을 테스트로 확인
- "알려진 단순화" 표의 `ma_position()` "판단불가" 항목 해소 확인: `MIN_CANDLES_REQUIRED(60) > ma_relation.DEFAULT_MA_PERIOD(20)`이므로 `analyze_and_summarize()` 진입점에서는 이 폴백이 구조적으로 발생 불가능함을 근거로 명시(코드 변경 아님, 진입점 게이트 순서에 의한 보장)
- 테스트 추가: `tests/test_volume_filter.py`(4건), `tests/test_candle_pattern.py`(4건), `tests/test_templates.py`에 거래량/패턴/최종요약 문장 케이스 7건 추가, `tests/test_build_summary.py`를 `analyze_and_summarize()` 기준으로 재작성(4건, uptrend/flat-fallback/engulfing 시나리오 포함)
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (45 tests). STOP GATE 3(실 데이터 육안 대조)은 여전히 미실시 — §8 5번(adapter 연동) 착수 시점으로 확정 유지

## 2026-07-08 (§8 5번 — adapters 구현 + Bybit 실 데이터 검증)

- 코단(`d:\www\코단-코인단타\app\adapters\bybit.py:401`)과 비단(`d:\www\비단_비트코인단타\app\adapters\bybit.py:71`)의 `get_kline()`을 직접 읽고 두 프로젝트가 완전히 동일한 반환 형태(컬럼 `timestamp,open,high,low,close,volume,turnover`, `int64`/`float64`, 시간 오름차순 정렬·중복제거까지 동일)임을 재확인 — `adapters/bybit_adapter.py` 하나로 코단/비단 공용 처리 확정
- 주단(`d:\www\주단-주식단타\app\core\bar_aggregator.py`)의 `Bar`/`BarAggregator` 구조 확인: REST 과거 조회 없이 WS 틱을 `interval_seconds` 단위로 실시간 집계, `bar_time`은 naive `datetime`(KST 벽시계로 추정), OHLCV는 전부 `int`
- `adapters/bybit_adapter.py` 구현: `to_chart_input(rows: list[BybitKlineRow], symbol, interval)` — `BybitKlineRow = tuple[int,float,float,float,float,float]`로 pandas 의존성 없이 원시 튜플만 받음(adapter 시그니처 원칙 확정). `BYBIT_INTERVAL_TO_TIMEFRAME` 매핑으로 Bybit 원본 interval 문자열(`"5"`,`"60"`,`"D"` 등)을 `schema.VALID_TIMEFRAMES` 표기로 변환. `ChartInput.candles` 오름차순 정렬 불변식을 라이브러리 경계에서도 재보장하도록 명시적으로 `sort()` 수행
- `adapters/kiwoom_adapter.py` 구현: `to_chart_input(bars: list[KiwoomBarRow], symbol, interval_seconds)` — `KiwoomBarRow = tuple[datetime,int,int,int,int,int]`. `bar_time`(naive KST) → UTC epoch 밀리초 변환은 `KST = timezone(timedelta(hours=9))`를 붙인 뒤 `.timestamp()` 사용. `KIWOOM_INTERVAL_SECONDS_TO_TIMEFRAME` 매핑 추가
- 두 adapter 모두 알 수 없는 interval 입력 시 `ValueError`로 명시적 실패(조용한 실패 금지 원칙)
- 단위테스트 8건 추가(`tests/test_bybit_adapter.py` 4건, `tests/test_kiwoom_adapter.py` 4건) — 필드 변환, 정렬 보장, interval 매핑, 알 수 없는 interval 예외. 첫 작성 시 `test_kiwoom_adapter.py`에서 naive `datetime.timestamp()`가 시스템 로컬 타임존을 가정한다는 점을 놓쳐 기대값 계산이 틀렸던 버그를 실행 중 발견·수정(기대값도 `tzinfo=timezone.utc`를 명시해야 함)
- **STOP GATE 3 실 데이터 검증(코단/비단)**: Bybit 공개 API(`GET https://api.bybit.com/v5/market/kline`, 인증 불필요, 읽기 전용)를 직접 호출해 BTCUSDT 1시간봉 100개(코단 시나리오)와 5분봉 100개(비단 시나리오, `비단_비트코인단타/app/config.py:13`의 기본 심볼과 동일)를 받아 `tests/fixtures/real/kodan_BTCUSDT_60.json` / `bidan_BTCUSDT_5.json`로 커밋. `bybit_adapter.to_chart_input()` → `analyze_and_summarize()` 전체 파이프라인을 실제로 실행해 5문장 요약이 정상 생성됨을 확인
- 수치 재대조(시각화 모듈이 아직 없어 눈으로 보는 캔들차트 대신 원본 데이터와의 재계산 대조로 STOP GATE 3 취지를 만족): `volume_ratio` 결과(0.0941...)를 원본 JSON에서 직접 재계산한 값과 정확히 일치 확인, 보고된 `pivot_high_recent`/`pivot_low_recent` 값이 원본 캔들 목록에서 실제로 존재하는 고가/저가이며 `right_bars=5` 제외 규칙에 부합하는 위치(마지막 5개 봉 이전)에서 나온 값임을 인덱스로 확인
- 남은 미완료 항목 명시(`docs/MASTER.md` "다음 액션" 갱신): (1) 주단은 REST 과거 조회가 없어 이 세션에서 실 데이터 fixture 확보 불가 — kiwoom_adapter는 합성 데이터 검증만 된 상태, (2) 3개 소비 프로젝트 저장소에 실제로 이 라이브러리를 의존성 추가해 연결하는 작업은 이 저장소 범위 밖이라 미착수, (3) 시각적 캔들차트 육안 대조는 §10 `visualizer/` 구현 이후로 이월
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (53 tests)

## 2026-07-08 (문서 보강 — GitHub 커밋 차단 대응 + 미니PC 배포 연결 정보)

- 사용자가 "GitHub 커밋도 안 됐었다(우회로 해결됨)"·"리눅스 미니PC 정보/배포 정보가 없다"고 지적 — 비단/코단/주단의 실제 이력과 대조해 두 가지 공백 확인 후 보강(코드 변경 없음, 문서 전용)
- **GitHub 커밋 차단**: 이 프로젝트 자체 이력(위 "gh CLI 설치·인증" 항목)은 "gh 인증 수단 부재"였지만, 코단에서는 **다른 유형**(하네스의 "Credential Leakage" 자동 차단, `d:\www\코단-코인단타\docs\HISTORY.md` 2026-07-06자)이 있었음을 확인 — 우회(`--no-verify`)하지 않고 `git diff --cached`/`git check-ignore`/광범위 정규식으로 재검증 후 사용자 승인받아 재시도하는 절차를 CLAUDE.md "절대 금지 패턴" 표에 신규 행으로 추가. 이 세션에서 직접 재확인한 결과 `gh`가 현재 PATH에 없는데도(`gh: command not found`) `git ls-remote origin`은 Windows Credential Manager 저장 자격증명으로 정상 동작함을 확인 — "gh 없음 = GitHub 접근 불가"로 오판하지 않도록 CLAUDE.md "환경 메모"에 명시
- **미니PC 배포 연결**: 기존 CLAUDE.md는 "라이브러리라 배포 대상 아님"이라고만 되어 있어, 정작 §8-5(코단/주단/비단 통합) 이후 이 라이브러리가 미니PC(`unrules-nucbox-g2`)에 어떻게 설치될지(PyPI/git 의존성/로컬 경로 — 기존에도 "미정"으로 남아있던 항목)가 배포 인프라 문서와 단절돼 있었음 — CLAUDE.md 환경 메모·문서 링크 표, `docs/MASTER.md` 다음 액션 2번에 상호 참조 추가(sudo 권한 없어 `uv sync` 기반 설치만 가능하다는 미니PC 제약상 PyPI/git 의존성 방식이 유력하다는 판단 근거도 함께 기록). 실제 결정은 여전히 §8-5 착수 시점으로 유지 — 이번 작업은 결정이 아니라 "결정할 때 참고할 연결고리"를 만든 것
- 코드/게이트 영향 없음(문서만 수정) — `ruff`/`mypy`/`pytest` 재실행 불필요

## 2026-07-08 (§8 5번 마무리 — 3개 소비 프로젝트 실제 통합)

- 사용자가 이 세션에서 "3개 소비 프로젝트 실제 통합" 진행을 확정 → Explore 에이전트 3개를 병렬로 띄워 주단/코단/비단 각각의 의존성 관리 방식·캔들 데이터 소비 지점·기존 요약 로직·패키지명 충돌·60봉 미만 처리 방식을 먼저 읽기 전용으로 조사(코드 수정 없음) 후 Plan 모드로 구체 계획을 세워 승인받음
- **의존성 방식 확정**: 3개 저장소 모두 `uv add git+https://github.com/xeonix0/chartnun.git`(git 의존성). 로컬 경로 의존성은 미니PC 등 다른 머신에서 절대경로가 다르므로 배제. 3개 저장소 전부 실제로 `uv add` 성공 확인(Windows Credential Manager 인증으로 비공개 저장소 clone 정상 동작)
- **주단 실제 연결**: `app/core/state_machine.py`의 `TradingEngine._on_bar_closed`(기존 매도 신호 알림 분기 내부)에서 `history`(누적 `Bar` 리스트)가 `MIN_CANDLES_REQUIRED`(60) 이상이면 `kiwoom_adapter.to_chart_input()` + `analyze_and_summarize()`를 호출해 `_build_chart_summary()` 신규 메서드로 요약 문장을 생성. `app/core/notifier.py`의 `Notification`/`Notifier.notify()`에 `chart_summary: str | None = None` 필드 추가 — `to_message()`가 `None`이 아니면 "[차트 해석 요약]" 섹션을 덧붙임. 매도 스코어 계산 로직(`compute_sell_score`) 자체는 변경 없음. 신규 통합 테스트(`test_chart_summary_attached_once_60_bars_accumulated`)로 60봉 미만/이상 양쪽 동작을 실제 `TradingEngine`으로 검증(RSI 과매수가 유지되도록 상승 시퀀스로 66틱 주입) — 주단 게이트(`ruff`/`mypy --strict`/`pytest` 129개, 신규 1건 포함) 전체 통과
- **코단 실제 연결**: `app/rebound_live.py`의 `ReboundLiveEngine`에 심볼별 원시 캔들 버퍼 `_candle_history`(maxlen=100)를 `_closes`(반등 신호 전용, maxlen 작음)와 별개로 추가, `on_kline()`마다 채움. `ReboundSignal`에 `chart_summary: str | None` 필드 추가 — 실제 신호 발화 시점(국면 필터까지 통과한 뒤)에만 `bybit_adapter.to_chart_input()` + `analyze_and_summarize()` 호출(60개 미만이면 `None`, 신호 자체는 그대로 발화 — 요약은 보충 정보일 뿐 신호 억제 사유가 아님). `notifications/templates.py`의 `format_rebound_entry_alert()`와 `notifications/alerts.py`의 `handle_rebound_signal()`에 `chart_summary` 파라미터를 관통시켜 Telegram 메시지에 "[차트 해석 요약]" 섹션으로 추가. `app/live_runner.py`의 `ReboundLiveEngine(on_signal)` 생성 호출에 `interval=kline_interval` 전달 추가(찰눈 어댑터가 Bybit interval 문자열을 알아야 하므로). 반등 신호 판정 로직(`rebound_entry_mask`·국면 필터) 자체는 변경 없음. 신규 통합 테스트 4건(`test_rebound_live.py` 2건, `test_templates.py` 1건, `test_alerts.py` 1건)으로 60개 미만/이상 양쪽과 메시지 관통을 실제 엔진으로 검증 — 코단 게이트(`ruff`/`mypy --strict`/`pytest` 183개, 신규 4건 포함, 84개 파일 전체) 전체 통과
- **비단**: 프로젝트가 Phase 0(백테스트 전용)에서 일시 중단 중이라 실시간 스캐너 자체가 없어(스캐너 부재를 이번 조사에서 재확인) 어댑터 배선은 하지 않음 — `uv add`로 의존성만 추가, 비단 자체 `docs/HISTORY.md`/`docs/MASTER.md`에 "Phase 1 재개 시 연결 예정"을 기록. 빈 소비 지점에 억지로 코드를 만들지 않는다는 원칙(CLAUDE.md 빈껍데기 패턴 금지)에 따른 판단
- `docs/MASTER.md` §8 5번을 `[~]`(부분 완료)에서 `[x]`(완료)로 갱신, "확정된 설계 계약" 표에 의존성 방식 행 추가, "다음 액션"을 주단 fixture 커밋·비단 배선·2차 개발·미니PC 배포 재확인으로 갱신. `CLAUDE.md`의 "소비 방식"/"미니PC 배포와의 관계"를 미정에서 git 의존성 확정으로 갱신
- 이번 세션은 3개 소비 프로젝트 저장소를 직접 수정한 세션 — 각 저장소의 자체 게이트(ruff/mypy strict/pytest)를 그 저장소 안에서 개별 실행해 통과 확인했으며, 이 저장소(찰눈) 자체의 코드는 변경하지 않음(문서만 갱신)

## 2026-07-08 (§10 2차 개발 착수 — visualizer/static_chart.py + core/trendline.py)

- `상태 확인` 결과 §8 1~5번 전부 완료 확인. `docs/MASTER.md` "다음 액션" 3항목(주단 fixture/비단 배선/2차 개발/미니PC 재확인) 중 앞의 둘은 다른 저장소의 실시간 데이터·진행 상황에 막혀 이 세션에서 착수 불가 — 사용자에게 확인받아 2차 개발(visualizer)부터 진행하기로 확정
- 착수 전 스펙 §10-1-1 목업 표를 다시 읽다가 "추세선(저점/고점 연결) → 대응 모듈 `trendline.py`"가 §8 1~5번 core 모듈 목록에 없다는 공백 발견 — `core/trendline.py`를 먼저 구현: `uptrend_line()`(직전 두 확정 저점 연결), `downtrend_line()`(직전 두 확정 고점 연결), `trendline_for_direction()`(`determine_trend_direction()` 결과에 맞는 쪽 선택). 스펙 §4 `ChartAnalysis`엔 추세선 필드가 없어 순수 visualizer 전용 계산으로 확정 — schema.py/summarizer 변경 없음(3개 소비 프로젝트 영향 없음). 단위테스트 6건 추가(`tests/test_trendline.py`)
- `pyproject.toml`에 `mplfinance`를 `[project.optional-dependencies] visualizer`로 추가(dependencies는 계속 빈 리스트 유지) — 시각화를 안 쓰는 소비 프로젝트가 `uv add git+...`만 해도 pandas/matplotlib/numpy를 받지 않도록 격리
- `visualizer/colors.py`(색상 상수 단일 출처) + `visualizer/static_chart.py`(`render_chart()`) 구현 — `overlays: list[str]`로 이평선/추세선/저항·지지/박스권/캔들패턴/거래량 on/off. 실제 Bybit 실 데이터 fixture(`tests/fixtures/real/kodan_BTCUSDT_60.json`)로 PNG를 렌더링해 Read 도구로 육안 대조(STOP GATE 3의 "실제 캔들차트 육안 대조"를 이 세션에서 처음으로 진짜 이미지로 수행 — 지금까지는 visualizer 부재로 수치 재계산 대조로만 대체해왔음): 초록/빨강 캔들, 파랑 EMA20, 주황 점선 추세선(하락 추세 데이터에서 실제로 우하향 확인), 자주색 저항/지지선, 보라색 박스권 상/하단, 하단 거래량 패널이 모두 스펙 §10-1-1 색상 규칙대로 나타남을 확인
- 실행 검증 중 실제 버그 2건을 발견해 코드로 수정(관찰만 하고 넘어가지 않음, CLAUDE.md 운영 원칙):
  1. **한글 폰트 미표시**: matplotlib 기본 폰트(DejaVu Sans)에 한글 글리프가 없어 범례/패턴 라벨이 경고만 뜨고 네모로 깨짐. `plt.rcParams["font.family"]`를 호출부에서 직접 바꿔도 mplfinance가 스타일 적용 시 내부적으로 되돌려 무시됨을 실측 확인 — `mpf.make_mpf_style(rc={"font.family": ...})`로 넘겨야 실제 반영됨을 확인 후 `_korean_font_rc()`로 수정. Windows 환경은 `Malgun Gothic`으로 확인, 후보 폰트가 전혀 없으면 `warnings.warn()`으로 명시(조용한 실패 금지)
  2. **mplfinance `addplot=None` TypeError**: `overlays=["candle_pattern"]`처럼 선/수평선 계열 오버레이가 하나도 없으면 `add_plots`가 빈 리스트가 되는데, 이때 `mpf.plot(..., addplot=None)`처럼 kwarg를 명시적으로 넘기면 mplfinance validator가 `TypeError`를 던짐(값이 없으면 kwarg 자체를 안 넘겨야 함) — 실제로 재현 후 조건부 kwargs 구성으로 수정, `tests/test_static_chart.py::test_render_chart_with_no_line_overlays_still_produces_file`로 회귀 방지
- `pytest`는 통과했지만 STOP GATE 2 게이트 전체 실행 중 `mypy --strict`가 실패하는 것을 발견해 함께 수정: `mplfinance`(stub/py.typed 없음) → `[[tool.mypy.overrides]] module=["mplfinance.*"] ignore_missing_imports=true`로 좁게 처리, `pandas`(stub 없음) → `pandas-stubs` dev 의존성 추가, numpy 최신 stub이 PEP 695 `type` 문을 써서 `python_version="3.11"`로는 stub 자체가 SyntaxError로 안 읽히는 문제 → `[tool.mypy] python_version="3.12"`로 조정(런타임 지원 버전은 여전히 `requires-python=">=3.11"`, mypy 정적 분석 설정만 분리)
- `tests/test_static_chart.py` 6건 추가(기본 오버레이로 PNG 생성, 파일명 규칙(`{symbol}_{timeframe}_{timestamp}.png`) 확인, 알 수 없는 overlay `ValueError`, 오버레이 없음/캔들패턴만/전체 오버레이 조합 각각 실제 렌더링 성공 확인)
- `uv build`로 wheel에 `visualizer/`·`core/trendline.py`가 포함되고 `py.typed` 마커가 여전히 유지됨을 확인(기존 불변식 회귀 없음)
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (65 tests, 신규 12건: trendline 6 + static_chart 6)
- `docs/MASTER.md`에 §10 진행 상태 섹션 신규 추가(§10-3 우선순위 1번만 완료, 2~4번은 미착수), "확정된 설계 계약" 표에 trendline/visualizer 의존성 격리/mypy python_version/addplot 버그/한글 폰트 5개 행 추가, "다음 액션"에서 2차 개발 항목을 "다음엔 interactive_chart.py 또는 Alert 연동 중 선택 필요"로 갱신
- Alert 시스템 이미지 첨부 연동(§10-3 2번)과 `interactive_chart.py`(3번)는 이 세션 범위 밖 — 다음 세션에서 사용자와 우선순위 재확인 필요
- 전체 게이트를 반복 실행하다가 `test_render_chart_with_no_line_overlays_still_produces_file`이 간헐적으로 `TclError`(Tcl 설치 문제)로 실패하는 것을 발견 — `render_chart()`는 항상 `savefig()`만 하고 화면에 띄우지 않는데도 matplotlib이 GUI 백엔드(TkAgg)를 자동 선택해 생기는 환경 의존 flaky였음. `static_chart.py` 최상단에서 `matplotlib.use("Agg")`를 pyplot import 전에 강제해 원천 차단, `pytest -q` 5회 연속 재실행으로 재현 안 됨을 확인(이전엔 5회 중 1회 재현)

## 2026-07-08 (§10-3 3번 — visualizer/interactive_chart.py 구현)

- `상태 확인` 결과 §8 전부 완료, §10-3은 1번(static_chart) 완료·2번(Alert 연동)은 이 저장소 범위 밖(주단/코단/비단 쪽 작업)이라 사실상 선택지가 3번(`interactive_chart.py`) 하나뿐임을 확인 — 별도 확인 없이 바로 착수
- `pyproject.toml`의 `[project.optional-dependencies] visualizer`와 `[dependency-groups] dev`에 `plotly>=5.0`을 추가(`uv add --optional visualizer` / `uv add --dev`). `mplfinance`와 마찬가지로 `dependencies`(필수)엔 넣지 않음 — 시각화를 안 쓰는 소비 프로젝트가 무거운 의존성을 받지 않는다는 기존 격리 원칙 유지
- `visualizer/interactive_chart.py`의 `render_interactive_chart()` 구현: `static_chart.py`가 정의한 `VALID_OVERLAYS`/`DEFAULT_OVERLAYS`를 새로 만들지 않고 그대로 import해서 재사용 — "어떤 요소를 켤 수 있는지"는 두 렌더러가 공유하는 계약이지 static_chart 전용 값이 아니므로 CLAUDE.md 단일 출처 원칙을 지키기 위함. `visualizer/colors.py` 색상 상수도 동일하게 재사용. plotly `go.Candlestick`(가격) + `go.Bar`(거래량, 공유 x축 서브플롯)를 뼈대로 하고, EMA/추세선/저항·지지/박스권은 `go.Scatter`, 캔들패턴은 `fig.add_annotation()`으로 표시. 범례는 static_chart와 동일하게 "실제로 켜진 오버레이 요소만"(§10-1-1 원칙 5) 나오도록 캔들/거래량 트레이스는 `showlegend=False`로 숨김
- `pytest`는 통과했으나 `mypy --strict`에서 `plotly`도 stub/py.typed가 없어 `import-untyped` 에러 — `mplfinance` 때와 동일한 패턴이므로 `[[tool.mypy.overrides]] module=["mplfinance.*", "plotly.*"]`로 확장해 해결
- `tests/test_interactive_chart.py` 6건 추가 — `test_static_chart.py`와 동일한 시나리오(기본 오버레이 렌더링, 파일명 규칙(`{symbol}_{timeframe}_{timestamp}.html`), 알 수 없는 overlay `ValueError`, 오버레이 없음(volume만)/캔들패턴만/전체 오버레이 조합). `tests/` 디렉터리에 `__init__.py`가 없어(패키지 아님) `test_static_chart.py`의 헬퍼를 상대 import로 재사용할 수 없다는 것을 실행 중 확인 — 기존 이 프로젝트에 테스트 파일 간 import 선례가 전혀 없는 것과 일관되게 헬퍼(`make_uptrend_candles`/`make_engulfing_chart_input`)를 그대로 복제
- **STOP GATE 3 실 데이터 검증**: `tests/fixtures/real/kodan_BTCUSDT_60.json`(코단 BTCUSDT 1H, §8 5번에서 이미 확보된 실 데이터)을 `bybit_adapter.to_chart_input()` → `analyze_and_summarize()` → `render_interactive_chart()` 전체 파이프라인으로 실제 실행. 생성된 요약 문장 5개(추세/위치/거래량/패턴/종합)가 §8 5번 당시와 동일한 수치(`volume_ratio=0.0941...`, 저항 64,234.0/지지 62,635.5)로 재현됨을 확인. interactive HTML은 PNG처럼 Read 도구로 직접 육안 대조할 수 없어(JS로 렌더링되는 SVG라 정적 텍스트가 아님) 대신 저장된 HTML 파일 텍스트에 `visualizer/colors.py`의 색상 상수(`UP_COLOR`/`DOWN_COLOR`/`MA_COLOR`/`TRENDLINE_COLOR`/`SUPPORT_RESISTANCE_COLOR`) 6개와 `analysis.resistance_price`/`support_price` 수치가 실제로 임베드돼 있는지, `candlestick`/`bar` 트레이스 타입이 모두 존재하는지 프로그래밍적으로 대조해 확인(검증 스크립트는 스크래치패드에서 실행 후 삭제, 저장소에 커밋된 파일 없음)
- 게이트 확인: `ruff check .` / `mypy . --strict` / `pytest` 전부 통과 (71 tests, 신규 6건)
- `docs/MASTER.md` §10-3 3번을 `[x]`로 갱신, "확정된 설계 계약" 표에 `visualizer/` 의존성 격리(plotly 추가 반영)·interactive_chart overlay 계약 재사용 2개 행 추가/수정, "다음 액션" 3번을 "`interactive_chart.py`는 완료, 다음은 `pinescript_export`(4번) 또는 Alert 연동(2번, 범위 밖) 중 선택"으로 갱신
- `pinescript_export`(§10-3 4번, "여유 있을 때 추가, 필수는 아님")와 Alert 이미지/HTML 첨부 연동(2번, 주단/코단/비단 쪽 작업)이 남은 항목 — 다음 세션에서 우선순위 재확인 필요
