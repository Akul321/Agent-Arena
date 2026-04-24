import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        arena: {
          bg: "#05080f",
          panel: "#0b1220",
          panel2: "#111a2e",
          border: "#1f2a44",
          text: "#e6edf7",
          muted: "#8696b5",
          accent: "#3b82f6",
          accent2: "#60a5fa",
          bull: "#22c55e",
          bear: "#ef4444",
          warn: "#f59e0b",
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(59,130,246,0.35), 0 0 24px rgba(59,130,246,0.25)",
      },
    },
  },
  plugins: [],
};

export default config;
