# app/database.py
"""
CONFIGURACIÓN DE BASE DE DATOS
Soporta SQLite (local) y PostgreSQL/Supabase (producción).
"""

import logging
from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# 🗄️ CREAR ENGINE DE BASE DE DATOS
# ============================================================================

def crear_engine():
    """
    Crea el engine según el tipo de BD configurada.
    """
    
    if settings.DATABASE_TYPE == "sqlite":
        logger.info("📦 Usando SQLite (local)")
        
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    
    elif settings.DATABASE_TYPE == "postgresql":
        logger.info("🌐 Usando PostgreSQL (cloud)")
        
        engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=False
        )
    
    else:
        raise ValueError(f"❌ DATABASE_TYPE '{settings.DATABASE_TYPE}' no soportado")
    
    return engine


engine = crear_engine()

# ============================================================================
# 📝 BASE DECLARATIVA
# ============================================================================

Base = declarative_base()

# ============================================================================
# 🔗 SESSION LOCAL
# ============================================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ============================================================================
# 🔄 DEPENDENCY: get_db
# ============================================================================

def get_db():
    """Dependency de FastAPI que provee sesión de BD a cada request."""
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# 🏥 HEALTH CHECK
# ============================================================================

def check_db_connection() -> dict:
    """Verifica que la conexión a BD funciona."""
    
    try:
        with engine.connect() as connection:
            # CORREGIDO: Usar text() para queries
            result = connection.execute(text("SELECT 1"))
            result.close()
        
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        
        logger.info(f"✅ BD conectada. Tablas: {tablas}")
        
        return {
            "conectado": True,
            "tipo": settings.DATABASE_TYPE,
            "tablas": tablas,
            "mensaje": "✅ BD operacional"
        }
    
    except Exception as e:
        logger.error(f"❌ Error conectando BD: {str(e)}")
        return {
            "conectado": False,
            "tipo": settings.DATABASE_TYPE,
            "mensaje": f"❌ Error: {str(e)}"
        }


# ============================================================================
# 🔧 INIT DATABASE
# ============================================================================

def init_db():
    """Crea todas las tablas en la BD."""
    
    logger.info("🔧 Inicializando base de datos...")
    
    try:
        Base.metadata.create_all(bind=engine)
        
        inspector = inspect(engine)
        tablas = inspector.get_table_names()
        
        logger.info(f"✅ BD inicializada. Tablas creadas: {tablas}")
        
        return {
            "exito": True,
            "tablas": tablas,
            "mensaje": "✅ BD lista"
        }
    
    except Exception as e:
        logger.error(f"❌ Error inicializando BD: {str(e)}")
        return {
            "exito": False,
            "mensaje": f"❌ Error: {str(e)}"
        }


# ============================================================================
# 🔄 EVENT LISTENERS
# ============================================================================

if settings.DEBUG:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        logger.debug("📥 Conexión a BD abierta")
    
    @event.listens_for(engine, "close")
    def receive_close(dbapi_conn, connection_record):
        logger.debug("📤 Conexión a BD cerrada")


# ============================================================================
# 📊 UTILIDADES
# ============================================================================

def get_db_stats() -> dict:
    """Obtiene estadísticas de la base de datos."""
    
    try:
        db = SessionLocal()
        
        from app.models.lead import Lead, ChatSession, ChatHistory
        
        total_leads = db.query(Lead).count()
        total_sesiones = db.query(ChatSession).count()
        total_mensajes = db.query(ChatHistory).count()
        
        db.close()
        
        return {
            "total_leads": total_leads,
            "total_sesiones_chat": total_sesiones,
            "total_mensajes": total_mensajes,
            "mensaje": "✅ Estadísticas obtenidas"
        }
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo stats: {str(e)}")
        return {
            "error": str(e),
            "mensaje": "❌ Error"
        }


def cleanup_old_data(dias: int = 30):
    """Limpia datos antiguos."""
    
    try:
        from datetime import datetime, timedelta
        from app.models.lead import ChatSession, ChatHistory
        
        db = SessionLocal()
        
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        
        sesiones_borradas = db.query(ChatSession).filter(
            ChatSession.fecha_inicio < fecha_limite
        ).delete()
        
        mensajes_borrados = db.query(ChatHistory).filter(
            ChatHistory.fecha < fecha_limite
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"🗑️ Cleanup completado: {sesiones_borradas} sesiones, {mensajes_borrados} mensajes")
        
        return {
            "exito": True,
            "sesiones_borradas": sesiones_borradas,
            "mensajes_borrados": mensajes_borrados,
            "mensaje": f"Cleaned {sesiones_borradas} sessions"
        }
    
    except Exception as e:
        logger.error(f"❌ Error en cleanup: {str(e)}")
        return {
            "exito": False,
            "mensaje": str(e)
        }


# ============================================================================
# 🧪 TEST DE CONEXIÓN
# ============================================================================

if settings.DEBUG:
    logger.info("🧪 Testando conexión a BD...")
    result = check_db_connection()
    if result["conectado"]:
        logger.info(f"✅ {result['mensaje']}")
    else:
        logger.warning(f"⚠️  {result['mensaje']}")