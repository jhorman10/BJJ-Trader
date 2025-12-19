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
    # Binary Options
    expiration: Optional[str] = None
    # Technical context
    atr: Optional[float] = None
    rsi: Optional[float] = None
    macd_hist: Optional[float] = None
    # TradingView confirmation
    tv_recommendation: Optional[str] = None  # STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    tv_confidence: Optional[str] = None  # ALTA, MEDIA, BAJA
    tv_buy_signals: Optional[int] = None
    tv_sell_signals: Optional[int] = None

@dataclass
class AnalysisResult:
    symbol: str
    signals: list[Signal]
    current_price: float
    indicators: dict  # Raw indicator values (RSI, MACD, etc) for display
