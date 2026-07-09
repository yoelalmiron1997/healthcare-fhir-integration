"""
Modelos de datos (Pydantic) para validar la información de pacientes
que llega a la API antes de transformarla al recurso FHIR Patient.
"""

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class GenderEnum(str, Enum):
    """Valores de género aceptados en la entrada (se mapean a FHIR AdministrativeGender)."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNKNOWN = "unknown"


class Address(BaseModel):
    """Dirección postal del paciente (opcional)."""

    line: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class PatientIn(BaseModel):
    """
    Payload de entrada esperado por el endpoint POST /patients.

    Campos obligatorios: first_name, last_name, birth_date, gender, document_id
    Campos opcionales: phone, email, address
    """

    first_name: str = Field(..., min_length=1, description="Nombre(s) del paciente")
    last_name: str = Field(..., min_length=1, description="Apellido(s) del paciente")
    birth_date: date = Field(..., description="Fecha de nacimiento (YYYY-MM-DD)")
    gender: GenderEnum = Field(..., description="Género administrativo")
    document_id: str = Field(..., min_length=1, description="Número de documento / identificador")

    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[Address] = None

    @field_validator("first_name", "last_name", "document_id")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("El campo no puede estar vacío ni contener solo espacios")
        return value.strip()

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Juan",
                "last_name": "Pérez",
                "birth_date": "1985-04-12",
                "gender": "male",
                "document_id": "12345678",
                "phone": "+541112345678",
                "email": "juan.perez@example.com",
                "address": {
                    "line": "Av. Siempre Viva 123",
                    "city": "Buenos Aires",
                    "state": "BA",
                    "postal_code": "1000",
                    "country": "AR",
                },
            }
        }


class PatientRecord(BaseModel):
    """Representación completa que se persiste: datos originales + recurso FHIR + metadatos."""

    id: str
    created_at: str
    source_data: dict
    fhir_resource: dict
