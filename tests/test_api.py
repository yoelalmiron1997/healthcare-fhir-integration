"""
Pruebas de integración de la API usando TestClient de FastAPI.

Se fuerza el backend de almacenamiento a JSON, apuntando a un directorio
temporal, para que los tests no dependan ni contaminen datos reales.
"""

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    Crea un TestClient con el backend de almacenamiento JSON apuntando
    a un directorio temporal, para aislar cada test.
    """
    monkeypatch.setenv("STORAGE_MODE", "json")

    from app import storage_json
    monkeypatch.setattr(storage_json, "JSON_STORE_DIR", tmp_path / "json_store")

    from app import main as main_module
    importlib.reload(main_module)  # recarga app.main para tomar el nuevo STORAGE_MODE

    with TestClient(main_module.app) as test_client:
        yield test_client


VALID_PATIENT = {
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


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_patient_valido(client):
    response = client.post("/patients", json=VALID_PATIENT)
    assert response.status_code == 201

    body = response.json()
    assert body["fhir_resource"]["resourceType"] == "Patient"
    assert body["fhir_resource"]["name"][0]["family"] == "Pérez"
    assert body["source_data"] == VALID_PATIENT


def test_create_patient_sin_campo_obligatorio(client):
    invalid_patient = VALID_PATIENT.copy()
    del invalid_patient["last_name"]

    response = client.post("/patients", json=invalid_patient)
    assert response.status_code == 422
    assert "errors" in response.json()["detail"]


def test_create_patient_gender_invalido(client):
    invalid_patient = VALID_PATIENT.copy()
    invalid_patient["gender"] = "no-es-un-genero-valido"

    response = client.post("/patients", json=invalid_patient)
    assert response.status_code == 422


def test_create_patient_fecha_nacimiento_futura(client):
    invalid_patient = VALID_PATIENT.copy()
    invalid_patient["birth_date"] = "2999-01-01"

    response = client.post("/patients", json=invalid_patient)
    assert response.status_code == 422


def test_get_patient_existente(client):
    create_response = client.post("/patients", json=VALID_PATIENT)
    patient_id = create_response.json()["id"]

    get_response = client.get(f"/patients/{patient_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == patient_id


def test_get_patient_inexistente(client):
    response = client.get("/patients/no-existe-este-id")
    assert response.status_code == 404


def test_list_patients(client):
    client.post("/patients", json=VALID_PATIENT)
    second_patient = VALID_PATIENT.copy()
    second_patient["document_id"] = "87654321"
    second_patient["first_name"] = "Ana"
    client.post("/patients", json=second_patient)

    response = client.get("/patients")
    assert response.status_code == 200
    assert len(response.json()) >= 2
