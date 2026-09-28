# Registro de Decisiones de Arquitectura (ADR) — Patrón ReAct y Evaluación de Calidad

Estado: Aceptado  
Fecha: 28 de septiembre de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-005: Patrón de Razonamiento ReAct y Evaluación de Calidad

### Contexto
El agente requiere resolver consultas complejas multi-paso aplicando el ciclo Thought -> Action -> Observation -> Final Answer sin incurrir en bucles infinitos, e incorporar un benchmark riguroso de evaluación con criterios objetivos de calidad.

### Decisión
1. **Patrón ReAct (`ReActAgent`)**:
   - Integrado con `AgentToolRegistry` de S2-04.
   - Generación determinista e intencional de pensamientos y selección dinámica de herramientas según la consulta (evitando secuencias fijas innecesarias).
   - Protección contra bucles infinitos por detección de firmas duplicadas (`tool_signature`).
2. **Suite de Evaluación (`AgentQualityEvaluator`)**:
   - Exige ausencia de herramientas para consultas conversacionales directas (`expected_tool = None`).
   - Calcula el puntaje de relevancia de 1.0 a 5.0 derivado de la exactitud en herramientas, completitud y términos del dominio.
   - Registra evidencias empíricas en `data/agent_evaluation_results.json` e informe `docs/agent_evaluation_report.md`.

### Consecuencias
- Positivas: Ciclo ReAct determinista, seguro y desacoplado de latencias innecesarias.
- Positivas: Evaluación objetiva del comportamiento del agente reflejando exactamente la exactitud de herramientas y relevancia.
