import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "rgba(148, 163, 184, 0.18)",
        background: "#071013",
        foreground: "#eef6f4",
        muted: "#8aa09c",
        panel: "rgba(10, 24, 28, 0.76)",
        accent: "#2ee6a6",
        gold: "#f7c948",
        coral: "#ff7a59"
      },
      boxShadow: {
        glass: "0 24px 90px rgba(0, 0, 0, 0.42)"
      }
    }
  },
  plugins: [tailwindcssAnimate]
};

export default config;
