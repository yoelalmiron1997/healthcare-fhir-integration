"""
Capa de persistencia alternativa: un archivo .json por paciente.
Útil para pruebas UAT o entornos donde no se quiera usar SQLite.

Cada archivo se guarda en data/json_store/<id>.json con la misma
estructura que devuelve la capa de SQLite (database.py), para que
ambos backends sean intercambiables desde la API.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

JSON_STORE_DIR = Path(__file__).resolve().parent.parent / "data" / "json_store"


def init_store() -> None:
    """Crea el directorio de almacenamiento si no existe."""
    JSON_STORE_DIR.mkdir(parents=True, exist_ok=True)


def save_patient(patient_id: str, source_data: dict, fhir_resource: dict) -> dict:
    """Guarda un paciente como archivo JSON individual."""
    init_store()
    created_at = datetime.now(timezone.utc).isoformat()
    record = {
        "id": patient_id,
        "created_at": created_at,
        "source_data": source_data,
        "fhir_resource": fhir_resource,
    }

    file_path = JSON_STORE_DIR / f"{patient_id}.json"
    file_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    return record


def get_patient(patient_id: str) -> Optional[dict]:
    """Recupera un paciente por id desde su archivo JSON."""
    file_path = JSON_STORE_DIR / f"{patient_id}.json"
    if not file_path.exists():
        return None
    return json.loads(file_path.read_text(encoding="utf-8"))


def list_patients() -> list[dict]:
    """Devuelve todos los pacientes almacenados, ordenados por fecha de creación descendente."""
    init_store()
    records = []
    for file_path in JSON_STORE_DIR.glob("*.json"):
        records.append(json.loads(file_path.read_text(encoding="utf-8")))
    records.sort(key=lambda r: r["created_at"], reverse=True)
    return records
