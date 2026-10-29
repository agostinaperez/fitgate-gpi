
# Punto de entrada de la app FastAPI (etapa 1: reconocimiento facial).
# Inicializa la app, monta los routers y crea las tablas en la db.

from sqlalchemy.exc import OperationalError, DatabaseError

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_s5 import router as s5_router
from database.session import Base, engine

import time


app = FastAPI(
    title="FitGate API",
    version="1.0.0",
    description="API de reconocimiento facial: alta de personas, enrolamiento de "
    "embeddings faciales y reconocimiento de rostros.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(s5_router, prefix="/api/v1", tags=["Persons"])


@app.on_event("startup")
def on_startup() -> None:

    # Crea las tablas en MySQL al iniciar la aplicación
    retries = 5
    while retries > 0:
        try:
            print("Intentando crear y sincronizar tablas en MySQL...")
            Base.metadata.create_all(bind=engine)
            print("¡Conexión exitosa a MySQL y tablas sincronizadas correctamente!")
            break
        except (OperationalError, DatabaseError) as e:
            retries -= 1
            print(f"MySQL no responde aún ({retries} reintentos restantes)... Esperando 3 segundos.")
            time.sleep(3)

    if retries == 0:
        print("ERROR CRÍTICO: No se pudo conectar a MySQL tras varios intentos.")
        raise RuntimeError("No se pudo establecer conexión con la base de datos MySQL.")


@app.get("/health", tags=["Monitoreo"])
def health_check():
    # Endpoint de uso interno para el Healthcheck
    return {"status": "ok"}
