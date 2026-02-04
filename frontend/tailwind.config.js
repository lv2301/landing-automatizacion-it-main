/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#0f172a',
        accent: '#22c55e',
        cardBg: '#1e293b',
        textMain: '#f8fafc',
        textDim: '#94a3b8',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      keyframes: {
        // Typing indicator mejorado
        'typing-dot': {
          '0%, 60%, 100%': { opacity: '0.4', transform: 'translateY(0)' },
          '30%': { opacity: '1', transform: 'translateY(-8px)' },
        },
        // Glow dinámico
        'glow-pulse': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(34, 197, 94, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(34, 197, 94, 0.6)' },
        },
        // Fade in arriba
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        // Float sutil
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        // Shimmer (efecto brillo)
        'shimmer': {
          '0%': { backgroundPosition: '-1000px 0' },
          '100%': { backgroundPosition: '1000px 0' },
        },
        // Pulse mejorado
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        // Rotate suave
        'rotate-slow': {
          'from': { transform: 'rotate(0deg)' },
          'to': { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        'typing-dot': 'typing-dot 1.4s infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'fade-in-up': 'fade-in-up 0.6s ease-out',
        'float': 'float 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
        'rotate-slow': 'rotate-slow 20s linear infinite',
      },
      boxShadow: {
        'glow-accent': '0 0 20px rgba(34, 197, 94, 0.25)',
        'glow-accent-lg': '0 0 40px rgba(34, 197, 94, 0.4)',
        'inner-glow': 'inset 0 0 20px rgba(34, 197, 94, 0.1)',
      },
    },
  },
  plugins: [],
}