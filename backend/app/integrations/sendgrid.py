# app/integrations/sendgrid.py
"""
INTEGRACIÓN SENDGRID
Envía emails transaccionales (confirmaciones, recordatorios, etc).

¿Para qué?
- Confirmación de contacto
- Recordatorio de cita
- Seguimiento automático
- Emails de bienvenida

Plan gratuito: 100 emails/día

Setup:
1. Registrate en https://sendgrid.com (gratuito)
2. Verifica email
3. Copia API Key al .env
"""

import logging
from typing import List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# 📧 FUNCIÓN PRINCIPAL: ENVIAR EMAIL CON SENDGRID
# ============================================================================

async def send_email_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    from_email: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None
) -> bool:
    """
    Envía un email usando SendGrid API.
    
    Parámetros:
    - to_email: Email del destinatario
    - subject: Asunto del email
    - html_content: Contenido en HTML
    - text_content: Versión en texto plano (opcional)
    - from_email: Quién envía (default: settings.SENDGRID_FROM_EMAIL)
    - cc: Lista de emails en copia
    - bcc: Lista de emails en copia oculta
    
    Retorna:
    - True si se envió exitosamente
    - False si hubo error
    
    Ejemplo:
    await send_email_sendgrid(
        to_email="juan@empresa.com",
        subject="Bienvenido a nuestro servicio",
        html_content="<h1>Hola Juan</h1><p>Gracias por contactarnos</p>"
    )
    """
    
    # Validación
    if not settings.SENDGRID_API_KEY:
        logger.error("❌ SENDGRID_API_KEY no configurada")
        return False
    
    if not from_email:
        from_email = settings.SENDGRID_FROM_EMAIL
    
    if not from_email:
        logger.error("❌ SENDGRID_FROM_EMAIL no configurada")
        return False
    
    # URL del API de SendGrid
    url = "https://api.sendgrid.com/v3/mail/send"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Construir payload
    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": from_email,
            "name": "Luciano Valinoti - IT Specialist"
        },
        "content": [
            {
                "type": "text/html",
                "value": html_content
            }
        ]
    }
    
    # Agregar texto plano si viene
    if text_content:
        payload["content"].append({
            "type": "text/plain",
            "value": text_content
        })
    
    # Agregar CC si viene
    if cc:
        payload["personalizations"][0]["cc"] = [{"email": email} for email in cc]
    
    # Agregar BCC si viene
    if bcc:
        payload["personalizations"][0]["bcc"] = [{"email": email} for email in bcc]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Email enviado a {to_email}")
                return True
            else:
                logger.error(f"❌ Error SendGrid: {response.status_code} - {response.text}")
                return False
    
    except httpx.TimeoutException:
        logger.error("❌ Timeout conectando a SendGrid")
        return False
    except Exception as e:
        logger.error(f"❌ Error enviando email: {str(e)}")
        return False


# ============================================================================
# 📨 FUNCIÓN: CONFIRMACIÓN AL USUARIO (Formulario)
# ============================================================================

async def send_email_confirmacion_usuario(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str
) -> bool:
    """
    Envía email de confirmación al usuario después de llenar el formulario.
    
    El usuario recibe:
    - Confirmación de que recibiste su mensaje
    - Sus datos
    - Links rápidos para contactar (WhatsApp, email)
    """
    
    # Sanitizar datos
    nombre = nombre.replace("<", "&lt;").replace(">", "&gt;")
    email = email.replace("<", "&lt;").replace(">", "&gt;")
    mensaje = mensaje.replace("<", "&lt;").replace(">", "&gt;")
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #22c55e; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">¡Hola {nombre}!</h1>
        </div>
        
        <!-- Body -->
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            
            <p style="font-size: 16px; line-height: 1.6;">
                Gracias por contactarme. He recibido tu mensaje correctamente.
            </p>
            
            <div style="background: white; padding: 20px; border-left: 5px solid #22c55e; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 0; color: #666;"><strong>Tu mensaje:</strong></p>
                <p style="margin: 10px 0 0 0; color: #333; font-style: italic;">"{mensaje}"</p>
            </div>
            
            <p style="font-size: 14px; color: #666;"><strong>Tus datos de contacto:</strong></p>
            <ul style="margin: 10px 0 20px 0; padding-left: 20px;">
                <li style="margin: 5px 0;">📧 Email: <strong>{email}</strong></li>
                <li style="margin: 5px 0;">📱 WhatsApp: <strong>{telefono}</strong></li>
            </ul>
            
            <p style="font-size: 14px; color: #666; line-height: 1.6;">
                Me pondré en contacto contigo a la brevedad para analizar cómo podemos automatizar tus procesos 
                y mejorar la eficiencia de tu empresa.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 14px; color: #666; margin: 15px 0;">
                <strong>¿Necesitas contactarme de inmediato?</strong>
            </p>
            
            <div style="text-align: center; margin: 20px 0;">
                <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}" 
                   style="display: inline-block; background: #25D366; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px; margin-bottom: 10px;">
                    📱 Contactar por WhatsApp
                </a>
                <a href="mailto:lucianovalinoti@gmail.com?subject=Re:%20tu%20consulta" 
                   style="display: inline-block; background: #0066cc; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    📧 Escribir Email
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 12px; color: #999; margin: 20px 0 0 0;">
                Saludos,<br>
                <strong>Luciano Valinoti</strong><br>
                <em>Especialista en Automatización IT</em><br>
                📍 Córdoba, Argentina
            </p>
        </div>
        
    </div>
    """
    
    return await send_email_sendgrid(
        to_email=email,
        subject=f"Recibí tu consulta - {nombre}",
        html_content=html_content
    )


# ============================================================================
# 📨 FUNCIÓN: NOTIFICACIÓN AL ADMIN (Nuevo Lead)
# ============================================================================

async def send_email_nuevo_lead_admin(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int,
    origen: str = "formulario_landing"
) -> bool:
    """
    Notifica al admin (Luciano) cuando llega un nuevo lead.
    
    El admin recibe:
    - Detalles completos del lead
    - Botones rápidos para responder (WhatsApp, email)
    - Score del lead
    """
    
    # Sanitizar
    nombre = nombre.replace("<", "&lt;").replace(">", "&gt;")
    email = email.replace("<", "&lt;").replace(">", "&gt;")
    mensaje = mensaje.replace("<", "&lt;").replace(">", "&gt;")
    
    # Color según score
    if lead_score >= 80:
        color_score = "#22c55e"  # Verde
        emoji_score = "🔥"
    elif lead_score >= 60:
        color_score = "#f59e0b"  # Naranja
        emoji_score = "⭐"
    else:
        color_score = "#ef4444"  # Rojo
        emoji_score = "⚡"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #22c55e; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">🚀 NUEVO LEAD DETECTADO</h1>
            <p style="margin: 10px 0 0 0; font-size: 14px;">Formulario de {origen.replace('_', ' ').title()}</p>
        </div>
        
        <!-- Body -->
        <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #eee;">
            
            <!-- Información del lead -->
            <table style="width: 100%; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; background: #f9f9f9; font-weight: bold; width: 120px;">👤 Nombre:</td>
                    <td style="padding: 10px;">{nombre}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">📧 Email:</td>
                    <td style="padding: 10px;"><a href="mailto:{email}" style="color: #0066cc;">{email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">📱 Teléfono:</td>
                    <td style="padding: 10px;">
                        <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}" style="color: #25D366;">
                            {telefono} (WhatsApp)
                        </a>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">💬 Mensaje:</td>
                    <td style="padding: 10px;"><em>{mensaje[:150]}...</em></td>
                </tr>
                <tr>
                    <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">⭐ Score:</td>
                    <td style="padding: 10px;">
                        <span style="background: {color_score}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">
                            {emoji_score} {lead_score}/100
                        </span>
                    </td>
                </tr>
            </table>
            
            <!-- Botones de acción -->
            <div style="text-align: center; margin: 30px 0; padding: 20px; background: #f0f9ff; border-radius: 10px;">
                <p style="margin: 0 0 15px 0; font-size: 14px; color: #666;"><strong>Acciones rápidas:</strong></p>
                <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}?text=Hola%20{nombre.replace(' ', '%20')},%20vi%20tu%20consulta" 
                   style="display: inline-block; background: #25D366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-right: 10px; margin-bottom: 10px;">
                    📲 RESPONDER POR WHATSAPP
                </a>
                <a href="mailto:{email}?subject=Re:%20tu%20consulta%20sobre%20automatizaci%C3%B3n" 
                   style="display: inline-block; background: #0066cc; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    📧 RESPONDER POR EMAIL
                </a>
            </div>
            
            <!-- Footer -->
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 12px; color: #999; margin: 10px 0;">
                <strong>💡 Tip:</strong> Responde en las próximas 2 horas para maximizar las chances de conversión.
            </p>
            
        </div>
        
    </div>
    """
    
    return await send_email_sendgrid(
        to_email=settings.SENDGRID_FROM_EMAIL,  # A ti mismo
        subject=f"🚀 NUEVO LEAD: {nombre}",
        html_content=html_content
    )


# ============================================================================
# ⏰ FUNCIÓN: RECORDATORIO DE CITA
# ============================================================================

async def send_email_recordatorio_cita(
    nombre: str,
    email: str,
    fecha_cita: str,
    hora_cita: str,
    enlace_meet: Optional[str] = None
) -> bool:
    """
    Envía recordatorio de cita 24 horas antes.
    
    Parámetros:
    - nombre: Nombre del contacto
    - email: Email del contacto
    - fecha_cita: Fecha (ej: "05 de Febrero 2025")
    - hora_cita: Hora (ej: "15:00 hs")
    - enlace_meet: URL de Google Meet (opcional)
    """
    
    nombre = nombre.replace("<", "&lt;").replace(">", "&gt;")
    
    enlace_html = ""
    if enlace_meet:
        enlace_html = f"""
        <p style="text-align: center; margin: 20px 0;">
            <a href="{enlace_meet}" 
               style="display: inline-block; background: #4285F4; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                🎥 UNIRSE A LA LLAMADA (Google Meet)
            </a>
        </p>
        """
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #22c55e; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 24px;">📅 RECORDATORIO DE CITA</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            
            <p>¡Hola {nombre}!</p>
            
            <p>Te recordamos que tenemos una cita agendada:</p>
            
            <div style="background: white; padding: 20px; border-left: 5px solid #22c55e; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 5px 0;"><strong>📅 Fecha:</strong> {fecha_cita}</p>
                <p style="margin: 5px 0;"><strong>⏰ Hora:</strong> {hora_cita} (Hora Argentina)</p>
            </div>
            
            {enlace_html}
            
            <p style="color: #666;">
                Si necesitas reagendar o cancelar, simplemente responde este email.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 12px; color: #999;">
                Luciano Valinoti<br>
                Especialista en Automatización IT
            </p>
        </div>
        
    </div>
    """
    
    return await send_email_sendgrid(
        to_email=email,
        subject=f"⏰ Recordatorio: Cita el {fecha_cita} a las {hora_cita}",
        html_content=html_content
    )


# ============================================================================
# 🧪 FUNCIÓN: TEST DE CONEXIÓN
# ============================================================================

async def test_conexion_sendgrid() -> dict:
    """
    Testa que la configuración de SendGrid sea correcta.
    
    Retorna:
    {
        "conectado": True,
        "email_from": "lucianovalinoti@gmail.com",
        "mensaje": "✅ Conexión exitosa"
    }
    """
    
    if not settings.SENDGRID_API_KEY:
        return {
            "conectado": False,
            "mensaje": "❌ SENDGRID_API_KEY no configurada"
        }
    
    if not settings.SENDGRID_FROM_EMAIL:
        return {
            "conectado": False,
            "mensaje": "❌ SENDGRID_FROM_EMAIL no configurada"
        }
    
    # Enviar email de prueba
    success = await send_email_sendgrid(
        to_email=settings.SENDGRID_FROM_EMAIL,
        subject="🧪 Email de prueba desde FastAPI",
        html_content="<h1>¡Hola!</h1><p>Si recibes esto, SendGrid está funcionando correctamente.</p>"
    )
    
    return {
        "conectado": success,
        "email_from": settings.SENDGRID_FROM_EMAIL,
        "mensaje": "✅ Conexión exitosa" if success else "❌ Error enviando email"
    }


# ============================================================================
# 📝 EJEMPLOS DE USO
# ============================================================================

"""
EJEMPLO 1: Confirmación al usuario
----
await send_email_confirmacion_usuario(
    nombre="Juan Pérez",
    email="juan@empresa.com",
    telefono="+54 9 351 123 4567",
    mensaje="Necesito automatizar facturas"
)

EJEMPLO 2: Notificación al admin
----
await send_email_nuevo_lead_admin(
    nombre="Juan Pérez",
    email="juan@empresa.com",
    telefono="+54 9 351 123 4567",
    mensaje="Necesito automatizar facturas",
    lead_score=85,
    origen="formulario_landing"
)

EJEMPLO 3: Recordatorio de cita
----
await send_email_recordatorio_cita(
    nombre="Juan Pérez",
    email="juan@empresa.com",
    fecha_cita="05 de Febrero 2025",
    hora_cita="15:00 hs",
    enlace_meet="https://meet.google.com/abc-def-ghi"
)

EJEMPLO 4: Email personalizado
----
await send_email_sendgrid(
    to_email="juan@empresa.com",
    subject="Tu propuesta de automatización",
    html_content="<h1>Hola Juan</h1><p>Aquí está tu propuesta...</p>"
)

EJEMPLO 5: Test de conexión
----
resultado = await test_conexion_sendgrid()
print(resultado)
# {"conectado": True, "email_from": "luciano@...", "mensaje": "✅ Conexión exitosa"}
"""