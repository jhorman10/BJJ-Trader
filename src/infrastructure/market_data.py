import yfinance as yf
import pandas as pd
from typing import Optional
from src.domain.interfaces import IMarketDataProvider

class YFinanceAdapter(IMarketDataProvider):
    def get_data(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"⚠️ No se encontraron datos para {symbol}")
                return None
            
            # Clean data
            df = df.dropna()
            return df
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de {symbol}: {str(e)}")
            return None
