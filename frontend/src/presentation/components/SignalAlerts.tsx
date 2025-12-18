import { memo } from "react";
import type { Signal } from "../../domain/models";

interface SignalAlertsProps {
  signals: Signal[];
}

export const SignalAlerts = memo(({ signals }: SignalAlertsProps) => {
  return (
    <div className="card shadow-lg glass-panel h-100 d-flex flex-column">
      <div className="card-header bg-transparent border-bottom border-secondary border-opacity-25 py-3">
        <h5 className="card-title fw-bold mb-0 text-light d-flex align-items-center gap-2">
          <i className="bi bi-exclamation-triangle-fill text-warning"></i> Live
          Signals
        </h5>
      </div>

      <div
        className="card-body p-0 d-flex flex-column"
        style={{ overflow: "hidden" }}
      >
        <div
          className="flex-grow-1 overflow-auto p-3"
          style={{ scrollbarWidth: "thin" }}
        >
          {signals.length === 0 ? (
            <div className="d-flex flex-column align-items-center justify-content-center h-100 text-light">
              <i className="bi bi-Reception-0 fs-1 mb-2"></i>
              <p className="fw-bold text-light fst-italic">
                Waiting for signals...
              </p>
            </div>
          ) : (
            <div className="d-flex flex-column gap-3">
              {signals.map((signal, idx) => {
                const typeUpper = String(signal.type).toUpperCase().trim();
                const isBuy = typeUpper === "BUY" || typeUpper === "COMPRA";
                const rr =
                  signal.price && signal.stopLoss && signal.takeProfit
                    ? Math.abs(
                        (signal.takeProfit - signal.price) /
                          (signal.price - signal.stopLoss)
                      ).toFixed(2)
                    : "N/A";
                const borderColor = isBuy ? "border-success" : "border-danger";
                const circleIcon = isBuy ? "🟢" : "🔴";

                // Safe Date Parsing
                let timeString = "Just Now";
                try {
                  const date = new Date(signal.time);
                  if (!isNaN(date.getTime())) {
                    timeString = date.toLocaleTimeString();
                  } else {
                    // Fallback if ISO format is slightly off (e.g. space instead of T)
                    timeString =
                      String(signal.time).split(" ")[1] || String(signal.time);
                  }
                } catch {
                  timeString = String(signal.time);
                }

                return (
                  <div
                    key={`${signal.time}-${idx}`}
                    className={`card bg-dark border ${borderColor} shadow-sm`}
                    style={{ borderLeftWidth: "5px" }}
                  >
                    <div
                      className="card-body p-3 text-light"
                      style={{ fontFamily: "Inter, sans-serif" }}
                    >
                      {/* Header */}
                      <div className="d-flex align-items-center gap-2 mb-3 border-bottom border-secondary border-opacity-25 pb-2">
                        <span className="fs-5">{circleIcon}</span>
                        <h6 className="fw-bold mb-0 text-white">
                          SEÑAL DE {isBuy ? "COMPRA" : "VENTA"} -{" "}
                          {signal.symbol.replace("=X", "").replace("=F", "")}
                        </h6>
                      </div>

                      {/* Block 1: Info */}
                      <div className="mb-3">
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <span>⏱️</span>
                          <span className="fw-bold text-light">Hora:</span>
                          <span className="fw-bold text-light">
                            {timeString}
                          </span>
                        </div>
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <span>📊</span>
                          <span className="fw-bold text-light">Indicador:</span>
                          <span className="fw-bold text-light">
                            {signal.indicator}
                          </span>
                        </div>
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <span>💡</span>
                          <span className="fw-bold text-light">Razón:</span>
                          <span className="fw-bold text-light">
                            {signal.reason}
                          </span>
                        </div>
                        <div className="d-flex align-items-center gap-2">
                          <span>⚡</span>
                          <span className="fw-bold text-light">Fuerza:</span>
                          <span className="fw-bold text-light">FUERTE</span>
                        </div>
                      </div>

                      {/* Block 2: Levels */}
                      <div className="mb-3">
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <span>💰</span>
                          <span className="fw-bold text-light">NIVELES:</span>
                        </div>
                        <div className="ps-3 border-start border-secondary border-opacity-25">
                          <div className="d-flex gap-2">
                            <span className="text-light text-nowrap">
                              • Entrada:
                            </span>
                            <span className="fw-bold font-monospace text-light">
                              {signal.price.toFixed(5)}
                            </span>
                          </div>
                          <div className="d-flex gap-2">
                            <span className="text-light text-nowrap">
                              • SL:
                            </span>
                            <span className="fw-bold font-monospace text-danger">
                              {signal.stopLoss.toFixed(5)}
                            </span>
                          </div>
                          <div className="d-flex gap-2">
                            <span className="text-light text-nowrap">
                              • TP:
                            </span>
                            <span className="fw-bold font-monospace text-success">
                              {signal.takeProfit.toFixed(5)}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Block 3: Context */}
                      <div>
                        <div className="d-flex align-items-center gap-2 mb-1">
                          <span>📈</span>
                          <span className="fw-bold text-light">CONTEXTO:</span>
                        </div>
                        <div className="ps-3 border-start border-secondary border-opacity-25">
                          <div className="d-flex gap-2">
                            <span className="text-light">• ATR:</span>
                            <span className="font-monospace text-light">
                              {signal.atr ? signal.atr.toFixed(5) : "N/A"}
                            </span>
                          </div>
                          <div className="d-flex gap-2">
                            <span className="text-light">• RSI:</span>
                            <span className="font-monospace text-light">
                              {signal.rsi ? signal.rsi.toFixed(1) : "N/A"}
                            </span>
                          </div>
                          <div className="d-flex gap-2">
                            <span className="text-light">• R/R:</span>
                            <span className="font-monospace text-light">
                              1:{rr}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
});
