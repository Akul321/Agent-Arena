"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { TapePoint } from "@/lib/api";

type Props = {
  tape: TapePoint[];
  shock?: number | null;
};

function niceTime(t: number) {
  const d = new Date(t * 1000);
  return d.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function MarketChart({ tape, shock }: Props) {
  const data = tape.map((p) => ({
    t: p.t,
    label: niceTime(p.t),
    price: p.price,
    sentiment: p.sentiment,
    event: p.event,
  }));

  if (data.length === 0) {
    return (
      <div className="h-[360px] grid place-items-center text-arena-muted text-sm">
        Waiting for market data…
      </div>
    );
  }

  const prices = data.map((d) => d.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const pad = Math.max((max - min) * 0.1, max * 0.001);

  return (
    <div className="h-[360px]">
      {shock !== undefined && shock !== null && (
        <div className="px-4 pt-2 pb-1 text-xs text-arena-muted">
          Last move:{" "}
          <span
            className={`font-mono ${
              shock > 0 ? "text-arena-bull" : shock < 0 ? "text-arena-bear" : ""
            }`}
          >
            {shock > 0 ? "+" : ""}
            {shock.toFixed(3)}%
          </span>
        </div>
      )}
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 12, right: 16, left: 0, bottom: 8 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%"  stopColor="#3b82f6" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1f2a44" strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            stroke="#8696b5"
            tick={{ fontSize: 11 }}
            minTickGap={40}
          />
          <YAxis
            stroke="#8696b5"
            domain={[min - pad, max + pad]}
            tick={{ fontSize: 11 }}
            width={72}
            tickFormatter={(v) => v.toFixed(2)}
          />
          <Tooltip
            contentStyle={{
              background: "#0b1220",
              border: "1px solid #1f2a44",
              borderRadius: 8,
              color: "#e6edf7",
              fontSize: 12,
            }}
            labelStyle={{ color: "#8696b5" }}
            formatter={(value: any, name: string) => {
              if (name === "price") return [Number(value).toFixed(2), "Price"];
              return [value, name];
            }}
          />
          {data
            .map((d, i) => (d.event ? i : -1))
            .filter((i) => i >= 0)
            .slice(-8)
            .map((i) => (
              <ReferenceLine
                key={i}
                x={data[i].label}
                stroke="#60a5fa"
                strokeDasharray="2 4"
                strokeOpacity={0.5}
              />
            ))}
          <Area
            type="monotone"
            dataKey="price"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#priceFill)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
