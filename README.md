# Healthcare FHIR Integration

Proyecto de ejemplo desarrollado en Python para simular una integración entre un sistema externo y una plataforma de salud.

La API recibe información de pacientes, valida los datos, los transforma a un recurso **FHIR Patient** y los almacena en SQLite.

## Links

- Demo API: https://healthcare-fhir-api.onrender.com
- Swagger UI: https://healthcare-fhir-api.onrender.com/docs
- Health check: https://healthcare-fhir-api.onrender.com/health
- Repositorio: https://github.com/yoelalmiron1997/healthcare-fhir-integration# Healthcare FHIR Integration

Proyecto de ejemplo desarrollado en Python para simular una integración entre un sistema externo y una plataforma de salud.

La API recibe información de pacientes, valida los datos, los transforma a un recurso **FHIR Patient** y los almacena en SQLite.

## Links

- Demo API: https://healthcare-fhir-api.onrender.com
- Swagger UI: https://healthcare-fhir-api.onrender.com/docs 
- Health check: https://healthcare-fhir-api.onrender.com/health
- Repositorio: https://github.com/yoelalmiron1997/healthcare-fhir-integration

## Tecnologías

- Python
- FastAPI
- Pydantic
- SQLite
- Docker
- Pytest
- GitHub Actions

## Funcionalidades

- API REST para gestión de pacientes
- Validación de datos de entrada
- Conversión a formato FHIR Patient
- Persistencia en SQLite
- Documentación automática con Swagger
- Tests automatizados
- Casos de prueba UAT
- Contenedor Docker

## Estructura

```
app/
tests/
uat/
Dockerfile
docker-compose.yml
requirements.txt
README.md
```

## Ejecutar localmente

```bash
git clone https://github.com/yoelalmiron1997/healthcare-fhir-integration.git

cd healthcare-fhir-integration

python -m venv .venv

# Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

La API estará disponible en:

```
http://localhost:8000
```

Documentación Swagger:

```
http://localhost:8000/docs
```

## Docker

```bash
docker compose up --build
```

## Ejecutar tests

```bash
pytest
```

## Ejemplo de uso

```http
POST /patients
```

```json
{
  "first_name": "Juan",
  "last_name": "Perez",
  "birth_date": "1985-05-15",
  "gender": "male",
  "document_id": "30123456"
}
```

## Objetivo

Este proyecto fue desarrollado como práctica para trabajar con:

- APIs REST
- Integración de sistemas
- Validación de datos
- Estándar FHIR
- Testing
- Docker
- CI/CD

## Licencia

MIT