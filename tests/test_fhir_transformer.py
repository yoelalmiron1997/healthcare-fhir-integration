"""Pruebas unitarias de app.fhir_transformer.build_fhir_patient."""

from app.fhir_transformer import build_fhir_patient
from app.models import Address, GenderEnum, PatientIn


def _sample_patient_in(**overrides) -> PatientIn:
    data = {
        "first_name": "Juan",
        "last_name": "Pérez",
        "birth_date": "1985-04-12",
        "gender": GenderEnum.MALE,
        "document_id": "12345678",
        "phone": "+541112345678",
        "email": "juan.perez@example.com",
        "address": Address(
            line="Av. Siempre Viva 123",
            city="Buenos Aires",
            state="BA",
            postal_code="1000",
            country="AR",
        ),
    }
    data.update(overrides)
    return PatientIn(**data)


def test_build_fhir_patient_estructura_basica():
    patient_in = _sample_patient_in()
    resource = build_fhir_patient(patient_in, resource_id="test-id-1")

    assert resource["resourceType"] == "Patient"
    assert resource["id"] == "test-id-1"
    assert resource["gender"] == "male"
    assert resource["birthDate"] == "1985-04-12"


def test_build_fhir_patient_identifier():
    patient_in = _sample_patient_in()
    resource = build_fhir_patient(patient_in, resource_id="test-id-2")

    assert resource["identifier"][0]["value"] == "12345678"
    assert resource["identifier"][0]["system"].startswith("urn:")


def test_build_fhir_patient_name():
    patient_in = _sample_patient_in()
    resource = build_fhir_patient(patient_in, resource_id="test-id-3")

    name = resource["name"][0]
    assert name["family"] == "Pérez"
    assert name["given"] == ["Juan"]
    assert name["use"] == "official"


def test_build_fhir_patient_telecom():
    patient_in = _sample_patient_in()
    resource = build_fhir_patient(patient_in, resource_id="test-id-4")

    systems = {t["system"] for t in resource["telecom"]}
    assert systems == {"phone", "email"}


def test_build_fhir_patient_sin_datos_opcionales():
    patient_in = _sample_patient_in(phone=None, email=None, address=None)
    resource = build_fhir_patient(patient_in, resource_id="test-id-5")

    assert "telecom" not in resource
    assert "address" not in resource


def test_build_fhir_patient_genera_id_si_no_se_provee():
    patient_in = _sample_patient_in()
    resource = build_fhir_patient(patient_in)

    assert isinstance(resource["id"], str)
    assert len(resource["id"]) > 0
