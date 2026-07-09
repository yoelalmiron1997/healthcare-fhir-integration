# Pruebas UAT (User Acceptance Testing)

Esta carpeta contiene las pruebas de aceptación de usuario para la API de
integración de pacientes → FHIR. A diferencia de los tests automatizados en
`/tests` (que corren con `pytest`), estas pruebas están pensadas para
ejecutarse **manualmente** (o con `curl`/Postman) y validar el comportamiento
end-to-end desde la perspectiva de un usuario / analista funcional.

## Contenido

| Archivo / carpeta                | Descripción                                                        |
|-----------------------------------|---------------------------------------------------------------------|
| `test_cases.md`                   | Casos de prueba UAT con pasos, datos, resultado esperado y criterios de validación |
| `sample_data/`                    | Payloads JSON de ejemplo (válidos e inválidos) usados en los casos  |
| `execution_results_template.md`   | Plantilla para volcar los resultados reales al ejecutar los casos   |

## Cómo ejecutar las pruebas

1. Levantar la API localmente:
   ```bash
   cd ..
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
   La API quedará disponible en `http://127.0.0.1:8000`.

2. Abrir `test_cases.md` y seguir los pasos de cada caso, usando los archivos
   de `sample_data/` como body de las requests (por ejemplo con `curl`,
   Postman/Insomnia, o la documentación interactiva de Swagger en
   `http://127.0.0.1:8000/docs`).

3. Registrar los resultados obtenidos en una copia de
   `execution_results_template.md` (o directamente en una herramienta de
   gestión de pruebas, si el equipo usa una).

## Convención de casos

Cada caso de prueba sigue el formato:

- **ID**: identificador único (`UAT-01`, `UAT-02`, ...)
- **Título**: qué se está validando
- **Precondición**: estado necesario antes de ejecutar
- **Datos de entrada**: archivo de `sample_data/` a usar
- **Pasos**: acciones concretas a ejecutar
- **Resultado esperado**: qué debería devolver la API
- **Criterios de validación**: puntos concretos a chequear en la respuesta
