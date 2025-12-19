import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    # Symbols
    # Forex pairs often need '=X' in Yahoo Finance, but let's check
    # Common format: EURUSD=X, GBPUSD=X, etc.
    SYMBOLS = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
        "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
        "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X",
        "EURAUD=X", "EURCHF=X", "GBPCHF=X",
    ]
    
    # Data Settings
    DATA_PERIOD = "3mo"
    DATA_INTERVAL = "1h"
    
    # Technical Indicators
    RSI_PERIOD = 14
    RSI_OVERSOLD = 25   # More selective (was 30) - reduces false signals
    RSI_OVERBOUGHT = 75  # More selective (was 70) - reduces false signals
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    SMA_FAST = 20
    SMA_SLOW = 50
    EMA_FAST = 12
    EMA_SLOW = 26
    EMA_TREND = 200
    
    ATR_PERIOD = 14
    
    # Signal Quality Filters (new)
    MIN_ATR_THRESHOLD = 0.0005  # Filter low volatility noise
    SIGNAL_COOLDOWN_SECONDS = 300  # 5 min between same-symbol signals
    
    # Binary Options
    BINARY_EXPIRATION_TIME = "5m"
    
    # Risk Management
    STOP_LOSS_ATR_MULTIPLIER = 1.5
    TAKE_PROFIT_ATR_MULTIPLIER = 2.0
    
    # Alerts Config
    ALERT_ON_RSI = True
    ALERT_ON_MACD_CROSS = True
    ALERT_ON_MA_CROSS = True
    
    # Execution
    CHECK_INTERVAL_MINUTES = 15
    DEBUG_MODE = os.environ.get("DEBUG_MODE", "False") == "True"
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
    TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED", "false").lower() == "true"

    @classmethod
    def as_dict(cls):
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('__') and not callable(v)}
