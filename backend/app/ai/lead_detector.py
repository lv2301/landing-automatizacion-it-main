# app/utils/lead_detector.py
import re

class LeadDetector:
    def analizar(self, texto: str):
        t = texto.lower()
        email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', t)
        telefono = re.search(r'\+?\d{7,15}', t)
        
        # Detectar si el usuario está dando una fecha o confirmando
        confirmacion = any(x in t for x in ["lunes", "martes", "miércoles", "jueves", "viernes", "mañana", "hs", "hora", "agendemos", "dale", "ok"])
        
        return {
            "es_lead": bool(email or telefono),
            "email": email.group(0) if email else None,
            "telefono": telefono.group(0) if telefono else None,
            "quiere_agendar": confirmacion,
            "texto_puro": texto
        }

detector = LeadDetector()