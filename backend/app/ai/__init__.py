# app/ai/__init__.py
from .chat import get_chatbot_response

async def get_chatbot_response(message: str, history: list = []):
    """
    Función puente que llama al motor de chat asíncrono.
    """
    return await get_ai_response(message, history)