# app/ai/chat.py

import os
from groq import Groq
from app.ai.prompts import (
    SYSTEM_PROMPT,
    detectar_tipo_pregunta,
    get_respuesta_predefinida
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_chatbot_response(user_message: str, history: list = None):
    """
    Genera respuesta del chatbot usando Groq LLM.
    
    Ahora:
    1. Intenta respuesta predefinida (rápido, sin IA)
    2. Si no hay coincidencia, usa Groq
    
    Args:
        user_message: El mensaje del usuario
        history: Lista de mensajes previos para mantener contexto
    
    Returns:
        str: Respuesta del bot
    """
    
    if history is None:
        history = []
    
    # 1️⃣ INTENTAR RESPUESTA PREDEFINIDA (rápido, sin IA)
    respuesta_rapida = get_respuesta_predefinida(user_message)
    if respuesta_rapida:
        return respuesta_rapida
    
    # 2️⃣ USAR GROQ CON SYSTEM PROMPT
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Agregar últimos 6 mensajes para contexto
    if history:
        messages.extend(history[-6:])
    
    # Agregar mensaje actual del usuario
    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.6,
            max_tokens=250
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        print(f"❌ Error en Groq: {e}")
        return "Lo siento, tengo problemas técnicos. ¿Puedes intentar de nuevo?"