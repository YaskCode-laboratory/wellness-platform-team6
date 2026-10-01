# Arquitectura de Integración de Datos y Servicios Multi-Agente — Wellness Platform (Issue #23 - S3-05)

## 1. Resumen Ejecutivo
Este documento detalla la estrategia de integración entre el **Sistema Multi-Agente del Sprint 3** y los almacenes de datos operacionales (**Google Cloud Firestore NoSQL** / Capa Unificada `database`), analíticos (**Capa de Analítica de Rendimiento / BigQuery Abstraction**) y **Servicios Nutricionales**, respondiendo al requerimiento **[S3-05 — Integrar el sistema multiagente con datos y servicios] (Issue #23)**.

---

## 2. Asignación de Datos y Conectores por Responsabilidad

Para preservar el principio de menor privilegio, desacoplamiento y resiliencia:

| Agente Especializado | Conector / Fuente de Datos | Tipo de Datos Accedidos | Modo Operativo |
| :--- | :--- | :--- | :--- |
| **Biomechanics & Safety Agent** | `FirestoreMultiAgentConnector` (vía `database`) | Expediente médico, lesiones activas, RPE. | Reutiliza la capa `database` (Firestore real si se configuran credenciales GCP, o BDD en memoria en entorno local). |
| **Training Periodization Agent** | `FirestoreMultiAgentConnector` (vía `database`) | Perfil de nivel, días de entreno, rutina activa. | Reutiliza la capa `database` unificada. |
| **Analytics & Performance Agent**| `BigQueryMultiAgentConnector` | Historial de volumen acumulado, adherencia, sobrecarga progresiva. | Motor analítico compuesto sobre `database.get_workout_sessions`, con abstracción lista para conector BigQuery en GCP. |
| **Nutrition & Recovery Agent** | `ExternalServicesConnector` | TDEE, distribución de macronutrientes. | Motor determinista local de cálculo nutricional con gestión de excepciones y fallback seguro. |

---

## 3. Configuración de Seguridad y Variables de Entorno

No se almacenan credenciales en el código fuente. Se utiliza el archivo `.env.example` para declarar la configuración del sistema:

```env
# GCP & Cloud Firestore / BigQuery Configuration
# (Sin credenciales en código fuente. Al definir GOOGLE_APPLICATION_CREDENTIALS o GCP_PROJECT_ID se activa GCP real; de lo contrario opera en MODO LOCAL / MOCK)
GCP_PROJECT_ID=wellness-platform-prod
GOOGLE_CLOUD_PROJECT=wellness-platform-prod
FIRESTORE_DATABASE=(default)
BIGQUERY_DATASET=wellness_analytics
# GOOGLE_APPLICATION_CREDENTIALS=/ruta/a/sus/credenciales_gcp.json

# API Keys de Inteligencia Artificial (Placeholders ficticios)
GEMINI_API_KEY=your-gemini-api-key-here
OPENROUTER_API_KEY=your-openrouter-api-key-here

# URL del Frontend para CORS
VITE_API_URL=http://localhost:5173
```

---

## 4. Resiliencia, Validación de Entrada y Fallbacks

El módulo `multiagent_data_connector.py` implementa manejo explícito de excepciones y políticas de degradación suave (*graceful fallback*):

- **Conmutación Operacional (Firestore)**: Si `GOOGLE_APPLICATION_CREDENTIALS` o `GCP_PROJECT_ID` no están presentes o presentan fallo de red/permisos, la capa `database` conmuta automáticamente al **Mock en Memoria**, permitiendo la continuidad operacional en entornos locales y de CI.
- **Manejo de Atletas Inexistentes o sin Datos**:
  - Si un atleta no existe en el sistema, `FirestoreMultiAgentConnector` retorna un perfil seguro por defecto con `health_conditions: []`.
  - Si un atleta no posee sesiones de entrenamiento, `BigQueryMultiAgentConnector` calcula `total_historical_sessions: 0`, `total_volume_lifted_kg: 0.0` y establece la tendencia en `"SIN DATOS / BASELINE (0 sesiones)"`.
- **Servicio de Nutrición (Local Engine)**:
  - `ExternalServicesConnector.fetch_nutrition_macronutrients()` valida estrictamente los parámetros de entrada (e.g. `weight_kg > 0`). Ante valores inválidos o excepciones, activa el estado `"FALLBACK"` retornando macronutrientes de seguridad predeterminados.

---

## 5. Diferenciación de Modos de Ejecución

1. **Modo Local / Mock (Entorno de Desarrollo y CI)**:
   - Se ejecuta por defecto sin requerir credenciales externas Cloud.
   - Utiliza la base de datos simulada en memoria y el motor analítico local sobre `database`.
2. **Modo Cloud Real (Entorno de Producción GCP)**:
   - Activado al proveer `GOOGLE_APPLICATION_CREDENTIALS` y `GCP_PROJECT_ID`.
   - Conecta a Google Cloud Firestore real y realiza consultas sobre la infraestructura GCP.

---

## 6. Verificación Automatizada

Suite de pruebas verificada con soporte para `unittest` y `pytest`:
```bash
python -m unittest discover -s tests -p "test_*.py"
# Ran 85 tests in 0.050s - OK

pytest tests/ -v
# 85 passed
```
