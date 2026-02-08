import csv
import time
from pathlib import Path
from adapters.base import ExchangeAdapter


class AsterPlaceholderAdapter(ExchangeAdapter):
    """
    Paper adapter now; wire real Aster API later.
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.paper_position = 0.0
        self.csv_fallback = Path('/home/ttang/Documents/btc_data/bitcoin_daily_usd_stooq.csv')

    def fetch_daily_closes(self, symbol: str, limit: int):
        # TODO (live): call Aster candles endpoint for completed 1D candles
        closes = []
        with self.csv_fallback.open() as f:
            r = csv.DictReader(f)
            for row in r:
                closes.append(float(row['Close']))
        return closes[-limit:]

    def get_mark_price(self, symbol: str) -> float:
        # TODO (live): call Aster mark/ticker endpoint
        closes = self.fetch_daily_closes(symbol, 2)
        return closes[-1]

    def get_position(self, symbol: str) -> float:
        # TODO (live): call Aster positions endpoint
        return self.paper_position

    def set_target_position(self, symbol: str, target_base_qty: float, reduce_only: bool = False):
        # TODO (live): translate delta into Aster market/limit order(s)
        self.paper_position = target_base_qty
        return {
            'ok': True,
            'mode': 'paper',
            'symbol': symbol,
            'target_base_qty': target_base_qty,
            'reduce_only': reduce_only,
        }

    def now_ts(self) -> float:
        return time.time()
