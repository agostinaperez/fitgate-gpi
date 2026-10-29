
# Servicio de personas y reconocimiento facial (etapa 1):
#  - CRUD de personas
#  - Carga y generación de embeddings faciales (asincrónico vía Celery)
#  - Reconocimiento facial por vecino más cercano (FAISS)

import base64

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database.session import get_db
from models.entities import EmbeddingTask, Embedding, Person
from schemas.dtos import EmbeddingAcceptedResponse, EmbeddingRequest, FaceRecognitionRequest, FaceRecognitionResponse, PersonCreate, PersonResponse
from services.person_service import get_or_create_person
from services.seaweed_ds import upload_image
from worker.celery_app import celery_app

router = APIRouter()


@router.post("/persons", response_model=PersonResponse, status_code=201)
def create_person(
    body: PersonCreate,
    response: Response,
    db: Session = Depends(get_db),
) -> Person:

    existing_person = db.query(Person).filter(Person.email == body.email).first()

    if existing_person:
        # Si ya existe, cambiamos el status a 200 OK y devolvemos sus datos
        response.status_code = status.HTTP_200_OK
        return existing_person

    return get_or_create_person(
        db,
        body.nombre,
        body.apellido,
        body.email,
        extra=body.extra,
        dni=body.dni,
        telefono=body.telefono,
        activo=body.activo,
        membresia_hasta=body.membresia_hasta,
    )


@router.get("/persons/{personId}", response_model=PersonResponse)
def get_person(
    personId: str,
    db: Session = Depends(get_db),
) -> Person:
    person = db.query(Person).filter(Person.personId == personId).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return person


@router.post("/persons/{personId}/embeddings", response_model=EmbeddingAcceptedResponse, status_code=202)
def create_embeddings(
    personId: str,
    body: EmbeddingRequest,
    db: Session = Depends(get_db),
) -> dict:
    person = db.query(Person).filter(Person.personId == personId).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # voy guardando los IDs de las tareas creadas
    # Cada imagen del request genera una tarea independiente en la tabla EmbeddingTask
    task_ids = []
    for idx, b64_str in enumerate(body.images):
        # se manda cada imagen en base64. La decodifico para volver a tener los bytes binarios reales del archivo.
        image_bytes = base64.b64decode(b64_str)

        fid = upload_image(image_bytes, f"embedding_{personId}_{idx}.jpg")

        # Creo un registro de tarea por cada imagen
        task = EmbeddingTask(
            personId=personId,
            seaweed_fid=fid,
            status="En Proceso",
        )
        db.add(task)

        # flush() manda el INSERT a la BD sin cerrar todavía la transacción.
        # Se usa para que SQLAlchemy ya tenga disponible task.taskId antes del commit.
        db.flush()
        task_ids.append(task.taskId)

    # Encolo una sola tarea de Celery y le paso:
    # - personId: la persona para la que se generan embeddings
    # - task_ids: todas las tareas creadas recién en la BD
    # El worker "worker.tasks.generate_embeddings_task" corre en segundo plano.
    db.commit()

    celery_app.send_task("worker.tasks.generate_embeddings_task", args=[personId, task_ids])

    # Devuelve 202 Accepted para indicar que el trabajo fue aceptado y quedó encolado.
    return {
        # se devuelve el primer task_id.
        "task_id": task_ids[0],
        "message": f"Procesamiento de embeddings iniciado para {len(task_ids)} imagen(es)",
        "total_images": len(task_ids),
    }


@router.get("/persons", response_model=list[PersonResponse])
def list_persons(
    db: Session = Depends(get_db),
) -> list[Person]:
    return db.query(Person).all()


@router.put("/persons/{personId}", response_model=PersonResponse)
def update_person(
    personId: str,
    body: PersonCreate,
    db: Session = Depends(get_db),
) -> Person:
    person = db.query(Person).filter(Person.personId == personId).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    person.nombre = body.nombre
    person.apellido = body.apellido
    person.email = body.email
    person.dni = body.dni
    person.telefono = body.telefono
    person.extra = body.extra
    person.activo = body.activo
    person.membresia_hasta = body.membresia_hasta
    db.commit()
    db.refresh(person)
    return person


@router.delete("/persons/{personId}", status_code=204)
def delete_person(
    personId: str,
    db: Session = Depends(get_db),
) -> None:
    person = db.query(Person).filter(Person.personId == personId).first()
    if not person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    # Eliminar registros relacionados antes de borrar la persona
    db.query(EmbeddingTask).filter(EmbeddingTask.personId == personId).delete()
    db.query(Embedding).filter(Embedding.personId == personId).delete()

    db.delete(person)
    db.commit()


@router.post("/face-recognition", response_model=FaceRecognitionResponse)
def face_recognition_endpoint(
    body: FaceRecognitionRequest,
) -> FaceRecognitionResponse:
    task = celery_app.send_task("worker.tasks.face_recognition_task", args=[body.image, body.threshold])
    result = task.get(timeout=30)

    if "error" in result:
        raise HTTPException(status_code=422, detail=result["detail"])

    return FaceRecognitionResponse(**result)
