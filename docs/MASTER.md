# MASTER — 진행 상태 및 설계 결정

기준: `차트해석엔진_프로젝트스펙.md` §8 개발 우선순위. 이 문서는 **현재 상태**만 유지한다 — 조사 과정·논의 이력은 `docs/HISTORY.md` 참고.

## §8 우선순위 진행 상태

- [x] 1. `pivot.py` — 고점/저점 탐지 + 지지/저항 거리(`price_distance_pct`) + 추세 판단(`determine_trend_direction`)
- [x] 1. `ma_relation.py` — EMA 계산 + 이평선 대비 위치/거리(`ma_position`)
- [x] 2. `summarizer` 1차 템플릿 — `templates.py` + `build_summary.build_partial_summary()`. pivot/ma_relation 두 모듈로 만들 수 있는 추세·위치 문장만 조합 (거래량/패턴/박스권 문장은 3·4번 완료 후 `analyze_and_summarize()`/`ChartAnalysis` 전체 조립 때 추가)
- [ ] 3. `range_box.py` — 박스권 압축/돌파 (미착수)
- [ ] 4. `volume_filter.py` + `candle_pattern.py` (미착수)
- [ ] 5. 주단 연동 테스트 → 코단/비단 순차 확장 (미착수 — `adapters/kiwoom_adapter.py`, `bybit_adapter.py`도 아직 빈 상태)

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
| adapter 함수 시그니처 원칙 | 라이브러리는 소비 프로젝트의 구체 타입(주단 `Bar`, 코단/비단 `pandas.DataFrame`)에 의존하지 않는다 — adapter 함수는 원시 값(수/문자열/딕셔너리)만 받는다. 정확한 파라미터 형태는 §8 5번(실제 착수 시점)에 확정 | `adapters/*.py` (미착수) |
| 실 데이터 검증 순서 | STOP GATE 3 검증은 **코단/비단부터** 진행 — Bybit REST `get_kline()`으로 60봉 이상을 즉시 받을 수 있어 fixture 확보가 빠름. 주단은 실시간 WS 집계라 60봉 쌓는 데 시간이 걸려 adapter 실제 연동 시점(§8 5번)에 별도 처리. "검증 순서"이지 스펙 §8-5의 "연동 순서(주단 먼저)"를 바꾸는 게 아님 — 두 트랙은 별개 | 미착수 |
| 타입 배포 | `py.typed` 마커 포함, `uv build` wheel에 포함 확인 완료 — 소비 프로젝트 `mypy --strict`가 stub 누락으로 안 막힘 | `src/chart_interpreter/py.typed` |
| 시각화 색상 | 상승/롱=초록, 하락/숏=빨강, 이평선=파랑, 추세선=주황, 지지/저항=자주색, 박스권=보라 (스펙 §10-1-1 기준으로 확정, CLAUDE.md 표 수정 완료) | `CLAUDE.md` 단일 출처 맵 |
| 실 데이터 검증 fixture | `tests/fixtures/real/{project}_{symbol}_{timeframe}.json` — 소비 프로젝트에서 1회 export한 정적 스냅샷을 커밋. 라이브러리가 거래소 API를 직접 호출하지 않는다는 원칙과 재현 가능성을 동시에 만족하는 가장 단순한 방법이라 이걸로 확정. 실제 export는 §8 우선순위 5번(연동 시점)에 진행 | 미생성 |

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
| `ma_position()`의 `"이평선 위 눌림"` 라벨은 이평선 대비 위/아래만 반영, 실제 눌림목 판단엔 추세 컨텍스트 필요 | `summarizer` 착수 시(§8 2번) `pivot.determine_trend_direction()`과 조합해 게이팅 |
| `ma_position()`이 캔들 부족 시 스펙 §4 enum에 없는 `"판단불가"`/`0.0`을 반환 | `analyze_and_summarize()`/`ChartAnalysis` 전체 조립 시(§8 4번 완료 후) 특별 처리 반영 |

## 다음 액션 (§8 순서)

1. `range_box.py` — 박스권 압축/돌파 (§8 3번)
2. `volume_filter.py` + `candle_pattern.py` (§8 4번) — 완료 후 `analyze_and_summarize()`/`ChartAnalysis` 전체 조립
3. `adapters/kiwoom_adapter.py`·`bybit_adapter.py` — "소비 프로젝트 실제 데이터 포맷" 표 + "adapter 함수 시그니처 원칙" 기준 구현
4. STOP GATE 3: 코단/비단 실 데이터로 `pivot.py`/`ma_relation.py`/`build_partial_summary()` 결과 육안 대조 검증, `tests/fixtures/real/` 스냅샷 확보
