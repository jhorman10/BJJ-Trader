import pandas as pd
import pandas_ta as ta
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from .entities import Signal

# Import TradingView adapter
try:
    from src.infrastructure.tradingview_adapter import TradingViewAdapter, TradingViewAnalysis
    TV_AVAILABLE = True
except ImportError:
    TV_AVAILABLE = False
    TradingViewAdapter = None
    TradingViewAnalysis = None

class TechnicalAnalysisService:
    def __init__(self, config: Dict):
        self.config = config
        # Initialize TradingView adapter
        self.tv_adapter = TradingViewAdapter() if TV_AVAILABLE else None
        if self.tv_adapter:
            print("✅ TradingView adapter initialized")
        else:
            print("⚠️ TradingView adapter not available")

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates distinct technical indicators."""
        df = df.copy()
        
        # Extract config
        rsi_period = self.config.get('RSI_PERIOD', 14)
        macd_fast = self.config.get('MACD_FAST', 12)
        macd_slow = self.config.get('MACD_SLOW', 26)
        macd_signal_len = self.config.get('MACD_SIGNAL', 9)
        sma_fast = self.config.get('SMA_FAST', 50)
        sma_slow = self.config.get('SMA_SLOW', 200)
        ema_fast = self.config.get('EMA_FAST', 12)
        ema_slow = self.config.get('EMA_SLOW', 26)
        atr_period = self.config.get('ATR_PERIOD', 14)

        # RSI
        df['RSI'] = ta.rsi(df['Close'], length=rsi_period)
        
        # MACD
        macd = ta.macd(df['Close'], fast=macd_fast, slow=macd_slow, signal=macd_signal_len)
        if macd is not None:
             # pandas_ta returns columns with specific names based on params
             # We need to find them or rename them. Standard naming:
            col_macd = f'MACD_{macd_fast}_{macd_slow}_{macd_signal_len}'
            col_signal = f'MACDs_{macd_fast}_{macd_slow}_{macd_signal_len}'
            col_hist = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal_len}'
            
            df['MACD'] = macd[col_macd]
            df['MACD_Signal'] = macd[col_signal]
            df['MACD_Histogram'] = macd[col_hist]

        # Moving Averages
        df['SMA_Fast'] = ta.sma(df['Close'], length=sma_fast)
        df['SMA_Slow'] = ta.sma(df['Close'], length=sma_slow)
        df['EMA_Fast'] = ta.ema(df['Close'], length=ema_fast)
        df['EMA_Slow'] = ta.ema(df['Close'], length=ema_slow)
        
        # EMA Trend (Expert Filter)
        ema_trend_len = self.config.get('EMA_TREND', 200)
        df['EMA_Trend'] = ta.ema(df['Close'], length=ema_trend_len)
        
        # ATR
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=atr_period)
        
        return df

    def get_tradingview_analysis(self, symbol: str) -> Optional[TradingViewAnalysis]:
        """Get TradingView technical analysis for confirmation"""
        if not self.tv_adapter:
            return None
        
        interval = self.config.get('DATA_INTERVAL', '1h')
        return self.tv_adapter.get_analysis(symbol, interval)

    def detect_signals(self, symbol: str, df: pd.DataFrame) -> List[Signal]:
        """Detects trading signals based on calculated indicators + TradingView confirmation."""
        signals = []
        if len(df) < 2:
            return signals

        # Get TradingView analysis for confirmation
        tv_analysis = self.get_tradingview_analysis(symbol)
        if tv_analysis:
            print(f"📊 TradingView {symbol}: {tv_analysis.recommendation} (Buy: {tv_analysis.buy_signals}, Sell: {tv_analysis.sell_signals})")

        # Config
        alert_on_rsi = self.config.get('ALERT_ON_RSI', True)
        alert_on_macd = self.config.get('ALERT_ON_MACD_CROSS', True)
        alert_on_ma = self.config.get('ALERT_ON_MA_CROSS', True)
        rsi_oversold = self.config.get('RSI_OVERSOLD', 30)
        rsi_overbought = self.config.get('RSI_OVERBOUGHT', 70)
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]

        common_data = {
           'price': float(curr['Close']),
           'atr': float(curr['ATR']) if pd.notna(curr['ATR']) else 0.0,
           'rsi': float(curr['RSI']) if pd.notna(curr['RSI']) else 50.0,
           'macd_hist': float(curr['MACD_Histogram']) if pd.notna(curr['MACD_Histogram']) else 0.0,
           'time': datetime.now().strftime('%H:%M:%S'),
           'tv_analysis': tv_analysis
        }
        
        # Expert Filters State
        price = curr['Close']
        ema_trend = curr.get('EMA_Trend', None)
        rsi = curr.get('RSI', 50)
        
        trend_bullish = pd.notna(ema_trend) and price > ema_trend
        trend_bearish = pd.notna(ema_trend) and price < ema_trend

        # --- TradingView-Confirmed Signals (Priority) ---
        if tv_analysis and tv_analysis.recommendation in ['STRONG_BUY', 'STRONG_SELL']:
            # Only trigger on strong TradingView recommendations with good consensus
            confidence = self.tv_adapter.get_signal_confidence(tv_analysis) if self.tv_adapter else 'BAJA'
            
            if tv_analysis.recommendation == 'STRONG_BUY' and trend_bullish:
                signals.append(self._create_signal(
                    symbol, 'COMPRA', 'TRADINGVIEW PRO',
                    f"TradingView COMPRA FUERTE ({tv_analysis.buy_signals} indicadores)",
                    'MUY FUERTE', **common_data
                ))
            elif tv_analysis.recommendation == 'STRONG_SELL' and trend_bearish:
                signals.append(self._create_signal(
                    symbol, 'VENTA', 'TRADINGVIEW PRO',
                    f"TradingView VENTA FUERTE ({tv_analysis.sell_signals} indicadores)",
                    'MUY FUERTE', **common_data
                ))

        # --- RSI Signals (with TradingView confirmation) ---
        if alert_on_rsi and pd.notna(curr['RSI']) and pd.notna(prev['RSI']):
            if prev['RSI'] < rsi_oversold and curr['RSI'] >= rsi_oversold:
                # RSI exit oversold - check TradingView confirms buy
                tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_BUY', 'BUY']
                strength = 'FUERTE' if tv_confirms else 'MODERADA'
                reason = f"RSI saliendo de sobreventa ({curr['RSI']:.1f})"
                if tv_confirms:
                    reason += f" + TV: {tv_analysis.recommendation}"
                signals.append(self._create_signal(symbol, 'COMPRA', 'RSI', reason, strength, **common_data))
                
            elif prev['RSI'] > rsi_overbought and curr['RSI'] <= rsi_overbought:
                tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_SELL', 'SELL']
                strength = 'FUERTE' if tv_confirms else 'MODERADA'
                reason = f"RSI saliendo de sobrecompra ({curr['RSI']:.1f})"
                if tv_confirms:
                    reason += f" + TV: {tv_analysis.recommendation}"
                signals.append(self._create_signal(symbol, 'VENTA', 'RSI', reason, strength, **common_data))

        # --- MACD Signals (with TradingView confirmation) ---
        if alert_on_macd and pd.notna(curr['MACD']) and pd.notna(prev['MACD']):
            if prev['MACD'] <= prev['MACD_Signal'] and curr['MACD'] > curr['MACD_Signal']:
                tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_BUY', 'BUY']
                strength = 'MUY FUERTE' if tv_confirms else 'FUERTE'
                reason = "Cruce alcista MACD"
                if tv_confirms:
                    reason += f" + TV: {tv_analysis.recommendation}"
                signals.append(self._create_signal(symbol, 'COMPRA', 'MACD', reason, strength, **common_data))
                
            elif prev['MACD'] >= prev['MACD_Signal'] and curr['MACD'] < curr['MACD_Signal']:
                tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_SELL', 'SELL']
                strength = 'MUY FUERTE' if tv_confirms else 'FUERTE'
                reason = "Cruce bajista MACD"
                if tv_confirms:
                    reason += f" + TV: {tv_analysis.recommendation}"
                signals.append(self._create_signal(symbol, 'VENTA', 'MACD', reason, strength, **common_data))

        # --- Expert EMA Signals (Filtered + TradingView) ---
        if alert_on_ma and pd.notna(curr['EMA_Fast']) and pd.notna(prev['EMA_Fast']):
            # Bullish Cross
            if prev['EMA_Fast'] <= prev['EMA_Slow'] and curr['EMA_Fast'] > curr['EMA_Slow']:
                if trend_bullish and rsi > 50:
                    tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_BUY', 'BUY']
                    reason = "Cruce Dorado + Tendencia + RSI > 50"
                    if tv_confirms:
                        reason += f" + TV: {tv_analysis.recommendation}"
                    signals.append(self._create_signal(symbol, 'COMPRA', 'PRO STRATEGY', reason, 'MUY FUERTE', **common_data))
            
            # Bearish Cross
            elif prev['EMA_Fast'] >= prev['EMA_Slow'] and curr['EMA_Fast'] < curr['EMA_Slow']:
                if trend_bearish and rsi < 50:
                    tv_confirms = tv_analysis and tv_analysis.recommendation in ['STRONG_SELL', 'SELL']
                    reason = "Cruce Muerte + Tendencia + RSI < 50"
                    if tv_confirms:
                        reason += f" + TV: {tv_analysis.recommendation}"
                    signals.append(self._create_signal(symbol, 'VENTA', 'PRO STRATEGY', reason, 'MUY FUERTE', **common_data))

        return signals

    def _create_signal(self, symbol, type, indicator, reason, strength, price, atr, rsi, macd_hist, time, tv_analysis=None):
        sl_mult = self.config.get('STOP_LOSS_ATR_MULTIPLIER', 1.5)
        tp_mult = self.config.get('TAKE_PROFIT_ATR_MULTIPLIER', 2.0)
        expiration = self.config.get('BINARY_EXPIRATION_TIME', "5m")
        
        sl_dist = atr * sl_mult
        tp_dist = atr * tp_mult
        
        if type == 'COMPRA':
            sl = price - sl_dist
            tp = price + tp_dist
        else:
            sl = price + sl_dist
            tp = price - tp_dist

        # TradingView data
        tv_recommendation = None
        tv_confidence = None
        tv_buy_signals = None
        tv_sell_signals = None
        
        if tv_analysis:
            tv_recommendation = tv_analysis.recommendation
            tv_confidence = self.tv_adapter.get_signal_confidence(tv_analysis) if self.tv_adapter else None
            tv_buy_signals = tv_analysis.buy_signals
            tv_sell_signals = tv_analysis.sell_signals

        return Signal(
            symbol=symbol,
            type=type,
            indicator=indicator,
            reason=reason,
            strength=strength,
            price=price,
            stop_loss=sl,
            take_profit=tp,
            time=time,
            expiration=expiration,
            atr=atr,
            rsi=rsi,
            macd_hist=macd_hist,
            tv_recommendation=tv_recommendation,
            tv_confidence=tv_confidence,
            tv_buy_signals=tv_buy_signals,
            tv_sell_signals=tv_sell_signals
        )

