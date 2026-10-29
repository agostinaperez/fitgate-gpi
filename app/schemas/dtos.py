# DTOs para serialización de requests/responses (etapa 1: reconocimiento facial).

from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    extra: Optional[dict[str, Any]] = None
    activo: bool = True
    membresia_hasta: Optional[date] = None


class PersonResponse(BaseModel):
    personId: str
    nombre: str
    apellido: str
    email: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    extra: Optional[dict[str, Any]] = None
    activo: bool
    membresia_hasta: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class EmbeddingRequest(BaseModel):
    images: list[str]


class EmbeddingAcceptedResponse(BaseModel):
    task_id: str
    message: str
    total_images: int


class FaceRecognitionRequest(BaseModel):
    image: str
    threshold: float = 0.8


class FaceRecognitionResponse(BaseModel):
    personId: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    confidence: float
