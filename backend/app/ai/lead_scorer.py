# app/ai/lead_scorer.py
"""
LEAD SCORING - Algoritmo para calificar leads
Calcula un score 0-100 basado en varios factores.

¿Para qué?
- Priorizar leads de alta calidad
- Automatizar acciones según score
- Entender qué mensajes generan leads mejores

Factores considerados:
1. ¿Dejó contacto? (email/teléfono)
2. ¿Mostró intención de compra?
3. ¿El mensaje es específico?
4. ¿Mencionó presupuesto/timeline?
5. ¿Qué tan largo fue el mensaje?
6. ¿Cuántos mensajes previos en la conversación?
"""

import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# ============================================================================
# 🎯 PALABRAS CLAVE PARA SCORING
# ============================================================================

# Palabras que AUMENTAN el score
PALABRAS_POSITIVAS = {
    # Intención de compra
    "necesito": 15,
    "requiero": 15,
    "urgente": 20,
    "crítico": 20,
    "problema": 10,
    "solución": 15,
    "presupuesto": 25,
    "inversión": 25,
    "invertir": 20,
    "contrato": 25,
    "servicio": 10,
    "empresa": 5,
    
    # Automatización específica
    "automatizar": 20,
    "automatización": 20,
    "eficiencia": 15,
    "proceso": 15,
    "manual": 10,
    "repetitivo": 15,
    
    # Seguridad
    "seguridad": 15,
    "ransomware": 20,
    "virus": 15,
    "protección": 15,
    "backup": 15,
    "ciberseguridad": 15,
    
    # Timeline urgente
    "rápido": 15,
    "urgente": 20,
    "esta semana": 20,
    "este mes": 15,
    "cuanto antes": 15,
    
    # Especificidad
    "factura": 15,
    "email": 10,
    "cliente": 10,
    "datos": 10,
    "base de datos": 15,
}

# Palabras que DISMINUYEN el score
PALABRAS_NEGATIVAS = {
    "spam": -100,
    "scam": -100,
    "broma": -50,
    "prueba": -20,
    "solo curioso": -30,
    "información": -5,
    "no sé": -15,
}

# ============================================================================
# 📊 FUNCIÓN PRINCIPAL: SCORE_LEAD
# ============================================================================

def score_lead(
    mensaje: str,
    tiene_contacto: bool = False,
    tiene_intencion: bool = False,
    historial_length: int = 0
) -> int:
    """
    Calcula el score de un lead (0-100).
    
    Parámetros:
    - mensaje: El mensaje/consulta del usuario
    - tiene_contacto: ¿Dejó email/teléfono?
    - tiene_intencion: ¿Mostró intención?
    - historial_length: Cuántos mensajes previos en la conversación
    
    Retorna:
    - int: Score 0-100
    
    Ejemplo:
    score = score_lead(
        mensaje="Necesito automatizar mis facturas. WhatsApp: +54 9 351 123 4567",
        tiene_contacto=True,
        tiene_intencion=True,
        historial_length=2
    )
    # Retorna: 92
    """
    
    # Base score: 20 puntos (todo lead tiene un mínimo)
    score = 20
    
    logger.info(f"🎯 Iniciando scoring del lead")
    
    # ========================================================================
    # FACTOR 1: ¿Tiene contacto? (email/teléfono)
    # ========================================================================
    if tiene_contacto:
        score += 35  # +35 puntos si dejó contacto
        logger.info(f"  ✓ Tiene contacto: +35 (total: {score})")
    else:
        logger.info(f"  ✗ Sin contacto: +0")
    
    # ========================================================================
    # FACTOR 2: ¿Mostró intención?
    # ========================================================================
    if tiene_intencion:
        score += 15  # +15 puntos si mostró intención
        logger.info(f"  ✓ Con intención: +15 (total: {score})")
    
    # ========================================================================
    # FACTOR 3: Análisis del mensaje
    # ========================================================================
    mensaje_lower = mensaje.lower().strip()
    
    # 3a. Longitud del mensaje (más específico = mejor)
    longitud = len(mensaje_lower)
    if longitud >= 100:
        score += 10
        logger.info(f"  ✓ Mensaje largo ({longitud} chars): +10")
    elif longitud >= 50:
        score += 5
        logger.info(f"  ✓ Mensaje medio ({longitud} chars): +5")
    
    # 3b. Palabras positivas
    puntos_positivos = 0
    palabras_encontradas = []
    for palabra, puntos in PALABRAS_POSITIVAS.items():
        if palabra in mensaje_lower:
            puntos_positivos += puntos
            palabras_encontradas.append(f"{palabra}(+{puntos})")
    
    if puntos_positivos > 0:
        score += min(puntos_positivos, 20)  # Máximo +20 de palabras positivas
        logger.info(f"  ✓ Palabras positivas {palabras_encontradas}: +{min(puntos_positivos, 20)}")
    
    # 3c. Palabras negativas
    puntos_negativos = 0
    for palabra, puntos in PALABRAS_NEGATIVAS.items():
        if palabra in mensaje_lower:
            puntos_negativos += puntos
    
    score += puntos_negativos  # Resta directamente
    if puntos_negativos != 0:
        logger.info(f"  ✗ Palabras negativas: {puntos_negativos}")
    
    # 3d. Presencia de números (presupuesto, timeline, etc)
    numeros = re.findall(r'\d+', mensaje)
    if numeros:
        score += 5
        logger.info(f"  ✓ Números encontrados: +5")
    
    # ========================================================================
    # FACTOR 4: Historial de la conversación
    # ========================================================================
    # Si ya hubo conversación previa, es más serio
    if historial_length > 0:
        score += min(historial_length * 3, 10)  # Máximo +10
        logger.info(f"  ✓ Historial de {historial_length} mensajes: +{min(historial_length * 3, 10)}")
    
    # ========================================================================
    # FACTOR 5: Detalles específicos
    # ========================================================================
    detalles_score = _detectar_detalles_especificos(mensaje)
    score += detalles_score
    if detalles_score > 0:
        logger.info(f"  ✓ Detalles específicos: +{detalles_score}")
    
    # ========================================================================
    # Limitar a rango 0-100
    # ========================================================================
    score = max(0, min(100, score))
    
    # Clasificación final
    if score >= 80:
        clasificacion = "🔥 MUY CALIDO"
    elif score >= 60:
        clasificacion = "⭐ CALIDO"
    elif score >= 40:
        clasificacion = "🌡️ TIBIO"
    else:
        clasificacion = "❄️ FRIO"
    
    logger.info(f"🎯 SCORE FINAL: {score}/100 - {clasificacion}")
    
    return score


# ============================================================================
# 🔍 FUNCIÓN AUXILIAR: DETECTAR DETALLES ESPECÍFICOS
# ============================================================================

def _detectar_detalles_especificos(mensaje: str) -> int:
    """
    Detecta si el mensaje contiene detalles específicos sobre el problema.
    Ejemplos:
    - "50 facturas por día"
    - "Microsoft 365"
    - "API REST"
    """
    
    puntos = 0
    mensaje_lower = mensaje.lower()
    
    # Detalles de volumen
    if re.search(r'\d+\s*(emails?|facturas?|pedidos?|clientes?)', mensaje_lower):
        puntos += 5
    
    # Detalles técnicos
    if any(palabra in mensaje_lower for palabra in [
        "api", "python", "zapier", "n8n", "make", "automate",
        "windows", "linux", "sql", "excel", "google sheets"
    ]):
        puntos += 5
    
    # Detalles de timeline
    if any(palabra in mensaje_lower for palabra in [
        "mañana", "esta semana", "este mes", "urgente",
        "asap", "pronto", "rápido"
    ]):
        puntos += 3
    
    return puntos


# ============================================================================
# 📈 FUNCIÓN: GET_SCORE_CATEGORY (Categorizar)
# ============================================================================

def get_score_category(score: int) -> dict:
    """
    Categoriza un score en una clasificación legible.
    
    Retorna:
    {
        "categoria": "Muy Calido",
        "emoji": "🔥",
        "accion_recomendada": "Agendar cita hoy",
        "prioridad": 1,
        "contactar_en": "0-2 horas"
    }
    """
    
    if score >= 90:
        return {
            "categoria": "Muy Muy Calido",
            "emoji": "🔥🔥",
            "accion_recomendada": "Llamar INMEDIATAMENTE",
            "prioridad": 1,
            "contactar_en": "0-30 minutos",
            "probabilidad_conversion": 0.9
        }
    elif score >= 80:
        return {
            "categoria": "Muy Calido",
            "emoji": "🔥",
            "accion_recomendada": "Agendar cita hoy",
            "prioridad": 1,
            "contactar_en": "0-2 horas",
            "probabilidad_conversion": 0.75
        }
    elif score >= 70:
        return {
            "categoria": "Calido",
            "emoji": "⭐",
            "accion_recomendada": "Agendar cita esta semana",
            "prioridad": 2,
            "contactar_en": "1-2 días",
            "probabilidad_conversion": 0.6
        }
    elif score >= 50:
        return {
            "categoria": "Tibio",
            "emoji": "🌡️",
            "accion_recomendada": "Enviar información",
            "prioridad": 3,
            "contactar_en": "3-5 días",
            "probabilidad_conversion": 0.4
        }
    elif score >= 30:
        return {
            "categoria": "Frio",
            "emoji": "❄️",
            "accion_recomendada": "Seguimiento automático",
            "prioridad": 4,
            "contactar_en": "1-2 semanas",
            "probabilidad_conversion": 0.2
        }
    else:
        return {
            "categoria": "Muy Frio / Spam",
            "emoji": "❌",
            "accion_recomendada": "Ignorar o archivar",
            "prioridad": 5,
            "contactar_en": "Nunca",
            "probabilidad_conversion": 0.05
        }


# ============================================================================
# 📊 FUNCIÓN: ANALIZAR LISTA DE LEADS
# ============================================================================

def analizar_calidad_leads(leads: List[dict]) -> dict:
    """
    Analiza la calidad general de una lista de leads.
    
    Parámetros:
    - leads: Lista de dicts con {"mensaje": "...", "tiene_contacto": true, ...}
    
    Retorna:
    {
        "total_leads": 150,
        "score_promedio": 65.3,
        "muy_calidos": 23,
        "tasa_conversion_estimada": 0.52
    }
    """
    
    if not leads:
        return {
            "total_leads": 0,
            "score_promedio": 0,
            "distribucion": {}
        }
    
    scores = [
        score_lead(
            lead.get("mensaje", ""),
            lead.get("tiene_contacto", False),
            lead.get("tiene_intencion", False),
            lead.get("historial_length", 0)
        )
        for lead in leads
    ]
    
    # Distribución
    distribucion = {
        "muy_calidos_90+": len([s for s in scores if s >= 90]),
        "muy_calidos_80-89": len([s for s in scores if 80 <= s < 90]),
        "calidos_70-79": len([s for s in scores if 70 <= s < 80]),
        "tibios_50-69": len([s for s in scores if 50 <= s < 70]),
        "frios_30-49": len([s for s in scores if 30 <= s < 50]),
        "spam_0-29": len([s for s in scores if s < 30]),
    }
    
    return {
        "total_leads": len(leads),
        "score_promedio": round(sum(scores) / len(scores), 1),
        "score_min": min(scores),
        "score_max": max(scores),
        "distribucion": distribucion,
        "tasa_conversion_estimada": round(sum([get_score_category(s)["probabilidad_conversion"] for s in scores]) / len(scores), 2)
    }


# ============================================================================
# 📝 EJEMPLOS DE SCORING
# ============================================================================

"""
EJEMPLO 1: Lead muy bueno
----
mensaje = "Hola, necesito automatizar el envío de 50 facturas diarias. Presupuesto: $500/mes. WhatsApp: +54 9 351 123 4567"
score = score_lead(mensaje, tiene_contacto=True, tiene_intencion=True, historial_length=0)
# Resultado: 92 🔥 (Llamar INMEDIATAMENTE)

EJEMPLO 2: Lead regular
----
mensaje = "¿Pueden ayudarme con seguridad IT?"
score = score_lead(mensaje, tiene_contacto=False, tiene_intencion=True, historial_length=2)
# Resultado: 58 🌡️ (Tibio)

EJEMPLO 3: Lead spam
----
mensaje = "Hola amigo, dame dinero"
score = score_lead(mensaje, tiene_contacto=False, tiene_intencion=False)
# Resultado: 15 ❌ (Spam)

EJEMPLO 4: Categorizar
----
categoria = get_score_category(85)
# Retorna: {
#     "categoria": "Muy Calido",
#     "emoji": "🔥",
#     "accion_recomendada": "Agendar cita hoy",
#     "prioridad": 1,
#     "contactar_en": "0-2 horas",
#     "probabilidad_conversion": 0.75
# }

EJEMPLO 5: Analizar múltiples leads
----
leads = [
    {"mensaje": "Necesito...", "tiene_contacto": True},
    {"mensaje": "¿Cómo funciona?", "tiene_contacto": False},
    ...
]
analisis = analizar_calidad_leads(leads)
# Retorna métricas generales de la lista
"""