# Healthcare FHIR Integration (Simulación)

Mini proyecto en Python que simula una integración de tipo *healthcare*:

1. Expone una **API REST con FastAPI** que recibe datos de pacientes en JSON.
2. **Valida** los campos obligatorios y formatos (Pydantic).
3. **Transforma** los datos a un recurso **FHIR Patient** (R4).
4. **Persiste** el resultado en **SQLite** o en **archivos JSON**, según configuración.
5. Incluye una carpeta de **pruebas UAT** con casos de prueba, datos de ejemplo,
   pasos de ejecución y resultados esperados, además de tests automatizados con `pytest`.

## Estructura del proyecto

```
healthcare-fhir-integration/
├── README.md                     <- este archivo
├── requirements.txt              <- dependencias del proyecto
├── Dockerfile                    <- imagen Docker de la API
├── docker-compose.yml            <- orquestación local con persistencia de datos
├── render.yaml                   <- blueprint de despliegue en Render (demo en vivo)
├── .dockerignore                 <- archivos excluidos al construir la imagen
├── app/                          <- código fuente de la API
│   ├── main.py                   <- endpoints FastAPI
│   ├── models.py                 <- validación de entrada (Pydantic)
│   ├── fhir_transformer.py       <- transformación a recurso FHIR Patient
│   ├── database.py               <- persistencia en SQLite
│   └── storage_json.py           <- persistencia alternativa en archivos JSON
├── tests/                        <- tests automatizados (pytest)
│   ├── test_api.py               <- tests de integración de la API
│   └── test_fhir_transformer.py  <- tests unitarios de la transformación FHIR
├── uat/                          <- pruebas de aceptación de usuario (UAT)
│   ├── README.md
│   ├── test_cases.md             <- casos de prueba con pasos y resultados esperados
│   ├── sample_data/              <- payloads JSON válidos e inválidos de ejemplo
│   └── execution_results_template.md
└── data/                         <- (generado en runtime) SQLite / JSON store
```

## Requisitos

- Python 3.10+

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución de la API

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`, con documentación
interactiva (Swagger UI) en `http://127.0.0.1:8000/docs`.

### Elegir el backend de almacenamiento

Por defecto se usa **SQLite** (`data/patients.db`). Para usar archivos JSON
individuales (`data/json_store/<id>.json`), definir la variable de entorno:

```bash
STORAGE_MODE=json uvicorn app.main:app --reload
```

## Endpoints

| Método | Ruta                  | Descripción                                              |
|--------|-----------------------|-----------------------------------------------------------|
| GET    | `/health`             | Chequeo de salud del servicio y backend activo            |
| POST   | `/patients`           | Recibe, valida, transforma a FHIR y guarda un paciente     |
| GET    | `/patients`           | Lista todos los pacientes almacenados                      |
| GET    | `/patients/{id}`      | Obtiene un paciente por id (incluye su recurso FHIR)       |

### Ejemplo de request — `POST /patients`

```json
{
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
    "country": "AR"
  }
}
```

Campos **obligatorios**: `first_name`, `last_name`, `birth_date` (`YYYY-MM-DD`),
`gender` (`male` | `female` | `other` | `unknown`), `document_id`.
Campos opcionales: `phone`, `email`, `address`.

### Ejemplo de respuesta (201 Created)

```json
{
  "id": "aa10e573-23d8-450e-ad29-c31055a82cc7",
  "created_at": "2026-07-08T19:55:30.903785+00:00",
  "source_data": { "...": "..." },
  "fhir_resource": {
    "resourceType": "Patient",
    "id": "aa10e573-23d8-450e-ad29-c31055a82cc7",
    "identifier": [
      { "system": "urn:example:health-integration:document-id", "value": "12345678" }
    ],
    "name": [{ "use": "official", "family": "Pérez", "given": ["Juan"] }],
    "gender": "male",
    "birthDate": "1985-04-12",
    "telecom": [
      { "system": "phone", "value": "+541112345678", "use": "mobile" },
      { "system": "email", "value": "juan.perez@example.com" }
    ],
    "address": [
      {
        "line": ["Av. Siempre Viva 123"],
        "city": "Buenos Aires",
        "state": "BA",
        "postalCode": "1000",
        "country": "AR"
      }
    ]
  }
}
```

### Ejemplo de error de validación (422)

```json
{
  "detail": {
    "message": "Error de validación en los datos del paciente",
    "errors": [
      { "type": "missing", "loc": ["last_name"], "msg": "Field required" }
    ]
  }
}
```

## Ejecución con Docker

El proyecto incluye `Dockerfile` y `docker-compose.yml` para correrlo sin
instalar Python ni dependencias localmente.

### Opción A: con docker-compose (recomendado)

```bash
docker compose up --build
```

- La API queda disponible en `http://localhost:8000` (docs en `/docs`).
- Los datos (`data/patients.db` o `data/json_store/`) se guardan en la
  carpeta `./data` del host gracias al volumen configurado, por lo que
  **persisten** aunque se detenga o borre el contenedor.
- Para usar el backend JSON en lugar de SQLite, editar `STORAGE_MODE` en
  `docker-compose.yml` (o sobreescribirlo al vuelo):
  ```bash
  STORAGE_MODE=json docker compose up --build
  ```
- Para detenerlo: `Ctrl+C` o `docker compose down`.

### Opción B: con docker directamente

```bash
docker build -t healthcare-fhir-api .
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" healthcare-fhir-api
```

Con backend JSON:

```bash
docker run --rm -p 8000:8000 -v "$(pwd)/data:/app/data" -e STORAGE_MODE=json healthcare-fhir-api
```

### Verificar que quedó arriba

```bash
curl http://localhost:8000/health
# {"status":"ok","storage_mode":"sqlite"}
```

La imagen incluye un `HEALTHCHECK` propio, por lo que `docker ps` mostrará el
estado `healthy` una vez que la API responda correctamente.

## Subir el proyecto a GitHub

```bash
cd healthcare-fhir-integration
git init
git add .
git commit -m "Proyecto inicial: API healthcare -> FHIR con Docker y UAT"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/<tu-repo>.git
git push -u origin main
```

(Reemplazá `<tu-usuario>/<tu-repo>` por los datos de tu repositorio en GitHub.
Si el repo ya existe con contenido, primero cloná y copiá estos archivos adentro
en lugar de `git init`.)

## Despliegue en la nube (demo en vivo con Render)

El proyecto incluye un `render.yaml` (blueprint de infraestructura como código)
para desplegarlo gratis en [Render](https://render.com), usando el mismo
`Dockerfile` que ya probamos localmente.

### Pasos

1. Subir el proyecto a GitHub (ver sección anterior). El repo puede ser público o privado.
2. Entrar a [render.com](https://render.com) y crear una cuenta (no pide tarjeta para el plan Free).
3. Click en **New +** → **Blueprint**.
4. Conectar tu cuenta de GitHub y seleccionar el repositorio.
5. Render detecta automáticamente `render.yaml` y propone crear el servicio
   `healthcare-fhir-api` (Docker, plan Free). Confirmar con **Apply**.
6. Esperar el primer build (unos minutos). Cuando termine, Render te da una URL
   pública del tipo `https://healthcare-fhir-api-xxxx.onrender.com`.
7. Probar: `https://healthcare-fhir-api-xxxx.onrender.com/health` y
   `https://healthcare-fhir-api-xxxx.onrender.com/docs`.

### Cosas a tener en cuenta sobre el plan Free de Render

- El servicio se "duerme" tras 15 minutos sin tráfico; el primer request
  después de eso tarda ~30-60 segundos en responder mientras arranca de nuevo
  (normal para una demo, no ideal para producción).
- El plan Free no incluye disco persistente: los datos guardados (SQLite o
  JSON) se pierden en cada redeploy o reinicio del servicio. Para esta demo
  no es un problema; si necesitás persistencia real, agregar un disco (plan
  pago) o una base de datos administrada.
- Incluye 750 horas gratis de cómputo por mes, más que suficiente para un
  proyecto de portfolio.

### Agregar el link al README (opcional, recomendado para GitHub)

Una vez que tengas la URL, podés agregar algo así arriba del todo del README:

```markdown
🔗 **Demo en vivo:** https://healthcare-fhir-api-xxxx.onrender.com/docs
```

## Tests automatizados

```bash
pytest tests/ -v
```

Incluye:
- Tests unitarios de la transformación a FHIR (`test_fhir_transformer.py`).
- Tests de integración de la API con `TestClient` (`test_api.py`), cubriendo
  casos válidos, campos faltantes, valores inválidos y consultas.

## Pruebas UAT

Ver [`uat/README.md`](uat/README.md) y [`uat/test_cases.md`](uat/test_cases.md)
para los casos de prueba de aceptación de usuario, con datos de ejemplo,
pasos de ejecución y resultados esperados pensados para validación manual
o por un equipo de QA / analistas funcionales.

## Notas de diseño

- El recurso FHIR generado es un subconjunto simplificado de **FHIR R4 Patient**,
  suficiente para fines didácticos / de simulación de integración (no certificado
  ni validado contra un servidor FHIR real).
- El campo `identifier.system` usa una URN de ejemplo
  (`urn:example:health-integration:document-id`); en un caso real correspondería
  reemplazarlo por el OID/URI oficial del sistema fuente de identificación.
- La capa de persistencia está desacoplada (`database.py` / `storage_json.py`)
  para poder intercambiar el backend sin tocar la lógica de la API.
