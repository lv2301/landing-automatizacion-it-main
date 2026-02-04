# app/routes/contact.py
"""
ENDPOINT DEL FORMULARIO DE CONTACTO
POST /api/contact - Recibe formularios del landing page

Flujo:
1. Usuario completa formulario en la landing
2. Frontend envía datos a /api/contact
3. Se valida y guarda en BD
4. Se envía email de confirmación (usuario + admin)
5. Se notifica por Telegram (al admin)
6. Se dispara webhook a n8n (para agendar cita)
7. Respuesta al frontend
"""

import os
import json
import httpx
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ContactForm
from app.models.lead import Lead
from app.ai.lead_scorer import score_lead
from app.config import settings
from app.integrations.telegram import send_telegram_message
from app.integrations.sendgrid import send_email_sendgrid
from app.integrations.airtable import save_lead_to_airtable

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# ============================================================================
# 📌 POST /api/contact - ENDPOINT PRINCIPAL DEL FORMULARIO
# ============================================================================

@router.post("/contact")
async def contact_submit(
    form: ContactForm,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recibe el formulario del landing page y procesa el lead.
    
    Request:
    {
        "name": "Juan Pérez",
        "email": "juan@empresa.com",
        "phone": "+54 9 351 123 4567",
        "message": "Necesito automatizar facturas"
    }
    
    Response:
    {
        "status": "success",
        "lead_id": 42,
        "message": "Formulario recibido. Te contactaré pronto."
    }
    """
    
    try:
        # Paso 1: Validación básica
        # ====================================================================
        logger.info(f"📝 Nuevo formulario recibido: {form.name} ({form.email})")
        
        # Validar que el email no esté duplicado recientemente
        lead_existente = db.query(Lead).filter(
            Lead.email == form.email
        ).first()
        
        if lead_existente:
            logger.warning(f"⚠️  Lead duplicado: {form.email}")
            return {
                "status": "warning",
                "message": "Ya tenemos tu contacto. Te escribiré pronto."
            }
        
        # Paso 2: Calcular lead score
        # ====================================================================
        lead_score = score_lead(
            mensaje=form.message,
            tiene_contacto=True,  # Siempre es lead si llena el formulario
            tiene_intencion=True,
            historial_length=0
        )
        logger.info(f"⭐ Lead Score: {lead_score}/100")
        
        # Paso 3: Guardar en base de datos
        # ====================================================================
        nuevo_lead = Lead(
            nombre=form.name,
            email=form.email,
            phone=form.phone,
            mensaje=form.message,
            lead_score=lead_score,
            origen="formulario_landing"
        )
        db.add(nuevo_lead)
        db.commit()
        db.refresh(nuevo_lead)  # Obtener el ID asignado
        
        logger.info(f"✅ Lead guardado en BD con ID: {nuevo_lead.id}")
        
        # Paso 4: Procesar en background (no bloquear respuesta)
        # ====================================================================
        # Enviar emails
        background_tasks.add_task(
            enviar_emails,
            nombre=form.name,
            email=form.email,
            telefono=form.phone,
            mensaje=form.message
        )
        
        # Notificar Telegram
        background_tasks.add_task(
            notificar_telegram,
            nombre=form.name,
            email=form.email,
            telefono=form.phone,
            mensaje=form.message,
            lead_score=lead_score
        )
        
        # Guardar en Airtable
        background_tasks.add_task(
            guardar_airtable,
            nombre=form.name,
            email=form.email,
            telefono=form.phone,
            mensaje=form.message,
            lead_score=lead_score,
            fecha=datetime.utcnow().isoformat()
        )
        
        # Disparar webhook n8n
        background_tasks.add_task(
            dispara_webhook_n8n,
            nombre=form.name,
            email=form.email,
            telefono=form.phone,
            mensaje=form.message,
            lead_score=lead_score
        )
        
        # Paso 5: Respuesta inmediata al usuario
        # ====================================================================
        return {
            "status": "success",
            "lead_id": nuevo_lead.id,
            "message": f"¡Gracias {form.name}! Recibí tu mensaje. Te contactaré dentro de 24hs."
        }
    
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"❌ Error en contact_submit: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Error procesando el formulario. Intenta más tarde."
        )


# ============================================================================
# 📧 FUNCIÓN AUXILIAR: ENVIAR EMAILS
# ============================================================================

async def enviar_emails(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str
):
    """
    Envía 2 emails:
    1. Al usuario (confirmación)
    2. Al admin (notificación)
    """
    
    try:
        # Email 1: Confirmación para el usuario
        # ====================================================================
        html_usuario = f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2 style="color: #0f172a;">¡Hola {nombre}!</h2>
            
            <p>Gracias por contactarme. He recibido tu mensaje correctamente:</p>
            
            <blockquote style="background: #f9f9f9; padding: 15px; border-left: 5px solid #22c55e;">
                "{mensaje}"
            </blockquote>
            
            <p><strong>Tus datos:</strong></p>
            <ul>
                <li>📧 Email: {email}</li>
                <li>📱 WhatsApp: {telefono}</li>
            </ul>
            
            <p>Me pondré en contacto contigo a la brevedad para analizar cómo podemos automatizar tus procesos.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            
            <p><strong>Opciones rápidas:</strong></p>
            <ul>
                <li>📞 Llamarme: {telefono}</li>
                <li>💬 WhatsApp: <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}">Abrir chat</a></li>
            </ul>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            
            <p>Saludos,<br>
            <strong>Luciano Valinoti</strong><br>
            <em>Especialista en Automatización IT</em></p>
        </div>
        """
        
        await send_email_sendgrid(
            to_email=email,
            subject="Recibí tu consulta - Luciano Valinoti",
            html_content=html_usuario
        )
        logger.info(f"✅ Email de confirmación enviado a {email}")
        
        # Email 2: Notificación para el admin (Luciano)
        # ====================================================================
        html_admin = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; border: 1px solid #eee; border-radius: 10px; overflow: hidden;">
            
            <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #22c55e; padding: 20px; text-align: center;">
                <h2 style="margin: 0;">🚀 NUEVO LEAD DETECTADO</h2>
            </div>
            
            <div style="padding: 20px;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; background: #f9f9f9; font-weight: bold; width: 120px;">👤 Nombre:</td>
                        <td style="padding: 10px;">{nombre}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">📧 Email:</td>
                        <td style="padding: 10px;"><a href="mailto:{email}">{email}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">📱 Teléfono:</td>
                        <td style="padding: 10px;"><a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}">{telefono}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background: #f9f9f9; font-weight: bold;">💬 Mensaje:</td>
                        <td style="padding: 10px;">{mensaje}</td>
                    </tr>
                </table>
                
                <div style="margin-top: 20px; padding: 15px; background: #f0f9ff; border-left: 4px solid #22c55e;">
                    <p style="margin: 0;"><strong>⏰ Timestamp:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}?text=Hola%20{nombre},%20vi%20tu%20consulta..." 
                       style="display: inline-block; background: #25D366; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-right: 10px;">
                        📲 RESPONDER POR WHATSAPP
                    </a>
                    <a href="mailto:{email}" 
                       style="display: inline-block; background: #0066cc; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                        📧 RESPONDER POR EMAIL
                    </a>
                </div>
            </div>
        </div>
        """
        
        await send_email_sendgrid(
            to_email=settings.SENDGRID_FROM_EMAIL,  # A ti mismo (admin)
            subject=f"🚀 NUEVO LEAD: {nombre}",
            html_content=html_admin
        )
        logger.info(f"✅ Email de notificación enviado al admin")
    
    except Exception as e:
        logger.error(f"❌ Error enviando emails: {str(e)}")


# ============================================================================
# 🤖 FUNCIÓN AUXILIAR: NOTIFICAR TELEGRAM
# ============================================================================

async def notificar_telegram(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int
):
    """
    Envía notificación instantánea por Telegram al admin.
    """
    
    try:
        telegram_text = f"""
🚀 <b>NUEVO LEAD - FORMULARIO</b>

👤 <b>Nombre:</b> {nombre}
📧 <b>Email:</b> {email}
📱 <b>WhatsApp:</b> {telefono}
💬 <b>Mensaje:</b> {mensaje}
⭐ <b>Lead Score:</b> {lead_score}/100

<a href="https://wa.me/{telefono.replace('+', '').replace(' ', '')}">📲 WHATSAPP</a> | <a href="mailto:{email}">📧 EMAIL</a>
"""
        
        await send_telegram_message(telegram_text)
        logger.info(f"✅ Notificación Telegram enviada")
    
    except Exception as e:
        logger.error(f"❌ Error en Telegram: {str(e)}")


# ============================================================================
# 📊 FUNCIÓN AUXILIAR: GUARDAR EN AIRTABLE
# ============================================================================

async def guardar_airtable(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int,
    fecha: str
):
    """
    Guarda el lead en Airtable para tener CRM visual.
    """
    
    try:
        await save_lead_to_airtable(
            nombre=nombre,
            email=email,
            telefono=telefono,
            mensaje=mensaje,
            lead_score=lead_score,
            origen="formulario_landing",
            fecha=fecha
        )
        logger.info(f"✅ Lead guardado en Airtable")
    
    except Exception as e:
        logger.error(f"❌ Error guardando en Airtable: {str(e)}")


# ============================================================================
# 🔄 FUNCIÓN AUXILIAR: DISPARAR WEBHOOK A n8n
# ============================================================================

async def dispara_webhook_n8n(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int
):
    """
    Dispara webhook a n8n para:
    - Enviar WhatsApp automático
    - Crear evento en Google Calendar
    - Enviar SMS recordatorio
    """
    
    payload = {
        "origen": "formulario_landing",
        "nombre": nombre,
        "email": email,
        "telefono": telefono,
        "mensaje": mensaje,
        "lead_score": lead_score,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.N8N_WEBHOOK_URL,
                json=payload,
                timeout=settings.N8N_TIMEOUT
            )
            logger.info(f"✅ Webhook n8n disparado. Status: {response.status_code}")
    
    except httpx.TimeoutException:
        logger.warning(f"⏱️  n8n timeout. Continuando sin esperar respuesta.")
    except Exception as e:
        logger.error(f"❌ Error disparando n8n: {str(e)}")


# ============================================================================
# 📊 GET /api/contact/leads - LISTAR TODOS LOS LEADS
# ============================================================================

@router.get("/contact/leads")
async def get_all_leads(
    db: Session = Depends(get_db),
    limit: int = 50,
    origen: Optional[str] = None
):
    """
    Obtiene los últimos N leads.
    
    Parámetros:
    - limit: Cuántos registros traer (default 50)
    - origen: Filtrar por origen (ej: "formulario_landing" o "chat")
    
    Uso:
    GET /api/contact/leads?limit=20&origen=formulario_landing
    """
    
    query = db.query(Lead)
    
    if origen:
        query = query.filter(Lead.origen == origen)
    
    leads = query.order_by(Lead.fecha.desc()).limit(limit).all()
    
    return {
        "total": len(leads),
        "leads": [
            {
                "id": lead.id,
                "nombre": lead.nombre,
                "email": lead.email,
                "telefono": lead.phone,
                "lead_score": lead.lead_score,
                "origen": lead.origen,
                "fecha": lead.fecha,
                "preview_mensaje": lead.mensaje[:100] + "..." if len(lead.mensaje) > 100 else lead.mensaje
            }
            for lead in leads
        ]
    }


# ============================================================================
# 📋 GET /api/contact/leads/{lead_id} - OBTENER LEAD ESPECÍFICO
# ============================================================================

@router.get("/contact/leads/{lead_id}")
async def get_lead_details(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los detalles completos de un lead.
    """
    
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    
    return {
        "id": lead.id,
        "nombre": lead.nombre,
        "email": lead.email,
        "telefono": lead.phone,
        "mensaje": lead.mensaje,
        "lead_score": lead.lead_score,
        "origen": lead.origen,
        "fecha": lead.fecha
    }