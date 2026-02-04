# app/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

# ============================================================================
# 💬 CHAT
# ============================================================================

class ChatQuery(BaseModel):
    """Schema para requests del chatbot."""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: Optional[str] = Field(None, description="ID de sesión (se genera si no existe)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hola, necesito automatizar facturas",
                "session_id": "abc123-def456"
            }
        }

class ChatResponse(BaseModel):
    """Schema para respuestas del chatbot."""
    status: str
    response: str
    session_id: str
    lead_score: int
    is_lead: bool
    contact_info: dict = {}
    timestamp: str

# ============================================================================
# 📧 CONTACT / FORMULARIO
# ============================================================================

class ContactForm(BaseModel):
    """Schema para formulario de contacto."""
    name: str = Field(..., min_length=2, max_length=100, description="Nombre completo")
    email: EmailStr = Field(..., description="Email válido")
    phone: str = Field(..., min_length=8, max_length=20, description="Teléfono")
    service: str = Field(..., description="Servicio requerido")
    message: str = Field(..., min_length=10, max_length=2000, description="Mensaje")
    
    @validator('phone')
    def validar_telefono(cls, v):
        """Validar que el teléfono sea válido."""
        # Eliminar espacios y caracteres especiales para validación
        phone_clean = ''.join(c for c in v if c.isdigit() or c == '+')
        if len(phone_clean) < 8:
            raise ValueError('Teléfono debe tener al menos 8 dígitos')
        return v
    
    @validator('name')
    def validar_nombre(cls, v):
        """Validar que el nombre solo contenga letras y espacios."""
        if not all(c.isalpha() or c.isspace() or c in '-áéíóúñüÁÉÍÓÚÑÜ' for c in v):
            raise ValueError('El nombre solo puede contener letras')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Pérez",
                "email": "juan@empresa.com",
                "phone": "+54 9 351 123 4567",
                "service": "Automatización e IA",
                "message": "Necesito automatizar el envío de 50 facturas diarias"
            }
        }

class ContactResponse(BaseModel):
    """Schema para respuesta del formulario."""
    status: str
    message: str
    lead_id: Optional[int] = None
    lead_score: Optional[int] = None

# ============================================================================
# 👤 LEADS / GESTIÓN
# ============================================================================

class LeadBase(BaseModel):
    """Base para Lead."""
    nombre: str
    email: str
    telefono: str
    mensaje: str
    origen: str = "formulario_landing"

class LeadCreate(LeadBase):
    """Schema para crear Lead."""
    pass

class LeadUpdate(BaseModel):
    """Schema para actualizar Lead."""
    estado: Optional[str] = Field(None, description="Nuevo estado del lead")
    notas: Optional[str] = Field(None, description="Notas internas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estado": "contactado",
                "notas": "Cliente interesado en Automatización"
            }
        }

class LeadResponse(LeadBase):
    """Schema para respuesta de Lead."""
    id: int
    lead_score: int
    estado: str
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class LeadListResponse(BaseModel):
    """Schema para lista de Leads."""
    status: str
    total: int
    leads: List[LeadResponse]

# ============================================================================
# 📅 CITAS / AGENDAR
# ============================================================================

class CitaAgendada(BaseModel):
    """Schema para confirmación de cita agendada."""
    lead_id: int
    fecha: datetime
    duracion_minutos: int = 30
    titulo: str = "Consulta con Luciano Valinoti"
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": 1,
                "fecha": "2025-02-05T10:00:00",
                "duracion_minutos": 30,
                "titulo": "Consulta con Luciano Valinoti"
            }
        }

# ============================================================================
# 📊 DASHBOARD / ESTADÍSTICAS
# ============================================================================

class DashboardStats(BaseModel):
    """Schema para estadísticas del dashboard."""
    total_leads: int
    leads_24h: int
    leads_7d: int
    score_promedio: float
    tasa_conversion: float
    leads_alto_valor: int

class ResponseBase(BaseModel):
    """Schema base para todas las respuestas."""
    status: str
    message: str = ""
    data: Optional[dict] = None
    timestamp: Optional[str] = None