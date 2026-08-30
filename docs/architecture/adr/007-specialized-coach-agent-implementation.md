# Registro de Decisiones de Arquitectura (ADR) — Agente Especializado del Equipo 6

Estado: Aceptado  
Fecha: 30 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-007: Implementación del Agente Especializado (Wellness Coach Agent 2.0)

### Contexto
En el Sprint 3 (S3-03), se requería definir e implementar la lógica del **agente especializado asignado al Equipo 6** dentro de la arquitectura multiagente de Wellness Lift, con responsabilidades claramente delimitadas, reutilización de las capacidades avanzadas desarrolladas en Sprints anteriores (Motor RAG, Memoria Conversacional de Doble Nivel, Tool Calling) y colaboración fluida con el **Orchestrator Agent**.

### Decisión
Se implementó la clase `WellnessCoachSpecialist` en `src/backend/app/wellness_agent/coach_specialist.py`:

1. **Delimitación Estricta de Dominio (`is_query_in_domain`)**:
   - **Dentro de Dominio (IN)**: Biomecánica del ejercicio, prescripción de rutinas adaptativas, alternativas seguras ante lesiones (hernia discal, lesión de rodilla, manguito rotador), intensidad (RPE/RIR) y evidencia científica RAG.
   - **Fuera de Dominio (OUT)**: Menús de cocina detallados o recetas vegetales (dominio de Nutrition Agent), terapia médica/psicológica clínica.
   - **Frontera de Dominio**: Ante consultas ajenas a su competencia principal, responde desde la perspectiva del entrenamiento adaptativo e indica la sugerencia de delegar al agente correspondiente.
2. **Reutilización de Sub-Sistemas Integrados**:
   - `ReasoningEngine`: Orquestador de Tool Calling y motor de razonamiento contextual.
   - `AgentToolRegistry`: Invocación de `get_exercise_alternative`, `assess_injury_risk` y `retrieve_rag_knowledge`.
   - `ConversationMemoryManager`: Memoria a corto plazo (buffer de contexto) y memoria a largo plazo (hechos extraídos).
3. **Integración con Orchestrator Agent**: Invocación transparente a través del supervisor central.

### Consecuencias
- Positivas: Responsabilidad modular limpia evitando que el agente asuma tareas correspondientes a otros agentes especializados.
- Positivas: Retrocompatibilidad total con la API FastAPI existente y los tests del backend.
- Positivas: Seguridad reforzada al validar filtros médicos biomecánicos antes de entregar recomendaciones al atleta.
