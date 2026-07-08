# MASTER — 진행 상태

기준: `차트해석엔진_프로젝트스펙.md` §8 개발 우선순위. 최신 상태만 유지, 이력은 `docs/HISTORY.md` 참고.

## §8 우선순위 진행 상태

- [x] 1. `pivot.py` — 고점/저점 탐지 + 지지/저항 거리(`price_distance_pct`) + 추세 판단(`determine_trend_direction`)
- [x] 1. `ma_relation.py` — EMA 계산 + 이평선 대비 위치/거리(`ma_position`)
- [ ] 2. `summarizer` 기본 템플릿 — pivot/ma_relation 결과로 1차 요약 문장 생성 (미착수)
- [ ] 3. `range_box.py` — 박스권 압축/돌파 (미착수)
- [ ] 4. `volume_filter.py` + `candle_pattern.py` (미착수)
- [ ] 5. 주단 연동 테스트 → 코단/비단 순차 확장 (미착수 — adapters/kiwoom_adapter.py, bybit_adapter.py도 아직 빈 상태)

## 스캐폴딩 (2026-07-08 완료)

- git 저장소 초기화 (`.git`, `.gitignore`)
- `pyproject.toml`: uv + `dependency-groups.dev`(mypy strict, ruff, pytest). `requires-python = ">=3.11"` — 주단(3.11)·코단(3.11)·비단(3.12) 중 가장 낮은 버전에 맞춤
- 의존성: 현재 런타임 의존성 0개. 순수 계산 라이브러리 성격 유지 — numpy/pandas는 core 모듈이 실제로 필요해지는 시점(예: volume_filter 롤링 통계)에 재검토
- 게이트 확인: `uv run ruff check .` / `uv run mypy . --strict` / `uv run pytest` 전부 통과 (14 tests)

## 스펙 문서와의 불일치 해소 — src-layout 채택

**문제**: 스펙 §2 폴더 구조 다이어그램은 `core/`, `summarizer/`, `adapters/`, `schema.py`를 프로젝트 루트 바로 아래 배치하지만,
§7 연동 예시는 `from chart_interpreter.adapters.kiwoom_adapter import ...` 형태로 import한다. 루트에 직접 두면 이 import가 성립하지 않는다.

**결정**: `src/chart_interpreter/` 아래에 `core/`, `summarizer/`, `adapters/`, `schema.py`를 배치하는 src-layout 채택.
`pyproject.toml`의 `[tool.hatch.build.targets.wheel] packages = ["src/chart_interpreter"]`로 빌드.

**이유**:
- §7의 import 문(`chart_interpreter.adapters...`)과 실제로 맞아떨어지는 유일한 구조
- CLAUDE.md 환경 메모가 명시적으로 경고하는 "소비 프로젝트 패키지명과 겹치는 문제"(코단에서 `dashboard/app.py`가 루트 `app/` 패키지와 겹쳐 재귀 임포트 크래시 난 전례)를 src-layout이 구조적으로 회피함 — 프로젝트 루트에 `chart_interpreter`라는 임포트 가능한 이름이 노출되지 않음

**영향 프로젝트**: 주단/코단/비단 — 아직 이 라이브러리를 import하는 코드가 3곳 어디에도 없음(확인 완료, 2026-07-08 기준). 연동 시점(§8 우선순위 5번)에 `from chart_interpreter... import ...` 형태로 그대로 쓰면 됨. 로컬 경로 참조 방식은 `uv add --editable ../찰눈_차트보는눈` 형태가 유력하나 최종 확정은 실제 연동 시점으로 보류.

## 소비 프로젝트 실제 데이터 포맷 조사 (2026-07-08)

adapter 설계 착수 전, 주단/코단/비단 3곳의 실제 캔들 데이터 코드를 직접 확인함 (grep/read, 코드 수정 없음).

| | 주단 (Kiwoom) | 코단 (Bybit linear) | 비단 (Bybit 무기한) |
|---|---|---|---|
| 캔들 소스 | REST 과거 조회 없음 — WS 틱을 `app/core/bar_aggregator.py`가 실시간 집계 | REST `get_kline()` (`app/adapters/bybit.py:401`) → `pandas.DataFrame` | 코단과 거의 동일 (`app/adapters/bybit.py:71`), 코단에서 포팅 |
| OHLCV 타입 | `int` (원 단위, 소수점 없음) | `float64` | `float64` |
| timestamp | naive `datetime` (tz 정보 없음, KST 벽시계로 추정) | `int64` epoch **밀리초, UTC** | `int64` epoch 밀리초, UTC |
| timeframe 표기 | `interval_seconds: int` (문자열 아님, 기본 300) | Bybit 원본 문자열(`"5"`,`"15"`,`"60"`,`"D"`) | Bybit 원본 문자열, 동일 |
| 최소 캔들 개수 | 메모리 상한 100봉(`_MAX_BAR_HISTORY`), 장 시작 직후엔 60봉 미만이 **실제로 발생함** | 함수별 산발적 체크(예: `rebound_live.py:38`), 공용 게이트 없음 | 코단과 동일 |
| 무기한선물 특이 필드 | 해당 없음 | funding rate는 `get_funding_history()`로 완전히 분리 — kline에 안 섞임 | funding/OI 모두 별도 함수로 분리 — kline에 안 섞임 (CLAUDE.md 경계 원칙이 이미 지켜지고 있음 확인) |

**스키마에 반영한 결정** (`schema.py` 갱신 완료):
- `Candle.timestamp`는 **UTC epoch 밀리초**로 통일 — 코단/비단 원본과 그대로 맞고, 주단만 adapter에서 KST naive datetime → UTC ms 변환 필요
- `ChartInput.timeframe`은 `VALID_TIMEFRAMES`(`"1m"~"1M"`, 스펙 5장 예시 표기와 동일한 `1D`/`4H`/`15m` 형태) 중 하나로 정규화 — 주단의 `interval_seconds`(정수)와 Bybit 원본 코드(`"D"`,`"240"` 등)는 서로 표기가 달라 adapter가 각자 이 표를 거쳐야 함
- `ChartInput.candles`는 마지막 원소가 미확정(진행 중) 캔들일 수 있음을 스키마 docstring에 명시 — `pivot.py`는 구조상 이미 마지막 `right_bars`개를 pivot 후보에서 제외하므로 안전하나, 앞으로 만들 `candle_pattern.py`는 "직전 확정 봉"을 `candles[-1]`이 아니라 `candles[-2]`로 봐야 함(adapter가 진행 중 캔들 여부를 별도로 표시하기 전까지)

**결정 완료**:
- 캔들 수 부족 신호 방식: **전용 예외**로 확정. `errors.py`에 `InsufficientCandlesError(symbol, timeframe, have, need)` + `MIN_CANDLES_REQUIRED = 60` 구현 완료. `summarizer/build_summary.py`(§8 우선순위 2, 아직 미착수) 작성 시 `analyze_and_summarize()` 진입부에서 `len(chart_input.candles) < MIN_CANDLES_REQUIRED`면 이 예외를 raise하도록 연결해야 함 — 주단은 장 시작 직후 이 경로가 상시 발생하므로 3개 소비 프로젝트 모두 반드시 try/except로 처리해야 함(스캔 사이클에서 해당 심볼 스킵)
- `py.typed` 마커 추가 완료 (`src/chart_interpreter/py.typed`, `uv build` wheel에 포함 확인) — 3개 소비 프로젝트가 이 라이브러리를 로컬 editable 의존성으로 붙였을 때 자기 자신의 `mypy --strict`가 "missing library stubs"로 안 막히게 하기 위함

## 알려진 단순화 (추후 보강 필요)

- `ma_relation.ma_position()`의 `"이평선 위 눌림"` 라벨은 현재 이평선 대비 위/아래 여부만 반영한다. 실제 "눌림목"은 상승 추세 컨텍스트(고점 형성 후 조정)까지 확인해야 의미가 맞음 — `summarizer`에서 `pivot.determine_trend_direction()`과 조합해 게이팅할 때 보강 필요
- `pivot.find_pivot_highs/lows`는 동일 고가/저가가 여러 봉에 걸쳐 타이인 경우 모두 pivot으로 반환함 (Pine Script의 좌우 비대칭 타이브레이크와 다름) — 지금까지는 문제 케이스 없음, 실 데이터 검증 시 재확인
- `ma_position` 등 데이터 부족(캔들 수 < period) 시 `"판단불가"`/`0.0`으로 명시적 폴백 반환 — 스펙 §4 enum(`"이평선 위 눌림"` 등)에는 없는 값이므로 `summarizer`가 이 값을 특별 처리해야 함

## 시각화(visualizer) 설계 점검 (2026-07-08)

§8 우선순위상 아직 착수 시점 아님(core/summarizer 미완성 — CLAUDE.md 금지패턴 "2차 개발 착수 전 core/summarizer 미완성 상태로 진행" 위반 방지). 코드는 만들지 않고 문서 간 충돌만 점검함.

**발견한 문제 — CLAUDE.md와 스펙 문서의 색상표가 서로 다름 (결정 완료)**:
- CLAUDE.md 단일 출처 맵은 "이동평균=노랑, 지지/저항=하늘색"이었고 스펙 §10-1-1은 "이평선=파랑, 저항/지지=자주색"이었음(상승/하락=초록/빨강, 추세선=주황, 박스권=보라는 원래 일치)
- CLAUDE.md는 이 표가 "코단 `docs/DASHBOARD_UI_GUIDE.md` 매핑과 동일"하다고 적어뒀지만, 실제로 그 문서를 확인해보니 표에 있는 것은 테이블 셀 색상(포지션 손익 초록/빨강, 롱/숏 초록/빨강) 규칙뿐이고 이평선·지지저항 **선 색상 규칙은 그 문서에 없었음** — CLAUDE.md 쪽 근거가 확인되지 않아 스펙(파랑/자주색) 기준으로 통일, `CLAUDE.md` 단일 출처 맵 표 수정 완료

## 다음 액션

1. STOP GATE 3 항목대로 주단/코단/비단 중 하나에서 실제 캔들 데이터를 가져와 `pivot.py`/`ma_relation.py` 결과를 육안 대조 검증 (현재는 합성 데이터 단위테스트만 통과한 상태) — 실 데이터는 이 라이브러리가 API를 직접 호출하지 않으므로, 소비 프로젝트에서 1회 export한 정적 fixture(csv/json)를 `tests/fixtures/real/`에 두는 방식이 유력. 아직 미확정
2. `summarizer/templates.py` + `build_summary.py` — pivot/ma_relation 결과를 스펙 5장 형식(수치 포함 문장)으로 조합. `analyze_and_summarize()` 진입부에 `errors.InsufficientCandlesError` 게이트 연결 포함
3. `adapters/kiwoom_adapter.py`·`bybit_adapter.py` — 위 "소비 프로젝트 실제 데이터 포맷 조사" 표 기준으로 구현 (아직 미착수, §8 순서상 4번 이후)
