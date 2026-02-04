# app/main.py
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# IMPORTAR MODELOS (CRÍTICO)
from app.models.lead import Base, ChatSession, ChatHistory, Lead
from app.config import settings, validate_setup
from app.database import engine

# Crear todas las tablas
Base.metadata.create_all(bind=engine)
print("✅ Tablas creadas correctamente")

# ============================================================================
# 🔐 VALIDAR SETUP DE SEGURIDAD
# ============================================================================
try:
    validate_setup()
except ValueError as e:
    print(f"❌ Error de configuración: {e}")
    sys.exit(1)

# ============================================================================
# 📝 CONFIGURAR LOGGING
# ============================================================================
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# ============================================================================
# 🚀 CREAR APP FASTAPI
# ============================================================================

# En producción, deshabilitar documentación interactiva
docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"
openapi_url = None if settings.ENVIRONMENT == "production" else "/openapi.json"

app = FastAPI(
    title="Luciano IT API",
    description="Backend para Landing Page de Servicios IT",
    version="1.0.0",
    docs_url=docs_url,
    redoc_url=redoc_url,
    openapi_url=openapi_url,
)

# ============================================================================
# 🚦 RATE LIMITING - PROTEGE CONTRA ATAQUES
# ============================================================================
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Manejo de limite de rate"""
    logger.warning(f"⚠️ Rate limit excedido desde {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "status": "error",
            "message": "Demasiadas solicitudes. Intenta más tarde.",
            "retry_after": 60
        }
    )

# ============================================================================
# 🔐 CORS - MUY IMPORTANTE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # ✅ Solo necesarios
    allow_headers=["Content-Type"],  # ✅ Restringido
)

# ============================================================================
# 📌 REGISTRAR ROUTERS
# ============================================================================
from app.routes.chat import router as chat_router
from app.routes.contact import router as contact_router
from app.routes.leads import router as leads_router

app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(contact_router, prefix="/api", tags=["Contact"])
app.include_router(leads_router, prefix="/api", tags=["Leads"])

# ============================================================================
# 📌 ENDPOINTS DE HEALTH CHECK
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raíz para verificar que el servidor está vivo."""
    return {
        "status": "ok",
        "message": "Servidor Luciano IT API funcionando",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/health")
@limiter.limit("100/minute")
async def health(request: Request):
    """Health check endpoint para monitoreo."""
    return {
        "status": "healthy",
        "service": "luciano-it-backend",
        "environment": settings.ENVIRONMENT,
    }

@app.get("/api/health")
@limiter.limit("100/minute")
async def api_health(request: Request):
    """Health check endpoint para frontend."""
    return {
        "status": "ok",
        "message": "Backend conectado",
        "environment": settings.ENVIRONMENT,
    }

# ============================================================================
# ⚠️ ERROR HANDLERS - SIN EXPONER INFORMACIÓN
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejo global de excepciones.
    ✅ NO expone detalles internos en producción
    """
    error_id = f"{request.client.host}:{id(exc)}"
    logger.error(f"❌ Error [{error_id}]: {str(exc)}", exc_info=True)
    
    # En producción, respuesta genérica
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Error procesando tu solicitud. Intenta más tarde."
            }
        )
    # En desarrollo, mostrar error completo
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(exc),
                "type": type(exc).__name__,
                "error_id": error_id
            }
        )

# ============================================================================
# 🔄 STARTUP Y SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup():
    """Eventos al iniciar"""
    logger.info("✅ Backend iniciado correctamente")
    logger.info(f"🌍 Entorno: {settings.ENVIRONMENT}")
    logger.info(f"📊 CORS habilitado para: {', '.join(settings.ALLOWED_ORIGINS)}")
    
    if settings.ENVIRONMENT == "development":
        logger.info(f"📚 Documentación en: http://localhost:{settings.PORT}/docs")
    else:
        logger.info("🔐 Documentación deshabilitada en producción")

@app.on_event("shutdown")
async def shutdown():
    """Eventos al detener"""
    logger.info("❌ Backend detenido")

# ============================================================================
# 🔒 MIDDLEWARE ADICIONAL DE SEGURIDAD
# ============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Agregar headers de seguridad"""
    response = await call_next(request)
    
    # Headers de seguridad
    response.headers["X-Content-Type-Options"] = "nosniff"  # Prevenir MIME type sniffing
    response.headers["X-Frame-Options"] = "DENY"  # Prevenir clickjacking
    response.headers["X-XSS-Protection"] = "1; mode=block"  # XSS protection
    
    # No revelar versión de servidor
    response.headers.pop("server", None)
    
    return response

# ============================================================================
# 🏃 RUN (solo para desarrollo local)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )