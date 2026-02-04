import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.database import get_db
from app.models.lead import Lead
from app.schemas import ContactForm
from app.config import settings

router = APIRouter()

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True
)

async def send_telegram_msg(message: str):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        async with httpx.AsyncClient() as client:
            try:
                await client.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"})
            except Exception as e:
                print(f"Error Telegram: {e}")

@router.post("/contact")
async def contact_submit(form: ContactForm, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        # 1. Guardar en Base de Datos
        nuevo_lead = Lead(
            nombre=form.name,
            email=form.email,
            phone=form.phone,
            mensaje=form.message
        )
        db.add(nuevo_lead)
        db.commit()

        # 2. Link de WhatsApp para respuesta rápida
        wa_text = f"Hola {form.name}, soy Luciano Valinoti. Recibí tu consulta sobre: {form.message}"
        wa_link = f"https://wa.me/{form.phone.replace('+', '').replace(' ', '')}?text={wa_text.replace(' ', '%20')}"

        # 3. HTML para vos (Admin)
        html_admin = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; border: 1px solid #eee; border-radius: 10px; overflow: hidden;">
            <div style="background: #0f172a; color: #00f2ff; padding: 20px; text-align: center;">
                <h2>🚀 NUEVO LEAD DETECTADO</h2>
            </div>
            <div style="padding: 20px;">
                <p><strong>Nombre:</strong> {form.name}</p>
                <p><strong>Email:</strong> {form.email}</p>
                <p><strong>Teléfono:</strong> {form.phone}</p>
                <p><strong>Mensaje:</strong> {form.message}</p>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="{wa_link}" style="background: #25D366; color: white; padding: 15px 25px; text-decoration: none; border-radius: 8px; font-weight: bold;">RESPONDER POR WHATSAPP</a>
                </div>
            </div>
        </div>
        """

        # 4. HTML para el Cliente (Validación)
        html_cliente = f"""
        <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <h2 style="color: #0f172a;">¡Hola {form.name}!</h2>
            <p>Gracias por contactarme. He recibido tu mensaje correctamente:</p>
            <blockquote style="background: #f9f9f9; padding: 15px; border-left: 5px solid #00f2ff;">
                {form.message}
            </blockquote>
            <p>Me pondré en contacto contigo a la brevedad para analizar cómo podemos automatizar tus procesos.</p>
            <p>Saludos,<br><strong>Luciano Valinoti</strong><br>Especialista en Automatización IT</p>
        </div>
        """

        fm = FastMail(conf)

        # Encolar correos
        msg_admin = MessageSchema(subject="⚡ NUEVO PROYECTO - Web", recipients=[settings.MAIL_USERNAME], body=html_admin, subtype=MessageType.html)
        msg_cliente = MessageSchema(subject="Recibí tu consulta - Luciano Valinoti", recipients=[form.email], body=html_cliente, subtype=MessageType.html)
        
        background_tasks.add_task(fm.send_message, msg_admin)
        background_tasks.add_task(fm.send_message, msg_cliente)

        # Encolar Telegram
        tg_text = f"🚀 <b>NUEVO LEAD</b>\n\n👤 <b>Nombre:</b> {form.name}\n📧 <b>Email:</b> {form.email}\n📱 <b>Tel:</b> {form.phone}\n💬 <b>Mensaje:</b> {form.message}"
        background_tasks.add_task(send_telegram_msg, tg_text)

        return {"status": "success"}

    except Exception as e:
        print(f"Error General: {e}")
        raise HTTPException(status_code=500, detail="Error en el procesamiento")