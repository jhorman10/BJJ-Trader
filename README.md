# 🤖 Bot de Alertas de Trading para Forex

Un bot de alertas para operaciones en Forex y opciones binarias con **dashboard en tiempo real** que utiliza indicadores técnicos para generar señales de trading.

## ✨ Características

### 📊 Dashboard en Tiempo Real

- **Gráficos de velas profesionales** (TradingView Lightweight Charts)
- **Actualización automática** via WebSockets
- **Alertas visuales y sonoras** cuando hay señales
- **Indicadores en vivo**: Precio, RSI, MACD, Tendencia, ATR

### 📈 Indicadores Técnicos

- **RSI** (Relative S trength Index) - Detecta sobreventa/sobrecompra
- **MACD** (Moving Average Convergence Divergence) - Detecta cruces
- **Medias Móviles** (EMA/SMA) - Detecta tendencias y cruces

### 💰 Gestión de Riesgo

- Stop Loss basado en múltiplos del ATR
- Take Profit basado en múltiplos del ATR
- Ratio Riesgo/Beneficio calculado automáticamente

### 🆓 Datos Gratuitos

- Utiliza `yfinance` para obtener datos (sin API key requerida)
- Utiliza `pandas-ta` (alternativa gratuita a TA-Lib)

## 📋 Requisitos

- Python 3.8 o superior
- Conexión a Internet

## 🚀 Instalación

```bash
# 1. Ir al directorio del proyecto
cd /Users/jhormanorozco/Documents/Personal-Projects/BJJ-Trader

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Mac/Linux

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 💻 Uso

### 🖥️ Dashboard Web (Recomendado)

```bash
source venv/bin/activate
python dashboard.py
```

Abre tu navegador en: **http://localhost:8888**

![Dashboard Preview](docs/dashboard.png)

### 📟 Modo Consola (Sin interfaz gráfica)

**Análisis único:**

```bash
python trading_bot.py
```

**Modo continuo:**

```bash
python run_continuous.py
```

## ⚙️ Configuración

Edita `config.py` para personalizar:

### Pares de Divisas

```python
SYMBOLS = [
    "EURUSD=X",   # Euro/Dólar
    "GBPUSD=X",   # Libra/Dólar
    "USDJPY=X",   # Dólar/Yen
    "AUDUSD=X",   # Dólar Australiano/Dólar
]
```

### Indicadores

| Parámetro        | Descripción          | Valor por Defecto |
| ---------------- | -------------------- | ----------------- |
| `RSI_PERIOD`     | Período del RSI      | 14                |
| `RSI_OVERSOLD`   | Nivel de sobreventa  | 30                |
| `RSI_OVERBOUGHT` | Nivel de sobrecompra | 70                |
| `MACD_FAST`      | Período EMA rápida   | 12                |
| `MACD_SLOW`      | Período EMA lenta    | 26                |

### Stop Loss y Take Profit

| Parámetro                    | Descripción               | Valor por Defecto |
| ---------------------------- | ------------------------- | ----------------- |
| `STOP_LOSS_ATR_MULTIPLIER`   | Multiplicador ATR para SL | 1.5               |
| `TAKE_PROFIT_ATR_MULTIPLIER` | Multiplicador ATR para TP | 2.0               |

## 📊 Señales de Trading

### Señal de Compra (🟢)

- RSI sale de zona de sobreventa (< 30)
- MACD cruza por encima de la línea de señal
- EMA rápida cruza por encima de EMA lenta

### Señal de Venta (🔴)

- RSI sale de zona de sobrecompra (> 70)
- MACD cruza por debajo de la línea de señal
- EMA rápida cruza por debajo de EMA lenta

## 📁 Estructura del Proyecto

```
BJJ-Trader/
├── dashboard.py          # Servidor web con dashboard en tiempo real
├── trading_bot.py        # Bot de consola (sin interfaz gráfica)
├── run_continuous.py     # Ejecución continua en consola
├── config.py             # Configuración de indicadores y pares
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo
├── templates/
│   └── dashboard.html    # Interfaz web del dashboard
└── venv/                 # Entorno virtual de Python
```

## ⚠️ Disclaimer

**Este bot es solo para fines educativos.**

- El trading de Forex y opciones binarias conlleva riesgos significativos
- Las señales generadas NO son consejos de inversión
- Siempre realiza tu propio análisis antes de operar
- Nunca inviertas dinero que no puedas permitirte perder
- Los resultados pasados no garantizan resultados futuros

## 📄 Licencia

MIT License - Uso libre para fines educativos y personales.
