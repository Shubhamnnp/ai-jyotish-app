import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        vedic: {
          gold: "#D97706",
          amber: "#F59E0B",
          saffron: "#EA580C",
          indigo: "#1E3A8A",
          green: "#15803D",
          red: "#DC2626",
          parchment: "#FAF8F5",
          cosmos: "#0B0F19",
          cardDark: "#111827",
          borderDark: "rgba(255, 255, 255, 0.1)",
        },
      },
      fontFamily: {
        devanagari: ["'Devanagari Sangam MN'", "'Noto Serif Devanagari'", "serif"],
        sans: ["system-ui", "-apple-system", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
