"""
TradingView Technical Analysis Adapter
Fetches real-time recommendations from TradingView for enhanced signal generation
"""
from typing import Dict, Optional
from dataclasses import dataclass

try:
    from tradingview_ta import TA_Handler, Interval, Exchange
    TRADINGVIEW_AVAILABLE = True
except ImportError:
    TRADINGVIEW_AVAILABLE = False
    print("⚠️ tradingview-ta not installed. TradingView integration disabled.")


@dataclass
class TradingViewAnalysis:
    """TradingView analysis result"""
    symbol: str
    recommendation: str  # STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    buy_signals: int
    sell_signals: int
    neutral_signals: int
    
    # Oscillators breakdown
    oscillators_recommendation: str
    oscillators_buy: int
    oscillators_sell: int
    oscillators_neutral: int
    
    # Moving Averages breakdown
    ma_recommendation: str
    ma_buy: int
    ma_sell: int
    ma_neutral: int
    
    # Key indicators
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    ema_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    adx: Optional[float] = None
    cci: Optional[float] = None
    stoch_k: Optional[float] = None
    stoch_d: Optional[float] = None


# Symbol mapping from Yahoo Finance format to TradingView format
SYMBOL_MAPPING = {
    # Forex pairs
    "EURUSD=X": ("EURUSD", "forex", "FX_IDC"),
    "GBPUSD=X": ("GBPUSD", "forex", "FX_IDC"),
    "USDJPY=X": ("USDJPY", "forex", "FX_IDC"),
    "USDCHF=X": ("USDCHF", "forex", "FX_IDC"),
    "AUDUSD=X": ("AUDUSD", "forex", "FX_IDC"),
    "USDCAD=X": ("USDCAD", "forex", "FX_IDC"),
    "NZDUSD=X": ("NZDUSD", "forex", "FX_IDC"),
    "EURGBP=X": ("EURGBP", "forex", "FX_IDC"),
    "EURJPY=X": ("EURJPY", "forex", "FX_IDC"),
    "GBPJPY=X": ("GBPJPY", "forex", "FX_IDC"),
    "AUDJPY=X": ("AUDJPY", "forex", "FX_IDC"),
    "EURAUD=X": ("EURAUD", "forex", "FX_IDC"),
    "EURCHF=X": ("EURCHF", "forex", "FX_IDC"),
    "GBPCHF=X": ("GBPCHF", "forex", "FX_IDC"),
    # Commodities
    "GC=F": ("GOLD", "cfd", "TVC"),
    # Crypto
    "BTC-USD": ("BTCUSD", "crypto", "BITSTAMP"),
}

# Interval mapping
INTERVAL_MAPPING = {
    "1m": Interval.INTERVAL_1_MINUTE if TRADINGVIEW_AVAILABLE else None,
    "5m": Interval.INTERVAL_5_MINUTES if TRADINGVIEW_AVAILABLE else None,
    "15m": Interval.INTERVAL_15_MINUTES if TRADINGVIEW_AVAILABLE else None,
    "30m": Interval.INTERVAL_30_MINUTES if TRADINGVIEW_AVAILABLE else None,
    "1h": Interval.INTERVAL_1_HOUR if TRADINGVIEW_AVAILABLE else None,
    "4h": Interval.INTERVAL_4_HOURS if TRADINGVIEW_AVAILABLE else None,
    "1d": Interval.INTERVAL_1_DAY if TRADINGVIEW_AVAILABLE else None,
    "1w": Interval.INTERVAL_1_WEEK if TRADINGVIEW_AVAILABLE else None,
    "1mo": Interval.INTERVAL_1_MONTH if TRADINGVIEW_AVAILABLE else None,
}


class TradingViewAdapter:
    """Adapter for fetching TradingView technical analysis"""
    
    def __init__(self):
        self.enabled = TRADINGVIEW_AVAILABLE
    
    def get_analysis(self, yahoo_symbol: str, interval: str = "1h") -> Optional[TradingViewAnalysis]:
        """
        Get TradingView technical analysis for a symbol
        
        Args:
            yahoo_symbol: Symbol in Yahoo Finance format (e.g., "EURUSD=X")
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1mo)
            
        Returns:
            TradingViewAnalysis object or None if unavailable
        """
        if not self.enabled:
            return None
        
        # Map Yahoo symbol to TradingView format
        if yahoo_symbol not in SYMBOL_MAPPING:
            print(f"⚠️ Symbol {yahoo_symbol} not mapped for TradingView")
            return None
        
        tv_symbol, screener, exchange = SYMBOL_MAPPING[yahoo_symbol]
        tv_interval = INTERVAL_MAPPING.get(interval, Interval.INTERVAL_1_HOUR)
        
        try:
            handler = TA_Handler(
                symbol=tv_symbol,
                screener=screener,
                exchange=exchange,
                interval=tv_interval
            )
            
            analysis = handler.get_analysis()
            
            # Extract summary
            summary = analysis.summary
            oscillators = analysis.oscillators
            moving_averages = analysis.moving_averages
            indicators = analysis.indicators
            
            return TradingViewAnalysis(
                symbol=yahoo_symbol,
                recommendation=summary.get('RECOMMENDATION', 'NEUTRAL'),
                buy_signals=summary.get('BUY', 0),
                sell_signals=summary.get('SELL', 0),
                neutral_signals=summary.get('NEUTRAL', 0),
                
                oscillators_recommendation=oscillators.get('RECOMMENDATION', 'NEUTRAL'),
                oscillators_buy=oscillators.get('BUY', 0),
                oscillators_sell=oscillators.get('SELL', 0),
                oscillators_neutral=oscillators.get('NEUTRAL', 0),
                
                ma_recommendation=moving_averages.get('RECOMMENDATION', 'NEUTRAL'),
                ma_buy=moving_averages.get('BUY', 0),
                ma_sell=moving_averages.get('SELL', 0),
                ma_neutral=moving_averages.get('NEUTRAL', 0),
                
                # Key indicators
                rsi=indicators.get('RSI'),
                macd=indicators.get('MACD.macd'),
                macd_signal=indicators.get('MACD.signal'),
                ema_20=indicators.get('EMA20'),
                sma_50=indicators.get('SMA50'),
                sma_200=indicators.get('SMA200'),
                adx=indicators.get('ADX'),
                cci=indicators.get('CCI20'),
                stoch_k=indicators.get('Stoch.K'),
                stoch_d=indicators.get('Stoch.D'),
            )
            
        except Exception as e:
            print(f"⚠️ TradingView analysis failed for {yahoo_symbol}: {e}")
            return None
    
    def is_strong_signal(self, analysis: TradingViewAnalysis, signal_type: str) -> bool:
        """
        Check if TradingView confirms a strong signal
        
        Args:
            analysis: TradingView analysis result
            signal_type: 'COMPRA' or 'VENTA'
            
        Returns:
            True if TradingView confirms the signal direction
        """
        if analysis is None:
            return False
        
        rec = analysis.recommendation
        
        if signal_type == 'COMPRA':
            return rec in ['STRONG_BUY', 'BUY']
        elif signal_type == 'VENTA':
            return rec in ['STRONG_SELL', 'SELL']
        
        return False
    
    def get_signal_confidence(self, analysis: TradingViewAnalysis) -> str:
        """
        Get confidence level based on TradingView consensus
        
        Returns:
            'ALTA', 'MEDIA', 'BAJA'
        """
        if analysis is None:
            return 'BAJA'
        
        total = analysis.buy_signals + analysis.sell_signals + analysis.neutral_signals
        if total == 0:
            return 'BAJA'
        
        # Check consensus strength
        max_signals = max(analysis.buy_signals, analysis.sell_signals)
        consensus_ratio = max_signals / total
        
        if consensus_ratio >= 0.7:
            return 'ALTA'
        elif consensus_ratio >= 0.5:
            return 'MEDIA'
        else:
            return 'BAJA'
