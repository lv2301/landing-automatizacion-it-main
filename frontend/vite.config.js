import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  server: {
    port: 3000,
    open: true,
    // CORS para desarrollo
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  },
  
  build: {
    // Minificación para producción
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remover console.logs en producción
        drop_debugger: true
      }
    },
    
    // Source maps solo en desarrollo
    sourcemap: process.env.NODE_ENV === 'development',
    
    // Optimizaciones
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'framer-motion': ['framer-motion'],
          'lucide': ['lucide-react']
        }
      }
    }
  },
  
  // Variables de entorno
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  
  // Optimizaciones de dependencias
  optimizeDeps: {
    include: ['react', 'react-dom', 'framer-motion', 'lucide-react']
  }
})