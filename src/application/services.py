from typing import List, Dict, Any
from src.domain.interfaces import IMarketDataProvider, INotifier
from src.domain.services import TechnicalAnalysisService
from src.domain.entities import Signal, AnalysisResult
from src.infrastructure.config import Config

class TradingOrchestrator:
    def __init__(
        self,
        data_provider: IMarketDataProvider,
        notifier: INotifier,
        analysis_service: TechnicalAnalysisService,
        config: Config
    ):
        self.data_provider = data_provider
        self.notifier = notifier
        self.analysis_service = analysis_service
        self.config = config

    def analyze_symbol(self, symbol: str) -> AnalysisResult:
        """
        Orchestrates the analysis for a single symbol:
        1. Fetch data
        2. Calculate indicators
        3. Detect signals
        4. Notify and return results
        """
        # Fetch Data
        df = self.data_provider.get_data(
            symbol, 
            period=self.config.DATA_PERIOD, 
            interval=self.config.DATA_INTERVAL
        )
        
        if df is None or df.empty:
            return AnalysisResult(symbol=symbol, signals=[], current_price=0.0, indicators={})

        # Calculate Indicators (Domain Service)
        df_indicators = self.analysis_service.calculate_indicators(df)
        
        # Detect Signals (Domain Service)
        signals = self.analysis_service.detect_signals(symbol, df_indicators)
        
        # Process Signals (Application Logic)
        for signal in signals:
            if self.config.TELEGRAM_ENABLED:
                self.notifier.send_alert(signal)
            # You could add persistency here (Save to DB) if needed
        
        # Prepare Result for Presentation
        last_row = df_indicators.iloc[-1]
        indicators = {
            'rsi': float(last_row['RSI']) if 'RSI' in last_row else 0,
            'macd': float(last_row['MACD']) if 'MACD' in last_row else 0,
            'macd_signal': float(last_row['MACD_Signal']) if 'MACD_Signal' in last_row else 0,
            'ema_fast': float(last_row['EMA_Fast']) if 'EMA_Fast' in last_row else 0,
            'ema_slow': float(last_row['EMA_Slow']) if 'EMA_Slow' in last_row else 0,
            'atr': float(last_row['ATR']) if 'ATR' in last_row else 0,
        }
        
        return AnalysisResult(
            symbol=symbol,
            signals=signals,
            current_price=float(last_row['Close']),
            indicators=indicators
        )

    def get_latest_candles(self, symbol: str) -> List[Dict[str, Any]]:
        """Helper to get clean candlestick data for the UI chart."""
        df = self.data_provider.get_data(
            symbol, 
            period=self.config.DATA_PERIOD, 
            interval=self.config.DATA_INTERVAL
        )
        if df is None:
            return []
            
        # Add EMAs for chart
        df = self.analysis_service.calculate_indicators(df)
        
        # Format for Lightweight Charts
        candles = []
        ema12 = []
        ema26 = []
        
        for index, row in df.iterrows():
            time_str = index.strftime('%Y-%m-%d %H:%M') # Simplified time
            # Note: For intraday, we might need timestamp. Lightweight charts supports multiple formats.
            # Using unix timestamp is often safer.
            timestamp = int(index.timestamp()) + 7200 # Adjusting for timezone roughly or keeping UTC
            
            candles.append({
                'time': timestamp,
                'open': row['Open'],
                'high': row['High'],
                'low': row['Low'],
                'close': row['Close']
            })
            if 'EMA_Fast' in row and not pd.isna(row['EMA_Fast']):
                 ema12.append(row['EMA_Fast'])
            else:
                 ema12.append(None)

            if 'EMA_Slow' in row and not pd.isna(row['EMA_Slow']):
                 ema26.append(row['EMA_Slow'])
            else:
                 ema26.append(None)
                 
        return {
            'candles': candles,
            'ema12': ema12,
            'ema26': ema26
        }
