from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class MarketData:
    symbol: str
    price: float
    high: float
    low: float
    time: datetime

@dataclass
class Signal:
    symbol: str
    type: str  # 'COMPRA' or 'VENTA'
    indicator: str
    reason: str
    strength: str
    price: float
    stop_loss: float
    take_profit: float
    time: str
    # Technical context
    atr: Optional[float] = None
    rsi: Optional[float] = None
    macd_hist: Optional[float] = None

@dataclass
class AnalysisResult:
    symbol: str
    signals: list[Signal]
    current_price: float
    indicators: dict  # Raw indicator values (RSI, MACD, etc) for display
