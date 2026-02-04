# app/integrations/telegram.py
"""
INTEGRACIÓN TELEGRAM - Notificaciones al admin (Luciano) por Telegram
"""

import httpx
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# 🤖 FUNCIÓN PRINCIPAL: ENVIAR MENSAJE A TELEGRAM
# ============================================================================

async def send_telegram_message(
    message: str,
    parse_mode: str = "HTML",
    disable_notification: bool = False
) -> bool:
    """
    Envía un mensaje de texto a Telegram.
    """
    
    if not settings.TELEGRAM_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("⚠️ TELEGRAM_TOKEN o TELEGRAM_CHAT_ID no configurados")
        return False
    
    if not message:
        logger.warning("⚠️ Mensaje vacío para Telegram")
        return False
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
        "disable_notification": disable_notification,
        "disable_web_page_preview": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                logger.info("✅ Mensaje Telegram enviado")
                return True
            else:
                logger.error(f"❌ Error Telegram: {response.text}")
                return False
    
    except httpx.TimeoutException:
        logger.error("❌ Timeout conectando a Telegram")
        return False
    except Exception as e:
        logger.error(f"❌ Error enviando Telegram: {str(e)}")
        return False


# ============================================================================
# 📊 FUNCIÓN: NOTIFICACIÓN DE NUEVO LEAD
# ============================================================================

async def notificar_nuevo_lead(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int,
    origen: str = "desconocido",
    tipo_cliente: str = "",
    problema: str = ""
) -> bool:
    """
    Notificación especifica cuando llega un nuevo lead del chatbot.
    
    Parámetros:
    - nombre: Nombre completo
    - email: Email del cliente
    - telefono: WhatsApp
    - mensaje: Servicio solicitado
    - lead_score: Score del lead (0-100)
    - origen: "chat" o "formulario_landing"
    - tipo_cliente: "Particular", "Comercio", "Oficina", "Empresa"
    - problema: Descripción del problema/necesidad
    """
    
    # Sanitizar entrada
    nombre = nombre.replace("<", "&lt;").replace(">", "&gt;").strip()
    email = email.replace("<", "&lt;").replace(">", "&gt;").strip()
    tipo_cliente = tipo_cliente.replace("<", "&lt;").replace(">", "&gt;").strip()
    problema = problema.replace("<", "&lt;").replace(">", "&gt;")[:150]
    mensaje = mensaje.replace("<", "&lt;").replace(">", "&gt;")[:100]
    
    # Validar que tenemos al menos nombre
    if not nombre or nombre.lower() == "usuario del chat":
        nombre = "Cliente Chatbot"
    
    # Emoji según score
    if lead_score >= 80:
        emoji_score = "🔥"
    elif lead_score >= 60:
        emoji_score = "⭐"
    else:
        emoji_score = "⚡"
    
    # Emoji según tipo de cliente
    emoji_tipo = {
        "Particular": "👤",
        "Comercio": "🏪",
        "Oficina": "🏢",
        "Empresa": "🏭"
    }.get(tipo_cliente, "💼")
    
    # Construir mensaje HTML
    mensaje_tg = f"""
<b>🚀 NUEVO LEAD - CHATBOT</b>

<b>👤 Nombre:</b> <code>{nombre}</code>
<b>📧 Email:</b> <code>{email}</code>
<b>📱 WhatsApp:</b> <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}">{telefono}</a>

<b>{emoji_tipo} Tipo:</b> {tipo_cliente if tipo_cliente else 'No especificado'}
<b>🎯 Servicio:</b> {mensaje}

<b>📝 Problema/Necesidad:</b>
<code>{problema if problema else 'No especificado'}</code>

<b>{emoji_score} Score:</b> <code>{lead_score}/100</code>
<b>📍 Origen:</b> {origen}

━━━━━━━━━━━━━━━━━━━━━━
<a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}?text=Hola%20{nombre.replace(' ', '%20')}%2C%20soy%20Luciano.%20Recib%C3%AD%20tu%20consulta.">📲 RESPONDER WHATSAPP</a> | <a href="mailto:{email}">📧 EMAIL</a>
"""
    
    return await send_telegram_message(mensaje_tg)


# ============================================================================
# ⚠️ FUNCIÓN: NOTIFICACIÓN DE ALERTA
# ============================================================================

async def notificar_alerta(
    titulo: str,
    descripcion: str,
    gravedad: str = "normal"
) -> bool:
    """
    Notificación de alerta/error.
    
    Parámetros:
    - titulo: Título de la alerta
    - descripcion: Descripción completa
    - gravedad: "baja", "normal", "alta", "crítica"
    """
    
    emojis = {
        "baja": "ℹ️",
        "normal": "⚠️",
        "alta": "🔴",
        "crítica": "🚨"
    }
    emoji = emojis.get(gravedad, "⚠️")
    
    titulo = titulo.replace("<", "&lt;").replace(">", "&gt;")
    descripcion = descripcion.replace("<", "&lt;").replace(">", "&gt;")
    
    mensaje_tg = f"""
<b>{emoji} ALERTA</b>

<b>Título:</b> {titulo}
<b>Descripción:</b> {descripcion}
<b>Gravedad:</b> {gravedad.upper()}

<i>⏰ {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
    
    return await send_telegram_message(
        mensaje_tg,
        disable_notification=(gravedad == "baja")
    )


# ============================================================================
# 📊 FUNCIÓN: REPORTE DIARIO
# ============================================================================

async def enviar_reporte_diario(
    total_leads_hoy: int,
    conversiones_hoy: int,
    score_promedio: float
) -> bool:
    """
    Reporte diario de métricas.
    """
    
    mensaje_tg = f"""
<b>📊 REPORTE DIARIO</b>

<b>📈 Métricas de hoy:</b>
  • Nuevos leads: <code>{total_leads_hoy}</code>
  • Conversiones: <code>{conversiones_hoy}</code>
  • Score promedio: <code>{score_promedio:.1f}/100</code>

<b>Tasa de conversión:</b> <code>{(conversiones_hoy/max(total_leads_hoy,1)*100):.1f}%</code>

<i>⏰ {__import__('datetime').datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
    
    return await send_telegram_message(mensaje_tg)