#!/usr/bin/env python3
"""
===========================================
SERVIDOR WEB PARA DASHBOARD EN TIEMPO REAL
===========================================

Este archivo ejecuta el servidor Flask con WebSockets
para proporcionar una interfaz gráfica en tiempo real.

Uso:
    python dashboard.py
    
Luego abre: http://localhost:5000
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import pandas_ta as ta
import yfinance as yf
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# Importar configuración
from config import (
    SYMBOLS,
    DATA_PERIOD,
    DATA_INTERVAL,
    RSI_PERIOD,
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
    MACD_FAST,
    MACD_SLOW,
    MACD_SIGNAL,
    EMA_FAST,
    EMA_SLOW,
    ATR_PERIOD,
    STOP_LOSS_ATR_MULTIPLIER,
    TAKE_PROFIT_ATR_MULTIPLIER,
    CHECK_INTERVAL_MINUTES,
)

# Importar notificador de Telegram
from telegram_notifier import send_telegram_alert

# ===========================================
# CONFIGURACIÓN DE FLASK Y SOCKETIO
# ===========================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trading-bot-secret-key'

# Configurar SocketIO con eventlet para mejor rendimiento
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# ===========================================
# ESTADO GLOBAL DEL BOT
# ===========================================

class TradingBotState:
    """
    Mantiene el estado global del bot para compartir entre hilos.
    """
    def __init__(self):
        self.data_cache: Dict[str, pd.DataFrame] = {}
        self.last_update: Dict[str, datetime] = {}
        self.previous_signals: Dict[str, Dict] = {}
        self.running = True
        
bot_state = TradingBotState()

# ===========================================
# FUNCIONES DE DATOS
# ===========================================

def get_market_data(symbol: str) -> Optional[pd.DataFrame]:
    """
    Obtiene datos del mercado usando yfinance.
    Incluye caché para evitar demasiadas llamadas a la API.
    """
    try:
        # Verificar caché (actualizar cada minuto)
        now = datetime.now()
        if symbol in bot_state.last_update:
            elapsed = (now - bot_state.last_update[symbol]).total_seconds()
            if elapsed < 60 and symbol in bot_state.data_cache:
                return bot_state.data_cache[symbol]
        
        # Descargar nuevos datos
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=DATA_PERIOD, interval=DATA_INTERVAL)
        
        if df.empty:
            return None
        
        df = df.dropna()
        
        # Guardar en caché
        bot_state.data_cache[symbol] = df
        bot_state.last_update[symbol] = now
        
        return df
        
    except Exception as e:
        print(f"Error obteniendo datos de {symbol}: {e}")
        return None


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula todos los indicadores técnicos.
    """
    df = df.copy()
    
    # RSI
    df['RSI'] = ta.rsi(df['Close'], length=RSI_PERIOD)
    
    # MACD
    macd_result = ta.macd(df['Close'], fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    df['MACD'] = macd_result[f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}']
    df['MACD_Signal'] = macd_result[f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}']
    
    # EMAs
    df['EMA_Fast'] = ta.ema(df['Close'], length=EMA_FAST)
    df['EMA_Slow'] = ta.ema(df['Close'], length=EMA_SLOW)
    
    # ATR
    df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=ATR_PERIOD)
    
    return df


def detect_signals(symbol: str, df: pd.DataFrame) -> List[Dict]:
    """
    Detecta señales de trading basadas en los indicadores.
    Solo emite señales nuevas (no repetidas).
    """
    signals = []
    
    if len(df) < 2:
        return signals
    
    # Valores actuales y anteriores
    current = df.iloc[-1]
    previous = df.iloc[-2]
    
    # Inicializar estado previo si no existe
    if symbol not in bot_state.previous_signals:
        bot_state.previous_signals[symbol] = {
            'rsi_oversold': False,
            'rsi_overbought': False,
            'macd_bullish': None,
            'ema_bullish': None,
        }
    
    prev_state = bot_state.previous_signals[symbol]
    
    # --- Señales RSI ---
    rsi_current = current['RSI']
    rsi_previous = previous['RSI']
    
    if pd.notna(rsi_current) and pd.notna(rsi_previous):
        # Saliendo de sobreventa
        if rsi_previous < RSI_OVERSOLD and rsi_current >= RSI_OVERSOLD:
            if not prev_state['rsi_oversold']:
                signals.append({
                    'type': 'COMPRA',
                    'indicator': 'RSI',
                    'reason': f'RSI saliendo de sobreventa ({rsi_current:.2f})',
                    'strength': 'MODERADA',
                })
                prev_state['rsi_oversold'] = True
        else:
            prev_state['rsi_oversold'] = False
        
        # Saliendo de sobrecompra
        if rsi_previous > RSI_OVERBOUGHT and rsi_current <= RSI_OVERBOUGHT:
            if not prev_state['rsi_overbought']:
                signals.append({
                    'type': 'VENTA',
                    'indicator': 'RSI',
                    'reason': f'RSI saliendo de sobrecompra ({rsi_current:.2f})',
                    'strength': 'MODERADA',
                })
                prev_state['rsi_overbought'] = True
        else:
            prev_state['rsi_overbought'] = False
    
    # --- Señales MACD ---
    macd_current = current['MACD']
    signal_current = current['MACD_Signal']
    macd_previous = previous['MACD']
    signal_previous = previous['MACD_Signal']
    
    if pd.notna(macd_current) and pd.notna(signal_current):
        is_bullish = macd_current > signal_current
        was_bullish = macd_previous > signal_previous if pd.notna(macd_previous) else None
        
        # Detectar cruce
        if was_bullish is not None and is_bullish != was_bullish:
            if is_bullish and prev_state['macd_bullish'] != True:
                signals.append({
                    'type': 'COMPRA',
                    'indicator': 'MACD',
                    'reason': 'Cruce alcista del MACD sobre la línea de señal',
                    'strength': 'FUERTE',
                })
            elif not is_bullish and prev_state['macd_bullish'] != False:
                signals.append({
                    'type': 'VENTA',
                    'indicator': 'MACD',
                    'reason': 'Cruce bajista del MACD bajo la línea de señal',
                    'strength': 'FUERTE',
                })
        
        prev_state['macd_bullish'] = is_bullish
    
    # --- Señales EMA ---
    ema_fast_current = current['EMA_Fast']
    ema_slow_current = current['EMA_Slow']
    ema_fast_previous = previous['EMA_Fast']
    ema_slow_previous = previous['EMA_Slow']
    
    if pd.notna(ema_fast_current) and pd.notna(ema_slow_current):
        is_bullish = ema_fast_current > ema_slow_current
        was_bullish = ema_fast_previous > ema_slow_previous if pd.notna(ema_fast_previous) else None
        
        # Detectar cruce
        if was_bullish is not None and is_bullish != was_bullish:
            if is_bullish and prev_state['ema_bullish'] != True:
                signals.append({
                    'type': 'COMPRA',
                    'indicator': 'EMA Cross',
                    'reason': f'EMA({EMA_FAST}) cruza por encima de EMA({EMA_SLOW})',
                    'strength': 'FUERTE',
                })
            elif not is_bullish and prev_state['ema_bullish'] != False:
                signals.append({
                    'type': 'VENTA',
                    'indicator': 'EMA Cross',
                    'reason': f'EMA({EMA_FAST}) cruza por debajo de EMA({EMA_SLOW})',
                    'strength': 'FUERTE',
                })
        
        prev_state['ema_bullish'] = is_bullish
    
    return signals


def calculate_sl_tp(df: pd.DataFrame, signal_type: str) -> tuple:
    """
    Calcula Stop Loss y Take Profit basados en ATR.
    """
    current_price = df['Close'].iloc[-1]
    atr = df['ATR'].iloc[-1]
    
    if pd.isna(atr):
        atr = current_price * 0.001
    
    sl_distance = atr * STOP_LOSS_ATR_MULTIPLIER
    tp_distance = atr * TAKE_PROFIT_ATR_MULTIPLIER
    
    if signal_type == 'COMPRA':
        stop_loss = current_price - sl_distance
        take_profit = current_price + tp_distance
    else:
        stop_loss = current_price + sl_distance
        take_profit = current_price - tp_distance
    
    return current_price, stop_loss, take_profit


# ===========================================
# RUTAS DE FLASK
# ===========================================

@app.route('/')
def index():
    """
    Página principal del dashboard.
    """
    return render_template('dashboard.html')


# ===========================================
# EVENTOS DE WEBSOCKET
# ===========================================

@socketio.on('connect')
def handle_connect():
    """
    Maneja nueva conexión de cliente.
    """
    print(f"🔗 Cliente conectado: {datetime.now()}")
    # Enviar datos iniciales del primer símbolo
    emit_chart_data(SYMBOLS[0])


@socketio.on('disconnect')
def handle_disconnect():
    """
    Maneja desconexión de cliente.
    """
    print(f"❌ Cliente desconectado: {datetime.now()}")


@socketio.on('request_data')
def handle_request_data(data):
    """
    Maneja solicitud de datos de un símbolo específico.
    """
    symbol = data.get('symbol', SYMBOLS[0])
    emit_chart_data(symbol)


def emit_chart_data(symbol: str):
    """
    Envía datos del gráfico e indicadores al cliente.
    """
    df = get_market_data(symbol)
    if df is None or len(df) < 50:
        return
    
    df = calculate_indicators(df)
    
    # Preparar datos para el gráfico
    candles = []
    for idx, row in df.iterrows():
        candles.append({
            'time': int(idx.timestamp()),
            'open': float(row['Open']),
            'high': float(row['High']),
            'low': float(row['Low']),
            'close': float(row['Close']),
        })
    
    # Preparar EMAs
    ema12 = [float(v) if pd.notna(v) else None for v in df['EMA_Fast'].values]
    ema26 = [float(v) if pd.notna(v) else None for v in df['EMA_Slow'].values]
    
    # Enviar datos del gráfico
    emit('chart_data', {
        'symbol': symbol,
        'candles': candles,
        'ema12': ema12,
        'ema26': ema26,
    })
    
    # Enviar indicadores actuales
    current = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else current
    
    price = float(current['Close'])
    prev_price = float(previous['Close'])
    change = price - prev_price
    change_percent = (change / prev_price) * 100 if prev_price != 0 else 0
    
    emit('indicators', {
        'symbol': symbol,
        'price': price,
        'change': change,
        'changePercent': change_percent,
        'rsi': float(current['RSI']) if pd.notna(current['RSI']) else 50,
        'macd': float(current['MACD']) if pd.notna(current['MACD']) else 0,
        'macdSignal': float(current['MACD_Signal']) if pd.notna(current['MACD_Signal']) else 0,
        'ema12': float(current['EMA_Fast']) if pd.notna(current['EMA_Fast']) else price,
        'ema26': float(current['EMA_Slow']) if pd.notna(current['EMA_Slow']) else price,
        'atr': float(current['ATR']) if pd.notna(current['ATR']) else 0,
    })


# ===========================================
# HILO DE MONITOREO EN SEGUNDO PLANO
# ===========================================

def background_monitor():
    """
    Hilo que monitorea los mercados y emite alertas en tiempo real.
    """
    print("\n🔄 Iniciando monitoreo en segundo plano...")
    
    while bot_state.running:
        try:
            for symbol in SYMBOLS:
                # Obtener datos frescos
                df = get_market_data(symbol)
                if df is None or len(df) < 50:
                    continue
                
                df = calculate_indicators(df)
                
                # Detectar señales
                signals = detect_signals(symbol, df)
                
                # Emitir alertas
                for signal in signals:
                    price, sl, tp = calculate_sl_tp(df, signal['type'])
                    
                    atr_value = float(df['ATR'].iloc[-1]) if pd.notna(df['ATR'].iloc[-1]) else 0
                    rsi_value = float(df['RSI'].iloc[-1]) if pd.notna(df['RSI'].iloc[-1]) else 50
                    macd_hist = float(df['MACD'].iloc[-1] - df['MACD_Signal'].iloc[-1]) if pd.notna(df['MACD'].iloc[-1]) else 0
                    
                    alert = {
                        'symbol': symbol,
                        'type': signal['type'],
                        'indicator': signal['indicator'],
                        'reason': signal['reason'],
                        'strength': signal['strength'],
                        'price': price,
                        'stopLoss': sl,
                        'takeProfit': tp,
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'atr': atr_value,
                        'rsi': rsi_value,
                        'macd_hist': macd_hist
                    }
                    
                    print(f"\n🚨 ALERTA: {signal['type']} en {symbol}")
                    print(f"   Razón: {signal['reason']}")
                    print(f"   Precio: {price:.5f} | SL: {sl:.5f} | TP: {tp:.5f}")
                    
                    # Enviar notificación a Telegram
                    send_telegram_alert(
                        symbol=symbol,
                        signal_type=signal['type'],
                        indicator=signal['indicator'],
                        reason=signal['reason'],
                        price=price,
                        stop_loss=sl,
                        take_profit=tp,
                        atr=atr_value,
                        strength=signal['strength'],
                        rsi=rsi_value,
                        macd_histogram=macd_hist
                    )
                    
                    # Emitir a todos los clientes conectados
                    socketio.emit('new_alert', alert)
                
                # Emitir actualización de precio
                if len(df) > 0:
                    socketio.emit('price_update', {
                        'symbol': symbol,
                        'price': float(df['Close'].iloc[-1]),
                    })
            
            # Esperar antes de la siguiente verificación
            # Usamos un intervalo más corto para WebSocket (cada 30 segundos)
            time.sleep(30)
            
        except Exception as e:
            print(f"Error en monitoreo: {e}")
            time.sleep(10)


# ===========================================
# PUNTO DE ENTRADA
# ===========================================

def main():
    """
    Función principal que inicia el servidor.
    """
    print("""
╔══════════════════════════════════════════════════════════╗
║       🤖 TRADING ALERT BOT - DASHBOARD EN VIVO           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  Abre tu navegador en:                                   ║
║                                                          ║
║     👉  http://localhost:8888                            ║
║                                                          ║
║  Presiona Ctrl+C para detener el servidor.               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Iniciar hilo de monitoreo
    monitor_thread = threading.Thread(target=background_monitor, daemon=True)
    monitor_thread.start()
    
    try:
        # Iniciar servidor Flask con SocketIO
        socketio.run(app, host='0.0.0.0', port=8888, debug=False)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor detenido.")
        bot_state.running = False


if __name__ == '__main__':
    main()
