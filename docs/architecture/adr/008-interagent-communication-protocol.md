# Registro de Decisiones de Arquitectura (ADR) — Protocolo de Comunicación Inter-Agente

Estado: Aceptado  
Fecha: 30 de agosto de 2026 (Actualizado: 26 de septiembre de 2026)  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-008: Protocolo Homogéneo de Mensajes, Trazabilidad y Prevención de Ciclos

### Contexto
En el Sprint 3 (S3-04), se requería implementar un protocolo estandarizado de comunicación e intercambio de información contextual entre el **Orchestrator Agent** y los agentes especializados (`WellnessCoachAgent2.0`, `NutritionAgent`, `MotivationAgent`, `AnalyticsAgent`), garantizando la trazabilidad de cada sub-tarea, transmitiendo el contexto completo y evitando bucles de delegación infinitos.

### Decisión
Se actualizó la implementación en `src/backend/app/wellness_agent/communication.py` y `src/backend/app/orchestrator.py`:

1. **Protocolo Homogéneo Real (`Orchestrator -> InterAgentMessage -> SpecializedAgent -> InterAgentResponse -> Orchestrator`)**:
   - Cada agente especializado expone e implementa el método `process_interagent_message(msg: InterAgentMessage) -> InterAgentResponse`, recibiendo formalmente el mensaje estandarizado y retornando la respuesta estructurada.

2. **Transmisión de Contexto Completo (`context_payload`)**:
   - El payload `context_payload` inyecta de forma transparente el mensaje original, perfil de salud (`health_conditions`, `limitations`), nivel de experiencia, objetivo y observaciones extraídas de la memoria a largo plazo.

3. **Propagación e Incremento de Saltos (`hop_count`)**:
   - Cada delegación y sub-delegación incrementa de forma activa `hop_count = parent_hop_count + 1`. Si un flujo excede `max_hops=5`, el mensaje es rechazado automáticamente por el `DelegationTracer`.

4. **Prevención de Ciclos Directos e Indirectos**:
   - `DelegationTracer.log_delegation()` analiza la cadena de agentes acumulada en la traza activa (`trace_id`), previniendo ciclos de 2 saltos (`A -> B -> A`) así como ciclos indirectos más largos (`A -> B -> C -> A`).

5. **Validación en Flujo Multidominio**:
   - Se valida explícitamente el valor booleano de `log_delegation()` en `handle_multidomain_delegation()` antes de proceder con las sub-delegaciones compuestas.

6. **Integración con pytest y CI**:
   - Se actualizó la suite en `tests/test_interagent_communication.py` y el flujo de GitHub Actions (`.github/workflows/ci.yml`) ejecutando `pytest tests/ -v`.

### Consecuencias
- **Positivas**: Trazabilidad completa e identificación transparente de qué agente atendió cada sub-solicitud.
- **Positivas**: Protección robusta frente a errores de configuración que pudieran derivar en llamadas recursivas infinitas directas o indirectas.
- **Positivas**: Preparación limpia de la base de código para la futura adopción de servidores MCP y endpoints A2A.
