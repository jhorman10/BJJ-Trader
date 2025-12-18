"""
===========================================
CONFIGURACIÓN DEL BOT DE ALERTAS DE TRADING
===========================================

Este archivo contiene todas las configuraciones ajustables del bot.
Modifica estos valores según tu estrategia de trading.
"""

# ===========================================
# PARES DE DIVISAS A MONITOREAR
# ===========================================
# Formato: "PAR=X" para Forex en Yahoo Finance
# Ejemplos: EURUSD=X, GBPUSD=X, USDJPY=X, etc.
# Principales pares de divisas del mundo (Major Pairs + Minor Pairs)
SYMBOLS = [
    # === MAJOR PAIRS (Los más operados) ===
    "EURUSD=X",   # Euro / Dólar Estadounidense
    "GBPUSD=X",   # Libra Esterlina / Dólar
    "USDJPY=X",   # Dólar / Yen Japonés
    "USDCHF=X",   # Dólar / Franco Suizo
    "AUDUSD=X",   # Dólar Australiano / Dólar
    "USDCAD=X",   # Dólar / Dólar Canadiense
    "NZDUSD=X",   # Dólar Neozelandés / Dólar
    
    # === CROSS PAIRS (Cruces importantes) ===
    "EURGBP=X",   # Euro / Libra
    "EURJPY=X",   # Euro / Yen
    "GBPJPY=X",   # Libra / Yen
    "AUDJPY=X",   # Dólar Australiano / Yen
    "EURAUD=X",   # Euro / Dólar Australiano
    "EURCHF=X",   # Euro / Franco Suizo
    "GBPCHF=X",   # Libra / Franco Suizo
    
    # === EXOTIC PAIRS (Divisas emergentes) ===
    # "USDMXN=X",   # Dólar / Peso Mexicano (descomentar si deseas)
    # "USDBRL=X",   # Dólar / Real Brasileño
    # "USDCOP=X",   # Dólar / Peso Colombiano
]

# ===========================================
# CONFIGURACIÓN DE DATOS
# ===========================================
# Período de datos históricos a descargar
# Opciones: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
DATA_PERIOD = "3mo"

# Intervalo de las velas (timeframe)
# Opciones: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
# Nota: Intervalos menores a 1d solo disponibles para períodos cortos
DATA_INTERVAL = "1h"

# ===========================================
# CONFIGURACIÓN DE INDICADORES TÉCNICOS
# ===========================================

# --- RSI (Relative Strength Index) ---
RSI_PERIOD = 14          # Período del RSI (estándar: 14)
RSI_OVERSOLD = 30        # Nivel de sobreventa (señal de compra)
RSI_OVERBOUGHT = 70      # Nivel de sobrecompra (señal de venta)

# --- MACD (Moving Average Convergence Divergence) ---
MACD_FAST = 12           # Período de la EMA rápida
MACD_SLOW = 26           # Período de la EMA lenta
MACD_SIGNAL = 9          # Período de la línea de señal

# --- Medias Móviles ---
SMA_FAST = 20            # Media móvil simple rápida
SMA_SLOW = 50            # Media móvil simple lenta
EMA_FAST = 12            # Media móvil exponencial rápida
EMA_SLOW = 26            # Media móvil exponencial lenta

# --- ATR (Average True Range) para Stop Loss / Take Profit ---
ATR_PERIOD = 14          # Período del ATR

# ===========================================
# CONFIGURACIÓN DE STOP LOSS Y TAKE PROFIT
# ===========================================
# Múltiplos del ATR para calcular niveles
STOP_LOSS_ATR_MULTIPLIER = 1.5    # SL = Precio actual ± (ATR × este valor)
TAKE_PROFIT_ATR_MULTIPLIER = 2.0  # TP = Precio actual ± (ATR × este valor)

# ===========================================
# CONFIGURACIÓN DE ALERTAS
# ===========================================
# Activar/desactivar tipos de alertas
ALERT_ON_RSI = True              # Alertas basadas en RSI
ALERT_ON_MACD_CROSS = True       # Alertas por cruce de MACD
ALERT_ON_MA_CROSS = True         # Alertas por cruce de medias móviles

# ===========================================
# CONFIGURACIÓN DE EJECUCIÓN
# ===========================================
# Intervalo de verificación en minutos (para modo continuo)
CHECK_INTERVAL_MINUTES = 15

# Mostrar información detallada de depuración
DEBUG_MODE = False

# ===========================================
# CONFIGURACIÓN DE TELEGRAM
# ===========================================
# Las credenciales se cargan desde variables de entorno
# Local: crear archivo .env con las variables
# Render: configurar en el panel de Environment Variables

import os

# Cargar .env para desarrollo local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # En producción no se necesita dotenv

# Token de tu bot de Telegram (obtener de @BotFather)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# Chat ID o Canal para enviar alertas
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Activar/desactivar notificaciones de Telegram
TELEGRAM_ENABLED = os.environ.get("TELEGRAM_ENABLED", "false").lower() == "true"


