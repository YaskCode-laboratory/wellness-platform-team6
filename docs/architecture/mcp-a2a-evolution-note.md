# Nota Arquitectónica — Evolución Futura Hacia Estándares MCP y A2A

Análisis de evolución arquitectónica para el ecosistema multiagente de **Wellness Lift** hacia los estándares **Model Context Protocol (MCP)** y **Agent-to-Agent (A2A)** (Sprint 3 — Issue #22).

---

## 1. Introducción y Contexto

A medida que el ecosistema multiagente de **Wellness Lift** crece en complejidad (incorporando agentes de biomecánica, nutrición, analítica y motivación), surge la necesidad de conectar herramientas y agentes externos mediante protocolos industriales estandarizados.

Actualmente, el sistema implementa un protocolo homogéneo interno basado en `InterAgentMessage`, `InterAgentResponse` y `AgentToolRegistry`. Esta nota describe cómo esta arquitectura puede evolucionar hacia dos estándares clave de la industria:
- **MCP (Model Context Protocol)**: Estándar abierto para exponer contextos, prompts y herramientas a modelos LLM.
- **A2A (Agent-to-Agent Communication Protocol)**: Estándar para comunicación descentralizada e inter-operabilidad entre sistemas multiagente independientes.

---

## 2. Alineación del Sistema Actual con MCP (Model Context Protocol)

El estándar **MCP** (desarrollado para conexión universal de herramientas) define tres primitivas principales:

| Primitiva MCP | Implementación Actual en Wellness Lift | Estrategia de Evolución MCP |
| :--- | :--- | :--- |
| **Tools (Herramientas)** | `AgentToolRegistry.get_tool_schemas()` (`get_exercise_alternative`, `calculate_nutrition_macros`, etc.) | Exponer las funciones del backend como un **MCP Tool Server** vía transporte stdio o HTTP SSE. |
| **Resources (Recursos)** | Base de datos NoSQL Firestore y Vector Store RAG (`embeddings.json`) | Exponer la base de datos de ejercicios y perfil del atleta como **MCP Resources** (`wellness://exercises/catalog`, `wellness://user/{id}/profile`). |
| **Prompts (Plantillas)** | `prompts/system_prompt_wellness_coach_2.0.txt` y `ReasoningEngine.build_routine_prompt` | Exponer plantillas especializadas como **MCP Prompts** parametrizables. |

---

## 3. Alineación del Sistema Actual con A2A (Agent-to-Agent)

El protocolo **A2A** permite que agentes desarrollados por diferentes equipos u organizaciones se descubran y colaboren de forma remota mediante mensajes estructurados sobre transporte HTTP / WebSockets.

### Mapeo de Componentes Actuales a A2A:
1. **Descubrimiento de Agentes (Agent Card / Manifest)**:
   Cada agente especializado (ej. `WellnessCoachAgent2.0`, `NutritionAgent`) expondrá una "Ficha de Agente" en formato JSON declarando sus capacidades y fronteras de dominio.
2. **Formato de Mensaje JSON-RPC 2.0**:
   El mensaje `InterAgentMessage` actual contiene todos los atributos necesarios (`task_id`, `trace_id`, `intent`, `context_payload`), permitiendo envolverlo fácilmente en solicitudes JSON-RPC 2.0 sobre HTTP POST (`/a2a/v1/message`).
3. **Delegación Asíncrona con Trazabilidad**:
   La clase `DelegationTracer` proporciona la auditoría necesaria (`trace_id`) para seguir las llamadas inter-organizaciones en un entorno A2A distribuido.

---

## 4. Hoja de Ruta Sugerida para la Evolución (Sprint 4 / Versión 3.0)

1. **Fase 1 (MCP Adapter Layer)**: Envolver `AgentToolRegistry` con un adaptador MCP oficial (`mcp-python-sdk`), permitiendo a clientes externos invocar herramientas de Wellness Lift.
2. **Fase 2 (A2A Endpoints)**: Publicar endpoints `/a2a/v1/agents` y `/a2a/v1/delegate` en FastAPI para permitir interacción remota entre repositorios de diferentes laboratorios.
3. **Fase 3 (Gobernanza y Seguridad A2A)**: Implementar tokens JWT / OAuth2 para autenticar la comunicación entre supervisores y agentes remotos.

---

## 5. Conclusión

La arquitectura multiagente implementada en el Sprint 3 con el patrón **Supervisor** y la clase `InterAgentMessage` sienta las bases conceptuales y técnicas para migrar hacia MCP y A2A con mínimo impacto en el código existente.
