# Registro de Decisiones de Arquitectura (ADR) — Patrón ReAct y Evaluación de Calidad

Estado: Aceptado  
Fecha: 29 de septiembre de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-005: Patrón de Razonamiento ReAct y Evaluación de Calidad del Agente

### Contexto
El agente requiere resolver consultas complejas multi-paso aplicando el ciclo Thought -> Action -> Observation -> nueva decisión -> Final Answer sin incurrir en bucles infinitos, e incorporar un benchmark riguroso de evaluación cuantitativa con criterios objetivos de calidad para evitar falsos positivos en memoria conversacional y recomendaciones biomecánicas.

### Decisión
1. **Patrón ReAct (`ReActAgent`)**:
   - Integrado con `AgentToolRegistry` de S2-04 y acoplado al flujo principal en `WellnessCoachAgent.generate_response()`.
   - Generación determinista e intencional de pensamientos y selección dinámica de herramientas según la consulta.
   - Protección contra bucles infinitos por detección de firmas de llamada duplicadas (`tool_signature = action_name:json.dumps(action_input)`) y límite estricto de 5 iteraciones.
2. **Suite de Evaluación (`AgentQualityEvaluator`)**:
   - Exige ausencia de herramientas previas a `FINAL_ANSWER` para consultas conversacionales directas (`expected_tool = None`).
   - Evaluación multiturno rigurosa distinguiendo explícitamente entre: (a) riesgo correctamente identificado, (b) grupo muscular objetivo y (c) coherencia de la alternativa frente a la restricción detectada.
   - Calcula el puntaje de relevancia en escala 1.0 a 5.0 penalizando inconsistencias biomecánicas.
   - Registra evidencias empíricas en `data/agent_evaluation_results.json` e informe `docs/agent_evaluation_report.md`.

### Consecuencias
- Positivas: Ciclo ReAct determinista, seguro y conectado de extremo a extremo con el agente real.
- Positivas: Detección rigurosa de inconsistencias biomecánicas (tasa de éxito global del 80.0%, 4/5 PASSED, 1/5 FAILED y relevancia promedio de 4.5/5.0).
- Positivas: Identificación y documentación formal de la limitación estocástica de `get_exercise_alternative` y su propuesta de filtrado contextual para futuros sprints.
