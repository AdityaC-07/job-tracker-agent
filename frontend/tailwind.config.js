/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0F4F8',
          100: '#D9E2EC',
          200: '#B3C5D9',
          300: '#8DA3C0',
          400: '#6B87A8',
          500: '#1E3A5F',
          600: '#1A2E4A',
          700: '#162235',
          800: '#121B2A',
          900: '#0D111F',
        },
        slate: {
          50: '#F8FAFC',
          600: '#475569',
          700: '#334155',
          900: '#0F172A',
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
