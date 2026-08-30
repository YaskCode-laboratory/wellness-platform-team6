# Registro de Decisiones de Arquitectura (ADR) — Patrón de Orquestación Multiagente

Estado: Aceptado  
Fecha: 30 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-005: Selección del Patrón Supervisor para la Arquitectura Multiagente

### Contexto
Al evolucionar la plataforma Wellness Lift hacia un sistema multiagente coordinado (Sprint 3), se requería seleccionar un patrón de orquestación que garantizara la correcta delegación de tareas especializadas (entrenamiento adaptativo, nutrición, analítica, motivación), manteniendo en todo momento los guardrails de seguridad médica y la coherencia del estado conversacional.

### Decisión
Se adoptó el patrón **Supervisor / Jerárquico** encabezado por el **Orchestrator Agent**:

- El Orchestrator Agent analiza cada mensaje del usuario, determina la intención primaria y secundaria, y delega de manera directa o paralela el trabajo a los agentes especializados.
- El agente especializado desarrollado por el Equipo 6 (**Wellness Coach Agent 2.0**) asume la responsabilidad exclusiva de la prescripción biomecánica y adaptaciones médicas.
- El Orchestrator Agent valida las respuestas de los agentes antes de consolidar la respuesta final entregada al cliente.

### Comparativa de Patrones Evaluados
1. **Supervisor (Seleccionado)**: Máximo control de seguridad, flexibilidad de ruteo y gestión unificada de memoria.
2. **Sequential**: Cadena rígida paso a paso. Descartado por ineficiencia en consultas simples.
3. **Swarm**: Comunicación descentralizada enjambre. Descartado por riesgo de incoherencia y falta de validación de seguridad centralizada.

### Consecuencias
- Positivas: Control riguroso de guardrails de seguridad médica en un único punto de supervisión.
- Positivas: Escalabilidad limpia para agregar nuevos agentes especializados sin modificar el código de los agentes existentes.
- Positivas: Reducción del consumo de tokens al invocar únicamente los agentes requeridos.
