# Registro de Decisiones de Arquitectura (ADR) — Implementación del Orchestrator Agent

Estado: Aceptado  
Fecha: 30 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-006: Implementación del Orchestrator Agent y Router de Delegación

### Contexto
En el Sprint 3 (S3-02), la arquitectura multiagente de Wellness Lift requería un componente supervisor centralizado capaz de recibir las peticiones de los usuarios, clasificar sus intenciones, delegar a los agentes especializados correspondientes (`WellnessCoachAgent2.0`, `NutritionAgent`, `MotivationAgent`, `AnalyticsAgent`), coordinar peticiones compuestas multidominio y garantizar el control de errores con fallbacks seguros.

### Decisión
Se implementó la clase `OrchestratorAgent` en `src/backend/app/orchestrator.py` y se integró directamente en el servidor FastAPI (`src/backend/app/main.py`):

1. **Clasificación de Intenciones (`classify_intent`)**: Identifica intenciones `WORKOUT_BIOMECHANICS`, `NUTRITION`, `MOTIVATION`, `ANALYTICS`, `MULTIDOMAIN` o `GENERAL`.
2. **Delegación a Agentes Especializados**:
   - `WORKOUT_BIOMECHANICS`: Delega al `WellnessCoachAgent` (Equipo 6).
   - `NUTRITION`: Delega al `NutritionAgent` utilizando la herramienta de cálculo de macronutrientes.
   - `MOTIVATION`: Delega al `MotivationAgent` para refuerzo positivo y adherencia.
   - `ANALYTICS`: Delega al `AnalyticsAgent` para métricas de volumen acumulado.
3. **Coordinación Multidominio (`handle_multidomain_delegation`)**: Asigna tareas en paralelo/secuencia a múltiples agentes y consolida la respuesta final.
4. **Manejo de Errores e Incompatibilidades (`handle_orchestration_error`)**: Respuesta estructurada de fallback ante excepciones sin detener el servicio FastAPI.

### Consecuencias
- Positivas: Desacoplamiento total entre la lógica de enrutamiento y la implementación interna de cada agente especializado.
- Positivas: 100% retrocompatible con los endpoints REST del backend y pruebas automatizadas en verde.
- Positivas: Trazabilidad clara de qué agente atendió cada solicitud (`delegated_agent` e `intent`).
