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
