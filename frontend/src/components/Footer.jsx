import React from 'react';

const Footer = () => {
  return (
    <footer className="py-16 px-6 bg-darkBg border-t border-white/5">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-10">
          
          {/* LOGO: Alineado y con subtítulo del mismo largo que el nombre */}
          <div className="group flex flex-col w-fit cursor-default">
            <div className="text-xl font-black tracking-tighter uppercase leading-none inline-block">
              <span className="text-accent">&lt;_</span>
              <span className="text-white">LUCIANO</span>
              <span className="text-accent">VALINOTI</span>
            </div>
            <span className="text-[7px] font-mono text-white/40 uppercase tracking-[0.48em] mt-1 group-hover:text-accent transition-colors block w-full text-justify">
              IT Specialist & Automation
            </span>
          </div>

          {/* INFORMACIÓN Y COPYRIGHT */}
          <div className="flex flex-col items-center md:items-end gap-2 text-textDim text-[9px] font-bold uppercase tracking-[0.2em]">
            <div className="flex gap-4 mb-2">
              <a href="#servicios" className="hover:text-accent transition-colors">Servicios</a>
              <a href="#about" className="hover:text-accent transition-colors">Sobre Mí</a>
              <a href="#contacto" className="hover:text-accent transition-colors">Contacto</a>
            </div>
            <p className="text-white/20">
              © {new Date().getFullYear()} Luciano Valinoti — Córdoba, AR
            </p>
          </div>

        </div>

        {/* DETALLE ESTÉTICO FINAL (Opcional, una línea sutil) */}
        <div className="mt-12 w-full h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
      </div>
    </footer>
  );
};

export default Footer;