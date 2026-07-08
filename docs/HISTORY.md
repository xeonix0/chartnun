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
