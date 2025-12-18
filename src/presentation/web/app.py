from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import threading
import time
import os
import signal
import sys

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
# Path to the frontend build directory (relative to this file)
# app.py is in src/presentation/web
# frontend is in root/frontend
project_root = os.path.abspath(os.path.join(app_dir, '../../../'))
dist_dir = os.path.join(project_root, 'frontend', 'dist')

from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(dist_dir, 'assets'), static_url_path='/assets', template_folder=dist_dir)
CORS(app) # Enable CORS for all routes
# Serve static files from root dist for files like favicon, etc if needed, 
# but mostly Flask handles static_folder for /static url. 
# We might need a catch-all route later if using React Router, but for now single page.
app.config['SECRET_KEY'] = 'secret_key_bjj_trader_secure'
# Using default async_mode (threading) for compatibility with Python 3.13+ and simple deployment
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global Orchestrator (Singleton-ish for this simple app)
config = Config()
orchestrator = TradingOrchestrator(
    data_provider=YFinanceAdapter(),
    notifier=TelegramAdapter(token=config.TELEGRAM_BOT_TOKEN, chat_id=config.TELEGRAM_CHAT_ID),
    analysis_service=TechnicalAnalysisService(config=config.as_dict()),
    config=config
)

# Application Service for Bot Logic
from src.application.bot_service import SignalBotService
bot_service = SignalBotService(orchestrator, config)

# Define Presentations Callbacks (connecting App Layer events to Web Layer sockets)
def on_new_signal(s):
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
        'macd_hist': s.macd_hist,
        'expiration': s.expiration
    }
    socketio.emit('new_alert', alert_payload)

def on_price_update(symbol, price):
    socketio.emit('price_update', {
        'symbol': symbol,
        'price': price
    })

def on_indicators_update(symbol, indicators, price):
    indicator_payload = indicators.copy()
    indicator_payload['price'] = price
    # Statless calc for now
    indicator_payload['change'] = 0.0 
    indicator_payload['changePercent'] = 0.0
    socketio.emit('indicators', indicator_payload)

# Register Callbacks
bot_service.register_on_signal(on_new_signal)
bot_service.register_on_price(on_price_update)
bot_service.register_on_indicator(on_indicators_update)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def static_proxy(path):
    # Avoid intercepting socket.io requests
    if path.startswith('socket.io') or 'transport=' in request.args:
        return
    
    # Try to serve file from dist directory (e.g. favicon.ico, vite.svg)
    try:
        return send_from_directory(dist_dir, path)
    except:
        # If not found, fall back to index.html for SPA routing
        return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")

@socketio.on('request_data')
def handle_data_request(data):
    symbol = data.get('symbol', config.SYMBOLS[0])
    print(f"📡 Sending chart data for {symbol}")
    
    # Use orchestrator to get formatted chart data
    # Trigger analysis to send immediate indicator state (WITHOUT external notification)
    try:
        # 1. Emit Initial Chart Data
        candles_data = orchestrator.get_latest_candles(symbol)
        if candles_data and 'candles' in candles_data:
            print(f"   ↳ Sending {len(candles_data['candles'])} candles")
            socketio.emit('chart_data', candles_data['candles'])

        # 2. Emit Initial Indicators
        result = orchestrator.analyze_symbol(symbol, notify_external=False)
        
        if result.indicators:
            indicator_payload = result.indicators
            indicator_payload['price'] = result.current_price
            indicator_payload['change'] = 0.0 
            indicator_payload['changePercent'] = 0.0
            socketio.emit('indicators', indicator_payload)
            
            # Also emit initial price update to set currentPrice
            socketio.emit('price_update', {
                'symbol': symbol,
                'price': result.current_price
            })

    except Exception as e:
        print(f"⚠️ Initial Analysis Failed for {symbol}: {e}")

# Main Entry Point
if __name__ == '__main__':
    # Start Monitor (Application Service)
    bot_service.start()

    # Handle Signals
    def signal_handler(sig, frame):
        print("\n👋 Shutting down...")
        bot_service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n🟢 BJJ Trader Pro (Clean Arch) Starting on port 8888...")
    socketio.run(app, host='0.0.0.0', port=8888, debug=config.DEBUG_MODE)
