/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        farm: {
          bg:       '#0a1209',
          bgcard:   '#111c0f',
          bgsec:    '#0f1a0d',
          accent:   '#6abf5e',
          accentlt: '#8dd983',
          accentdk: '#4d9443',
          text:     '#c8e6c0',
          textmuted:'#7aab72',
          border:   '#1e3b1a',
          gold:     '#f5c842',
          blue:     '#5bc0de',
        },
      },
      fontFamily: {
        syne:  ['Syne', 'sans-serif'],
        mono:  ['"Space Mono"', 'monospace'],
      },
      animation: {
        'fade-in':    'fadeIn 0.5s ease-out',
        'slide-up':   'slideUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'spin-slow':  'spin 8s linear infinite',
      },
      keyframes: {
        fadeIn:  { from: { opacity: '0' }, to: { opacity: '1' } },
        slideUp: { from: { opacity: '0', transform: 'translateY(20px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
