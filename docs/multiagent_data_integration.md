# 🗄️ Arquitectura de Integración de Datos y Servicios Multi-Agente — Wellness Platform (Issue #23)

## 1. Resumen Ejecutivo
Este documento detalla la estrategia de integración entre el **Sistema Multi-Agente del Sprint 3** y los almacenes de datos operacionales (**Google Cloud Firestore NoSQL**), analíticos (**Google Cloud BigQuery**) y **Servicios Externos/APIs**, respondiendo al requerimiento **[S3-05 — Integrar el sistema multiagente con datos y servicios] (Issue #23)**.

---

## 2. Asignación de Datos por Responsabilidades de Agente

Para preservar el principio de menor privilegio y evitar acoplamiento excesivo:

| Agente Especializado | Fuente de Datos Primaria | Tipo de Datos Accedidos | Propósito |
| :--- | :--- | :--- | :--- |
| **Biomechanics & Safety Agent** | Cloud Firestore / Technical File | Expediente médico, lesiones activas, RPE. | Verificar contraindicaciones y ejercicios prohibidos. |
| **Training Periodization Agent** | Cloud Firestore / Routine Store | Perfil de nivel, días de entreno, rutina activa. | Diseñar programas semanales y sobrecarga progresiva. |
| **Analytics & Performance Agent**| Cloud BigQuery Data Warehouse | Historial de volumen acumulado, PRs, adherencia. | Generar reportes analíticos de rendimiento por sucursal. |
| **Nutrition & Recovery Agent** | External Services / Nutrition API | TDEE, distribución de macronutrientes. | Calcular requerimientos calóricos según objetivo corporal. |

---

## 3. Configuración de Seguridad y Variables de Entorno

No se almacenan credenciales reales en el código fuente. Se utiliza el archivo `.env.example` para declarar las variables de entorno requeridas:

```env
# GCP & Cloud Firestore Configuration
GCP_PROJECT_ID=wellness-platform-prod
FIRESTORE_DATABASE=(default)

# BigQuery Analytics Configuration
BIGQUERY_DATASET=wellness_analytics

# External AI & Nutrition APIs
OPENROUTER_API_KEY=your_openrouter_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 4. Resiliencia y Manejo de Errores
El módulo `ExternalServicesConnector` (`src/backend/app/multiagent_data_connector.py`) implementa bloques `try/except` con política de degradación suave (*graceful fallback*):
- Si las variables de entorno de GCP no están configuradas, el sistema conmuta automáticamente a la **Base de Datos Simulada en Memoria** sin interrumpir la ejecución.
- Si las APIs de LLM externas presentan timeout o 404, el conector invoca el motor determinista local.

---

## 5. Verificación Automatizada

Suite de pruebas ejecutada con éxito:
```bash
python -m unittest tests/test_multiagent_data.py
# Ran 3 tests in 0.000s - OK
```
