import type { Signal, Indicators, ChartDataPoint } from "../../domain/models";

export interface IMarketStream {
  connect(symbol: string): void;
  disconnect(): void;
  onConnect(callback: () => void): void;
  onDisconnect(callback: () => void): void;
  onPriceUpdate(callback: (price: number) => void): void;
  onChartData(callback: (data: ChartDataPoint[]) => void): void;
  onNewAlert(callback: (signal: Signal) => void): void;
  onIndicators(callback: (data: Indicators) => void): void;
  requestData(symbol: string): void;
}
