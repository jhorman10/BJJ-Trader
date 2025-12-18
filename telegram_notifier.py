#!/usr/bin/env python3
"""
===========================================
MÓDULO DE NOTIFICACIONES DE TELEGRAM
===========================================

Envía alertas de trading a Telegram usando la API HTTP.
"""

import requests
from datetime import datetime

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TELEGRAM_ENABLED,
)


def enviar_telegram(mensaje: str) -> bool:
    """
    Envía un mensaje a Telegram usando la API HTTP.
    """
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            print(f"❌ Error Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {e}")
        return False


def generar_mensaje_expandido(ticker, direccion, precio, rsi, sl, tp, macd_h):
    """
    Genera mensaje expandido con todos los detalles de la señal.
    """
    # Limpiamos el nombre del ticker para que se vea mejor
    nombre_limpio = ticker.replace('=X', '').replace('-', '/')
    
    # Determinamos el emoji de dirección
    emoji_dir = "🟢 COMPRA (LONG)" if "COMPRA" in direccion else "🔴 VENTA (SHORT)"
    
    # Construcción del mensaje con espacios (f-string)
    mensaje = (
        f"🚀 *NUEVA SEÑAL DETECTADA*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 *INSTRUMENTO*\n"
        f"Activo: {nombre_limpio}\n"
        f"Mercado: Forex / Derivados\n\n"
        f"📢 *OPERACIÓN*\n"
        f"Acción: {emoji_dir}\n"
        f"Precio Actual: `{precio:.5f}`\n\n"
        f"📊 *ANÁLISIS TÉCNICO*\n"
        f"• RSI: {rsi:.2f}\n"
        f"• MACD Hist: {macd_h:.6f}\n"
        f"• Filtro: EMA 20 Superada\n\n"
        f"🛡️ *GESTIÓN DE RIESGO*\n"
        f"🚫 *Stop Loss:* `{sl:.5f}`\n"
        f"🎯 *Take Profit:* `{tp:.5f}`\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⏰ {datetime.now().strftime('%d/%m/%Y | %H:%M:%S')}\n"
        f"⚠️ _Análisis automático basado en indicadores._"
    )
    return mensaje


def send_telegram_alert(
    symbol: str,
    signal_type: str,
    indicator: str,
    reason: str,
    price: float,
    stop_loss: float,
    take_profit: float,
    atr: float,
    strength: str = "MODERADA",
    rsi: float = 50.0,
    macd_histogram: float = 0.0
) -> bool:
    """
    Función principal para enviar alertas desde el dashboard.
    """
    if not TELEGRAM_ENABLED:
        return False
    
    mensaje = generar_mensaje_expandido(
        ticker=symbol,
        direccion=signal_type,
        precio=price,
        rsi=rsi,
        sl=stop_loss,
        tp=take_profit,
        macd_h=macd_histogram
    )
    
    result = enviar_telegram(mensaje)
    
    if result:
        print(f"📱 Alerta enviada a Telegram: {signal_type} {symbol}")
    
    return result


# ===========================================
# PRUEBA DEL MÓDULO
# ===========================================

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 Probando notificaciones de Telegram...")
    print("=" * 50)
    
    if TELEGRAM_ENABLED:
        # Enviar alerta de ejemplo
        print("Enviando alerta de ejemplo...")
        send_telegram_alert(
            symbol="EURUSD=X",
            signal_type="COMPRA",
            indicator="MACD",
            reason="Cruce alcista",
            price=1.08750,
            stop_loss=1.08600,
            take_profit=1.08950,
            atr=0.00100,
            strength="FUERTE",
            rsi=35.5,
            macd_histogram=0.000150
        )
    else:
        print("⚠️ Telegram no está activado en config.py")
