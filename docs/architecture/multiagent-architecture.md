# Diseño de la Arquitectura Multiagente de Wellness Lift

Documentación técnica formal del diseño, responsabilidades, mecanismos de delegación y patrón de orquestación para el ecosistema multiagente de la plataforma **Wellness Lift** (Sprint 3).

---

## 1. Propósito y Evolución del Sistema Multiagente

La evolución de **Wellness Lift** hacia una arquitectura multiagente responde a la necesidad de resolver tareas complejas y multidominio (entrenamiento adaptativo, nutrición personalizada, soporte psicológico/motivacional y analítica de rendimiento) mediante agentes autónomos especializados.

En lugar de concentrar toda la lógica en una entidad monolítica, el sistema se estructura bajo una topología coordinada donde un **Orchestrator Agent** centralizado clasifica las intenciones del usuario, delega sub-tareas a agentes expertos y sintetiza una respuesta unificada.

> [!IMPORTANT]
> **Separación entre Diseño e Implementación**: El alcance del presente documento (S3-01) establece la especificación arquitectónica formal, delimitación de responsabilidades, árbol de ruteo y el contrato de comunicación JSON inter-agente que servirá de base para la implementación técnica progresiva en los siguientes entregables del Sprint 3.

---

## 2. Mapa de Agentes y Responsabilidades

| Agente | Tipo / Rol | Responsabilidades Principales | Integración / Herramientas |
| :--- | :--- | :--- | :--- |
| **Orchestrator Agent** | Supervisor / Enrutador Central | Clasificación de intenciones, ruteo de solicitudes, agregación de resultados y control de seguridad global. | `ConversationMemoryManager`, `LLMProviderManager` |
| **Wellness Coach Agent 2.0** | Agente Especializado (Equipo 6) | Prescripción de rutinas semanales, filtros de seguridad biomecánica ante lesiones, alternativas de ejercicios. | `get_exercise_alternative`, `assess_injury_risk`, RAG Vector Store |
| **Nutrition Agent** | Agente Especializado | Planificación de menús alimentarios, cálculo de TDEE y ajuste de distribución de macronutrientes. | `calculate_nutrition_macros`, Catálogo Nutricional |
| **Motivation Agent** | Agente Especializado | Análisis de sentimiento, refuerzo psicológico positivo, estrategias de formación de hábitos. | Registro de Adherencia, Sentiment Analyzer |
| **Analytics Agent** | Agente Especializado | Análisis de progresiones de carga, cálculo de volumen acumulado y proyecciones de rendimiento. | Base de Sesiones Firestore, Volume Calculator |

### 2.1 Trazabilidad y Estado de Implementación de Componentes

Para asegurar claridad técnica entre los entregables históricos y el nuevo diseño del Sprint 3:

| Componente | Estado de Desarrollo | Ámbito de Desarrollo |
| :--- | :--- | :--- |
| **Wellness Coach Agent 2.0** | Existente / Desarrollado | Sprint 2 |
| **Conversation Memory (`ConversationMemoryManager`)** | Existente / Desarrollado | Sprint 2 |
| **RAG / Vector Store (`VectorDatabaseStore`)** | Existente / Desarrollado | Sprint 1 |
| **Orchestrator Agent** | Diseñado / En desarrollo | Sprint 3 (S3-02) |
| **Nutrition Agent** | Propuesto (Arquitectura Objetivo) | Sprint 3 (S3-03+) |
| **Motivation Agent** | Propuesto (Arquitectura Objetivo) | Sprint 3 (S3-03+) |
| **Analytics Agent** | Propuesto (Arquitectura Objetivo) | Sprint 3 (S3-03+) |

---

## 3. Justificación del Patrón de Orquestación: Supervisor (Centralizado)

Se evaluaron cuatro patrones principales de arquitectura multiagente:

1. **Supervisor (centralizado) (SELECCIONADO)**: Un agente supervisor centralizado (Orchestrator Agent) coordina y delega tareas a los agentes especializados, evaluando y consolidando los resultados antes de responder al usuario.
2. **Sequential (Secuencial)**: Los agentes ejecutan en una cadena rígida paso a paso. Se descartó por rigidez y latencia acumulada innecesaria en consultas simples.
3. **Hierarchical (Jerárquico Multinivel)**: Árboles profundos de supervisores en múltiples niveles jerárquicos. Se descartó por complejidad de coordinación y sobrecosto de latencia en comparación con el patrón Supervisor centralizado.
4. **Swarm (Enjambre Autónomo)**: Comunicación libre entre agentes sin supervisor. Se descartó por falta de determinismo y riesgo de romper guardrails de seguridad médica.

### Justificación Técnica de la Selección:
- **Control Centralizado de Seguridad**: El Orchestrator Agent garantiza que las reglas de salud (ej. hernia discal, dolor de rodilla) se apliquen estrictamente antes de retornar cualquier recomendación al atleta.
- **Eficiencia en Invocación**: Permite invocar únicamente a los agentes especializados requeridos por la consulta actual, reduciendo el consumo de tokens y el tiempo de respuesta.
- **Gestión de Memoria Unificada**: La memoria conversacional multi-turno se gestiona de forma transparente a nivel del supervisor.

---

## 4. Diagramas Arquitectónicos en Mermaid

> [!NOTE]
> **Delimitación entre Arquitectura Objetivo y Estado Real**: Los diagramas Mermaid a continuación ilustran la **arquitectura objetivo** del sistema multiagente (Sprint 3). Los agentes `Nutrition Agent`, `Motivation Agent` y `Analytics Agent`, junto con sus herramientas específicas, corresponden a componentes **propuestos/planificados** dentro del contrato de diseño de S3-01, mientras que el `Wellness Coach Agent 2.0`, `ConversationMemoryManager` y `VectorDatabaseStore` corresponden a componentes funcionales existentes desarrollados en los Sprints 1 y 2.

### A. Diagrama General de la Arquitectura Multiagente

```mermaid
flowchart TD
    Client(["Usuario / Cliente Frontend"]) --> FastAPI["Servidor Backend FastAPI"]
    FastAPI --> Orchestrator["Orchestrator Agent (Supervisor Central)"]

    subgraph MemoryLayer["Capa de Estado y Conocimiento"]
        Memory["ConversationMemoryManager (Short/Long Term)"]
        VectorStore[("Vector Store RAG (Embeddings)")]
        FirestoreDB[("Firestore DB NoSQL (Perfil Atleta)")]
    end

    Orchestrator <--> Memory
    Orchestrator <--> FirestoreDB

    subgraph SpecialistAgents["Ecosistema de Agentes Especializados (Propuestos/Existentes)"]
        CoachAgent["Wellness Coach Agent 2.0 (Existente - Equipo 6)"]
        NutriAgent["Nutrition Agent (Propuesto - Sprint 3)"]
        MotiAgent["Motivation Agent (Propuesto - Sprint 3)"]
        AnalyAgent["Analytics Agent (Propuesto - Sprint 3)"]
    end

    Orchestrator -- "Delegación: Entrenamiento / Lesiones" --> CoachAgent
    Orchestrator -- "Delegación: Dieta / Macros" --> NutriAgent
    Orchestrator -- "Delegación: Estado Anímico" --> MotiAgent
    Orchestrator -- "Delegación: Métricas / Récords" --> AnalyAgent

    CoachAgent <--> VectorStore
```

---

### B. Diagrama de Secuencia de Orquestación y Delegación

```mermaid
sequenceDiagram
    autonumber
    actor Atleta as Atleta (Usuario)
    participant Supervisor as Orchestrator Agent (Supervisor)
    participant Coach as Wellness Coach Agent 2.0
    participant Nutri as Nutrition Agent (Propuesto)
    participant Memory as ConversationMemory

    Atleta->>Supervisor: "Tengo hernia discal, dame una rutina y mi plan de nutrición"
    Supervisor->>Memory: Cargar Perfil y Memoria Conversacional
    Memory-->>Supervisor: Historial + Hechos Extraídos

    Note over Supervisor: Clasificación de Intenciones Múltiples

    par Delegación Concurrente / Secuencial Controlada
        Supervisor->>Coach: Solicitar Rutina Adaptada (Filtro Hernia Discal)
        Coach-->>Supervisor: Rutina con Prensa 45° (Sin Sentadilla Libre)
    and
        Supervisor->>Nutri: Solicitar Plan de Macronutrientes
        Nutri-->>Supervisor: TDEE 2400 kcal (Proteínas 160g, Carbs 250g, Grasas 70g)
    end

    Supervisor->>Supervisor: Sintetizar Respuestas + Validar Guardrails de Seguridad
    Supervisor->>Memory: Guardar Interacción en Memoria
    Supervisor-->>Atleta: Entrega de Respuesta Integrada
```

---

### C. Árbol de Decisión de Ruteo del Supervisor

```mermaid
flowchart TD
    InputQuery["Recepción de Mensaje del Usuario"] --> IntentClassifier{"Analizar Intención Principal"}

    IntentClassifier -- "Rutina / Ejercicios / Lesiones" --> RouteCoach["Delegar a Wellness Coach Agent 2.0"]
    IntentClassifier -- "Comida / Macros / Calorías" --> RouteNutri["Delegar a Nutrition Agent (Propuesto)"]
    IntentClassifier -- "Progreso / Volumen / Récords" --> RouteAnaly["Delegar a Analytics Agent (Propuesto)"]
    IntentClassifier -- "Desmotivación / Hábito" --> RouteMoti["Delegar a Motivation Agent (Propuesto)"]
    IntentClassifier -- "Consulta Multidominio" --> RouteMulti["Delegación Compuesta (Coach + Nutri)"]

    RouteCoach --> Synthesize["Sintetizar Respuesta Final"]
    RouteNutri --> Synthesize
    RouteAnaly --> Synthesize
    RouteMoti --> Synthesize
    RouteMulti --> Synthesize

    Synthesize --> ReturnClient(["Retornar Respuesta al Cliente"])
```

---

## 5. Protocolo de Comunicación Inter-Agente (Payload Schema)

Las solicitudes delegadas por el **Orchestrator Agent** hacia los agentes especializados utilizan una estructura JSON homogénea:

```json
{
  "task_id": "TASK-2026-0830-01",
  "source_agent": "OrchestratorAgent",
  "target_agent": "WellnessCoachAgent2.0",
  "user_id": "user_12345",
  "intent": "generate_routine_with_medical_guardrails",
  "payload": {
    "fitness_level": "intermedio",
    "goal": "hipertrofia",
    "health_conditions": ["hernia discal L4-L5"],
    "extracted_facts": ["Condición reportada en chat: Dolor lumbar."]
  }
}
```

---

## 6. Conclusión y Coherencia con el Sistema

La arquitectura propuesta evoluciona de manera natural los desarrollos de los Sprints 1 y 2, posicionando al **Wellness Coach Agent 2.0** como el agente experto en ciencia del ejercicio y preservando la retrocompatibilidad con la API FastAPI existente.
