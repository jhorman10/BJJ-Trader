export type UTCTimestamp = number;

export interface ChartDataPoint {
  time: UTCTimestamp | string;
  open: number;
  high: number;
  low: number;
  close: number;
}

export interface Signal {
  symbol: string;
  type: string;
  indicator: string;
  reason: string;
  strength: string;
  price: number;
  stopLoss: number;
  takeProfit: number;
  time: string;
  expiration?: string | null;
  atr?: number | null;
  rsi?: number | null;
  macd_hist?: number | null;
}

export interface MarketData {
  price: number;
  change: number;
  changePercent: number;
}

export interface Indicators {
  rsi: number;
  macd: number;
  macd_signal: number;
  macd_hist: number;
  adx?: number; // Optional if not always sent
  ema_fast: number;
  ema_slow: number;
  trend?: string;
  atr: number;
  price: number;
  change: number;
  changePercent: number;
}
