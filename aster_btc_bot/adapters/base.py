from abc import ABC, abstractmethod


class ExchangeAdapter(ABC):
    @abstractmethod
    def fetch_daily_closes(self, symbol: str, limit: int):
        """Return list[float] close prices for completed daily candles only."""

    @abstractmethod
    def get_mark_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    def get_position(self, symbol: str) -> float:
        """Return current signed position in base units (BTC)."""

    @abstractmethod
    def set_target_position(self, symbol: str, target_base_qty: float, reduce_only: bool = False):
        """Adjust position to target signed base quantity."""

    @abstractmethod
    def now_ts(self) -> float:
        pass
