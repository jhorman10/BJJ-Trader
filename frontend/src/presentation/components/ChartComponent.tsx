import { memo } from "react";
import { AdvancedRealTimeChart } from "react-ts-tradingview-widgets";
import type { ChartDataPoint } from "../../domain/models";

interface ChartComponentProps {
  data: ChartDataPoint[]; // Kept for prop compatibility, though unused by widget
  symbol: string;
  updateData?: ChartDataPoint | null; // Kept for prop compatibility
}

export const ChartComponent = memo(({ symbol }: ChartComponentProps) => {
  // Format symbol for TradingView (remove =X, =F suffix)
  const formattedSymbol = symbol.replace("=X", "").replace("=F", "");
  // Default to FX prefix if it's a forex pair, or just send the clean symbol.
  // TradingView widget is smart enough usually. Let's send plain "EURUSD".

  return (
    <div style={{ height: "100%", width: "100%" }}>
      <AdvancedRealTimeChart
        symbol={formattedSymbol}
        theme="dark"
        autosize
        hide_side_toolbar={false}
        allow_symbol_change={false}
        save_image={false}
        details={false}
        hotlist={false}
        calendar={false}
      />
    </div>
  );
});
