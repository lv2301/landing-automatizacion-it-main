import React, { useState } from 'react';
import { MessageCircle, Menu, X, MessageSquare } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleWhatsApp = () => {
    window.open("https://wa.me/543516889414", "_blank");
  };

  const handleChatbotClick = () => {
    setIsOpen(false); // Cierra el menú móvil si está abierto
  };

  return (
    <nav className="fixed top-0 w-full z-50 bg-darkBg/80 backdrop-blur-md border-b border-white/5 px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        
        {/* LOGO */}
        <a href="#home" className="group flex flex-col w-fit">
          <div className="text-xl font-black tracking-tighter uppercase leading-none inline-block">
            <span className="text-accent">&lt;_</span>
            <span className="text-white">LUCIANO</span>
            <span className="text-accent">VALINOTI</span>
          </div>
          <span className="text-[7px] font-mono text-white/40 uppercase tracking-[0.48em] mt-1 group-hover:text-accent transition-colors block w-full text-justify">
            IT Specialist & Automation
          </span>
        </a>

        {/* DESKTOP MENU */}
        <div className="hidden md:flex items-center gap-8">
          <div className="flex gap-6 text-[10px] font-bold uppercase tracking-widest text-textDim">
            <a href="#home" className="hover:text-accent transition-colors">Inicio</a>
            <a href="#servicios" className="hover:text-accent transition-colors">Servicios</a>
            <a href="#casos" className="hover:text-accent transition-colors">Experiencia</a>
            <a href="#about" className="hover:text-accent transition-colors">Sobre mí</a>
            <a href="#chatbot-section" onClick={handleChatbotClick} className="flex items-center gap-1.5 text-accent hover:text-green-300 transition-colors">
              <MessageSquare size={12} /> Asesoría
            </a>
            <a href="#contacto" className="hover:text-accent transition-colors">Contacto</a>
          </div>
          
          {/* BOTÓN WHATSAPP */}
          <button 
            onClick={handleWhatsApp}
            className="flex items-center gap-2 bg-accent/10 border border-accent/20 text-accent px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-accent hover:text-darkBg transition-all shadow-[0_0_15px_rgba(34,197,94,0.1)] hover:shadow-[0_0_25px_rgba(34,197,94,0.3)]"
          >
            <MessageCircle size={14} /> WhatsApp
          </button>
        </div>

        {/* MOBILE TOGGLE */}
        <button 
          className="md:hidden text-accent p-2 hover:bg-accent/10 rounded-lg transition-colors" 
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* MOBILE MENU */}
      {isOpen && (
        <div className="absolute top-full left-0 w-full bg-darkBg/95 backdrop-blur-lg border-b border-white/5 px-6 py-10 flex flex-col items-center gap-8 md:hidden">
          <div className="flex flex-col items-center gap-6 text-[10px] font-bold uppercase tracking-[0.3em] text-textDim w-full">
            <a href="#home" onClick={() => setIsOpen(false)} className="hover:text-accent transition-colors">Inicio</a>
            <a href="#servicios" onClick={() => setIsOpen(false)} className="hover:text-accent transition-colors">Servicios</a>
            <a href="#casos" onClick={() => setIsOpen(false)} className="hover:text-accent transition-colors">Experiencia</a>
            <a href="#about" onClick={() => setIsOpen(false)} className="hover:text-accent transition-colors">Sobre mí</a>
            <a href="#chatbot-section" onClick={() => setIsOpen(false)} className="flex items-center gap-1.5 text-accent hover:text-green-300 transition-colors">
              <MessageSquare size={12} /> Asesoría
            </a>
            <a href="#contacto" onClick={() => setIsOpen(false)} className="hover:text-accent transition-colors">Contacto</a>
          </div>
          
          {/* BOTÓN WHATSAPP MÓVIL */}
          <button 
            onClick={handleWhatsApp}
            className="w-full flex items-center justify-center gap-2 bg-accent/10 border border-accent/20 text-accent py-4 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-accent hover:text-darkBg transition-all shadow-[0_0_15px_rgba(34,197,94,0.1)] hover:shadow-[0_0_25px_rgba(34,197,94,0.3)]"
          >
            <MessageCircle size={16} /> WhatsApp
          </button>
        </div>
      )}
    </nav>
  );
};

export default Navbar;