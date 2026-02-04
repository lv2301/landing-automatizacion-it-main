# app/config.py
"""
CONFIGURACIÓN CENTRALIZADA - VERSIÓN SEGURA PARA PRODUCCIÓN
Todas las variables de entorno en un lugar.
"""

import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

class Settings:
    """
    Clase que agrupa TODAS las configuraciones.
    Accedible desde cualquier parte como: from app.config import settings; settings.GROQ_API_KEY
    """
    
    # ========================================================================
    # 🎯 INFORMACIÓN DEL PROYECTO
    # ========================================================================
    PROJECT_NAME: str = "Luciano Valinoti - IT Automation API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # ========================================================================
    # 🌐 CONFIGURACIÓN DEL SERVIDOR
    # ========================================================================
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8001))
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    
    # ========================================================================
    # 🤖 GROQ API (LLM - Chatbot IA) - CRÍTICO
    # ========================================================================
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.6
    GROQ_MAX_TOKENS: int = 250
    
    # Validación crítica
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY no está configurada en .env - REQUERIDA")
    
    # ========================================================================
    # 🗄️ BASE DE DATOS - SEGURA
    # ========================================================================
    DATABASE_TYPE: str = os.getenv("DATABASE_TYPE", "sqlite")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app/proyectos.db"
    )
    
    # Validación
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL no configurada en .env")
    
    # ========================================================================
    # 📧 EMAIL - SENDGRID (Recomendado)
    # ========================================================================
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "")
    
    # Email alternativo: Gmail SMTP
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    # ========================================================================
    # 💬 TWILIO (WhatsApp)
    # ========================================================================
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")
    TWILIO_WEBHOOK_URL: str = os.getenv("TWILIO_WEBHOOK_URL", "")
    
    # ========================================================================
    # 🤖 TELEGRAM (Notificaciones al Admin) - CRÍTICO
    # ========================================================================
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("❌ TELEGRAM_TOKEN y TELEGRAM_CHAT_ID son REQUERIDAS")
    
    # ========================================================================
    # 📊 AIRTABLE (CRM Gratuito)
    # ========================================================================
    AIRTABLE_TOKEN: str = os.getenv("AIRTABLE_TOKEN", "")
    AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
    AIRTABLE_TABLE_LEADS: str = "Leads"
    AIRTABLE_TABLE_SESSIONS: str = "Sessions"
    
    # ========================================================================
    # 🗓️ GOOGLE CALENDAR
    # ========================================================================
    GOOGLE_CALENDAR_CREDENTIALS: str = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS",
        ".secrets/google_calendar.json"
    )
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    
    # ========================================================================
    # 🔗 n8n WEBHOOK
    # ========================================================================
    N8N_WEBHOOK_URL: str = os.getenv(
        "N8N_WEBHOOK_URL",
        "http://localhost:5678/webhook/lead-manager"
    )
    N8N_TIMEOUT: float = 2.0
    
    # ========================================================================
    # 🔐 SEGURIDAD - CRÍTICO PARA PRODUCCIÓN
    # ========================================================================
    
    # SECRET KEY - DEBE ESTAR EN .env EN PRODUCCIÓN
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    if not SECRET_KEY and ENVIRONMENT == "production":
        raise ValueError("❌ SECRET_KEY es REQUERIDA en producción - No usar default!")
    
    if not SECRET_KEY:
        # En desarrollo, usar default débil (pero advertencia)
        SECRET_KEY = "dev-secret-key-only-for-development-change-in-production"
        print("⚠️  ADVERTENCIA: Usando SECRET_KEY débil en desarrollo")
    
    # ALLOWED ORIGINS - DESDE .env
    _allowed_origins_str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
    )
    ALLOWED_ORIGINS: list = [origin.strip() for origin in _allowed_origins_str.split(",")]
    
    # Validar CORS en producción
    if ENVIRONMENT == "production":
        if "localhost" in str(ALLOWED_ORIGINS) or "127.0.0.1" in str(ALLOWED_ORIGINS):
            raise ValueError("❌ ALLOWED_ORIGINS en producción no puede contener localhost!")
    
    # ========================================================================
    # 📊 LEAD SCORING
    # ========================================================================
    LEAD_SCORE_MIN_AGENDABLE: int = 70
    LEAD_SCORE_CONTACTABLE: int = 50
    
    # ========================================================================
    # ⏰ TIEMPOS
    # ========================================================================
    CHAT_HISTORY_LIMIT: int = 6
    SESSION_TIMEOUT: int = 3600
    FOLLOW_UP_DELAY_HOURS: int = 24
    
    # ========================================================================
    # 📝 LOGGING
    # ========================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if ENVIRONMENT == "production" else "DEBUG")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # ========================================================================
    # 🚦 RATE LIMITING
    # ========================================================================
    RATE_LIMIT_CHAT: str = "10/minute"  # Max 10 requests por minuto
    RATE_LIMIT_CONTACT: str = "5/minute"  # Max 5 requests por minuto
    RATE_LIMIT_GENERAL: str = "100/hour"  # Max 100 requests por hora

# Crear instancia global
settings = Settings()

# ============================================================================
# 🧪 VALIDACIÓN DE SETUP
# ============================================================================
def validate_setup():
    """
    Verifica que todas las variables críticas estén configuradas.
    Llama esto en main.py al inicio.
    """
    print("\n" + "="*70)
    print("🔐 VERIFICACIÓN DE SEGURIDAD")
    print("="*70)
    
    checks = {
        "DEBUG": not settings.DEBUG,  # Debe ser False
        "GROQ_API_KEY": bool(settings.GROQ_API_KEY),
        "TELEGRAM_TOKEN": bool(settings.TELEGRAM_TOKEN),
        "TELEGRAM_CHAT_ID": bool(settings.TELEGRAM_CHAT_ID),
        "SECRET_KEY": bool(settings.SECRET_KEY) and settings.SECRET_KEY != "dev-secret-key-only-for-development-change-in-production",
        "DATABASE_URL": bool(settings.DATABASE_URL),
    }
    
    all_ok = True
    for check_name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result and check_name in ["GROQ_API_KEY", "TELEGRAM_TOKEN"]:
            all_ok = False
    
    print("="*70 + "\n")
    
    if not all_ok:
        raise ValueError("❌ Validación fallida. Revisa tu .env")
    
    return True

# ============================================================================
# 🌐 INFORMACIÓN PARA DEBUGGING
# ============================================================================
def get_environment_info():
    """Retorna info del entorno (sin secrets)"""
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_type": settings.DATABASE_TYPE,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "telegram_configured": bool(settings.TELEGRAM_TOKEN),
        "allowed_origins": settings.ALLOWED_ORIGINS,
    }