#!/usr/bin/env python3
"""
===========================================
BOT DE ALERTAS DE TRADING PARA FOREX
===========================================

Un bot de alertas para operaciones en Forex y opciones binarias.
Utiliza indicadores técnicos (RSI, MACD, Medias Móviles) y 
genera alertas cuando se cumplen condiciones de entrada.

Autor: Trading Bot
Versión: 1.0.0
Licencia: MIT

DISCLAIMER: Este bot es solo para fines educativos.
El trading conlleva riesgos significativos. Nunca inviertas
dinero que no puedas permitirte perder.
"""

import warnings
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import pandas_ta as ta
import yfinance as yf

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
    SMA_FAST,
    SMA_SLOW,
    EMA_FAST,
    EMA_SLOW,
    ATR_PERIOD,
    STOP_LOSS_ATR_MULTIPLIER,
    TAKE_PROFIT_ATR_MULTIPLIER,
    ALERT_ON_RSI,
    ALERT_ON_MACD_CROSS,
    ALERT_ON_MA_CROSS,
    DEBUG_MODE,
)

# Suprimir warnings de yfinance para una salida más limpia
warnings.filterwarnings("ignore", category=FutureWarning)


# ===========================================
# CLASE PRINCIPAL DEL BOT
# ===========================================

class TradingAlertBot:
    """
    Bot de alertas de trading que analiza pares de divisas
    y genera señales basadas en indicadores técnicos.
    """
    
    def __init__(self):
        """
        Inicializa el bot con la configuración cargada.
        """
        self.symbols = SYMBOLS
        self.alerts_generated = []
        
        print("=" * 60)
        print("🤖 BOT DE ALERTAS DE TRADING INICIADO")
        print("=" * 60)
        print(f"📊 Pares a monitorear: {', '.join(self.symbols)}")
        print(f"⏱️  Intervalo: {DATA_INTERVAL}")
        print(f"📅 Período de datos: {DATA_PERIOD}")
        print("=" * 60)
        print()
    
    # -------------------------------------------
    # OBTENCIÓN DE DATOS
    # -------------------------------------------
    
    def get_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Obtiene datos históricos del mercado usando yfinance.
        
        Args:
            symbol: Símbolo del par de divisas (ej: "EURUSD=X")
            
        Returns:
            DataFrame con datos OHLCV o None si hay error
        """
        try:
            if DEBUG_MODE:
                print(f"📥 Descargando datos para {symbol}...")
            
            # Descargar datos usando yfinance
            # yfinance es gratuito y no requiere API key
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=DATA_PERIOD, interval=DATA_INTERVAL)
            
            if df.empty:
                print(f"⚠️  No se encontraron datos para {symbol}")
                return None
            
            # Limpiar y preparar datos
            df = df.dropna()
            
            if DEBUG_MODE:
                print(f"✅ {len(df)} velas descargadas para {symbol}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error obteniendo datos de {symbol}: {str(e)}")
            return None
    
    # -------------------------------------------
    # CÁLCULO DE INDICADORES TÉCNICOS
    # -------------------------------------------
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores técnicos necesarios.
        
        Indicadores calculados:
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - SMA (Simple Moving Average)
        - EMA (Exponential Moving Average)
        - ATR (Average True Range)
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            DataFrame con indicadores añadidos
        """
        # Hacer una copia para no modificar el original
        df = df.copy()
        
        # --- RSI (Relative Strength Index) ---
        # El RSI mide la fuerza del movimiento del precio
        # Valores < 30 = sobreventa (posible compra)
        # Valores > 70 = sobrecompra (posible venta)
        df['RSI'] = ta.rsi(df['Close'], length=RSI_PERIOD)
        
        # --- MACD (Moving Average Convergence Divergence) ---
        # MACD muestra la relación entre dos medias móviles
        # Cruce alcista: MACD cruza por encima de Signal = Compra
        # Cruce bajista: MACD cruza por debajo de Signal = Venta
        macd_result = ta.macd(
            df['Close'], 
            fast=MACD_FAST, 
            slow=MACD_SLOW, 
            signal=MACD_SIGNAL
        )
        df['MACD'] = macd_result[f'MACD_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}']
        df['MACD_Signal'] = macd_result[f'MACDs_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}']
        df['MACD_Histogram'] = macd_result[f'MACDh_{MACD_FAST}_{MACD_SLOW}_{MACD_SIGNAL}']
        
        # --- Medias Móviles Simples (SMA) ---
        # Cruce alcista: SMA rápida cruza por encima de SMA lenta = Compra
        # Cruce bajista: SMA rápida cruza por debajo de SMA lenta = Venta
        df['SMA_Fast'] = ta.sma(df['Close'], length=SMA_FAST)
        df['SMA_Slow'] = ta.sma(df['Close'], length=SMA_SLOW)
        
        # --- Medias Móviles Exponenciales (EMA) ---
        # Similar a SMA pero da más peso a precios recientes
        df['EMA_Fast'] = ta.ema(df['Close'], length=EMA_FAST)
        df['EMA_Slow'] = ta.ema(df['Close'], length=EMA_SLOW)
        
        # --- ATR (Average True Range) ---
        # Mide la volatilidad del mercado
        # Se usa para calcular Stop Loss y Take Profit dinámicos
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], length=ATR_PERIOD)
        
        return df
    
    # -------------------------------------------
    # DETECCIÓN DE SEÑALES
    # -------------------------------------------
    
    def detect_rsi_signals(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta señales basadas en el RSI.
        
        Señales:
        - COMPRA: RSI cruza hacia arriba desde sobreventa (< 30)
        - VENTA: RSI cruza hacia abajo desde sobrecompra (> 70)
        
        Args:
            df: DataFrame con indicadores calculados
            
        Returns:
            Diccionario con señal o None si no hay señal
        """
        if not ALERT_ON_RSI or len(df) < 2:
            return None
        
        # Obtener valores actuales y anteriores del RSI
        rsi_current = df['RSI'].iloc[-1]
        rsi_previous = df['RSI'].iloc[-2]
        
        # Señal de COMPRA: RSI sale de sobreventa
        # El RSI estaba por debajo del nivel de sobreventa y ahora está por encima
        if rsi_previous < RSI_OVERSOLD and rsi_current >= RSI_OVERSOLD:
            return {
                'type': 'COMPRA',
                'indicator': 'RSI',
                'reason': f'RSI saliendo de sobreventa ({rsi_current:.2f})',
                'strength': 'MODERADA'
            }
        
        # Señal de VENTA: RSI sale de sobrecompra
        # El RSI estaba por encima del nivel de sobrecompra y ahora está por debajo
        if rsi_previous > RSI_OVERBOUGHT and rsi_current <= RSI_OVERBOUGHT:
            return {
                'type': 'VENTA',
                'indicator': 'RSI',
                'reason': f'RSI saliendo de sobrecompra ({rsi_current:.2f})',
                'strength': 'MODERADA'
            }
        
        return None
    
    def detect_macd_signals(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta señales basadas en cruces del MACD.
        
        Señales:
        - COMPRA: MACD cruza por encima de la línea de señal
        - VENTA: MACD cruza por debajo de la línea de señal
        
        Args:
            df: DataFrame con indicadores calculados
            
        Returns:
            Diccionario con señal o None si no hay señal
        """
        if not ALERT_ON_MACD_CROSS or len(df) < 2:
            return None
        
        # Obtener valores actuales y anteriores
        macd_curr = df['MACD'].iloc[-1]
        signal_curr = df['MACD_Signal'].iloc[-1]
        macd_prev = df['MACD'].iloc[-2]
        signal_prev = df['MACD_Signal'].iloc[-2]
        
        # Verificar si hay NaN (datos insuficientes)
        if pd.isna(macd_curr) or pd.isna(signal_curr):
            return None
        
        # Cruce alcista: MACD cruza por encima de Signal
        if macd_prev <= signal_prev and macd_curr > signal_curr:
            return {
                'type': 'COMPRA',
                'indicator': 'MACD',
                'reason': 'Cruce alcista del MACD sobre la línea de señal',
                'strength': 'FUERTE'
            }
        
        # Cruce bajista: MACD cruza por debajo de Signal
        if macd_prev >= signal_prev and macd_curr < signal_curr:
            return {
                'type': 'VENTA',
                'indicator': 'MACD',
                'reason': 'Cruce bajista del MACD bajo la línea de señal',
                'strength': 'FUERTE'
            }
        
        return None
    
    def detect_ma_signals(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detecta señales basadas en cruces de medias móviles.
        
        Señales:
        - COMPRA: EMA rápida cruza por encima de EMA lenta
        - VENTA: EMA rápida cruza por debajo de EMA lenta
        
        Args:
            df: DataFrame con indicadores calculados
            
        Returns:
            Diccionario con señal o None si no hay señal
        """
        if not ALERT_ON_MA_CROSS or len(df) < 2:
            return None
        
        # Usamos EMA por ser más reactiva que SMA
        ema_fast_curr = df['EMA_Fast'].iloc[-1]
        ema_slow_curr = df['EMA_Slow'].iloc[-1]
        ema_fast_prev = df['EMA_Fast'].iloc[-2]
        ema_slow_prev = df['EMA_Slow'].iloc[-2]
        
        # Verificar si hay NaN
        if pd.isna(ema_fast_curr) or pd.isna(ema_slow_curr):
            return None
        
        # Cruce alcista (Golden Cross): EMA rápida cruza por encima de EMA lenta
        if ema_fast_prev <= ema_slow_prev and ema_fast_curr > ema_slow_curr:
            return {
                'type': 'COMPRA',
                'indicator': 'EMA Cross',
                'reason': f'EMA({EMA_FAST}) cruza por encima de EMA({EMA_SLOW})',
                'strength': 'FUERTE'
            }
        
        # Cruce bajista (Death Cross): EMA rápida cruza por debajo de EMA lenta
        if ema_fast_prev >= ema_slow_prev and ema_fast_curr < ema_slow_curr:
            return {
                'type': 'VENTA',
                'indicator': 'EMA Cross',
                'reason': f'EMA({EMA_FAST}) cruza por debajo de EMA({EMA_SLOW})',
                'strength': 'FUERTE'
            }
        
        return None
    
    # -------------------------------------------
    # CÁLCULO DE STOP LOSS Y TAKE PROFIT
    # -------------------------------------------
    
    def calculate_sl_tp(
        self, 
        df: pd.DataFrame, 
        signal_type: str
    ) -> Tuple[float, float, float]:
        """
        Calcula los niveles de Stop Loss y Take Profit basados en ATR.
        
        El ATR (Average True Range) mide la volatilidad del mercado.
        Usar múltiplos del ATR nos da niveles de SL/TP adaptativos
        que se ajustan a la volatilidad actual del mercado.
        
        Args:
            df: DataFrame con indicadores (debe incluir ATR)
            signal_type: 'COMPRA' o 'VENTA'
            
        Returns:
            Tupla (precio_actual, stop_loss, take_profit)
        """
        # Obtener precio actual y ATR
        current_price = df['Close'].iloc[-1]
        atr = df['ATR'].iloc[-1]
        
        # Si ATR es NaN, usar un valor por defecto basado en el precio
        if pd.isna(atr):
            atr = current_price * 0.001  # 0.1% del precio
        
        # Calcular distancias basadas en múltiplos del ATR
        sl_distance = atr * STOP_LOSS_ATR_MULTIPLIER
        tp_distance = atr * TAKE_PROFIT_ATR_MULTIPLIER
        
        if signal_type == 'COMPRA':
            # Para compra: SL por debajo, TP por encima
            stop_loss = current_price - sl_distance
            take_profit = current_price + tp_distance
        else:
            # Para venta: SL por encima, TP por debajo
            stop_loss = current_price + sl_distance
            take_profit = current_price - tp_distance
        
        return current_price, stop_loss, take_profit
    
    # -------------------------------------------
    # GENERACIÓN DE ALERTAS
    # -------------------------------------------
    
    def generate_alert(
        self, 
        symbol: str, 
        signal: Dict, 
        price: float, 
        stop_loss: float, 
        take_profit: float,
        atr: float
    ) -> str:
        """
        Genera una alerta formateada en texto.
        
        Args:
            symbol: Símbolo del par de divisas
            signal: Diccionario con información de la señal
            price: Precio actual
            stop_loss: Nivel de Stop Loss sugerido
            take_profit: Nivel de Take Profit sugerido
            atr: Valor actual del ATR
            
        Returns:
            String con la alerta formateada
        """
        # Determinar emoji según el tipo de operación
        emoji = "🟢" if signal['type'] == 'COMPRA' else "🔴"
        
        # Calcular ratio riesgo/beneficio
        risk = abs(price - stop_loss)
        reward = abs(take_profit - price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        # Construir el mensaje de alerta
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        alert = f"""
{'=' * 60}
{emoji} ALERTA DE {signal['type']} - {symbol}
{'=' * 60}
📅 Fecha/Hora: {timestamp}
📊 Indicador: {signal['indicator']}
💡 Razón: {signal['reason']}
⚡ Fuerza de la señal: {signal['strength']}

💰 NIVELES DE PRECIO:
   ├─ Precio Actual:  {price:.5f}
   ├─ Stop Loss:      {stop_loss:.5f} ({STOP_LOSS_ATR_MULTIPLIER}x ATR)
   └─ Take Profit:    {take_profit:.5f} ({TAKE_PROFIT_ATR_MULTIPLIER}x ATR)

📈 MÉTRICAS:
   ├─ ATR actual:     {atr:.5f}
   └─ Ratio R/R:      1:{rr_ratio:.2f}

⚠️  DISCLAIMER: Esta es solo una sugerencia educativa.
    Siempre realiza tu propio análisis antes de operar.
{'=' * 60}
"""
        return alert
    
    # -------------------------------------------
    # ANÁLISIS PRINCIPAL
    # -------------------------------------------
    
    def analyze_symbol(self, symbol: str) -> List[str]:
        """
        Analiza un símbolo específico y genera alertas si hay señales.
        
        Args:
            symbol: Símbolo del par de divisas
            
        Returns:
            Lista de alertas generadas
        """
        alerts = []
        
        # Paso 1: Obtener datos del mercado
        df = self.get_market_data(symbol)
        if df is None or len(df) < SMA_SLOW:  # Necesitamos suficientes datos
            return alerts
        
        # Paso 2: Calcular indicadores técnicos
        df = self.calculate_indicators(df)
        
        # Paso 3: Detectar señales de cada indicador
        signals = []
        
        rsi_signal = self.detect_rsi_signals(df)
        if rsi_signal:
            signals.append(rsi_signal)
        
        macd_signal = self.detect_macd_signals(df)
        if macd_signal:
            signals.append(macd_signal)
        
        ma_signal = self.detect_ma_signals(df)
        if ma_signal:
            signals.append(ma_signal)
        
        # Paso 4: Generar alertas para cada señal detectada
        for signal in signals:
            price, sl, tp = self.calculate_sl_tp(df, signal['type'])
            atr = df['ATR'].iloc[-1]
            
            alert = self.generate_alert(symbol, signal, price, sl, tp, atr)
            alerts.append(alert)
            print(alert)
        
        return alerts
    
    def run_analysis(self) -> List[str]:
        """
        Ejecuta el análisis completo para todos los símbolos configurados.
        
        Returns:
            Lista de todas las alertas generadas
        """
        print(f"\n🔍 Iniciando análisis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        all_alerts = []
        
        for symbol in self.symbols:
            print(f"\n📈 Analizando {symbol}...")
            alerts = self.analyze_symbol(symbol)
            all_alerts.extend(alerts)
        
        if not all_alerts:
            print("\n✨ No se detectaron señales en este momento.")
            print("   El bot continuará monitoreando...\n")
        else:
            print(f"\n📣 Se generaron {len(all_alerts)} alerta(s) en total.\n")
        
        self.alerts_generated = all_alerts
        return all_alerts
    
    def show_current_status(self):
        """
        Muestra el estado actual de los indicadores para todos los símbolos.
        Útil para debugging y monitoreo manual.
        """
        print("\n" + "=" * 60)
        print("📊 ESTADO ACTUAL DE LOS INDICADORES")
        print("=" * 60)
        
        for symbol in self.symbols:
            df = self.get_market_data(symbol)
            if df is None:
                continue
            
            df = self.calculate_indicators(df)
            
            # Obtener últimos valores
            price = df['Close'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            macd = df['MACD'].iloc[-1]
            macd_signal = df['MACD_Signal'].iloc[-1]
            ema_fast = df['EMA_Fast'].iloc[-1]
            ema_slow = df['EMA_Slow'].iloc[-1]
            atr = df['ATR'].iloc[-1]
            
            # Determinar tendencia de medias móviles
            trend = "↗️ ALCISTA" if ema_fast > ema_slow else "↘️ BAJISTA"
            
            # Determinar estado del RSI
            if rsi < RSI_OVERSOLD:
                rsi_status = "🔵 Sobreventa"
            elif rsi > RSI_OVERBOUGHT:
                rsi_status = "🔴 Sobrecompra"
            else:
                rsi_status = "⚪ Neutral"
            
            print(f"""
┌─ {symbol}
│  Precio: {price:.5f}
│  
│  RSI({RSI_PERIOD}): {rsi:.2f} {rsi_status}
│  MACD: {macd:.6f} | Signal: {macd_signal:.6f}
│  EMA({EMA_FAST}): {ema_fast:.5f} | EMA({EMA_SLOW}): {ema_slow:.5f}
│  
│  Tendencia: {trend}
│  ATR({ATR_PERIOD}): {atr:.5f}
└─────────────────────────────────────────""")


# ===========================================
# PUNTO DE ENTRADA PRINCIPAL
# ===========================================

def main():
    """
    Función principal que ejecuta el bot de alertas.
    """
    try:
        # Crear instancia del bot
        bot = TradingAlertBot()
        
        # Mostrar estado actual de indicadores
        bot.show_current_status()
        
        # Ejecutar análisis para detectar señales
        bot.run_analysis()
        
        print("\n" + "=" * 60)
        print("✅ Análisis completado")
        print("=" * 60)
        print("\nPara ejecución continua, usa: python run_continuous.py")
        print("Para más opciones, edita el archivo config.py")
        
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido por el usuario.")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        raise


if __name__ == "__main__":
    main()
