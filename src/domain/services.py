import pandas as pd
import pandas_ta as ta
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from .entities import Signal

class TechnicalAnalysisService:
    def __init__(self, config: Dict):
        self.config = config

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
        
        # ATR
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=atr_period)
        
        return df

    def detect_signals(self, symbol: str, df: pd.DataFrame) -> List[Signal]:
        """Detects trading signals based on calculated indicators."""
        signals = []
        if len(df) < 2:
            return signals

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
           'time': datetime.now().strftime('%H:%M:%S')
        }

        # --- RSI Signals ---
        if alert_on_rsi and pd.notna(curr['RSI']) and pd.notna(prev['RSI']):
            if prev['RSI'] < rsi_oversold and curr['RSI'] >= rsi_oversold:
                signals.append(self._create_signal(symbol, 'COMPRA', 'RSI', f"RSI saliendo de sobreventa ({curr['RSI']:.1f})", 'MODERADA', **common_data))
            elif prev['RSI'] > rsi_overbought and curr['RSI'] <= rsi_overbought:
                signals.append(self._create_signal(symbol, 'VENTA', 'RSI', f"RSI saliendo de sobrecompra ({curr['RSI']:.1f})", 'MODERADA', **common_data))

        # --- MACD Signals ---
        if alert_on_macd and pd.notna(curr['MACD']) and pd.notna(prev['MACD']):
            if prev['MACD'] <= prev['MACD_Signal'] and curr['MACD'] > curr['MACD_Signal']:
                signals.append(self._create_signal(symbol, 'COMPRA', 'MACD', "Cruce alcista MACD", 'FUERTE', **common_data))
            elif prev['MACD'] >= prev['MACD_Signal'] and curr['MACD'] < curr['MACD_Signal']:
                signals.append(self._create_signal(symbol, 'VENTA', 'MACD', "Cruce bajista MACD", 'FUERTE', **common_data))

        # --- EMA Signals ---
        if alert_on_ma and pd.notna(curr['EMA_Fast']) and pd.notna(prev['EMA_Fast']):
            if prev['EMA_Fast'] <= prev['EMA_Slow'] and curr['EMA_Fast'] > curr['EMA_Slow']:
                signals.append(self._create_signal(symbol, 'COMPRA', 'EMA Cross', "Cruce Dorado (EMA)", 'FUERTE', **common_data))
            elif prev['EMA_Fast'] >= prev['EMA_Slow'] and curr['EMA_Fast'] < curr['EMA_Slow']:
                signals.append(self._create_signal(symbol, 'VENTA', 'EMA Cross', "Cruce de la Muerte (EMA)", 'FUERTE', **common_data))

        return signals

    def _create_signal(self, symbol, type, indicator, reason, strength, price, atr, rsi, macd_hist, time):
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
            macd_hist=macd_hist
        )
