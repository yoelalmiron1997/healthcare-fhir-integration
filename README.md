# Healthcare FHIR Integration (Simulación)

[![CI/CD](https://github.com/yoelalmiron1997/healthcare-fhir-integration/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yoelalmiron1997/healthcare-fhir-integration/actions/workflows/ci-cd.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED.svg)](Dockerfile)

Mini proyecto en Python que simula una integración de tipo *healthcare*:

1. Expone una **API REST con FastAPI** que recibe datos de pacientes en JSON.
2. **Valida** los campos obligatorios y formatos (Pydantic).
3. **Transforma** los datos a un recurso **FHIR Patient** (R4).
4. **Persiste** el resultado en **SQLite** o en **archivos JSON**, según configuración.
5. Incluye una carpeta de **pruebas UAT** con casos de prueba, datos de ejemplo,
   pasos de ejecución y resultados esperados, además de tests automatizados con `pytest`.

> 🔗 **Demo en vivo:** [https://healthcare-fhir-api.onrender.com/docs](https://healthcare-fhir-api.onrender.com/docs)
> (desplegada en Render con el plan Free — puede tardar ~30-60s en responder
> si estuvo inactiva; ver [Despliegue en la nube](#despliegue-en-la-nube-demo-en-vivo-con-render))

## Índice

- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución de la API](#ejecución-de-la-api)
- [Endpoints](#endpoints)
- [Ejecución con Docker](#ejecución-con-docker)
- [CI/CD (GitHub Actions)](#cicd-github-actions)
- [Subir el proyecto a GitHub](#subir-el-proyecto-a-github)
- [Despliegue en la nube (Render)](#despliegue-en-la-nube-demo-en-vivo-con-render)
- [Tests automatizados](#tests-automatizados)
- [Pruebas UAT](#pruebas-uat)
- [Notas de diseño](#notas-de-diseño)
- [Licencia](#licencia)

## Estructura del proyecto

```
healthcare-fhir-integration/
├── README.md                     <- este archivo
├── requirements.txt              <- dependencias del proyecto
├── .github/
│   └── workflows/
│       └── ci-cd.yml             <- pipeline de CI/CD (tests, build Docker, deploy)
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

## CI/CD (GitHub Actions)

El proyecto incluye un pipeline en `.github/workflows/ci-cd.yml` que corre
automáticamente en cada `push` y en cada Pull Request contra `main`. Así, a
medida que el proyecto evoluciona, cada cambio se valida solo antes de llegar
a producción.

### Qué hace el pipeline

| Job              | Cuándo corre                          | Qué valida                                                    |
|-------------------|----------------------------------------|-----------------------------------------------------------------|
| `test`            | Todo push y todo PR contra `main`      | Corre `pytest tests/ -v` (los 14 tests de API + transformación FHIR) |
| `docker-build`    | Después de `test`, si pasó             | Que la imagen Docker sigue construyendo sin errores            |
| `deploy`          | Solo en push directo a `main`, después de que los dos anteriores pasen | Dispara un deploy en Render (opcional, ver abajo) |

Si `test` falla, `docker-build` y `deploy` ni siquiera se ejecutan — el
pipeline corta ahí. Esto evita desplegar código que rompe algo.

### Configurar el deploy automático a Render (opcional)

Por defecto, Render ya redepliega automáticamente cada vez que detecta un
push a la rama conectada (esto pasa por fuera de GitHub Actions). Si en cambio
querés que el deploy dependa explícitamente de que los tests pasen en CI:

1. En Render: abrí tu servicio → **Settings** → buscá **Deploy Hook** → copiá la URL.
2. En Render: en el mismo servicio, desactivá **Auto-Deploy** (para que no
   despliegue automáticamente en cada push, y lo haga solo cuando este
   workflow lo dispare después de que los tests pasen).
3. En GitHub: andá a tu repo → **Settings** → **Secrets and variables** →
   **Actions** → **New repository secret**.
4. Nombre: `RENDER_DEPLOY_HOOK_URL`. Valor: la URL que copiaste en el paso 1.
5. Listo — a partir del próximo push a `main` que pase los tests, el job
   `deploy` va a llamar a esa URL y disparar el redeploy en Render.

Si no configurás el secret, el job `deploy` simplemente se salta ese paso sin
marcar error (podés dejar el auto-deploy nativo de Render funcionando como
está, y usar el pipeline solo para tests + validación de Docker).

### Proteger la rama `main` (recomendado)

Para que nadie (ni vos sin querer) pueda mergear código que rompe los tests:

1. En GitHub: **Settings** → **Branches** → **Add branch protection rule**.
2. Rama: `main`.
3. Activá **Require status checks to pass before merging** y seleccioná el
   check `Tests (pytest)` (y opcionalmente `Build de la imagen Docker
   (validación)`).
4. Guardar.

A partir de ahí, un Pull Request contra `main` no se puede mergear hasta que
el pipeline esté en verde.

### Ver el estado del pipeline

En GitHub, pestaña **Actions** del repo vas a ver cada corrida, con el detalle
de qué job pasó o falló y los logs completos de `pytest`. El badge al inicio
de este README también refleja el estado del último run sobre `main`.

## Subir el proyecto a GitHub

```bash
cd healthcare-fhir-integration
git init
git add .
git commit -m "Proyecto inicial: API healthcare -> FHIR con Docker y UAT"
git branch -M main
git remote add origin https://github.com/yoelalmiron1997/healthcare-fhir-integration.git
git push -u origin main
```

(Esto ya está hecho en el repo actual — dejamos estos comandos documentados
para el caso de que alguien clone el proyecto desde cero y quiera subirlo a
su propia cuenta.)

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

### Link a la demo en el README

✅ Ya agregado arriba del todo de este README, apuntando a
`https://healthcare-fhir-api.onrender.com/docs`.

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

## Licencia

Este proyecto está bajo la licencia **MIT** — ver el archivo [`LICENSE`](LICENSE)
para el texto completo. En resumen: podés usar, copiar, modificar y distribuir
este código libremente, incluso con fines comerciales, manteniendo el aviso
de copyright original.
