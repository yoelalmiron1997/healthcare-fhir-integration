"""
Lógica de transformación: convierte un PatientIn (payload validado)
en un recurso FHIR Patient (https://www.hl7.org/fhir/patient.html).

Se mantiene deliberadamente simple (subset de FHIR R4) para fines
didácticos / de simulación de integración.
"""

import uuid

from app.models import PatientIn

# Sistema de identificación utilizado para el "identifier" del paciente.
# En un caso real esto sería la URN/OID oficial del sistema fuente.
IDENTIFIER_SYSTEM = "urn:example:health-integration:document-id"


def build_fhir_patient(patient_in: PatientIn, resource_id: str | None = None) -> dict:
    """
    Construye un recurso FHIR Patient a partir de los datos validados de entrada.

    Args:
        patient_in: datos de entrada ya validados por Pydantic.
        resource_id: id a asignar al recurso; si no se provee se genera uno nuevo.

    Returns:
        dict con la estructura de un recurso FHIR Patient (R4).
    """

    resource_id = resource_id or str(uuid.uuid4())

    telecom = []
    if patient_in.phone:
        telecom.append({"system": "phone", "value": patient_in.phone, "use": "mobile"})
    if patient_in.email:
        telecom.append({"system": "email", "value": patient_in.email})

    address = []
    if patient_in.address:
        addr = patient_in.address
        fhir_address = {}
        if addr.line:
            fhir_address["line"] = [addr.line]
        if addr.city:
            fhir_address["city"] = addr.city
        if addr.state:
            fhir_address["state"] = addr.state
        if addr.postal_code:
            fhir_address["postalCode"] = addr.postal_code
        if addr.country:
            fhir_address["country"] = addr.country
        if fhir_address:
            address.append(fhir_address)

    fhir_patient = {
        "resourceType": "Patient",
        "id": resource_id,
        "identifier": [
            {
                "system": IDENTIFIER_SYSTEM,
                "value": patient_in.document_id,
            }
        ],
        "name": [
            {
                "use": "official",
                "family": patient_in.last_name,
                "given": [patient_in.first_name],
            }
        ],
        "gender": patient_in.gender.value,
        "birthDate": patient_in.birth_date.isoformat(),
    }

    if telecom:
        fhir_patient["telecom"] = telecom
    if address:
        fhir_patient["address"] = address

    return fhir_patient
