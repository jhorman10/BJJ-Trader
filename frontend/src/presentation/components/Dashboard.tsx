import { useState, useEffect } from "react";
// Clean Arch: Import Use Case Hook
import { useMarketData } from "../../application/usecases/useMarketData";
import { ChartComponent } from "./ChartComponent";
import { IndicatorsCard } from "./IndicatorsCard";
import { SignalAlerts } from "./SignalAlerts";

export const Dashboard = () => {
  // Initialize from localStorage or default
  const [selectedSymbol, setSelectedSymbol] = useState(() => {
    return localStorage.getItem("bjj_selectedSymbol") || "EURUSD=X";
  });

  const [isMuted, setIsMuted] = useState(() => {
    return localStorage.getItem("bjj_isMuted") === "true";
  });

  // Persist Symbol
  useEffect(() => {
    localStorage.setItem("bjj_selectedSymbol", selectedSymbol);
    // Update Document Title
    const cleanSymbol = selectedSymbol.replace("=X", "").replace("=F", "");
    document.title = `BJJ Trader Pro | ${cleanSymbol}`;
  }, [selectedSymbol]);

  // Persist Mute State
  useEffect(() => {
    localStorage.setItem("bjj_isMuted", String(isMuted));
  }, [isMuted]);

  // Top 15 Forex Pairs + Gold/BTC
  const symbols = [
    "AUDJPY=X",
    "AUDUSD=X",
    "BTC-USD",
    "EURAUD=X",
    "EURCHF=X",
    "EURGBP=X",
    "EURJPY=X",
    "EURNZD=X",
    "EURUSD=X",
    "GBPCHF=X",
    "GBPJPY=X",
    "GBPUSD=X",
    "GC=F",
    "NZDUSD=X",
    "USDCAD=X",
    "USDCHF=X",
    "USDJPY=X",
  ];

  // Clean Architecture Hook
  const {
    isConnected,
    chartData,
    signals,
    indicators,
    currentPrice,
    currentCandle,
  } = useMarketData(selectedSymbol);

  // Simple sound effect handler
  useEffect(() => {
    if (!isMuted && signals.length > 0) {
      // Play sound on new signal (checked via length change or timestamp in real app)
      // logic to play only on NEW signal would go here
    }
  }, [signals, isMuted]);

  // Removed separate title effect since it's combined with persistence above

  const toggleMute = () => setIsMuted(!isMuted);

  return (
    <div className="d-flex flex-column app-layout">
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-secondary shadow-sm">
        <div className="container-fluid">
          <a className="navbar-brand d-flex align-items-center gap-2" href="#">
            <i className="bi bi-graph-up-arrow text-primary fs-4"></i>
            <span className="fw-bold text-gradient fs-4">BJJ Trader Pro</span>
          </a>

          <div className="d-flex align-items-center gap-3">
            <span
              className={`badge ${
                isConnected
                  ? "bg-success bg-opacity-25 text-success"
                  : "bg-danger bg-opacity-25 text-danger"
              } border border-${
                isConnected ? "success" : "danger"
              } rounded-pill`}
            >
              {isConnected ? "● LIVE" : "○ OFFLINE"}
            </span>

            <div className="input-group input-group-sm">
              <select
                className="form-select bg-dark text-light border-secondary"
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
              >
                {symbols.map((s) => (
                  <option key={s} value={s}>
                    {s.replace("=X", "").replace("=F", "")}
                  </option>
                ))}
              </select>
            </div>

            <a
              href="https://t.me/+ET239uZ0NGhhOTRh"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-sm btn-outline-primary rounded-circle"
              title="Join Telegram Channel"
            >
              <i className="bi bi-telegram"></i>
            </a>

            <button
              className={`btn btn-sm rounded-circle ${
                isMuted ? "btn-outline-danger" : "btn-outline-success"
              }`}
              onClick={toggleMute}
              title={isMuted ? "Unmute Alerts" : "Mute Alerts"}
            >
              <i
                className={`bi ${
                  isMuted ? "bi-bell-slash-fill" : "bi-bell-fill"
                }`}
              ></i>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container-fluid flex-grow-1 p-3 app-content">
        <div className="row g-3 h-lg-100">
          {/* Left Column: Chart & Indicators (9 cols on large screens) */}
          <div className="col-lg-9 d-flex flex-column h-lg-100 gap-3">
            {/* Price Header */}
            <div className="d-flex align-items-baseline gap-3 flex-shrink-0">
              <h2 className="display-6 fw-bold mb-0 text-light">
                {selectedSymbol.replace("=X", "")}
              </h2>
              <span className="fs-2 font-monospace text-info">
                {currentPrice ? (
                  currentPrice.toFixed(5)
                ) : (
                  <span className="spinner-border spinner-border-sm text-secondary"></span>
                )}
              </span>
            </div>

            {/* Chart Card - FLEX GROW to take available space */}
            <div
              className="card shadow-lg glass-panel flex-grow-1 d-flex flex-column chart-card-container"
              style={{ minHeight: "450px" }}
            >
              <div className="card-body p-0 flex-grow-1 position-relative">
                <ChartComponent
                  data={chartData}
                  symbol={selectedSymbol}
                  updateData={currentCandle}
                />
              </div>
            </div>

            {/* Mobile-only Signals: Show below chart on mobile */}
            <div className="d-lg-none w-100" style={{ height: "400px" }}>
              <SignalAlerts signals={signals} />
            </div>

            {/* Indicators - Fixed height or natural height, but shouldn't overflow main view */}
            <div className="flex-shrink-0">
              <IndicatorsCard data={indicators} />
            </div>
          </div>

          {/* Right Column: Signals (3 cols) - Desktop Only */}
          <div className="col-lg-3 h-lg-100 d-flex flex-column d-none d-lg-flex">
            <div
              className="flex-grow-1 overflow-auto pe-1 signals-container"
              style={{ minHeight: "300px" }}
            >
              <SignalAlerts signals={signals} />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
