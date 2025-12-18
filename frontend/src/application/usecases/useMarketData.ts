import { useState, useEffect, useRef } from "react";
import { SocketService } from "../../infrastructure/adapters/SocketService";
import type { Signal, Indicators, ChartDataPoint } from "../../domain/models";

// In a stricter DI setup, we'd inject the service via Context.
// For simplicity, we use the singleton directly here, but via the Port interface logically.
const streamService = SocketService.getInstance();

export const useMarketData = (symbol: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(0);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [indicators, setIndicators] = useState<Indicators | null>(null);

  // For local candle updates before full redraw
  const lastCandleRef = useRef<ChartDataPoint | null>(null);
  const [currentCandle, setCurrentCandle] = useState<ChartDataPoint | null>(
    null
  );

  useEffect(() => {
    streamService.connect(symbol);

    // Subscribe to connection events
    streamService.onConnect(() => {
      setIsConnected(true);
    });

    streamService.onDisconnect(() => {
      setIsConnected(false);
    });

    // Subscribe
    streamService.onPriceUpdate((price) => {
      setCurrentPrice(price);

      // Local candle update logic
      if (lastCandleRef.current) {
        const updated = { ...lastCandleRef.current };
        updated.close = price;
        if (price > updated.high) updated.high = price;
        if (price < updated.low) updated.low = price;
        lastCandleRef.current = updated;
        setCurrentCandle(updated);
      }
    });

    streamService.onChartData((data) => {
      setChartData(data);
      if (data.length > 0) {
        const last = data[data.length - 1];
        lastCandleRef.current = { ...last };
        setCurrentCandle(lastCandleRef.current);
      }
    });

    streamService.onNewAlert((signal) => {
      setSignals((prev) => [signal, ...prev].slice(0, 50));
      // Sound logic could be moved to a NotificationService
      try {
        const audio = new Audio("/alert.mp3");
        audio.play().catch((e) => console.error(e));
      } catch (e) {
        console.error(e);
      }
    });

    streamService.onIndicators((data) => {
      setIndicators(data);
    });

    return () => {
      // We don't necessarily disconnect the global socket if other components use it,
      // but we should probably clean up specific listeners or just leave them if they are overwritten.
      // Our SocketService implementation blindly adds listeners.
      // Ideally it should return an unsubscribe function.
      // For this refactor, we accept that listeners might pile up or we need to refine SocketService.
      // Let's rely on SocketService.removeListeners being called if we implemented it,
      // but since it removes ALL, that's risky if multiple components used it.
      // Dashboard is the main user, so it's fine.
      streamService.removeListeners();
    };
  }, [symbol]);

  return {
    isConnected,
    chartData,
    currentPrice,
    signals,
    indicators,
    currentCandle,
  };
};
