import requests
from src.domain.interfaces import INotifier
from src.domain.entities import Signal

class TelegramAdapter(INotifier):
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_alert(self, signal: Signal) -> bool:
        if not self.token or not self.chat_id:
            return False

        message = self._format_message(signal)
        try:
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(self.base_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False

    def _format_message(self, signal: Signal) -> str:
        emoji = "🟢" if signal.type == 'COMPRA' else "🔴"
        sl_mult = 1.5 # Should ideally come from config, but passed in signal or calculated
        tp_mult = 2.0 
        
        # Calculate Risk/Reward ratio for display
        risk = abs(signal.price - signal.stop_loss)
        reward = abs(signal.take_profit - signal.price)
        rr_ratio = reward / risk if risk > 0 else 0

        # TradingView confirmation section
        tv_section = ""
        if signal.tv_recommendation:
            tv_emoji = "✅" if signal.tv_recommendation in ['STRONG_BUY', 'BUY', 'STRONG_SELL', 'SELL'] else "⚠️"
            tv_section = (
                f"\n<b>📺 TRADINGVIEW:</b>\n"
                f"• Recomendación: {tv_emoji} <b>{signal.tv_recommendation}</b>\n"
                f"• Confianza: {signal.tv_confidence or 'N/A'}\n"
                f"• Señales Compra: {signal.tv_buy_signals or 0}\n"
                f"• Señales Venta: {signal.tv_sell_signals or 0}\n"
            )

        # Construct message using HTML for Telegram
        msg = (
            f"<b>{emoji} SEÑAL DE {signal.type} - {signal.symbol.replace('=X', '')}</b>\n\n"
            f"<b>⏱ Hora:</b> {signal.time}\n"
            f"<b>📊 Indicador:</b> {signal.indicator}\n"
            f"<b>💡 Razón:</b> {signal.reason}\n"
            f"<b>⚡ Fuerza:</b> {signal.strength}\n\n"
            f"<b>💰 NIVELES:</b>\n"
            f"• Entrada: <code>{signal.price:.5f}</code>\n"
            f"• SL: <code>{signal.stop_loss:.5f}</code>\n"
            f"• TP: <code>{signal.take_profit:.5f}</code>\n\n"
            f"<b>📈 CONTEXTO:</b>\n"
            f"• ATR: {signal.atr:.5f}\n"
            f"• RSI: {signal.rsi:.1f}\n"
            f"• R/R: 1:{rr_ratio:.2f}\n"
            f"{tv_section}"
        )
        return msg
