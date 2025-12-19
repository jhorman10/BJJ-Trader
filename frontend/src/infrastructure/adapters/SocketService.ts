import { io, Socket } from "socket.io-client";
import type { IMarketStream } from "../../application/ports/IMarketStream";
import type { Signal, Indicators, ChartDataPoint } from "../../domain/models";
import { throttle } from "../utils/throttle";

// Backend URL from environment variable (set in .env or Render dashboard)
// In production: VITE_BACKEND_URL should be set to the backend service URL
// In development: defaults to localhost:8888
const SOCKET_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8888";

// Throttle intervals for performance optimization
const PRICE_UPDATE_THROTTLE_MS = 500; // Max 2 price updates per second
const INDICATORS_THROTTLE_MS = 1000; // Max 1 indicator update per second

export class SocketService implements IMarketStream {
  private socket: Socket | null = null;
  private static instance: SocketService;

  // Store throttled callbacks to maintain references
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private throttledCallbacks: Map<string, (...args: any[]) => void> = new Map();

  // Singleton pattern to share connection
  public static getInstance(): SocketService {
    if (!SocketService.instance) {
      SocketService.instance = new SocketService();
    }
    return SocketService.instance;
  }

  connect(symbol: string): void {
    if (!this.socket) {
      this.socket = io(SOCKET_URL, {
        transports: ["polling", "websocket"],
      });

      this.socket.on("connect", () => {
        console.log("✅ Socket connected");
        this.requestData(symbol);
      });
    } else {
      // If already connected, just request data for new symbol
      if (this.socket.connected) {
        this.requestData(symbol);
      }
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.throttledCallbacks.clear();
  }

  requestData(symbol: string): void {
    if (this.socket) {
      this.socket.emit("request_data", { symbol });
    }
  }

  onConnect(callback: () => void): void {
    if (this.socket?.connected) {
      callback();
    }
    this.socket?.on("connect", () => {
      callback();
    });
  }

  onDisconnect(callback: () => void): void {
    this.socket?.on("disconnect", () => {
      callback();
    });
  }

  onPriceUpdate(callback: (price: number) => void): void {
    // Throttle price updates to reduce re-renders
    const throttledCallback = throttle((data: { price: number }) => {
      callback(data.price);
    }, PRICE_UPDATE_THROTTLE_MS);

    this.throttledCallbacks.set("price_update", throttledCallback);
    this.socket?.on("price_update", throttledCallback);
  }

  onChartData(callback: (data: ChartDataPoint[]) => void): void {
    this.socket?.on("chart_data", (data: ChartDataPoint[]) => {
      // Transform if necessary, or just pass through if matches interface
      callback(data);
    });
  }

  onNewAlert(callback: (signal: Signal) => void): void {
    // Alerts are not throttled - they're already sampled on backend
    this.socket?.on("new_alert", (signal: Signal) => {
      callback(signal);
    });
  }

  onIndicators(callback: (data: Indicators) => void): void {
    // Throttle indicator updates to reduce re-renders
    const throttledCallback = throttle((data: Indicators) => {
      callback(data);
    }, INDICATORS_THROTTLE_MS);

    this.throttledCallbacks.set("indicators", throttledCallback);
    this.socket?.on("indicators", throttledCallback);
  }

  // Cleanup listeners to prevent duplicates if useful
  removeListeners(): void {
    if (this.socket) {
      this.socket.off("connect");
      this.socket.off("disconnect");
      this.socket.off("price_update");
      this.socket.off("chart_data");
      this.socket.off("new_alert");
      this.socket.off("indicators");
    }
    this.throttledCallbacks.clear();
  }
}
