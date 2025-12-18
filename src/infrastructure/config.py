import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    # Symbols
    SYMBOLS = [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X",
        "AUDUSD=X", "USDCAD=X", "NZDUSD=X",
        "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X",
        "EURAUD=X", "EURCHF=X", "GBPCHF=X"
    ]
    
    # Data Settings
    DATA_PERIOD = "3mo"
    DATA_INTERVAL = "1h"
    
    # Technical Indicators
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    
    SMA_FAST = 20
    SMA_SLOW = 50
    EMA_FAST = 12
    EMA_SLOW = 26
    
    ATR_PERIOD = 14
    
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
