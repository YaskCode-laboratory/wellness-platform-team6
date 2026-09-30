# Registro de Decisiones de Arquitectura (ADR) — Integración de Tool Calling

Estado: Aceptado  
Fecha: 29 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-004: Integración de Herramientas mediante Tool Calling y Esquemas JSON

### Contexto
El Wellness Coach Agent 2.0 requiere interactuar dinámicamente con servicios del dominio de entrenamiento y salud (cálculo de macronutrientes, evaluación de riesgos de lesiones por ejercicio, búsqueda semántica en la base de conocimiento RAG y generación de alternativas de ejercicios). La codificación rígida de lógica dentro de los prompts limita la precisión y la expansibilidad del sistema.

### Decisión
Se implementó un orquestador de **Tool Calling (Function Calling)** compuesto por:
1. **Esquemas JSON Schema (`AgentToolRegistry.get_tool_schemas`)**: Declaración formal de funciones y parámetros con tipado estricto.
2. **Detección Dinámica de Intenciones (`ReasoningEngine.detect_and_execute_tools`)**: Identificación automatizada de consultas que requieren herramientas vs aquellas que responden de manera puramente conversacional.
3. **Manejo Controlado de Errores (`execute_tool`)**: Encapsulamiento de excepciones con respuestas de fallback estructuradas (`status: "error"`).

### Consecuencias
- Positivas: El agente identifica de forma precisa cuándo invocar herramientas y sintetiza sus resultados en el diálogo con el usuario.
- Positivas: Desacoplamiento total entre las funciones de cálculo/consultas y el modelo LLM.
- Positivas: Resiliencia ante parámetros inválidos o fallos de ejecución.
