import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, ChevronRight, Sparkles } from 'lucide-react';

const ChatbotSection = () => {
  const [step, setStep] = useState('inicio');
  const [selectedService, setSelectedService] = useState(null);
  const [selectedClientType, setSelectedClientType] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [formData, setFormData] = useState({
    service: '',
    clientType: '',
    nombre: '',
    email: '',
    problema: '',
    telefono: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([
    { role: 'bot', content: '¡Hola! Puedo responder tus preguntas o ayudarte a solicitar una asesoría. ¿Qué necesitas?' }
  ]);
  const scrollRef = useRef(null);

  useEffect(() => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(id);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const servicios = [
    { id: 'automatizacion', label: 'Automatización', emoji: '⚙️' },
    { id: 'seguridad', label: 'Seguridad IT', emoji: '🔐' },
    { id: 'soporte', label: 'Soporte IT', emoji: '🛠️' },
    { id: 'consulta', label: 'Consulta General', emoji: '💡' }
  ];

  const tiposCliente = [
    { id: 'particular', label: 'Particular', emoji: '👤' },
    { id: 'comercio', label: 'Comercio', emoji: '🏪' },
    { id: 'oficina', label: 'Oficina', emoji: '🏢' },
    { id: 'empresa', label: 'Empresa', emoji: '🏭' }
  ];

  const handleSendGeneralQuestion = async () => {
    if (!userInput.trim()) return;
    const question = userInput;
    setUserInput('');
    setIsLoading(true);

    setMessages(prev => [
      ...prev,
      { role: 'user', content: question }
    ]);

    try {
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: question,
          session_id: sessionId
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [
          ...prev,
          { role: 'bot', content: data.response }
        ]);
      } else {
        throw new Error(data.detail);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Error procesando tu pregunta. Intenta de nuevo.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectService = (serviceId) => {
    const service = servicios.find(s => s.id === serviceId);
    setSelectedService(service);
    setFormData(prev => ({ ...prev, service: service.label }));
    setMessages(prev => [
      ...prev,
      { role: 'user', content: service.label, emoji: service.emoji },
      { role: 'bot', content: `Perfecto, ${service.label}. ¿Eres Particular, Comercio, Oficina o Empresa?` }
    ]);
    setStep('clientType');
  };

  const handleSelectClientType = (typeId) => {
    const type = tiposCliente.find(t => t.id === typeId);
    setSelectedClientType(type);
    setFormData(prev => ({ ...prev, clientType: type.label }));
    setMessages(prev => [
      ...prev,
      { role: 'user', content: type.label, emoji: type.emoji },
      { role: 'bot', content: `Entendido. ¿Cuál es tu nombre?` }
    ]);
    setStep('nombre');
  };

  const handleConfirmNombre = () => {
    if (!formData.nombre.trim()) return;
    setMessages(prev => [
      ...prev,
      { role: 'user', content: formData.nombre },
      { role: 'bot', content: `¿Tu email?` }
    ]);
    setStep('email');
  };

  const handleConfirmEmail = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Email inválido. Por favor, escribe un email válido.' }
      ]);
      return;
    }
    setMessages(prev => [
      ...prev,
      { role: 'user', content: formData.email },
      { role: 'bot', content: `Describe brevemente tu problema o qué necesitas (máximo 200 caracteres).` }
    ]);
    setStep('problema');
  };

  const handleConfirmProblema = () => {
    if (!formData.problema.trim() || formData.problema.length < 10) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Por favor, describe más detalladamente (mínimo 10 caracteres).' }
      ]);
      return;
    }
    setMessages(prev => [
      ...prev,
      { role: 'user', content: formData.problema },
      { role: 'bot', content: `¿Tu WhatsApp o teléfono?` }
    ]);
    setStep('telefono');
  };

  const handleConfirmTelefono = async () => {
    if (!formData.telefono.trim() || formData.telefono.length < 8) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Teléfono inválido, mínimo 8 dígitos.' }
      ]);
      return;
    }

    setMessages(prev => [
      ...prev,
      { role: 'user', content: formData.telefono },
      { role: 'bot', content: `Procesando tu consulta...` }
    ]);

    setStep('resumen');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `${formData.nombre} | ${formData.email} | ${formData.clientType} | ${formData.problema} | ${formData.telefono} | Interesado en: ${formData.service}`,
          session_id: sessionId
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessages(prev => [
          ...prev,
          { role: 'bot', content: `¡Perfecto ${formData.nombre}! He recibido tu consulta. Luciano se pondrá en contacto contigo pronto por WhatsApp.` }
        ]);
      } else {
        throw new Error(data.detail);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: `Error al procesar. Contacta: +54 351 6889414` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setStep('inicio');
    setSelectedService(null);
    setSelectedClientType(null);
    setUserInput('');
    setFormData({ service: '', clientType: '', nombre: '', email: '', problema: '', telefono: '' });
    setMessages([{ role: 'bot', content: '¡Hola! Puedo responder tus preguntas o ayudarte a solicitar una asesoría. ¿Qué necesitas?' }]);
  };

  // Typing indicator custom
  const TypingIndicator = () => (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start"
    >
      <div className="bg-cardBg/60 border border-accent/20 px-4 py-3 rounded-2xl backdrop-blur-lg shadow-lg flex gap-1.5">
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            animate={{ y: [0, -8, 0] }}
            transition={{ 
              duration: 0.6, 
              delay: i * 0.15, 
              repeat: Infinity,
              repeatDelay: 0.3
            }}
            className="w-2 h-2 bg-accent rounded-full"
          />
        ))}
      </div>
    </motion.div>
  );

  return (
    <section id="chatbot-section" className="py-20 px-6 bg-darkBg relative overflow-hidden">
      {/* Animated Background Premium */}
      <div className="absolute inset-0 -z-10 pointer-events-none">
        <motion.div 
          animate={{ rotate: 360 }}
          transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-gradient-to-b from-accent/12 via-transparent to-transparent rounded-full blur-3xl"
        />
        <div className="absolute bottom-1/4 -right-32 w-80 h-80 bg-gradient-to-l from-accent/8 to-transparent rounded-full blur-3xl" />
        <div className="absolute top-1/3 -left-40 w-64 h-64 bg-gradient-to-r from-accent/7 via-transparent to-transparent rounded-full blur-3xl" />
      </div>

      <div className="max-w-2xl mx-auto">
        {/* Header mejorado */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-8"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            whileInView={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-accent/20 to-accent/10 border border-accent/40 mb-4 backdrop-blur-sm hover:border-accent/60 transition-all duration-300"
          >
            <motion.div 
              animate={{ rotate: 360 }} 
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            >
              <Sparkles size={14} className="text-accent" />
            </motion.div>
            <span className="text-accent text-xs font-bold tracking-widest uppercase">Asistente IA</span>
          </motion.div>

          <h2 className="text-3xl md:text-4xl lg:text-5xl font-black text-textMain uppercase tracking-tighter mb-2 leading-tight">
            Solicita tu <span className="text-accent italic">Asesoría</span>
          </h2>

          <p className="text-textDim text-xs md:text-sm max-w-xl mx-auto font-light">
            Haz preguntas o completa el formulario para solicitar una evaluación personalizada.
          </p>
        </motion.div>

        {/* Chat Container Premium */}
        <motion.div
          initial={{ opacity: 0, y: 25 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative"
        >
          {/* Glow effect mejorado */}
          <div className="absolute -inset-1 bg-gradient-to-r from-accent/20 via-accent/10 to-accent/20 rounded-3xl blur-2xl opacity-40 group-hover:opacity-60 transition-opacity duration-300" />

          <div className="relative backdrop-blur-2xl bg-gradient-to-br from-cardBg/50 via-cardBg/40 to-cardBg/30 border border-accent/25 rounded-3xl shadow-2xl overflow-hidden hover:border-accent/40 transition-all duration-300">
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-accent/50 to-transparent" />

            {/* Messages Container */}
            <div ref={scrollRef} className="h-56 md:h-72 overflow-y-auto p-6 space-y-3 bg-gradient-to-b from-cardBg/40 to-transparent custom-scrollbar">
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 12, x: msg.role === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, y: 0, x: 0 }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <motion.div
                    whileHover={{ scale: 1.02, translateY: -2 }}
                    className={`max-w-xs px-5 py-3 rounded-2xl text-sm backdrop-blur-lg transition-all duration-300 ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-accent/30 to-accent/20 text-textMain border border-accent/50 shadow-lg shadow-accent/20 hover:shadow-accent/30'
                        : 'bg-gradient-to-r from-cardBg/70 to-cardBg/50 text-textDim border border-accent/25 shadow-lg shadow-darkBg/50 hover:border-accent/40'
                    }`}
                  >
                    {msg.emoji && <span className="mr-2 text-lg">{msg.emoji}</span>}
                    <span className="font-light leading-relaxed">{msg.content}</span>
                  </motion.div>
                </motion.div>
              ))}

              {isLoading && <TypingIndicator />}
            </div>

            {/* Input Section Premium */}
            <div className="border-t border-accent/15 p-5 md:p-6 bg-gradient-to-t from-cardBg/40 via-cardBg/25 to-transparent">
              {/* Input inicial */}
              {step === 'inicio' && !isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-3"
                >
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      placeholder="Escribe tu pregunta o selecciona un servicio..."
                      className="flex-1 bg-cardBg/50 border border-accent/25 backdrop-blur-lg rounded-xl py-3 px-4 text-textMain placeholder-textDim text-sm focus:outline-none focus:border-accent/60 focus:bg-cardBg/70 focus:shadow-lg focus:shadow-accent/20 transition-all duration-300 font-light"
                      autoFocus
                      onKeyPress={(e) => e.key === 'Enter' && handleSendGeneralQuestion()}
                    />
                    <motion.button
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={handleSendGeneralQuestion}
                      className="bg-gradient-to-br from-accent/30 to-accent/20 border border-accent/50 text-accent p-3 rounded-xl hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300"
                    >
                      <Send size={18} />
                    </motion.button>
                  </div>

                  <div className="pt-2">
                    <p className="text-textDim text-xs mb-3 font-light">O selecciona un servicio para solicitar asesoría:</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {servicios.map((service, idx) => (
                        <motion.button
                          key={service.id}
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.08 }}
                          whileHover={{ scale: 1.05, translateY: -3 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleSelectService(service.id)}
                          className="p-4 rounded-2xl backdrop-blur-lg bg-gradient-to-br from-cardBg/60 to-cardBg/40 border border-accent/20 hover:border-accent/60 hover:from-cardBg/80 hover:to-cardBg/60 hover:shadow-lg hover:shadow-accent/20 transition-all duration-300 text-left group"
                        >
                          <div className="text-3xl mb-2 group-hover:scale-125 transition-transform duration-300">{service.emoji}</div>
                          <p className="text-textMain font-semibold text-xs leading-tight">{service.label}</p>
                        </motion.button>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Resto de pasos con mismo estilo mejorado */}
              {step === 'clientType' && !isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.4 }}
                  className="grid grid-cols-2 md:grid-cols-4 gap-3"
                >
                  {tiposCliente.map((tipo, idx) => (
                    <motion.button
                      key={tipo.id}
                      initial={{ opacity: 0, y: 12 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.08 }}
                      whileHover={{ scale: 1.05, translateY: -3 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleSelectClientType(tipo.id)}
                      className="p-4 rounded-2xl backdrop-blur-lg bg-gradient-to-br from-cardBg/60 to-cardBg/40 border border-accent/20 hover:border-accent/60 hover:from-cardBg/80 hover:to-cardBg/60 hover:shadow-lg hover:shadow-accent/20 transition-all duration-300 text-left group"
                    >
                      <div className="text-3xl mb-2 group-hover:scale-125 transition-transform duration-300">{tipo.emoji}</div>
                      <p className="text-textMain font-semibold text-xs leading-tight">{tipo.label}</p>
                    </motion.button>
                  ))}
                </motion.div>
              )}

              {step === 'nombre' && !isLoading && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3">
                  <input
                    type="text"
                    value={formData.nombre}
                    onChange={(e) => setFormData(prev => ({ ...prev, nombre: e.target.value }))}
                    placeholder="Escribe tu nombre..."
                    className="flex-1 bg-cardBg/50 border border-accent/25 backdrop-blur-lg rounded-xl py-3 px-4 text-textMain placeholder-textDim text-sm focus:outline-none focus:border-accent/60 focus:bg-cardBg/70 focus:shadow-lg focus:shadow-accent/20 transition-all duration-300 font-light"
                    autoFocus
                    onKeyPress={(e) => e.key === 'Enter' && handleConfirmNombre()}
                  />
                  <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} onClick={handleConfirmNombre} className="bg-gradient-to-br from-accent/30 to-accent/20 border border-accent/50 text-accent p-3 rounded-xl hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300">
                    <ChevronRight size={18} />
                  </motion.button>
                </motion.div>
              )}

              {step === 'email' && !isLoading && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3">
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="tu@email.com"
                    className="flex-1 bg-cardBg/50 border border-accent/25 backdrop-blur-lg rounded-xl py-3 px-4 text-textMain placeholder-textDim text-sm focus:outline-none focus:border-accent/60 focus:bg-cardBg/70 focus:shadow-lg focus:shadow-accent/20 transition-all duration-300 font-light"
                    autoFocus
                    onKeyPress={(e) => e.key === 'Enter' && handleConfirmEmail()}
                  />
                  <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} onClick={handleConfirmEmail} className="bg-gradient-to-br from-accent/30 to-accent/20 border border-accent/50 text-accent p-3 rounded-xl hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300">
                    <ChevronRight size={18} />
                  </motion.button>
                </motion.div>
              )}

              {step === 'problema' && !isLoading && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-3">
                  <textarea
                    value={formData.problema}
                    onChange={(e) => setFormData(prev => ({ ...prev, problema: e.target.value.substring(0, 200) }))}
                    placeholder="Describe tu problema o necesidad (máx. 200 caracteres)..."
                    className="flex-1 bg-cardBg/50 border border-accent/25 backdrop-blur-lg rounded-xl py-3 px-4 text-textMain placeholder-textDim text-sm focus:outline-none focus:border-accent/60 focus:bg-cardBg/70 focus:shadow-lg focus:shadow-accent/20 transition-all duration-300 font-light resize-none h-24"
                    autoFocus
                    onKeyPress={(e) => e.key === 'Enter' && e.ctrlKey && handleConfirmProblema()}
                  />
                  <div className="flex justify-between items-center">
                    <span className="text-textDim text-xs">{formData.problema.length}/200</span>
                    <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} onClick={handleConfirmProblema} className="bg-gradient-to-br from-accent/30 to-accent/20 border border-accent/50 text-accent p-3 rounded-xl hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300">
                      <ChevronRight size={18} />
                    </motion.button>
                  </div>
                </motion.div>
              )}

              {step === 'telefono' && !isLoading && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3">
                  <input
                    type="tel"
                    value={formData.telefono}
                    onChange={(e) => setFormData(prev => ({ ...prev, telefono: e.target.value }))}
                    placeholder="Tu WhatsApp..."
                    className="flex-1 bg-cardBg/50 border border-accent/25 backdrop-blur-lg rounded-xl py-3 px-4 text-textMain placeholder-textDim text-sm focus:outline-none focus:border-accent/60 focus:bg-cardBg/70 focus:shadow-lg focus:shadow-accent/20 transition-all duration-300 font-light"
                    autoFocus
                    onKeyPress={(e) => e.key === 'Enter' && handleConfirmTelefono()}
                  />
                  <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.95 }} onClick={handleConfirmTelefono} className="bg-gradient-to-br from-accent/30 to-accent/20 border border-accent/50 text-accent p-3 rounded-xl hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/30 transition-all duration-300">
                    <Send size={18} />
                  </motion.button>
                </motion.div>
              )}

              {step === 'resumen' && !isLoading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="grid grid-cols-2 gap-3">
                  <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={handleReset} className="px-5 py-3 rounded-xl bg-gradient-to-r from-accent/30 to-accent/20 border border-accent/50 text-accent font-semibold text-sm hover:from-accent/40 hover:to-accent/30 hover:shadow-lg hover:shadow-accent/20 transition-all duration-300">
                    Nueva consulta
                  </motion.button>
                  <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} onClick={() => window.location.href = '#contacto'} className="px-5 py-3 rounded-xl bg-gradient-to-r from-cardBg/70 to-cardBg/50 border border-accent/25 text-textMain font-semibold text-sm hover:from-cardBg/80 hover:to-cardBg/60 hover:border-accent/40 transition-all duration-300">
                    Ir a contacto
                  </motion.button>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(34, 197, 94, 0.3);
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(34, 197, 94, 0.5);
        }
      `}</style>
    </section>
  );
};

export default ChatbotSection;