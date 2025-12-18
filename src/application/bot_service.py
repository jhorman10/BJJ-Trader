import time
import threading
from typing import List, Callable
from src.domain.interfaces import INotifier
from src.application.services import TradingOrchestrator
from src.infrastructure.config import Config

class SignalBotService:
    def __init__(self, orchestrator: TradingOrchestrator, config: Config):
        self.orchestrator = orchestrator
        self.config = config
        self.running = False
        self._thread = None
        self._on_signal_callbacks: List[Callable] = []
        self._on_price_callbacks: List[Callable] = []
        self._on_indicator_callbacks: List[Callable] = []

    def start(self):
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._run_loop)
        self._thread.daemon = True
        self._thread.start()
        print(f"🚀 Signal Bot Service Started with {len(self.config.SYMBOLS)} symbols")

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join(timeout=2)
        print("🛑 Signal Bot Service Stopped")

    def register_on_signal(self, callback: Callable):
        self._on_signal_callbacks.append(callback)

    def register_on_price(self, callback: Callable):
        self._on_price_callbacks.append(callback)

    def register_on_indicator(self, callback: Callable):
        self._on_indicator_callbacks.append(callback)

    def _run_loop(self):
        while self.running:
            for symbol in self.config.SYMBOLS:
                if not self.running:
                    break
                
                try:
                    # 1. Orchestrate Analysis
                    result = self.orchestrator.analyze_symbol(symbol)

                    # 2. Emit Real-time Events (Application -> Presentation via callbacks)
                    
                    # Signals
                    for signal in result.signals:
                        for cb in self._on_signal_callbacks:
                            cb(signal)
                    
                    # Price Update
                    if result.current_price > 0:
                        for cb in self._on_price_callbacks:
                            cb(symbol, result.current_price)

                    # Indicators
                    if result.indicators:
                        for cb in self._on_indicator_callbacks:
                            cb(symbol, result.indicators, result.current_price)

                except Exception as e:
                    print(f"Error in Bot Service for {symbol}: {e}")
                
                # Small yield for CPU
                time.sleep(0.1)

            # Cycle delay
            time.sleep(10)
