# Registro de Decisiones de Arquitectura (ADR) — Implementación del Orchestrator Agent

Estado: Aceptado  
Fecha: 30 de agosto de 2026 (Actualizado: 26 de septiembre de 2026)  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-006: Implementación del Orchestrator Agent y Router de Delegación

### Contexto
En el Sprint 3 (S3-02), la arquitectura multiagente de Wellness Lift requería un componente supervisor centralizado capaz de recibir las peticiones de los usuarios, clasificar sus intenciones, delegar a los agentes especializados correspondientes (`WellnessCoachAgent2.0`, `NutritionAgent`, `MotivationAgent`, `AnalyticsAgent`), coordinar peticiones compuestas multidominio y garantizar el control de errores con fallbacks seguros.

### Decisión
Se implementó la clase `OrchestratorAgent` en `src/backend/app/orchestrator.py` y se integró directamente en el servidor FastAPI (`src/backend/app/main.py`):

1. **Clasificación de Intenciones (`classify_intent` / `detect_domains`)**: Identifica intenciones `WORKOUT_BIOMECHANICS`, `NUTRITION`, `MOTIVATION`, `ANALYTICS`, `MULTIDOMAIN` o `GENERAL` detectando dinámicamente los dominios presentes en la consulta.
2. **Desacoplamiento de Agentes Especializados**:
   - `WORKOUT_BIOMECHANICS`: Delega al `WellnessCoachAgent` (Equipo 6).
   - `NUTRITION`: Delega a la clase especializada `NutritionAgent`.
   - `MOTIVATION`: Delega a la clase especializada `MotivationAgent`.
   - `ANALYTICS`: Delega a la clase especializada `AnalyticsAgent`.
3. **Coordinación Multidominio (`handle_multidomain_delegation`)**: Ejecuta la delegación de forma secuencial hacia los agentes correspondientes a los dominios detectados y sintetiza la respuesta unificada.
4. **Evaluación de Estado Compuesto**: Evalúa la tasa de éxito de las delegaciones participantes retornando `success`, `partial_success` o `error_fallback`.
5. **Manejo de Errores e Incompatibilidades (`handle_orchestration_error`)**: Genera respuestas estructuradas de fallback ante excepciones sin interrumpir el servicio FastAPI.
6. **Integración y Pruebas en CI/CD**: Verificación automatizada mediante `pytest tests/ -v` en GitHub Actions e inclusión de prueba de integración con el endpoint `POST /api/v1/ai/chat/{user_id}` mediante `TestClient`.

### Consecuencias
- Positivas: Separación limpia de responsabilidades entre el supervisor (enrutamiento y consolidación) y los agentes especializados (lógica de dominio).
- Positivas: Delegación compuesta dinámica y trazabilidad completa del estado de la interacción (`delegated_agent`, `intent` y `status`).
- Positivas: 100% retrocompatible con los endpoints REST del backend y verificación en verde por la suite de pruebas `pytest`.
