# FitGate — Etapa 1: Reconocimiento facial

Primera entrega del sistema de control de acceso al gimnasio por reconocimiento
facial

## Stack

- **Backend**: FastAPI (Python 3.10+) + SQLAlchemy (MySQL 8)
- **Cola/worker**: Celery + Redis (procesamiento asincrónico de embeddings)
- **Reconocimiento facial**: `face_recognition` + FAISS (index de vectores de 128 dims)
- **Storage**: SeaweedFS (imágenes de rostro de las personas)
- **Infra**: Docker Compose (MySQL, Redis, SeaweedFS, Nginx, API, Worker)

## Arquitectura

### Carga de embeddings (asincrónico)
```
POST /api/v1/persons/{personId}/embeddings
  → sube las imágenes a SeaweedFS
  → escribe la tarea "En Proceso" en MySQL
  → encola el ticket en Redis (broker de Celery)
  → responde: "Tarea aceptada, ID = X"

Celery Worker (segundo plano)
  → toma el ticket de Redis
  → descarga la imagen de SeaweedFS
  → genera el embedding facial (128 floats)
  → guarda el vector en la tabla embeddings
```

### Reconocimiento facial
```
POST /api/v1/face-recognition
  → genera el embedding de la imagen consultada
  → busca el vecino más cercano en FAISS
  → devuelve persona + confidence si supera el umbral
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/v1/persons` | alta de persona (idempotente por email) |
| `GET` | `/api/v1/persons` | listar personas |
| `GET` | `/api/v1/persons/{personId}` | detalle de persona |
| `PUT` | `/api/v1/persons/{personId}` | actualizar persona |
| `DELETE` | `/api/v1/persons/{personId}` | baja de persona (y sus embeddings) |
| `POST` | `/api/v1/persons/{personId}/embeddings` | enrolar fotos de rostro |
| `POST` | `/api/v1/face-recognition` | reconocer un rostro |

> En esta etapa los endpoints son públicos (sin autenticación). El login, la barrera
> de acceso y el dominio del gimnasio se incorporan en etapas posteriores.

## Requisitos

- Python 3.10+
- Docker y Docker Compose

## Setup rápido

```bash
# 1. Configuración
cp .env.example .env

# 2. Infraestructura (MySQL, Redis, SeaweedFS)
docker compose up -d db redis seaweed_master seaweed_volume
# Opcional: API + worker + nginx desde las imágenes locales
# docker compose up -d --build

# 3. Dependencias Python
pip install -r app/requirements.txt

# 4. API
uvicorn app.main:app --reload --port 8000
# En la primera ejecución se crean las tablas automáticamente.

# 5. Worker (en otra terminal)
celery -A app.worker.tasks worker --loglevel=info
```

Documentación Swagger: `http://localhost:8000/docs`.
