import React from 'react';
import { motion } from 'framer-motion';
import { Monitor, ShieldCheck, Zap, ArrowUpRight, Sparkles, Eye } from 'lucide-react';

const services = [
  { 
    title: 'Soporte IT e Infraestructura', 
    desc: 'Gestión profesional de equipos y servidores. Mantengo tu tecnología operativa y actualizada para que tu actividad nunca se detenga.', 
    icon: <Monitor />, 
    size: 'md:col-span-2', 
    highlight: 'Continuidad operativa y Hardware',
    gradient: 'from-blue-500/10 to-transparent'
  },
  { 
    title: 'Ciberseguridad', 
    desc: 'Blindaje de información crítica. Gestión de respaldos y configuración de redes seguras para evitar accesos no deseados.', 
    icon: <ShieldCheck />, 
    size: 'md:col-span-1',
    highlight: 'Protección de Datos',
    gradient: 'from-red-500/10 to-transparent'
  },
  { 
    title: 'Automatización de Procesos', 
    desc: 'Optimizo tu tiempo mediante Python y n8n. Flujos inteligentes que eliminan tareas repetitivas y errores manuales.', 
    icon: <Zap />, 
    size: 'md:col-span-1',
    highlight: 'Eficiencia con Python',
    gradient: 'from-accent/10 to-transparent'
  },
  { 
    title: 'Seguridad Electrónica', 
    desc: 'Protección física avanzada. Instalación de cámaras IP con monitoreo móvil y sistemas de alarmas domiciliarias o comerciales.', 
    icon: <Eye />, 
    size: 'md:col-span-1',
    highlight: 'Cámaras y Alarmas',
    gradient: 'from-orange-500/10 to-transparent'
  },
  { 
    title: 'IA Aplicada', 
    desc: 'Integro Inteligencia Artificial para potenciar la atención al cliente y el análisis de datos mediante agentes y modelos avanzados.', 
    icon: <Sparkles />, 
    size: 'md:col-span-1',
    highlight: 'Innovación con LLMs',
    gradient: 'from-purple-500/10 to-transparent'
  },
];

const Services = () => (
  <section id="servicios" className="py-24 px-6 bg-darkBg relative overflow-hidden">
    <div className="max-w-7xl mx-auto text-left">
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true }}
        className="mb-16"
      >
        <div className="flex items-center gap-2 text-accent font-mono text-[10px] tracking-[0.3em] uppercase mb-4">
          <span className="w-8 h-[1px] bg-accent"></span> Expertise Técnico
        </div>
        <h2 className="text-4xl md:text-6xl font-black text-white uppercase tracking-tighter">
          SOLUCIONES <span className="text-accent">ESTRATÉGICAS</span>
        </h2>
      </motion.div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {services.map((s, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className={`${s.size} group relative bg-cardBg border border-white/5 rounded-[2.5rem] p-10 hover:border-accent/30 transition-all duration-500 flex flex-col justify-between overflow-hidden shadow-2xl`}
          >
            <div className={`absolute inset-0 bg-gradient-to-br ${s.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
            <div className="relative z-10">
              <div className="flex justify-between items-start mb-8">
                <div className="text-accent bg-accent/5 w-14 h-14 flex items-center justify-center rounded-2xl border border-accent/10 group-hover:bg-accent group-hover:text-darkBg transition-all duration-300">
                  {React.cloneElement(s.icon, { size: 28 })}
                </div>
                <ArrowUpRight className="text-white/10 group-hover:text-accent transition-all duration-300" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-4 tracking-tight">{s.title}</h3>
              <p className="text-textDim text-sm leading-relaxed max-w-sm group-hover:text-white/90 transition-colors">{s.desc}</p>
            </div>
            <div className="relative z-10 mt-12 flex items-center justify-between border-t border-white/5 pt-6 font-bold text-accent text-[10px] uppercase tracking-widest">
              {s.highlight}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  </section>
);

export default Services;