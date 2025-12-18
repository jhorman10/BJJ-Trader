import type { Indicators } from "../../domain/models";

interface IndicatorsCardProps {
  data: Indicators | null;
}

export const IndicatorsCard = ({ data }: IndicatorsCardProps) => {
  if (!data)
    return (
      <div className="text-muted fst-italic">Waiting for indicators...</div>
    );

  // Helpers for states
  const getRSIState = (rsi: number) => {
    if (rsi > 70) return { text: "SOBRECOMPRA", color: "text-danger" };
    if (rsi < 30) return { text: "SOBREVENTA", color: "text-success" };
    return { text: "NEUTRO", color: "text-light" };
  };

  const getMACDState = (hist: number) => {
    if (hist > 0) return { text: "ALCISTA", color: "text-success" };
    return { text: "BAJISTA", color: "text-danger" };
  };

  const getTrendState = (trend: string) => {
    if (trend === "UP") return { text: "ALCISTA", color: "text-success" };
    if (trend === "DOWN") return { text: "BAJISTA", color: "text-danger" };
    return { text: "LATERAL", color: "text-warning" };
  };

  const rsiState = getRSIState(data.rsi || 50);
  const macdState = getMACDState(data.macd_hist || 0);
  const trendState = getTrendState(data.trend || "FLAT");

  return (
    <div className="card shadow-lg glass-panel h-100">
      <div className="card-header bg-transparent border-bottom border-secondary border-opacity-25 py-2">
        <h5 className="card-title fw-bold mb-0 text-light">
          <i className="bi bi-activity text-primary me-2"></i>Market Vitals
        </h5>
      </div>
      <div className="card-body">
        <div className="row g-3">
          {/* RSI */}
          <div className="col-md-3">
            <div className="p-3 rounded bg-dark border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
              <small
                className="text-secondary text-uppercase fw-semibold"
                style={{ fontSize: "0.75rem" }}
              >
                RSI (14)
              </small>
              <div className={`fs-3 fw-bold ${rsiState.color}`}>
                {data.rsi ? data.rsi.toFixed(2) : "0.00"}
              </div>
              <small
                className={`${rsiState.color} fw-bold text-uppercase`}
                style={{ fontSize: "0.8rem" }}
              >
                {rsiState.text}
              </small>
            </div>
          </div>

          {/* MACD */}
          <div className="col-md-3">
            <div className="p-3 rounded bg-dark border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
              <small
                className="text-secondary text-uppercase fw-semibold"
                style={{ fontSize: "0.75rem" }}
              >
                MACD
              </small>
              <div
                className={`fs-5 fw-bold ${macdState.color} text-uppercase mb-1`}
              >
                {macdState.text}
              </div>
              <small
                className="text-muted fw-light"
                style={{ fontSize: "0.7rem" }}
              >
                Hist: {data.macd_hist ? data.macd_hist.toFixed(5) : "0.00"}
              </small>
            </div>
          </div>

          {/* Tendencia */}
          <div className="col-md-3">
            <div className="p-3 rounded bg-dark border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
              <small
                className="text-secondary text-uppercase fw-semibold"
                style={{ fontSize: "0.75rem" }}
              >
                Tendencia
              </small>
              <div
                className={`fs-4 fw-bold ${trendState.color} text-uppercase`}
              >
                {trendState.text}
              </div>
              <small className="text-muted" style={{ fontSize: "0.7rem" }}>
                EMA 12/26
              </small>
            </div>
          </div>

          {/* Volatilidad (ATR) */}
          <div className="col-md-3">
            <div className="p-3 rounded bg-dark border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
              <small
                className="text-secondary text-uppercase fw-semibold"
                style={{ fontSize: "0.75rem" }}
              >
                Volatilidad
              </small>
              <div className="fs-4 fw-bold text-info">
                {data.atr ? data.atr.toFixed(5) : "0.00000"}
              </div>
              <small className="text-muted" style={{ fontSize: "0.7rem" }}>
                ATR
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
