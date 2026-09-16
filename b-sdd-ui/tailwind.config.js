/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: '#070B12',
        panel: '#0D1424',
        card: '#162035',
        'border-subtle': '#24324D',
        'border-active': '#F59E0B',
        amber: {
          DEFAULT: '#F59E0B',
        },
        emerald: {
          DEFAULT: '#10B981',
        },
        violet: {
          DEFAULT: '#8B5CF6',
        },
        rose: {
          DEFAULT: '#F43F5E',
        },
        blue: {
          DEFAULT: '#3B82F6',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
