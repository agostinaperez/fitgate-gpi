# Lógica compartida de creación de personas (Person), usada por el CRUD de
# personas (routes_s5.create_person).

from datetime import date
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.entities import Person


def get_or_create_person(
    db: Session,
    nombre: str,
    apellido: str,
    email: str,
    extra: Optional[Dict[str, Any]] = None,
    dni: Optional[str] = None,
    telefono: Optional[str] = None,
    activo: bool = True,
    membresia_hasta: Optional[date] = None,
) -> Person:
    """Busca una Person por email; si no existe, la crea."""
    person = db.query(Person).filter(Person.email == email).first()

    if person:
        return person

    person = Person(
        nombre=nombre,
        apellido=apellido,
        email=email,
        extra=extra,
        dni=dni,
        telefono=telefono,
        activo=activo,
        membresia_hasta=membresia_hasta,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person
