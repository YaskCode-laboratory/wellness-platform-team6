# Registro de Decisiones de Arquitectura (ADR) — Agente Especializado del Equipo 6

Estado: Aceptado  
Fecha: 30 de agosto de 2026 (Actualizado: 26 de septiembre de 2026)  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-007: Implementación del Agente Especializado (Wellness Coach Agent 2.0)

### Contexto
En el Sprint 3 (S3-03), se requería definir e implementar la lógica del **agente especializado asignado al Equipo 6** dentro de la arquitectura multiagente de Wellness Lift, con responsabilidades claramente delimitadas, reutilización de las capacidades avanzadas desarrolladas en Sprints anteriores (Motor RAG, Memoria Conversacional de Doble Nivel, Tool Calling) y colaboración fluida con el **Orchestrator Agent**.

### Decisión
Se actualizó e implementó la clase `WellnessCoachSpecialist` en `src/backend/app/wellness_agent/coach_specialist.py`:

1. **Delimitación Estricta y Verificable de Dominio (`is_query_in_domain`)**:
   - **Dentro de Dominio (IN)**: Biomecánica del ejercicio, prescripción de rutinas adaptativas, alternativas seguras ante lesiones (hernia discal, lesión de rodilla, manguito rotador), intensidad (RPE/RIR), técnica y evidencia científica RAG.
   - **Fuera de Dominio (OUT)**: Menús de cocina/recetas (dominio de Nutrition Agent), consultas generales no relacionadas con entrenamiento (informática, finanzas, preguntas generales).
   - **Manejo de Frontera de Dominio**: Ante consultas ajenas a su competencia principal, retorna `in_domain=False` y estado `"out_of_domain"`, permitiendo que el Orchestrator Agent gestione centralizadamente la selección o redelegación de agentes.

2. **Estructura Real del Perfil de Usuario (`fitness_profile`)**:
   - Se adaptó la lectura del perfil a la estructura almacenada en la base de datos (`fitness_profile`), extrayendo adecuadamente `health_conditions`, `goal`, `level` y `limitations` para alimentar el flujo contextual del agente.

3. **Única Fuente de Verdad para Prompts**:
   - El sistema carga formalmente las instrucciones desde el archivo de prompt oficial `prompts/system_prompt_wellness_coach_2.0.txt`, evitando construcciones aisladas en línea y previniendo divergencias de comportamiento.

4. **Integración Real de Herramientas y RAG**:
   - Durante el procesamiento de solicitudes en `process_specialized_request()`, se ejecuta la consulta semántica RAG (`retrieve_rag_knowledge`) y la evaluación biomecánica de riesgo (`assess_injury_risk`), enriqueciendo directamente el prompt contextual antes de generar la respuesta.

5. **Pruebas Automatizadas en CI**:
   - Se configuró el flujo de CI en `.github/workflows/ci.yml` para ejecutar la suite completa usando `pytest tests/ -v`, garantizando la ejecución continua de `tests/test_specialized_coach_agent.py`.

### Consecuencias
- **Positivas**: Responsabilidad modular limpia evitando que el agente asuma tareas correspondientes a otros agentes especializados o consultas fuera del ámbito fitness.
- **Positivas**: Retrocompatibilidad total con la API FastAPI existente y los tests del backend.
- **Positivas**: Alineación 100% entre lo documentado en ADR-007, la arquitectura del sistema y la ejecución real en código.
