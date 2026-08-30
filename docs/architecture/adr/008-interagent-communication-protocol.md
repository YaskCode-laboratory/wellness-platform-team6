# Registro de Decisiones de Arquitectura (ADR) — Protocolo de Comunicación Inter-Agente

Estado: Aceptado  
Fecha: 30 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-008: Protocolo Homogéneo de Mensajes, Trazabilidad y Prevención de Ciclos

### Contexto
En el Sprint 3 (S3-04), se requería implementar un protocolo estandarizado de comunicación e intercambio de información contextual entre el **Orchestrator Agent** y los agentes especializados (`WellnessCoachAgent2.0`, `NutritionAgent`, `MotivationAgent`, `AnalyticsAgent`), garantizando la trazabilidad de cada sub-tarea y evitando bucles de delegación infinitos.

### Decisión
Se implementó el módulo `src/backend/app/wellness_agent/communication.py`:

1. **Estructura Homogénea de Entrada (`InterAgentMessage`)**: Atributos `task_id`, `trace_id`, `source_agent`, `target_agent`, `user_id`, `intent`, `context_payload`, `timestamp` y `hop_count`.
2. **Estructura Homogénea de Salida (`InterAgentResponse`)**: Atributos `task_id`, `trace_id`, `source_agent`, `status`, `content`, `metadata` y `execution_time_ms`.
3. **Mecanismo de Trazabilidad y Prevención de Ciclos (`DelegationTracer`)**:
   - Registro centralizado por `trace_id`.
   - Control de saltos máximos (`max_hops=5`) y bloqueo directo ante detección de patrones cíclicos (`A -> B -> A`).
4. **Retrocompatibilidad & Evolución**: Diseñado en compatibilidad conceptual directa con los estándares de la industria **MCP** (Model Context Protocol) y **A2A** (Agent-to-Agent).

### Consecuencias
- Positivas: Trazabilidad completa e identificación transparente de qué agente atendió cada sub-solicitud.
- Positivas: Protección robusta frente a errores de configuración que pudieran derivar en llamadas recursivas infinitas.
- Positivas: Preparación limpia de la base de código para la futura adopción de servidores MCP y endpoints A2A.
