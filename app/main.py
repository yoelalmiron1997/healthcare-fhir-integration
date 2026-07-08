"""
API REST (FastAPI) que simula una integración de salud:

1. Recibe datos de pacientes en JSON (POST /patients).
2. Valida los campos obligatorios (Pydantic, ver app/models.py).
3. Transforma los datos a un recurso FHIR Patient (app/fhir_transformer.py).
4. Persiste el registro en SQLite o en archivos JSON, según la
   variable de entorno STORAGE_MODE (default: "sqlite").

Ejecutar con:
    uvicorn app.main:app --reload
"""

import os
from typing import Literal

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app import database as sqlite_storage
from app import storage_json
from app.fhir_transformer import build_fhir_patient
from app.models import PatientIn

STORAGE_MODE: Literal["sqlite", "json"] = os.getenv("STORAGE_MODE", "sqlite").lower()  # type: ignore

app = FastAPI(
    title="Healthcare FHIR Integration (Simulación)",
    description=(
        "Mini proyecto que simula una integración healthcare: recibe datos de "
        "pacientes, los valida, los transforma a un recurso FHIR Patient y los "
        "persiste en SQLite o JSON."
    ),
    version="1.0.0",
)


def _storage():
    """Devuelve el módulo de almacenamiento activo según STORAGE_MODE."""
    return sqlite_storage if STORAGE_MODE == "sqlite" else storage_json


@app.on_event("startup")
def on_startup() -> None:
    if STORAGE_MODE == "sqlite":
        sqlite_storage.init_db()
    else:
        storage_json.init_store()


@app.get("/health", tags=["Sistema"])
def health_check() -> dict:
    """Chequeo simple de salud del servicio."""
    return {"status": "ok", "storage_mode": STORAGE_MODE}


@app.post(
    "/patients",
    status_code=status.HTTP_201_CREATED,
    tags=["Pacientes"],
    summary="Crear paciente: valida, transforma a FHIR y persiste",
)
def create_patient(payload: dict) -> JSONResponse:
    """
    Recibe un JSON con datos de paciente, lo valida contra PatientIn,
    lo transforma a un recurso FHIR Patient y lo guarda.

    Devuelve 201 con el registro completo (datos originales + recurso FHIR)
    si todo es correcto, o 422 con el detalle de los errores de validación.
    """
    try:
        patient_in = PatientIn(**payload)
    except ValidationError as exc:
        # exc.errors() puede incluir objetos no serializables (p. ej. excepciones
        # dentro de "ctx"), por lo que nos quedamos solo con los campos serializables.
        clean_errors = [
            {
                "type": err.get("type"),
                "loc": list(err.get("loc", [])),
                "msg": err.get("msg"),
            }
            for err in exc.errors()
        ]
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Error de validación en los datos del paciente",
                "errors": clean_errors,
            },
        )

    fhir_resource = build_fhir_patient(patient_in)
    resource_id = fhir_resource["id"]

    record = _storage().save_patient(
        patient_id=resource_id,
        source_data=payload,
        fhir_resource=fhir_resource,
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=record)


@app.get("/patients", tags=["Pacientes"], summary="Listar todos los pacientes guardados")
def list_patients() -> list[dict]:
    return _storage().list_patients()


@app.get(
    "/patients/{patient_id}",
    tags=["Pacientes"],
    summary="Obtener un paciente por id (incluye su recurso FHIR)",
)
def get_patient(patient_id: str) -> dict:
    record = _storage().get_patient(patient_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente no encontrado")
    return record
