import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#172033",
        staff: "#f7f8fb",
        accent: "#2563eb",
      },
    },
  },
  plugins: [],
} satisfies Config;
