import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import threading
import time
import os
import signal
import sys

# Injection Imports
from src.infrastructure.config import Config
from src.infrastructure.market_data import YFinanceAdapter
from src.infrastructure.notification import TelegramAdapter
from src.domain.services import TechnicalAnalysisService
from src.application.services import TradingOrchestrator

# Setup Flask
app_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(app_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)
app.config['SECRET_KEY'] = 'secret_key_bjj_trader_secure'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global Orchestrator (Singleton-ish for this simple app)
config = Config()
orchestrator = TradingOrchestrator(
    data_provider=YFinanceAdapter(),
    notifier=TelegramAdapter(token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID),
    analysis_service=TechnicalAnalysisService(config=config.as_dict()),
    config=config
)

# Control State
class BotState:
    def __init__(self):
        self.running = True

bot_state = BotState()

# Background Thread
def background_monitor():
    print(f"\n🚀 Background Monitor Started with {len(config.SYMBOLS)} symbols")
    while bot_state.running:
        for symbol in config.SYMBOLS:
            try:
                # 1. Analyze and Notify (Domain/App Logic)
                result = orchestrator.analyze_symbol(symbol)
                
                # 2. Emit Real-time Data to Frontend (Presentation Logic)
                # Signals/Alerts are handled inside orchestrator via notifier,
                # but we also want to display them on the dashboard via websockets.
                for s in result.signals:
                    # Map Signal entity to frontend dictionary
                    alert_payload = {
                        'symbol': s.symbol,
                        'type': s.type,
                        'indicator': s.indicator,
                        'reason': s.reason,
                        'strength': s.strength,
                        'price': s.price,
                        'stopLoss': s.stop_loss,
                        'takeProfit': s.take_profit,
                        'time': s.time,
                        'atr': s.atr,
                        'rsi': s.rsi,
                        'macd_hist': s.macd_hist
                    }
                    socketio.emit('new_alert', alert_payload)
                
                # Market Data Update (for live price)
                socketio.emit('price_update', {
                    'symbol': symbol,
                    'price': result.current_price
                })
                
                # Indicators Update (for cards)
                # We also send indicators for the UI
                if result.indicators:
                    indicator_payload = result.indicators
                    indicator_payload['price'] = result.current_price
                    # Calculate change (dummy for now as we don't store prev price easily in this stateless loop without DB)
                    # For a real system we'd persist state. Here we fetch the chart history anyway for the chart.
                    indicator_payload['change'] = 0.0 
                    indicator_payload['changePercent'] = 0.0
                    socketio.emit('indicators', indicator_payload)

            except Exception as e:
                print(f"Error processing {symbol}: {e}")
            
            eventlet.sleep(1) # Small delay between symbols
            
        eventlet.sleep(config.CHECK_INTERVAL_MINUTES * 60) # Interval wait

# Routes
@app.route('/')
def index():
    return render_template('dashboard.html')

@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")

@socketio.on('request_data')
def handle_data_request(data):
    symbol = data.get('symbol', config.SYMBOLS[0])
    print(f"📡 Sending chart data for {symbol}")
    
    # Use orchestrator to get formatted chart data
    chart_payload = orchestrator.get_latest_candles(symbol)
    socketio.emit('chart_data', chart_payload)

    # Trigger analysis to send immediate indicator state
    orchestrator.analyze_symbol(symbol)

# Main Entry Point
if __name__ == '__main__':
    # Start Monitor
    monitor_thread = threading.Thread(target=background_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()

    # Handle Signals
    def signal_handler(sig, frame):
        print("\n👋 Shutting down...")
        bot_state.running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n🟢 BJJ Trader Pro (Clean Arch) Starting on port 8888...")
    socketio.run(app, host='0.0.0.0', port=8888, debug=config.DEBUG_MODE)
