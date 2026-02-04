# app/routes/leads.py
"""
ENDPOINT DE ADMINISTRACIÓN DE LEADS
GET/POST endpoints para que el admin (Luciano) gestione los leads
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.lead import Lead, ChatSession, ChatHistory
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# 📊 ENUMS Y MODELOS
# ============================================================================

class EstadoLead(str, Enum):
    """Estados posibles de un lead"""
    NUEVO = "nuevo"
    CONTACTADO = "contactado"
    EN_NEGOCIACION = "en_negociacion"
    AGENDADO = "agendado"
    CONVERTIDO = "convertido"
    PERDIDO = "perdido"
    SPAM = "spam"


# ============================================================================
# 📊 GET /api/leads/dashboard - DASHBOARD PRINCIPAL
# ============================================================================

@router.get("/leads/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    """Devuelve estadísticas generales de leads."""
    
    try:
        total_leads = db.query(Lead).count()
        
        hace_24h = datetime.utcnow() - timedelta(hours=24)
        leads_hoy = db.query(Lead).filter(Lead.fecha >= hace_24h).count()
        
        hace_7d = datetime.utcnow() - timedelta(days=7)
        leads_semana = db.query(Lead).filter(Lead.fecha >= hace_7d).count()
        
        score_promedio = db.query(func.avg(Lead.lead_score)).scalar() or 0
        
        por_origen = db.query(
            Lead.origen,
            func.count(Lead.id).label("cantidad")
        ).group_by(Lead.origen).all()
        
        origen_dict = {origen: cantidad for origen, cantidad in por_origen}
        
        por_estado = db.query(
            Lead.estado,
            func.count(Lead.id).label("cantidad")
        ).group_by(Lead.estado).all()
        
        estado_dict = {estado: cantidad for estado, cantidad in por_estado}
        
        convertidos = db.query(Lead).filter(Lead.estado == "convertido").count()
        tasa_conversion = (convertidos / total_leads * 100) if total_leads > 0 else 0
        
        leads_alto_valor = db.query(Lead).filter(Lead.lead_score >= 80).count()
        
        logger.info(f"📊 Dashboard consultado. Total leads: {total_leads}")
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "resumen": {
                "total_leads": total_leads,
                "leads_24h": leads_hoy,
                "leads_7d": leads_semana,
                "score_promedio": round(score_promedio, 1),
                "tasa_conversion": round(tasa_conversion, 1),
                "leads_alto_valor": leads_alto_valor
            },
            "por_origen": origen_dict,
            "por_estado": estado_dict,
            "salud_pipeline": {
                "estado": "bueno" if leads_alto_valor >= 5 else "regular",
                "mensaje": f"{leads_alto_valor} leads con score > 80"
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Error en dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generando dashboard")


# ============================================================================
# 📋 GET /api/leads - LISTAR LEADS CON FILTROS
# ============================================================================

@router.get("/leads")
async def list_leads(
    db: Session = Depends(get_db),
    estado: Optional[EstadoLead] = None,
    origen: Optional[str] = None,
    score_min: int = Query(0, ge=0, le=100),
    score_max: int = Query(100, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    ordenar_por: str = Query("fecha", pattern="^(fecha|score|nombre)$")  # CORREGIDO: regex → pattern
):
    """
    Lista leads con filtros avanzados.
    
    Ejemplos:
    GET /api/leads?estado=nuevo&score_min=70
    GET /api/leads?origen=chat&limit=20&offset=20
    GET /api/leads?ordenar_por=score
    """
    
    try:
        query = db.query(Lead)
        
        if estado:
            query = query.filter(Lead.estado == estado.value)
        
        if origen:
            query = query.filter(Lead.origen == origen)
        
        query = query.filter(
            Lead.lead_score >= score_min,
            Lead.lead_score <= score_max
        )
        
        if ordenar_por == "fecha":
            query = query.order_by(Lead.fecha.desc())
        elif ordenar_por == "score":
            query = query.order_by(Lead.lead_score.desc())
        elif ordenar_por == "nombre":
            query = query.order_by(Lead.nombre.asc())
        
        total = query.count()
        
        leads = query.limit(limit).offset(offset).all()
        
        logger.info(f"📋 Leads listados. Filtros: estado={estado}, origen={origen}")
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "resultado": [
                {
                    "id": lead.id,
                    "nombre": lead.nombre,
                    "email": lead.email,
                    "telefono": lead.phone,
                    "lead_score": lead.lead_score,
                    "estado": lead.estado,
                    "origen": lead.origen,
                    "fecha": lead.fecha,
                    "mensaje_preview": lead.mensaje[:60] + "..." if len(lead.mensaje) > 60 else lead.mensaje
                }
                for lead in leads
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Error listando leads: {str(e)}")
        raise HTTPException(status_code=500, detail="Error listando leads")


# ============================================================================
# 📄 GET /api/leads/{lead_id} - VER DETALLES DE UN LEAD
# ============================================================================

@router.get("/leads/{lead_id}")
async def get_lead_detail(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los detalles de un lead específico."""
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        chats = db.query(ChatHistory).filter(
            ChatHistory.session_id.in_(
                db.query(ChatSession.session_id).all()
            )
        ).all()
        
        chat_history = [
            {
                "fecha": chat.fecha,
                "mensaje_usuario": chat.mensaje_usuario,
                "respuesta_bot": chat.respuesta_bot,
                "lead_score": chat.lead_score
            }
            for chat in chats
            if lead.email.lower() in chat.mensaje_usuario.lower()
        ]
        
        logger.info(f"📄 Detalles de lead {lead_id} consultados")
        
        return {
            "id": lead.id,
            "nombre": lead.nombre,
            "email": lead.email,
            "telefono": lead.phone,
            "mensaje": lead.mensaje,
            "lead_score": lead.lead_score,
            "estado": lead.estado,
            "origen": lead.origen,
            "fecha_creacion": lead.fecha,
            "fecha_contacto": lead.fecha_contacto,
            "notas": lead.notas,
            "interacciones_chat": chat_history,
            "acciones_rapidas": {
                "whatsapp": f"https://wa.me/{lead.phone.replace('+', '').replace(' ', '')}",
                "email": f"mailto:{lead.email}",
                "telegram": f"tg://user?id={lead.id}"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo detalles: {str(e)}")
        raise HTTPException(status_code=500, detail="Error obteniendo detalles")


# ============================================================================
# ✏️ PUT /api/leads/{lead_id} - ACTUALIZAR ESTADO DE UN LEAD
# ============================================================================

@router.put("/leads/{lead_id}")
async def update_lead(
    lead_id: int,
    estado: EstadoLead,
    notas: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Actualiza el estado de un lead."""
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        estado_anterior = lead.estado
        lead.estado = estado.value
        
        if estado.value == "contactado" and not lead.fecha_contacto:
            lead.fecha_contacto = datetime.utcnow()
        
        if notas:
            lead.notas = notas
        
        db.commit()
        
        logger.info(f"✏️  Lead {lead_id}: {estado_anterior} → {estado.value}")
        
        return {
            "status": "success",
            "message": f"Lead actualizado: {estado_anterior} → {estado.value}",
            "lead_id": lead_id,
            "nuevo_estado": estado.value
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando lead: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error actualizando lead")


# ============================================================================
# 📊 GET /api/leads/stats/por-semana - ESTADÍSTICAS POR SEMANA
# ============================================================================

@router.get("/leads/stats/por-semana")
async def get_stats_por_semana(db: Session = Depends(get_db)):
    """Devuelve cantidad de leads generados por día (últimas 4 semanas)."""
    
    try:
        hace_28d = datetime.utcnow() - timedelta(days=28)
        
        leads = db.query(Lead).filter(Lead.fecha >= hace_28d).all()
        
        stats_por_dia = {}
        for lead in leads:
            dia = lead.fecha.date()
            stats_por_dia[str(dia)] = stats_por_dia.get(str(dia), 0) + 1
        
        resultado = [
            {"fecha": fecha, "cantidad": cantidad}
            for fecha, cantidad in sorted(stats_por_dia.items())
        ]
        
        logger.info(f"📊 Stats por semana generadas")
        
        return {
            "periodo": "últimos 28 días",
            "datos": resultado,
            "total": sum(d["cantidad"] for d in resultado)
        }
    
    except Exception as e:
        logger.error(f"❌ Error generando stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generando estadísticas")


# ============================================================================
# 🗑️ DELETE /api/leads/{lead_id} - ELIMINAR UN LEAD
# ============================================================================

@router.delete("/leads/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Elimina un lead (operación irreversible)."""
    
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        nombre = lead.nombre
        db.delete(lead)
        db.commit()
        
        logger.warning(f"🗑️  Lead {lead_id} ({nombre}) ELIMINADO")
        
        return {
            "status": "success",
            "message": f"Lead {nombre} eliminado",
            "lead_id": lead_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error eliminando lead: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Error eliminando lead")


# ============================================================================
# 📈 GET /api/leads/export/csv - EXPORTAR LEADS A CSV
# ============================================================================

@router.get("/leads/export/csv")
async def export_leads_csv(
    estado: Optional[EstadoLead] = None,
    origen: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Exporta leads a formato CSV."""
    
    try:
        import csv
        from io import StringIO
        
        query = db.query(Lead)
        
        if estado:
            query = query.filter(Lead.estado == estado.value)
        if origen:
            query = query.filter(Lead.origen == origen)
        
        leads = query.all()
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "ID", "Nombre", "Email", "Teléfono", "Mensaje", 
            "Score", "Estado", "Origen", "Fecha", "Notas"
        ])
        
        for lead in leads:
            writer.writerow([
                lead.id,
                lead.nombre,
                lead.email,
                lead.phone,
                lead.mensaje[:100],
                lead.lead_score,
                lead.estado,
                lead.origen,
                lead.fecha,
                lead.notas or ""
            ])
        
        logger.info(f"📥 CSV exportado con {len(leads)} leads")
        
        return {
            "status": "success",
            "total_leads": len(leads),
            "csv_data": output.getvalue(),
            "filename": f"leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    
    except Exception as e:
        logger.error(f"❌ Error exportando CSV: {str(e)}")
        raise HTTPException(status_code=500, detail="Error exportando CSV")