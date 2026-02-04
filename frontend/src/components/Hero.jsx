import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Shield, Zap, Monitor } from 'lucide-react';

// Componente de fondo geométrico animado
const GeometricBackground = () => (
  <div className="absolute inset-0 -z-20 overflow-hidden">
    {/* Círculos de fondo animados */}
    <motion.div 
      animate={{ rotate: 360 }}
      transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
      className="absolute top-20 left-10 w-64 h-64 bg-gradient-to-br from-accent/15 via-accent/5 to-transparent blur-[100px] rounded-full"
    />
    <motion.div 
      animate={{ rotate: -360 }}
      transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
      className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-tl from-blue-500/12 via-blue-500/5 to-transparent blur-[120px] rounded-full"
    />
    
    {/* Líneas geométricas SVG sutiles */}
    <svg className="absolute inset-0 w-full h-full opacity-10" preserveAspectRatio="none">
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path d="M 50 0 L 0 0 0 50" fill="none" stroke="currentColor" strokeWidth="0.5" className="text-accent"/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>

    {/* Gradiente radial de fondo */}
    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-darkBg/50" />
  </div>
);

const Hero = () => {
  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center pt-20 px-6 overflow-hidden">
      <GeometricBackground />
      
      <div className="max-w-6xl mx-auto relative z-10">
        <div className="flex flex-col items-center text-center">
          
          {/* Badge mejorado */}
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative group mb-8"
          >
            {/* Glow dinámico */}
            <div className="absolute -inset-1 bg-gradient-to-r from-accent/30 via-accent/10 to-blue-500/20 rounded-full blur-lg opacity-60 group-hover:opacity-100 transition-all duration-500 animate-pulse-soft"></div>
            
            {/* Badge body */}
            <div className="relative flex items-center px-5 py-2.5 bg-darkBg/50 backdrop-blur-xl border border-accent/40 rounded-full hover:border-accent/60 transition-all duration-300 group-hover:bg-darkBg/60">
              <span className="text-accent text-[10px] font-black uppercase tracking-[0.2em] flex items-center gap-2">
                Soporte IT 
                <span className="w-1 h-1 bg-white/30 rounded-full"></span> 
                Ciberseguridad 
                <span className="w-1 h-1 bg-white/30 rounded-full"></span> 
                Automatización
                {/* LED indicador */}
                <span className="relative flex h-1.5 w-1.5 ml-1">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent shadow-lg shadow-accent/50"></span>
                </span>
              </span>
            </div>
          </motion.div>

          {/* Título principal con efecto premium */}
          <motion.h1 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1 }}
            className="text-5xl md:text-8xl font-black text-textMain tracking-tighter leading-[0.9] mb-8"
          >
            TECNOLOGÍA SÓLIDA <br />
            <motion.span 
              initial={{ backgroundPosition: '200% center' }}
              animate={{ backgroundPosition: '0% center' }}
              transition={{ duration: 2, delay: 0.5 }}
              className="text-transparent bg-clip-text bg-gradient-to-r from-accent via-accent to-green-300 bg-200% animate-shimmer"
            >
              RESULTADOS REALES
            </motion.span>
          </motion.h1>

          {/* Descripción mejorada */}
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-textDim text-lg md:text-2xl max-w-4xl mx-auto mb-12 leading-relaxed font-light"
          >
            Soy Administrador de Sistemas con <strong className="text-textMain">más de 20 años</strong> de experiencia. 
            Me especializo en <strong className="text-accent">Soporte IT avanzado</strong>, el fortalecimiento de la <strong className="text-accent">Ciberseguridad</strong> operativa y la <strong className="text-accent">Automatización de Tareas y Procesos</strong> para que tu infraestructura y sistemas trabajen de forma <strong className="text-textMain">efectiva</strong>.
          </motion.p>

          {/* CTA Mejorado */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="flex flex-col sm:flex-row items-center gap-6 w-full sm:w-auto"
          >
            <motion.a 
              href="#chatbot-section"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="group w-full sm:w-auto bg-gradient-to-r from-accent to-green-400 text-darkBg px-10 py-5 rounded-2xl font-black text-lg flex items-center justify-center gap-3 hover:shadow-[0_0_50px_rgba(34,197,94,0.5)] transition-all duration-300 border border-accent/50 hover:border-accent"
            >
              SOLICITAR ASESORÍA IT 
              <motion.div
                animate={{ x: [0, 4, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <Zap size={20} fill="currentColor" />
              </motion.div>
            </motion.a>
            
            {/* Pills informativos */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="flex gap-3 items-center text-white/60 font-mono text-sm flex-wrap justify-center sm:justify-start"
            >
              <motion.span whileHover={{ textShadow: '0 0 20px rgba(34, 197, 94, 0.5)' }} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-accent/30 transition-all">
                <Monitor size={16} className="text-accent"/> Soporte
              </motion.span>
              <span className="text-white/20">•</span>
              <motion.span whileHover={{ textShadow: '0 0 20px rgba(34, 197, 94, 0.5)' }} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-accent/30 transition-all">
                <Shield size={16} className="text-accent"/> Seguridad
              </motion.span>
              <span className="text-white/20">•</span>
              <motion.span whileHover={{ textShadow: '0 0 20px rgba(34, 197, 94, 0.5)' }} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-accent/30 transition-all">
                <Zap size={16} className="text-accent"/> RPA
              </motion.span>
            </motion.div>
          </motion.div>

          {/* Divider decorativo */}
          <motion.div 
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
            className="mt-16 h-px w-24 bg-gradient-to-r from-transparent via-accent to-transparent"
          />

          {/* Scroll indicator */}
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="mt-8 text-accent/50 text-xs uppercase tracking-widest font-mono"
          >
            Scroll para explorar →
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;