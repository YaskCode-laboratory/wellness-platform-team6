# Registro de Decisiones de Arquitectura (ADR) — Estrategia de Memoria Conversacional

Estado: Aceptado  
Fecha: 28 de septiembre de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-003: Memoria Conversacional de Doble Nivel y Extracción de Hechos

### Contexto
En asistentes deportivos como el Wellness Coach Agent 2.0, los atletas interactúan en múltiples turnos reportando lesiones, metas y progresos. Mantener un historial ilimitado en cada llamada al LLM resulta ineficiente en costos y ventana de contexto, mientras que no mantener memoria produce respuestas descontextualizadas.

### Decisión
Se adoptó una arquitectura de **Memoria Conversacional de Doble Nivel** gestionada por `ConversationMemoryManager`:

1. **Buffer a Corto Plazo (Short-Term Memory)**: Mantiene los últimos 10 turnos de conversación (`max_history_turns * 2`) mediante `get_history()` para inyección directa en el prompt.
2. **Persistencia a Largo Plazo (Long-Term Persistence)**: Almacena en archivos JSON locales (`data/memory/{user_id}_memory.json`) la totalidad del historial sin truncar y los hechos extraídos. La arquitectura está diseñada para permitir extensión a Google Cloud Firestore en producción.
3. **Extracción Automática de Hechos (Fact Extraction)**: Analiza el texto del usuario (`extract_and_save_facts`) para identificar condiciones de salud y récords de peso.

### Consecuencias
- Positivas: Respuestas consistentes y seguras en diálogos multi-turno.
- Positivas: Auto-carga de memoria previa en nuevas sesiones evitando sobrescrituras.
- Positivas: Reducción del consumo de tokens al limitar la ventana del prompt a corto plazo mientras se preserva el historial completo en JSON.
