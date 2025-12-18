import sys
import os

# Set path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infrastructure.config import Config
from src.infrastructure.notification import TelegramAdapter
from src.domain.entities import Signal

def test_telegram():
    print("📋 Testing Telegram Configuration...")
    
    config = Config()
    
    print(f"🔹 Token Present: {'✅ Yes' if config.TELEGRAM_BOT_TOKEN else '❌ No'}")
    print(f"🔹 Chat ID Present: {'✅ Yes' if config.TELEGRAM_CHAT_ID else '❌ No'}")
    print(f"🔹 Enabled in Config: {'✅ Yes' if config.TELEGRAM_ENABLED else '❌ No'}")
    
    if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
        print("\n❌ Error: Missing configuration.")
        print("Please ensure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in your .env file.")
        return

    adapter = TelegramAdapter(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
    
    # Create a dummy signal
    dummy_signal = Signal(
        symbol="TEST=X",
        type="COMPRA",
        indicator="TEST",
        reason="Prueba de conexión",
        strength="TEST",
        price=1.0000,
        stop_loss=0.9900,
        take_profit=1.0200,
        time="00:00:00",
        atr=0.0010,
        rsi=50.0,
        macd_hist=0.0
    )
    
    print("\n📨 Attempting to send test message...")
    success = adapter.send_alert(dummy_signal)
    
    if success:
        print("\n✅ SUCCESS: Test message sent successfully!")
        print(f"Check the channel/chat: {config.TELEGRAM_CHAT_ID}")
    else:
        print("\n❌ ID FAILED: Could not send message.")
        print("Possible reasons:")
        print("1. Bot Token is invalid.")
        print("2. Chat ID is incorrect (For channels, ensure it starts with -100 or use @channelname).")
        print("3. Bot is not an Administrator in the channel.")
        print("4. Bot has not been started (for personal chats).")

if __name__ == "__main__":
    test_telegram()
