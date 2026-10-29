# Modelos SQLAlchemy para las tablas persons, embeddings y embedding_tasks
# (etapa 1: reconocimiento facial).
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, ForeignKey, String

from database.session import Base


class Person(Base):

    __tablename__ = "persons"

    personId = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(255), nullable=False)
    apellido = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    dni = Column(String(50), nullable=True)
    telefono = Column(String(50), nullable=True)
    extra = Column(JSON, nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    membresia_hasta = Column(Date, nullable=True)


# Tabla embedding_tasks: seguimiento del estado de cada imagen encolada
class EmbeddingTask(Base):

    __tablename__ = "embedding_tasks"

    taskId = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personId = Column(String(36), ForeignKey("persons.personId"), nullable=False)
    seaweed_fid = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="En Proceso")
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

# Tabla embeddings: vectores faciales generados por face_recognition
class Embedding(Base):

    __tablename__ = "embeddings"

    embeddingId = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    personId = Column(String(36), ForeignKey("persons.personId"), nullable=False)
    vector = Column(JSON, nullable=False)
