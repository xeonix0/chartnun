MIN_CANDLES_REQUIRED = 60


class InsufficientCandlesError(Exception):
    """analyze_and_summarize()가 캔들 수 부족을 신호할 때 사용한다.

    주단은 장 시작 직후 항상 60봉 미만 상태를 거치므로(REST 과거 조회가 없고 실시간
    WS 집계만 사용), 이 상태를 개별 core 모듈이 조용히 폴백하는 대신 summarizer
    진입점에서 명시적으로 raise해서 3개 소비 프로젝트가 "이번 사이클은 건너뛴다"를
    스스로 결정하게 한다.
    """

    def __init__(
        self, symbol: str, timeframe: str, have: int, need: int = MIN_CANDLES_REQUIRED
    ) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self.have = have
        self.need = need
        super().__init__(
            f"{symbol}({timeframe}): 캔들 {have}개 — 최소 {need}개 필요"
        )
