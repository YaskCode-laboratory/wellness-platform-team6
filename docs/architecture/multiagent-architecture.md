# Arquitectura del Sistema Multiagente — Wellness Lift (Sprint 3)

## 1. Visión General y Patrón Arquitectónico

La plataforma **Wellness Lift** implementa una arquitectura multiagente basada en el **Patrón Supervisor (Orchestrator-Workers)**, en el cual un agente central (**Orchestrator Agent**) actúa como punto único de entrada para el usuario, clasificando intenciones y coordinando la ejecución de tareas especializadas entre múltiples agentes de dominio.

---

## 2. Diagrama Arquitectónico General

`mermaid
graph TD
    Client([Usuario / Atleta]) -->|Solicitud HTTP / REST| API[Backend FastAPI]
    API --> Orchestrator[Orchestrator Agent - Supervisor]
    
    subgraph Supervisor Layer
        Orchestrator --> IntentClassifier[Clasificador de Intenciones]
        Orchestrator --> Tracer[DelegationTracer / Observabilidad]
        Orchestrator --> CompoundCoordinator[Coordinador Compuesto Multidominio]
    end
    
    subgraph Specialized Agents Layer
        IntentClassifier -->|WORKOUT_BIOMECHANICS| CoachAgent[Wellness Coach Agent 2.0 (Equipo 6)]
        IntentClassifier -->|NUTRITION| NutritionAgent[Nutrition Agent]
        IntentClassifier -->|MOTIVATION| MotivationAgent[Motivation Agent]
        IntentClassifier -->|ANALYTICS| AnalyticsAgent[Analytics Agent]
        
        CompoundCoordinator -->|Petición Subtask 1| CoachAgent
        CompoundCoordinator -->|Petición Subtask 2| NutritionAgent
    end
    
    subgraph Data & Knowledge Services
        CoachAgent --> RAG[(Motor RAG / Base Vectorial)]
        CoachAgent --> LLMProvider[Proveedores LLM: OpenRouter / Gemini]
        NutritionAgent --> Firestore[(Firestore / User Profiles)]
        AnalyticsAgent --> BigQuery[(BigQuery / Workout Analytics)]
    end
    
    CoachAgent -->|InterAgentResponse| Orchestrator
    NutritionAgent -->|InterAgentResponse| Orchestrator
    MotivationAgent -->|InterAgentResponse| Orchestrator
    AnalyticsAgent -->|InterAgentResponse| Orchestrator
    
    Orchestrator -->|Respuesta Consolidada + Trace ID| Client
`

---

## 3. Catálogo de Agentes Especializados y Roles

| Agente | Tipo | Responsabilidad Principal | Fuente de Datos / Servicios |
| :--- | :--- | :--- | :--- |
| **Orchestrator Agent** | Supervisor | Clasificación de intenciones, enrutamiento, prevención de ciclos y síntesis de respuestas multidominio. | Memoria conversacional, DelegationTracer. |
| **Wellness Coach Agent 2.0** | Especialista (Equipo 6) | Biomecánica del ejercicio, selección de alternativas, adaptación por lesiones y generación de rutinas. | Vector Store RAG (384d), catálogo biomecánico, LLMs. |
| **Nutrition Agent** | Especialista | Cálculo de TDEE, estimación de requerimientos calóricos y desglose de macronutrientes. | Perfil de usuario en Firestore, calculador de macros. |
| **Motivation Agent** | Especialista | Refuerzo psicológico de adherencia, constancia y validación de hábitos deportivos. | Historial de entrenamientos en base de datos. |
| **Analytics Agent** | Especialista | Cómputo de volumen de carga acumulado (kg), progreso por grupo muscular y récords personales. | Telemetría de sesiones en BigQuery. |

---

## 4. Protocolo de Comunicación Inter-Agente

La comunicación entre el Supervisor y los agentes subordinados se rige por contratos tipados inmutables:

1. **InterAgentMessage**: Mensaje de delegación que encapsula 	ask_id, 	race_id, source_agent, 	arget_agent, intent, context_payload y delegation_depth.
2. **InterAgentResponse**: Respuesta estructurada que retorna 	ask_id, 	race_id, source_agent, status (success, error_fallback, error_cycle_detected), content, metadata y execution_time_ms.
3. **DelegationTracer**: Singleton de observabilidad que audita cada mensaje enviado y respuesta recibida, detectando bucles infinitos cuando delegation_depth > max_delegations o cuando se repite un ciclo de agentes.

---

## 5. Integración de Datos y Servicios

El sistema multiagente se desacopla del almacenamiento físico mediante conectores de servicio unificados (src/backend/app/multiagent_data_connector.py):

- **Modo Producción:** Conexión directa a Google Cloud Firestore (@google-cloud/firestore) y Google Cloud BigQuery.
- **Modo Local / CI:** Fallback transparente a base de datos simulada en memoria y almacén vectorial local en formato JSON (data/vector_store/embeddings.json).

---

## 6. Evolución Hacia Model Context Protocol (MCP)

Como decisión arquitectónica documentada en [ADR 008](../architecture/adr/008-interagent-communication-protocol.md), la mensajería interna está preparada para evolucionar hacia **Model Context Protocol (MCP)** y Agent-to-Agent (A2A), permitiendo que los agentes se expongan como herramientas remotas seguras en infraestructuras distribuidas.
