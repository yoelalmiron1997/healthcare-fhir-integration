"""
Capa de persistencia usando SQLite.

Guarda, por cada paciente:
 - id (uuid)
 - fecha de creación
 - datos originales recibidos (JSON crudo)
 - recurso FHIR generado (JSON)
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "patients.db"


def _get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Crea la tabla de pacientes si no existe. Se llama al iniciar la app."""
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                source_data TEXT NOT NULL,
                fhir_resource TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_patient(patient_id: str, source_data: dict, fhir_resource: dict) -> dict:
    """Inserta un nuevo registro de paciente y devuelve el registro completo."""
    created_at = datetime.now(timezone.utc).isoformat()
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT INTO patients (id, created_at, source_data, fhir_resource) VALUES (?, ?, ?, ?)",
            (
                patient_id,
                created_at,
                json.dumps(source_data, ensure_ascii=False),
                json.dumps(fhir_resource, ensure_ascii=False),
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "id": patient_id,
        "created_at": created_at,
        "source_data": source_data,
        "fhir_resource": fhir_resource,
    }


def get_patient(patient_id: str) -> Optional[dict]:
    """Recupera un paciente por id. Devuelve None si no existe."""
    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "source_data": json.loads(row["source_data"]),
        "fhir_resource": json.loads(row["fhir_resource"]),
    }


def list_patients() -> list[dict]:
    """Devuelve todos los pacientes almacenados."""
    conn = _get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM patients ORDER BY created_at DESC"
        ).fetchall()
    finally:
        conn.close()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "source_data": json.loads(row["source_data"]),
            "fhir_resource": json.loads(row["fhir_resource"]),
        }
        for row in rows
    ]
