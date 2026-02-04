# app/integrations/airtable.py
"""
INTEGRACIÓN AIRTABLE
Guarda leads en una base de datos visual para tener un CRM sin código.

¿Para qué?
- CRM visual (puedes ver todos tus leads en una tabla)
- Filtros y ordenamiento sin código
- Automatizaciones (cambiar estado, etc)
- Reportes y gráficos
- Compartir con tu equipo

Plan gratuito: 1,200 registros / 2 workspaces

Setup:
1. Registrate en https://airtable.com (gratuito)
2. Crea base llamada "Luciano-IT"
3. Crea tabla "Leads" con columnas específicas
4. Genera API Token
5. Copia Base ID y Token al .env
"""

import httpx
import logging
from typing import Optional, Dict
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)

# ============================================================================
# 📊 FUNCIÓN PRINCIPAL: GUARDAR LEAD EN AIRTABLE
# ============================================================================

async def save_lead_to_airtable(
    nombre: str,
    email: str,
    telefono: str,
    mensaje: str,
    lead_score: int,
    origen: str = "chat",
    fecha: str = None,
    notas: Optional[str] = None
) -> Dict:
    """
    Guarda un lead en Airtable.
    
    Parámetros:
    - nombre: Nombre del contacto
    - email: Email
    - telefono: Teléfono/WhatsApp
    - mensaje: Consulta/necesidad
    - lead_score: Score 0-100
    - origen: Dónde vino (formulario_landing, chat, etc)
    - fecha: Timestamp (auto-generado si no viene)
    - notas: Notas adicionales
    
    Retorna:
    {
        "exito": True/False,
        "record_id": "rec123456789",
        "mensaje": "Lead guardado"
    }
    
    Ejemplo:
    resultado = await save_lead_to_airtable(
        nombre="Juan Pérez",
        email="juan@empresa.com",
        telefono="+54 9 351 123 4567",
        mensaje="Necesito automatizar facturas",
        lead_score=85,
        origen="formulario_landing"
    )
    """
    
    # Validaciones
    if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_ID:
        logger.error("❌ AIRTABLE_TOKEN o AIRTABLE_BASE_ID no configurados")
        return {
            "exito": False,
            "mensaje": "Airtable no configurado"
        }
    
    if not fecha:
        fecha = datetime.utcnow().isoformat()
    
    # URL del API de Airtable
    url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_LEADS}"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Mapeo de estados según score
    if lead_score >= 80:
        estado = "Calido"
    elif lead_score >= 50:
        estado = "Tibio"
    else:
        estado = "Frio"
    
    # Payload - Las columnas deben coincidir con tu tabla en Airtable
    payload = {
        "records": [
            {
                "fields": {
                    "Nombre": nombre,
                    "Email": email,
                    "Teléfono": telefono,
                    "Mensaje": mensaje,
                    "Lead Score": lead_score,
                    "Estado": estado,  # Calido, Tibio, Frio
                    "Origen": origen,
                    "Fecha": fecha,
                    "Notas": notas or ""
                }
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                record_id = data["records"][0]["id"]
                logger.info(f"✅ Lead guardado en Airtable: {record_id}")
                return {
                    "exito": True,
                    "record_id": record_id,
                    "mensaje": f"Lead '{nombre}' guardado en Airtable"
                }
            else:
                logger.error(f"❌ Error Airtable: {response.status_code} - {response.text}")
                return {
                    "exito": False,
                    "mensaje": f"Error: {response.status_code}"
                }
    
    except httpx.TimeoutException:
        logger.error("❌ Timeout conectando a Airtable")
        return {
            "exito": False,
            "mensaje": "Timeout"
        }
    except Exception as e:
        logger.error(f"❌ Error guardando en Airtable: {str(e)}")
        return {
            "exito": False,
            "mensaje": str(e)
        }


# ============================================================================
# 🔄 FUNCIÓN: ACTUALIZAR ESTADO DE UN LEAD EN AIRTABLE
# ============================================================================

async def update_lead_state_airtable(
    record_id: str,
    nuevo_estado: str,
    notas: Optional[str] = None
) -> Dict:
    """
    Actualiza el estado de un lead en Airtable.
    
    Estados posibles: Nuevo, Contactado, Negociando, Agendado, Convertido, Perdido, Spam
    
    Parámetros:
    - record_id: ID del record en Airtable
    - nuevo_estado: Nuevo estado
    - notas: Agregar notas
    
    Ejemplo:
    await update_lead_state_airtable(
        record_id="rec123456789",
        nuevo_estado="Contactado",
        notas="Lo llamé a las 14:30"
    )
    """
    
    if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_ID:
        logger.error("❌ Airtable no configurado")
        return {"exito": False}
    
    url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_LEADS}/{record_id}"
    
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Validar estado
    estados_validos = ["Nuevo", "Contactado", "Negociando", "Agendado", "Convertido", "Perdido", "Spam"]
    if nuevo_estado not in estados_validos:
        return {
            "exito": False,
            "mensaje": f"Estado inválido. Válidos: {', '.join(estados_validos)}"
        }
    
    payload = {
        "fields": {
            "Estado": nuevo_estado,
            "Fecha Contacto": datetime.utcnow().isoformat() if nuevo_estado == "Contactado" else None
        }
    }
    
    # Agregar notas si vienen
    if notas:
        payload["fields"]["Notas"] = notas
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ Lead actualizado en Airtable: {nuevo_estado}")
                return {
                    "exito": True,
                    "mensaje": f"Estado actualizado a: {nuevo_estado}"
                }
            else:
                logger.error(f"❌ Error: {response.text}")
                return {"exito": False}
    
    except Exception as e:
        logger.error(f"❌ Error actualizando: {str(e)}")
        return {"exito": False}


# ============================================================================
# 📋 FUNCIÓN: OBTENER TODOS LOS LEADS DE AIRTABLE
# ============================================================================

async def get_all_leads_airtable(
    filtro: Optional[str] = None,
    max_records: int = 100
) -> Dict:
    """
    Obtiene todos los leads de Airtable.
    
    Parámetros:
    - filtro: Fórmula de Airtable (ej: "{Estado} = 'Nuevo'")
    - max_records: Máximo de registros a traer
    
    Ejemplo sin filtro:
    leads = await get_all_leads_airtable()
    
    Ejemplo con filtro:
    leads = await get_all_leads_airtable(
        filtro="{Estado} = 'Nuevo'"
    )
    
    Ejemplo filtrar por score alto:
    leads = await get_all_leads_airtable(
        filtro="{Lead Score} >= 80"
    )
    """
    
    if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_ID:
        logger.error("❌ Airtable no configurado")
        return {"exito": False, "leads": []}
    
    url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_LEADS}"
    
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}"
    }
    
    params = {
        "maxRecords": max_records,
        "pageSize": 100  # Airtable limita a 100 por página
    }
    
    # Agregar filtro si viene
    if filtro:
        params["filterByFormula"] = filtro
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                # Formatear respuesta
                leads = [
                    {
                        "id": record["id"],
                        **record["fields"]
                    }
                    for record in records
                ]
                
                logger.info(f"✅ {len(leads)} leads obtenidos de Airtable")
                return {
                    "exito": True,
                    "total": len(leads),
                    "leads": leads
                }
            else:
                logger.error(f"❌ Error: {response.text}")
                return {"exito": False, "leads": []}
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo leads: {str(e)}")
        return {"exito": False, "leads": []}


# ============================================================================
# 🧪 FUNCIÓN: TEST DE CONEXIÓN
# ============================================================================

async def test_conexion_airtable() -> Dict:
    """
    Testa que la configuración de Airtable sea correcta.
    
    Retorna:
    {
        "conectado": True,
        "tabla": "Leads",
        "base": "Luciano-IT",
        "mensaje": "✅ Conexión exitosa"
    }
    """
    
    if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_ID:
        return {
            "conectado": False,
            "mensaje": "❌ AIRTABLE_TOKEN o AIRTABLE_BASE_ID no configurados"
        }
    
    url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_LEADS}"
    
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test 1: GET para verificar acceso
            response = await client.get(url, headers=headers, params={"maxRecords": 1})
            
            if response.status_code == 200:
                # Test 2: POST para verificar escritura
                test_record = {
                    "records": [
                        {
                            "fields": {
                                "Nombre": "🧪 Test",
                                "Email": "test@test.com",
                                "Teléfono": "0000000000",
                                "Mensaje": "Mensaje de prueba",
                                "Lead Score": 0,
                                "Estado": "Test",
                                "Origen": "test"
                            }
                        }
                    ]
                }
                
                response_test = await client.post(url, json=test_record, headers=headers)
                
                if response_test.status_code == 200:
                    # Eliminarlo después
                    data = response_test.json()
                    test_id = data["records"][0]["id"]
                    await client.delete(
                        f"{url}/{test_id}",
                        headers=headers
                    )
                    
                    return {
                        "conectado": True,
                        "tabla": settings.AIRTABLE_TABLE_LEADS,
                        "base": settings.AIRTABLE_BASE_ID,
                        "mensaje": "✅ Conexión exitosa (lectura y escritura)"
                    }
                else:
                    return {
                        "conectado": False,
                        "mensaje": f"❌ Error escribiendo: {response_test.status_code}"
                    }
            else:
                return {
                    "conectado": False,
                    "mensaje": f"❌ Error leyendo: {response.status_code}"
                }
    
    except Exception as e:
        return {
            "conectado": False,
            "mensaje": f"❌ Error: {str(e)}"
        }


# ============================================================================
# 📊 FUNCIÓN: CREAR SESIÓN DE CHAT EN AIRTABLE
# ============================================================================

async def save_chat_session_airtable(
    session_id: str,
    email: Optional[str] = None,
    mensaje_inicial: str = "",
    lead_score: int = 0
) -> Dict:
    """
    Guarda una sesión de chat en tabla "Sessions" de Airtable.
    
    Útil para trackear conversaciones por separado.
    """
    
    if not settings.AIRTABLE_TOKEN or not settings.AIRTABLE_BASE_ID:
        return {"exito": False}
    
    url = f"https://api.airtable.com/v0/{settings.AIRTABLE_BASE_ID}/{settings.AIRTABLE_TABLE_SESSIONS}"
    
    headers = {
        "Authorization": f"Bearer {settings.AIRTABLE_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "records": [
            {
                "fields": {
                    "Session ID": session_id,
                    "Email": email or "No identificado",
                    "Mensaje Inicial": mensaje_inicial[:100],
                    "Lead Score": lead_score,
                    "Fecha": datetime.utcnow().isoformat()
                }
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ Sesión chat guardada en Airtable")
                return {"exito": True}
            else:
                return {"exito": False}
    
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return {"exito": False}


# ============================================================================
# 📝 EJEMPLOS DE USO
# ============================================================================

"""
EJEMPLO 1: Guardar nuevo lead
----
await save_lead_to_airtable(
    nombre="Juan Pérez",
    email="juan@empresa.com",
    telefono="+54 9 351 123 4567",
    mensaje="Necesito automatizar facturas",
    lead_score=85,
    origen="formulario_landing"
)

EJEMPLO 2: Actualizar estado
----
await update_lead_state_airtable(
    record_id="rec123456789",
    nuevo_estado="Contactado",
    notas="Lo llamé a las 14:30, no atendió"
)

EJEMPLO 3: Obtener leads nuevos
----
leads = await get_all_leads_airtable(
    filtro="{Estado} = 'Nuevo'"
)

EJEMPLO 4: Obtener leads de alta calidad
----
leads = await get_all_leads_airtable(
    filtro="{Lead Score} >= 80"
)

EJEMPLO 5: Test de conexión
----
resultado = await test_conexion_airtable()
print(resultado)
# {
#     "conectado": True,
#     "tabla": "Leads",
#     "mensaje": "✅ Conexión exitosa"
# }
"""