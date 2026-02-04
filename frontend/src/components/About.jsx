import React from 'react';
import { motion } from 'framer-motion';
import { Target, Award, Download } from 'lucide-react';

const About = () => {
  const handleDownloadCV = () => {
    // Al estar en public, la ruta es directa
    window.open("/cv-luciano-valinoti.pdf", "_blank");
  };

  return (
    <section id="about" className="py-24 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
          >
            <div className="flex items-center gap-2 text-accent font-mono text-[10px] tracking-[0.3em] uppercase mb-4">
              <span className="w-8 h-[1px] bg-accent"></span> Algo Sobre Mí
            </div>
            <h2 className="text-4xl md:text-6xl font-black text-white uppercase tracking-tighter">
              Trayectoria y <span className="text-accent">Expertise</span>
            </h2>
            <p className="text-textDim text-lg mt-6 mb-8 leading-relaxed">
              Con más de 20 años en infraestructura IT, he vivido la evolución tecnológica desde las bases. Hace 4 años decidí especializarme en <strong>Python y Automatización</strong> para resolver el problema que veo en todas las empresas: el tiempo perdido en tareas repetitivas.
            </p>
            
            <div className="space-y-6 mb-10">
              <div className="flex items-start gap-4">
                <div className="bg-accent/10 p-2 rounded-lg text-accent"><Target size={20}/></div>
                <div>
                  <h4 className="text-white font-bold">Misión</h4>
                  <p className="text-textDim text-sm">Transformar flujos manuales en activos digitales autónomos.</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="bg-accent/10 p-2 rounded-lg text-accent"><Award size={20}/></div>
                <div>
                  <h4 className="text-white font-bold">Visión Técnica</h4>
                  <p className="text-textDim text-sm">Integrar IA y RPA para maximizar la eficiencia operativa.</p>
                </div>
              </div>
            </div>

            {/* BOTÓN DESCARGAR CV - Estilo consistente con el sitio */}
            <button 
              onClick={handleDownloadCV}
              className="flex items-center gap-3 bg-accent/10 border border-accent/20 text-accent px-8 py-4 rounded-xl text-[11px] font-black uppercase tracking-[0.2em] hover:bg-accent hover:text-darkBg transition-all shadow-[0_0_20px_rgba(34,197,94,0.05)] group"
            >
              <Download size={16} className="group-hover:animate-bounce" /> Descargar CV_Full
            </button>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="aspect-square rounded-[3rem] border border-white/10 overflow-hidden bg-cardBg relative group">
              <img 
                src="/perfil-about.jpg" 
                alt="Luciano Valinoti" 
                className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all duration-700 ease-in-out"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-darkBg/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>

            <div className="absolute -bottom-6 -right-6 bg-accent p-6 rounded-2xl shadow-2xl z-20">
              <p className="text-darkBg font-black text-4xl leading-none">+20</p>
              <p className="text-darkBg text-[10px] font-bold uppercase tracking-tighter">Años de Exp.</p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default About;