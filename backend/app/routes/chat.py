# app/routes/chat.py

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import uuid
import re
from datetime import datetime
import logging

from app.database import get_db
from app.schemas import ChatQuery
from app.models.lead import ChatSession, ChatHistory
from app.ai.chat import get_chatbot_response
from app.ai.lead_scorer import score_lead
from app.integrations.telegram import notificar_nuevo_lead
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# ============================================================================
# 📌 ENDPOINT PRINCIPAL: POST /api/chat - CON RATE LIMITING
# ============================================================================

@router.post("/chat")
async def chat_endpoint(
    request: Request,
    query: ChatQuery,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal del chatbot.
    
    Rate Limit: 10 requests por minuto
    """
    
    # Aplicar rate limiting manual (extra seguridad)
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # 1️⃣ Validar mensaje
        if not query.message or len(query.message) > 1000:
            logger.warning(f"⚠️ Mensaje inválido desde {client_ip}")
            return {
                "status": "error",
                "response": "Mensaje debe tener entre 1 y 1000 caracteres.",
                "session_id": query.session_id or None
            }
        
        # 2️⃣ Generar o recuperar session_id
        session_id = query.session_id or str(uuid.uuid4())
        
        # 3️⃣ Recuperar sesión existente o crear nueva
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.flush()
        
        # 4️⃣ Recuperar historial de esta sesión (CON LÍMITE)
        history_records = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).limit(settings.CHAT_HISTORY_LIMIT).all()
        
        # Intercalar respuestas del bot
        history_with_bot = []
        for h in history_records:
            history_with_bot.append({"role": "user", "content": h.mensaje_usuario})
            history_with_bot.append({"role": "assistant", "content": h.respuesta_bot})
        
        # 5️⃣ Llamar a Groq para obtener respuesta
        response_text = get_chatbot_response(query.message, history_with_bot)
        
        # 6️⃣ Calcular score
        lead_score = score_lead(query.message)
        
        # 7️⃣ EXTRAER DATOS DEL HISTORIAL COMPLETO
        all_messages = " ".join([h.mensaje_usuario for h in history_records]) + " " + query.message
        contact_info = extract_contact_info(all_messages)
        
        # 8️⃣ Guardar en base de datos
        chat_history = ChatHistory(
            session_id=session_id,
            mensaje_usuario=query.message,
            respuesta_bot=response_text,
            lead_score=lead_score
        )
        db.add(chat_history)
        
        # 9️⃣ NOTIFICAR - Solo si tiene datos completos
        if contact_info.get("nombre") and contact_info.get("email") and contact_info.get("telefono"):
            servicio = contact_info.get("servicio", "No especificado")
            
            background_tasks.add_task(
                notificar_nuevo_lead,
                nombre=contact_info.get("nombre"),
                email=contact_info.get("email"),
                telefono=contact_info.get("telefono"),
                mensaje=servicio,
                lead_score=lead_score,
                origen="chat",
                tipo_cliente=contact_info.get("tipo_cliente", ""),
                problema=contact_info.get("problema", "")
            )
            
            logger.info(f"✅ Lead capturado: {contact_info.get('nombre')} ({contact_info.get('tipo_cliente')}) - {contact_info.get('telefono')}")
        
        db.commit()
        
        # 🔟 Responder al frontend - SIN EXPONER INFORMACIÓN SENSIBLE
        return {
            "status": "success",
            "response": response_text,
            "session_id": session_id,
            "lead_score": lead_score,
            "is_lead": len(contact_info.get("telefono", "")) > 5,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"❌ Error en /api/chat desde {client_ip}: {str(e)}")
        
        # En producción, NO exponer detalles
        if settings.ENVIRONMENT == "production":
            return {
                "status": "error",
                "response": "Error procesando tu mensaje. Intenta de nuevo.",
                "session_id": query.session_id if hasattr(query, 'session_id') else None
            }
        else:
            return {
                "status": "error",
                "response": f"Error: {str(e)}",
                "session_id": query.session_id if hasattr(query, 'session_id') else None
            }


# ============================================================================
# 🔧 FUNCIÓN: EXTRAER INFORMACIÓN DE CONTACTO
# ============================================================================

def extract_contact_info(message: str) -> dict:
    """
    Extrae nombre, email, teléfono, tipo de cliente y problema del mensaje.
    Formato esperado: nombre | email | tipoCliente | problema | telefono | Interesado en: servicio
    """
    contact = {
        "nombre": "",
        "email": "",
        "telefono": "",
        "tipo_cliente": "",
        "problema": "",
        "servicio": ""
    }
    
    try:
        # 1️⃣ INTENTAR PARSEAR FORMATO NUEVO
        if " | " in message:
            partes = message.split(" | ")
            
            if len(partes) >= 6:
                # Validar y sanitizar cada campo
                contact["nombre"] = partes[0].strip()[:100]  # Máximo 100 caracteres
                contact["email"] = partes[1].strip()[:255]
                contact["tipo_cliente"] = partes[2].strip()[:50]
                contact["problema"] = partes[3].strip()[:500]
                contact["telefono"] = partes[4].strip()[:20]
                
                # Extraer servicio
                servicio_parte = partes[5].strip()
                if "Interesado en:" in servicio_parte:
                    contact["servicio"] = servicio_parte.replace("Interesado en:", "").strip()[:100]
                
                logger.info(f"✅ Parseado formato nuevo: {contact['nombre']}")
                return contact
    
    except Exception as e:
        logger.error(f"⚠️ Error parseando contacto: {str(e)}")
    
    # 2️⃣ FALLBACK: Extraer manualmente
    
    # EMAIL - Validación regex
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, message)
    if email_match:
        contact["email"] = email_match.group()[:255]
    
    # TELÉFONO - Validación múltiple
    phone_patterns = [
        r'\+\d{1,3}\s?\d{1,4}\s?\d{1,4}\s?\d{1,4}',
        r'\+\d{1,3}\s?\d{7,14}',
        r'(?:^|\s)(\d{2,4}\s?\d{3,4}\s?\d{4})',
        r'3\d{9}',
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, message)
        if phone_match:
            telefono = phone_match.group().strip()
            digitos = re.sub(r'\D', '', telefono)
            if len(digitos) >= 8:
                contact["telefono"] = telefono[:20]
                break
    
    # NOMBRE - Validación
    words = message.split()
    palabras_excluir = [
        "interesado", "en:", "automatización", "seguridad", "soporte", 
        "consulta", "hola", "perfecto", "gracias", "particular", "comercio"
    ]
    
    for word in words:
        clean_word = word.replace(",", "").replace(".", "").replace("!", "").replace("?", "")
        
        if (clean_word and 
            clean_word[0].isupper() and 
            len(clean_word) > 2 and 
            clean_word.lower() not in palabras_excluir and
            not any(char.isdigit() for char in clean_word) and
            '@' not in clean_word):
            
            contact["nombre"] = clean_word[:100]
            break
    
    # TIPO DE CLIENTE
    tipo_patterns = {
        "Particular": ["particular", "autónomo"],
        "Comercio": ["comercio"],
        "Oficina": ["oficina"],
        "Empresa": ["empresa"]
    }
    
    message_lower = message.lower()
    for tipo, palabras in tipo_patterns.items():
        if any(p in message_lower for p in palabras):
            contact["tipo_cliente"] = tipo
            break
    
    # SERVICIO
    servicio_patterns = {
        "Automatización": ["automatización", "automatizar"],
        "Seguridad IT": ["seguridad"],
        "Soporte IT": ["soporte"],
        "Consulta General": ["consulta"]
    }
    
    for servicio, palabras in servicio_patterns.items():
        if any(p in message_lower for p in palabras):
            contact["servicio"] = servicio
            break
    
    return contact


# ============================================================================
# 📊 ENDPOINTS ADICIONALES - CON VALIDACIONES
# ============================================================================

@router.get("/chat/sessions")
async def get_sessions(
    request: Request,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Obtiene las últimas N sesiones de chat.
    Límite máximo: 100
    """
    try:
        # Validar limit (prevenir DoS)
        limit = min(int(limit), 100)
        limit = max(limit, 1)
        
        sessions = db.query(ChatSession).order_by(
            ChatSession.fecha_creacion.desc()
        ).limit(limit).all()
        
        return {
            "status": "success",
            "total": len(sessions),
            "sessions": [
                {
                    "session_id": s.session_id,
                    "fecha": s.fecha_creacion.isoformat(),
                    "mensajes": len(db.query(ChatHistory).filter(
                        ChatHistory.session_id == s.session_id
                    ).all())
                }
                for s in sessions
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error en GET /api/chat/sessions: {str(e)}")
        return {
            "status": "error",
            "message": "Error obteniendo sesiones."
        }


@router.get("/chat/sessions/{session_id}")
async def get_session_history(
    request: Request,
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial completo de una sesión.
    session_id debe tener formato válido (uuid).
    """
    try:
        # Validar formato session_id básico
        if len(session_id) > 100:
            return {
                "status": "error",
                "message": "Session ID inválido."
            }
        
        history = db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id
        ).limit(100).all()
        
        if not history:
            return {
                "status": "not_found",
                "message": "Sesión no encontrada"
            }
        
        return {
            "status": "success",
            "session_id": session_id,
            "total_mensajes": len(history),
            "messages": [
                {
                    "user": h.mensaje_usuario[:500],  # Limitar size
                    "bot": h.respuesta_bot[:500],
                    "score": h.lead_score,
                    "timestamp": h.fecha.isoformat()
                }
                for h in history
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error en GET /api/chat/sessions/{{id}}: {str(e)}")
        return {
            "status": "error",
            "message": "Error obteniendo historial."
        }


@router.get("/health")
async def health_check():
    """Health check para monitoreo."""
    return {"status": "ok", "service": "chat_api"}