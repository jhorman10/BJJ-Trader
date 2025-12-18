import { io, Socket } from "socket.io-client";
import type { IMarketStream } from "../../application/ports/IMarketStream";
import type { Signal, Indicators, ChartDataPoint } from "../../domain/models";

// In production, connect directly to the backend API.
// In development, use localhost.
const SOCKET_URL = import.meta.env.PROD
  ? "https://bjj-trader-api.onrender.com"
  : "http://localhost:8888";

export class SocketService implements IMarketStream {
  private socket: Socket | null = null;
  private static instance: SocketService;

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
    this.socket?.on("price_update", (data: { price: number }) => {
      callback(data.price);
    });
  }

  onChartData(callback: (data: ChartDataPoint[]) => void): void {
    this.socket?.on("chart_data", (data: ChartDataPoint[]) => {
      // Transform if necessary, or just pass through if matches interface
      callback(data);
    });
  }

  onNewAlert(callback: (signal: Signal) => void): void {
    this.socket?.on("new_alert", (signal: Signal) => {
      callback(signal);
    });
  }

  onIndicators(callback: (data: Indicators) => void): void {
    this.socket?.on("indicators", (data: Indicators) => {
      callback(data);
    });
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
  }
}
