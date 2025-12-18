from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd
from .entities import Signal

class IMarketDataProvider(ABC):
    @abstractmethod
    def get_data(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        pass

class INotifier(ABC):
    @abstractmethod
    def send_alert(self, signal: Signal) -> bool:
        pass
