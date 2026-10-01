# Registro de Decisiones de Arquitectura (ADR) — Refactorización del Wellness Agent

Estado: Aceptado  
Fecha: 28 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-002 / ADR-004: Modularización del Wellness Agent, Memoria y Registro de Herramientas

### Contexto
La implementación inicial del Wellness Agent en `src/backend/app/agent.py` se encontraba contenida en un único archivo monolítico de 579 líneas donde convivían llamadas a múltiples proveedores LLM (OpenRouter, Gemini, Groq), el catálogo de ejercicios, las reglas de volumen por nivel/edad, el motor local determinista y la construcción de prompts. Esta estructura limitaba la mantenibilidad del código y la incorporación de capacidades avanzadas como memoria conversacional multi-turno y ejecución de herramientas (*Tool Calling*).

### Decisión
Se refactorizó el agente dividiéndolo en un paquete modular extensible bajo la ruta `src/backend/app/wellness_agent/`:

1. **`catalog.py`**: Aísla los diccionarios de ejercicios (`EXERCISE_CATALOG`), plantillas de división semanal (`SPLIT_TEMPLATES`) y el calculador de volumen `get_set_rep_scheme`.
2. **`providers.py`**: Encapsula las llamadas a servicios externos de IA (`LLMProviderManager`) gestionando fallbacks automáticos y timeouts entre OpenRouter, Gemini, Groq y Motor Local.
3. **`memory.py`**: Implementa la clase `ConversationMemoryManager` para almacenar y limitar el historial de diálogos por usuario.
4. **`tools.py`**: Implementa `AgentToolRegistry` registrando funciones ejecutables (`get_exercise_alternative`, `calculate_nutrition_macros`, `assess_injury_risk`, `retrieve_rag_knowledge`).
5. **`reasoning.py`**: Implementa `ReasoningEngine` para la construcción de prompts con contexto RAG y lógica determinista local.
6. **`agent.py`**: Mantiene una interfaz de fachada (*Facade*) 100% retrocompatible con las funciones públicas existentes (`generate_weekly_routine`, `generate_chat_response`).

### Consecuencias
- Positivas: Código modular, comprensible y desacoplado. Facilita la adición de nuevas herramientas y la integración con el motor RAG.
- Positivas: 100% de compatibilidad garantizada con los endpoints de la API FastAPI en `src/backend/app/main.py` y las pruebas existentes.
- Neutrales: Requiere importar los submódulos desde `app.wellness_agent`.
