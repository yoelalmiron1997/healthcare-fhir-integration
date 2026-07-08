# Casos de Prueba UAT — Integración Healthcare (Patient → FHIR)

URL base asumida: `http://127.0.0.1:8000`

---

## UAT-01 — Alta de paciente con todos los datos (caso feliz completo)

- **Precondición:** API levantada, storage vacío o indistinto.
- **Datos de entrada:** `sample_data/valid_patient_01.json`
- **Pasos:**
  1. Ejecutar:
     ```bash
     curl -s -X POST http://127.0.0.1:8000/patients \
       -H "Content-Type: application/json" \
       -d @uat/sample_data/valid_patient_01.json
     ```
  2. Guardar el `id` devuelto en la respuesta.
  3. Ejecutar `GET /patients/{id}` con ese id.
- **Resultado esperado:**
  - El POST responde `201 Created`.
  - El GET responde `200 OK` con el mismo registro.
- **Criterios de validación:**
  - `fhir_resource.resourceType == "Patient"`
  - `fhir_resource.name[0].family == "Pérez"` y `given[0] == "Juan"`
  - `fhir_resource.gender == "male"`
  - `fhir_resource.birthDate == "1985-04-12"`
  - `fhir_resource.identifier[0].value == "12345678"`
  - `fhir_resource.telecom` contiene entradas `phone` y `email`
  - `fhir_resource.address[0].city == "Buenos Aires"`
  - `source_data` refleja exactamente el JSON enviado

---

## UAT-02 — Alta de paciente solo con campos obligatorios (caso feliz mínimo)

- **Precondición:** API levantada.
- **Datos de entrada:** `sample_data/valid_patient_02_minimo.json`
- **Pasos:**
  1. Enviar `POST /patients` con el archivo indicado.
- **Resultado esperado:** `201 Created`.
- **Criterios de validación:**
  - El recurso FHIR se genera correctamente aun sin `phone`, `email` ni `address`.
  - `fhir_resource` **no** contiene las claves `telecom` ni `address` (no se agregan vacías).
  - `fhir_resource.identifier[0].value == "87654321"`.

---

## UAT-03 — Rechazo por campo obligatorio faltante

- **Precondición:** API levantada.
- **Datos de entrada:** `sample_data/invalid_patient_falta_campo.json` (falta `last_name`)
- **Pasos:**
  1. Enviar `POST /patients` con el archivo indicado.
- **Resultado esperado:** `422 Unprocessable Entity`.
- **Criterios de validación:**
  - El cuerpo de la respuesta incluye `detail.errors`.
  - Al menos un error tiene `"loc": ["last_name"]` y `"type": "missing"`.
  - **No** se crea ningún registro (verificar con `GET /patients` que no aumentó el conteo).

---

## UAT-04 — Rechazo por valor de género inválido

- **Precondición:** API levantada.
- **Datos de entrada:** `sample_data/invalid_patient_genero_invalido.json` (`"gender": "masculino"`)
- **Pasos:**
  1. Enviar `POST /patients` con el archivo indicado.
- **Resultado esperado:** `422 Unprocessable Entity`.
- **Criterios de validación:**
  - El error referencia el campo `gender`.
  - Los valores válidos aceptados son únicamente: `male`, `female`, `other`, `unknown`.

---

## UAT-05 — Rechazo por fecha de nacimiento futura

- **Precondición:** API levantada.
- **Datos de entrada:** `sample_data/invalid_patient_fecha_futura.json` (`"birth_date": "2999-01-01"`)
- **Pasos:**
  1. Enviar `POST /patients` con el archivo indicado.
- **Resultado esperado:** `422 Unprocessable Entity`.
- **Criterios de validación:**
  - El error referencia el campo `birth_date`.
  - El mensaje indica que la fecha no puede ser futura.

---

## UAT-06 — Rechazo por formato de fecha y email inválidos

- **Precondición:** API levantada.
- **Datos de entrada:** `sample_data/invalid_patient_formato_incorrecto.json`
  (`birth_date` en formato `DD-MM-YYYY` en lugar de `YYYY-MM-DD`, y `email` sin `@`)
- **Pasos:**
  1. Enviar `POST /patients` con el archivo indicado.
- **Resultado esperado:** `422 Unprocessable Entity`.
- **Criterios de validación:**
  - Se reportan errores tanto para `birth_date` como para `email`.

---

## UAT-07 — Consulta de paciente inexistente

- **Precondición:** API levantada.
- **Pasos:**
  1. Ejecutar `GET /patients/id-que-no-existe-123`.
- **Resultado esperado:** `404 Not Found`.
- **Criterios de validación:**
  - El cuerpo indica `"detail": "Paciente no encontrado"`.

---

## UAT-08 — Listado de pacientes

- **Precondición:** haber ejecutado al menos UAT-01 y UAT-02 previamente.
- **Pasos:**
  1. Ejecutar `GET /patients`.
- **Resultado esperado:** `200 OK` con un array JSON.
- **Criterios de validación:**
  - El array contiene al menos los pacientes creados en UAT-01 y UAT-02.
  - Cada elemento tiene las claves `id`, `created_at`, `source_data`, `fhir_resource`.

---

## UAT-09 — Persistencia entre reinicios (SQLite)

- **Precondición:** `STORAGE_MODE` no seteado o `STORAGE_MODE=sqlite`.
- **Pasos:**
  1. Crear un paciente (POST /patients).
  2. Detener el servidor (`Ctrl+C`) y volver a iniciarlo (`uvicorn app.main:app`).
  3. Ejecutar `GET /patients/{id}` con el id creado en el paso 1.
- **Resultado esperado:** el paciente sigue existiendo tras el reinicio.
- **Criterios de validación:**
  - `200 OK` y los mismos datos que al momento de la creación.
  - El archivo `data/patients.db` existe en disco.

---

## UAT-10 — Cambio de backend a almacenamiento JSON

- **Precondición:** API detenida.
- **Pasos:**
  1. Iniciar la API con `STORAGE_MODE=json uvicorn app.main:app`.
  2. Ejecutar `GET /health` y verificar `storage_mode`.
  3. Crear un paciente (POST /patients).
  4. Verificar en el sistema de archivos que existe
     `data/json_store/{id}.json` con el contenido esperado.
- **Resultado esperado:**
  - `GET /health` responde `{"status": "ok", "storage_mode": "json"}`.
  - El archivo JSON individual se crea correctamente y su contenido
    coincide con la respuesta del POST.

---

## UAT-11 — Health check

- **Precondición:** API levantada.
- **Pasos:**
  1. Ejecutar `GET /health`.
- **Resultado esperado:** `200 OK`, `{"status": "ok", "storage_mode": "<sqlite|json>"}`.
