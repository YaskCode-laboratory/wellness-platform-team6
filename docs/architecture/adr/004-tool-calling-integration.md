# Registro de Decisiones de Arquitectura (ADR) — Integración de Tool Calling

Estado: Aceptado  
Fecha: 29 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-004: Integración de Herramientas mediante Tool Calling y Esquemas JSON

### Contexto
El Wellness Coach Agent 2.0 requiere interactuar dinámicamente con servicios del dominio de entrenamiento y salud (cálculo de macronutrientes, evaluación de riesgos de lesiones por ejercicio, búsqueda semántica en la base de conocimiento RAG y generación de alternativas de ejercicios). La codificación rígida de lógica dentro de los prompts limita la precisión y la expansibilidad del sistema.

### Decisión
Se implementó un registro unificado `AgentToolRegistry` (`src/backend/app/wellness_agent/tools.py`) que expone declaraciones formales en formato JSON Schema (`get_tool_schemas`) y el método de ejecución `execute_tool(tool_name, **kwargs)` para:
1. `get_exercise_alternative`: Sustitución segura de ejercicios del catálogo.
2. `calculate_nutrition_macros`: Cálculo de TDEE y desglose de macronutrientes del atleta.
3. `assess_injury_risk`: Evaluación del riesgo biomecánico según patología y memoria del atleta.
4. `retrieve_rag_knowledge`: Recuperación semántica vectorial en la base RAG.

Se integró la detección y ejecución de herramientas tanto en el ciclo ReAct (`ReActAgent.run_react_loop`) como en la entrada principal `WellnessCoachAgent.generate_response()`, encapsulando excepciones con respuestas de fallback estructuradas (`status: "error"`).

### Consecuencias
- Positivas: El agente identifica de forma precisa cuándo invocar herramientas y sintetiza sus observaciones en el diálogo con el usuario.
- Positivas: Desacoplamiento total entre las funciones de cálculo/consultas y el modelo LLM.
- Positivas: Trazabilidad completa end-to-end (Mensaje -> Detección -> Ejecución `execute_tool()` -> Observación -> Respuesta Final).
- Positivas: Resiliencia ante parámetros inválidos o fallos de ejecución.
