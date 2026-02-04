# app/utils/lead_detector.py
"""
Detecta automáticamente cuando un usuario deja su WhatsApp, email
o muestra intención de contacto en el chat.
"""

import re
from typing import Dict, Optional

class LeadDetector:
    """Detecta información de contacto en mensajes del usuario"""
    
    # Patrones para detectar teléfonos argentinos
    PHONE_PATTERNS = [
        r'\+?54\s?9?\s?11\s?\d{4}\s?\d{4}',      # +54 9 11 1234 5678
        r'\+?54\s?9?\s?3\d{2}\s?\d{3}\s?\d{4}',  # +54 9 351 123 4567
        r'\d{2,4}\s?\d{3,4}\s?\d{4}',            # 351 123 4567
    ]
    
    # Palabras que indican que quiere que lo contactes
    PALABRAS_INTENCION = [
        'reunion', 'reunión', 'llamame', 'llámame', 
        'contactame', 'contáctame', 'agenda', 'agendar',
        'whatsapp', 'wp', 'wa', 'presupuesto', 'cotización',
        'enviame', 'envíame', 'necesito', 'me interesa'
    ]
    
    def __init__(self):
        # Compilar expresiones regulares
        self.phone_regex = re.compile('|'.join(self.PHONE_PATTERNS))
        self.email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    def detectar_telefono(self, mensaje: str) -> Optional[str]:
        """Busca un número de teléfono en el mensaje"""
        match = self.phone_regex.search(mensaje)
        if match:
            # Limpiar el número (sacar espacios y guiones)
            numero = match.group().replace(' ', '').replace('-', '')
            return numero
        return None
    
    def detectar_email(self, mensaje: str) -> Optional[str]:
        """Busca un email en el mensaje"""
        match = self.email_regex.search(mensaje)
        return match.group() if match else None
    
    def detectar_intencion(self, mensaje: str) -> bool:
        """Detecta si el usuario quiere que lo contactes"""
        mensaje_lower = mensaje.lower()
        return any(palabra in mensaje_lower for palabra in self.PALABRAS_INTENCION)
    
    def analizar(self, mensaje: str) -> Dict:
        """
        Analiza el mensaje completo y retorna toda la info detectada.
        
        Retorna:
            {
                'es_lead': True/False,
                'telefono': '+543516889414' o None,
                'email': 'usuario@email.com' o None,
                'tiene_intencion': True/False,
                'razon': 'descripción de por qué es lead'
            }
        """
        telefono = self.detectar_telefono(mensaje)
        email = self.detectar_email(mensaje)
        tiene_intencion = self.detectar_intencion(mensaje)
        
        # Es un lead si tiene teléfono, email o mostró intención
        es_lead = bool(telefono or email or tiene_intencion)
        
        # Construir descripción
        razon_partes = []
        if telefono:
            razon_partes.append(f"Teléfono: {telefono}")
        if email:
            razon_partes.append(f"Email: {email}")
        if tiene_intencion and not (telefono or email):
            razon_partes.append("Palabras de intención de contacto")
        
        razon = " | ".join(razon_partes) if razon_partes else "Sin señales"
        
        return {
            'es_lead': es_lead,
            'telefono': telefono,
            'email': email,
            'tiene_intencion': tiene_intencion,
            'razon': razon
        }

# Crear instancia global para usar en main.py
detector = LeadDetector()