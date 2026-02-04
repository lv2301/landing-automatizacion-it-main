# app/models/lead.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# ============================================================================
# 💬 CHAT SESSIONS
# ============================================================================

class ChatSession(Base):
    """Modelo para sesiones de chat."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actividad = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatSession {self.session_id}>"


# ============================================================================
# 💬 CHAT HISTORY
# ============================================================================

class ChatHistory(Base):
    """Modelo para historial de mensajes en chat."""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    mensaje_usuario = Column(Text, nullable=False)
    respuesta_bot = Column(Text, nullable=False)
    lead_score = Column(Integer, default=0)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ChatHistory {self.session_id}>"


# ============================================================================
# 👤 LEADS
# ============================================================================

class Lead(Base):
    """Modelo para leads/contactos."""
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), index=True, nullable=False)
    telefono = Column(String(20), nullable=False)
    mensaje = Column(Text, nullable=True)
    servicio = Column(String(100), nullable=True)
    
    # Lead scoring
    lead_score = Column(Integer, default=0)
    estado = Column(String(20), default="nuevo", index=True)  # nuevo, contactado, negociando, agendado, convertido, perdido, spam
    origen = Column(String(50), default="formulario_landing")  # formulario_landing, chat, importado
    
    # Timestamps
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    fecha_ultima_actividad = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notas internas
    notas = Column(Text, nullable=True)
    
    # Métodos útiles
    def es_lead_calido(self):
        """¿Es un lead de alto valor?"""
        return self.lead_score >= 80
    
    def dias_desde_creacion(self):
        """Cuántos días pasaron desde que se creó."""
        return (datetime.utcnow() - self.fecha_creacion).days
    
    def estado_display(self):
        """Mostrar estado con emoji."""
        emojis = {
            "nuevo": "🆕",
            "contactado": "📞",
            "negociando": "💬",
            "agendado": "📅",
            "convertido": "✅",
            "perdido": "❌",
            "spam": "🚫"
        }
        return f"{emojis.get(self.estado, '?')} {self.estado.capitalize()}"
    
    def __repr__(self):
        return f"<Lead {self.nombre} ({self.email})>"