import React from 'react';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, MessageCircle, ExternalLink } from 'lucide-react';

const Contact = () => {
  const handleWhatsApp = () => {
    window.open("https://wa.me/543516889414?text=Hola%20Luciano,%20vi%20tu%20web%20y%20me%20gustaría%20consultar%20por...", "_blank");
  };

  return (
    <section id="contacto" className="py-20 px-6 bg-darkBg border-t border-white/10">
      <div className="max-w-5xl mx-auto">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
        >
          <div className="flex items-center gap-2 text-accent font-mono text-[10px] tracking-[0.3em] uppercase mb-6">
            <span className="w-8 h-[1px] bg-accent"></span> Contacto
          </div>
          
          <h2 className="text-4xl md:text-5xl font-black text-white uppercase tracking-tighter mb-8 leading-none">
            CONTACTAME Y <br /> <span className="text-accent italic">HABLAMOS DE LO QUE NECESITAS</span>
          </h2>
          
          <div className="space-y-4 max-w-2xl">
            {/* WhatsApp */}
            <motion.button 
              whileHover={{ scale: 1.02 }}
              onClick={handleWhatsApp}
              className="w-full flex items-center gap-4 p-6 rounded-2xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-accent/50 hover:bg-accent/5 transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent group-hover:bg-accent/20 transition-all">
                <MessageCircle size={22} />
              </div>
              <div className="text-left flex-1">
                <p className="text-[10px] uppercase tracking-widest text-white/40 font-bold">WhatsApp Directo</p>
                <p className="text-white font-semibold">+54 351 6889414</p>
              </div>
              <ExternalLink size={16} className="text-white/20 group-hover:text-accent transition-all" />
            </motion.button>

            {/* Email */}
            <motion.a 
              whileHover={{ scale: 1.02 }}
              href="mailto:lucianovalinoti@gmail.com"
              className="flex items-center gap-4 p-6 rounded-2xl backdrop-blur-sm bg-white/5 border border-white/10 hover:border-accent/50 hover:bg-accent/5 transition-all group"
            >
              <div className="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent group-hover:bg-accent/20 transition-all">
                <Mail size={22} />
              </div>
              <div className="text-left flex-1">
                <p className="text-[10px] uppercase tracking-widest text-white/40 font-bold">Email</p>
                <p className="text-white font-semibold">lucianovalinoti@gmail.com</p>
              </div>
              <ExternalLink size={16} className="text-white/20 group-hover:text-accent transition-all" />
            </motion.a>

            {/* Ubicación */}
            <div className="flex items-center gap-4 p-6 rounded-2xl bg-white/5 border border-white/10">
              <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-white/40">
                <MapPin size={22} />
              </div>
              <div className="text-left">
                <p className="text-[10px] uppercase tracking-widest text-white/40 font-bold">Ubicación</p>
                <p className="text-white font-semibold">Córdoba Capital, Argentina</p>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Contact;