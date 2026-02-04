import React from 'react';
import { motion } from 'framer-motion';
import { Monitor, Camera, MessageSquare, Shield, Zap, ArrowRight } from 'lucide-react';

const cases = [
  { 
    category: "Soporte IT", 
    project: "Continuidad en Oficina Jurídica", 
    description: "Reorganización de infraestructura y servidores, eliminando caídas de sistema.", 
    impact: "99.9% Uptime", 
    tech: ["Windows Server", "Active Directory", "Mikrotik"],
    gradient: "from-blue-500/10 to-transparent",
    icon: <Monitor size={18} /> 
  },
  { 
    category: "Seguridad Electrónica", 
    project: "Vigilancia en Comercio", 
    description: "Instalación de cámaras IP con detección de movimiento y alertas en tiempo real.", 
    impact: "Control 24/7", 
    tech: ["Cámaras IP", "NVR Dahua", "App Monitoreo"],
    gradient: "from-orange-500/10 to-transparent",
    icon: <Camera size={18} /> 
  },
  { 
    category: "IA & Automatización", 
    project: "Asistente de Turnos con IA", 
    description: "Bot inteligente para WhatsApp que gestiona consultas y agenda citas.", 
    impact: "Ahorro 70% tiempo", 
    tech: ["Python", "OpenAI API", "Twilio"],
    gradient: "from-accent/10 to-transparent",
    icon: <MessageSquare size={18} /> 
  },
  { 
    category: "Ciberseguridad", 
    project: "Protección de Datos", 
    description: "Implementación de backups automáticos y cifrado contra ransomware.", 
    impact: "Cero pérdida de datos", 
    tech: ["Veeam Backup", "Cifrado AES", "Cloud Storage"],
    gradient: "from-red-500/10 to-transparent",
    icon: <Shield size={18} /> 
  },
  { 
    category: "Automatización", 
    project: "Gestión de Stock Inteligente", 
    description: "Flujo en n8n que automatiza el inventario y alerta faltantes automáticamente.", 
    impact: "Eficiencia Operativa", 
    tech: ["n8n", "PostgreSQL", "Telegram Bot"],
    gradient: "from-purple-500/10 to-transparent",
    icon: <Zap size={18} /> 
  },
  { 
    category: "Redes", 
    project: "Acceso Remoto Seguro", 
    description: "Configuración de redes VPN para trabajo remoto seguro en PyMEs.", 
    impact: "Conexión Encriptada", 
    tech: ["VPN L2TP/IPSec", "Mikrotik", "Firewalling"],
    gradient: "from-blue-400/10 to-transparent",
    icon: <Shield size={18} /> 
  }
];

const Experience = () => {
  return (
    <section id="casos" className="py-24 px-6 bg-transparent">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-16">
          <div className="flex items-center gap-2 text-accent font-mono text-[10px] tracking-[0.3em] uppercase mb-4">
            <span className="w-8 h-[1px] bg-accent"></span> Casos de Éxito
          </div>
          <h2 className="text-4xl md:text-6xl font-black text-white uppercase tracking-tighter">SOLUCIONES EN <span className="text-accent italic">ACCIÓN</span></h2>
        </div>

        {/* Cases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-24">
          {cases.map((item, index) => (
            <div key={index} className="group relative bg-cardBg border border-white/5 p-8 rounded-[2.5rem] hover:border-accent/20 transition-all duration-500 overflow-hidden shadow-2xl flex flex-col justify-between">
              <div className={`absolute inset-0 bg-gradient-to-br ${item.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              
              <div className="relative z-10">
                <div className="flex items-center gap-2 text-accent mb-6">
                  {item.icon} <span className="text-[10px] font-black uppercase tracking-widest">{item.category}</span>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{item.project}</h3>
                <p className="text-textDim text-sm font-light leading-relaxed mb-6">"{item.description}"</p>
                
                <div className="flex flex-wrap gap-2 mb-6">
                  {item.tech.map((t, idx) => (
                    <span key={idx} className="text-[8px] font-mono px-2 py-1 rounded-md bg-white/5 text-white/40 border border-white/5">
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="relative z-10 pt-6 border-t border-white/5 flex items-center justify-between text-[10px] font-bold text-accent uppercase tracking-widest">
                <span className="text-white/20">Impacto:</span> {item.impact}
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="border-t border-white/10 pt-12 flex flex-col md:flex-row items-center justify-between gap-10"
        >
          <div className="max-w-2xl">
            <h3 className="text-3xl md:text-4xl font-black text-white uppercase tracking-tighter leading-none mb-4">
              Hagamos tu entorno <span className="text-accent italic">más eficiente</span>
            </h3>
            <p className="text-white/50 text-sm leading-relaxed">
              ¿Tienes un desafío técnico o quieres optimizar un proceso? Cuéntame tu necesidad y recibirás un diagnóstico personalizado.
            </p>
          </div>
          
          <motion.a
            href="#contacto"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="group shrink-0 px-6 py-3 rounded-lg bg-accent text-darkBg font-black uppercase tracking-widest text-xs hover:bg-white transition-all flex items-center gap-2 cursor-pointer"
          >
            Consultar <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
};

export default Experience;