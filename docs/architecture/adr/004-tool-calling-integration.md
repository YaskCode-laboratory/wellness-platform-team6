# Registro de Decisiones de Arquitectura (ADR) — Integración de Tool Calling

Estado: Aceptado  
Fecha: 28 de septiembre de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-004: Integración de Herramientas mediante Tool Calling

### Contexto
El agente requiere capacidades específicas de consulta de alternativas de ejercicio, cálculo de macronutrientes, evaluación de riesgo biomecánico de lesiones y recuperación RAG. Mantener funciones dispersas dificulta el mantenimiento, la trazabilidad y la reutilización entre patrones conversacionales y ReAct.

### Decisión
Se implementó un registro unificado `AgentToolRegistry` (`src/backend/app/wellness_agent/tools.py`) que expone declaraciones formales en formato JSON Schema (`get_tool_schemas`) y el método de ejecución `execute_tool(tool_name, **kwargs)` para:

1. `get_exercise_alternative`: Sustitución segura de ejercicios del catálogo.
2. `calculate_nutrition_macros`: Cálculo de TDEE y macronutrientes del atleta.
3. `assess_injury_risk`: Evaluación del riesgo biomecánico según patología.
4. `retrieve_rag_knowledge`: Recuperación semántica vectorial en la base RAG.

Se integró `detect_and_execute_tools()` directamente en la entrada principal `WellnessCoachAgent.generate_response()`, permitiendo que la observación capturada se inyecte en el prompt y en la síntesis final.

### Consecuencias
- Positivas: Punto centralizado de registro y ejecución de herramientas para el agente.
- Positivas: Eliminación de registros paralelos redundantes en ReActAgent.
- Positivas: Trazabilidad completa end-to-end (Mensaje -> Detección -> Ejecución `execute_tool()` -> Observación -> Respuesta Final).
