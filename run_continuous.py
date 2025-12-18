#!/usr/bin/env python3
"""
===========================================
SCRIPT DE EJECUCIÓN CONTINUA
===========================================

Este script ejecuta el bot de alertas de forma continua,
verificando señales a intervalos regulares definidos en config.py.

Uso:
    python run_continuous.py

Para detener: Presiona Ctrl+C
"""

import time
from datetime import datetime

import schedule

from config import CHECK_INTERVAL_MINUTES
from trading_bot import TradingAlertBot


def job():
    """
    Tarea programada que ejecuta el análisis del bot.
    Se ejecuta cada CHECK_INTERVAL_MINUTES minutos.
    """
    print("\n" + "=" * 60)
    print(f"⏰ Ejecutando análisis programado - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)
    
    # Crear nueva instancia para obtener datos frescos
    # (evita problemas de caché de yfinance)
    bot = TradingAlertBot()
    bot.run_analysis()


def main():
    """
    Función principal que configura y ejecuta el scheduler.
    """
    print("""
╔══════════════════════════════════════════════════════════╗
║         BOT DE ALERTAS - MODO CONTINUO                   ║
╠══════════════════════════════════════════════════════════╣
║  El bot verificará señales cada {0:>3} minutos.            ║
║  Presiona Ctrl+C para detener.                           ║
╚══════════════════════════════════════════════════════════╝
    """.format(CHECK_INTERVAL_MINUTES))
    
    # Ejecutar análisis inicial inmediatamente
    print("🚀 Ejecutando análisis inicial...\n")
    job()
    
    # Programar ejecuciones periódicas
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(job)
    
    print(f"\n⏳ Próximo análisis en {CHECK_INTERVAL_MINUTES} minutos...")
    print("   (Presiona Ctrl+C para detener)\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Verificar cada segundo si hay tareas pendientes
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("👋 Bot detenido por el usuario")
        print("=" * 60)
        print("¡Gracias por usar el Bot de Alertas de Trading!")
        print("Recuerda: Siempre realiza tu propio análisis antes de operar.\n")


if __name__ == "__main__":
    main()
