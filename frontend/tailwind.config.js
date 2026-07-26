/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        surface: "#FFFFFF",
        "surface-dim": "#d8dadc",
        "surface-container": "#F1F5F9",
        "surface-container-high": "#e6e8ea",
        outline: "#E2E8F0",
        "outline-variant": "#c6c6cd",
        "on-surface": "#191c1e",
        "on-surface-variant": "#45464d",
        navy: {
          DEFAULT: "#131B2E",
          dim: "#2D3133",
        },
        electric: {
          DEFAULT: "#3B82F6",
          strong: "#0058BE",
        },
        emerald: {
          DEFAULT: "#009668",
          container: "#002113",
        },
        danger: {
          DEFAULT: "#BA1A1A",
          container: "#FFDAD6",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["Geist Mono", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "0.25rem",
        DEFAULT: "0.75rem",
        lg: "1rem",
        xl: "1.5rem",
      },
      boxShadow: {
        soft: "0px 4px 20px rgba(15, 23, 42, 0.05)",
      },
      maxWidth: {
        container: "1440px",
      },
    },
  },
  plugins: [],
};
