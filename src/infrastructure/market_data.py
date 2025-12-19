import yfinance as yf
import pandas as pd
from typing import Optional
from datetime import datetime, timedelta
from src.domain.interfaces import IMarketDataProvider

class YFinanceAdapter(IMarketDataProvider):
    def __init__(self):
        # In-memory cache to reduce API calls
        self._cache = {}
        self._cache_ttl = 30  # seconds
    
    def get_data(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        cache_key = f"{symbol}_{period}_{interval}"
        now = datetime.now()
        
        # Check cache first
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if now - cached_time < timedelta(seconds=self._cache_ttl):
                return cached_data
        
        # Fetch fresh data
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"⚠️ No se encontraron datos para {symbol}")
                return None
            
            # Clean data
            df = df.dropna()
            
            # Store in cache
            self._cache[cache_key] = (now, df)
            return df
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de {symbol}: {str(e)}")
            return None

