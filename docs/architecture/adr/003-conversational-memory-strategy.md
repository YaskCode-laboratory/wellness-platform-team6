# Registro de Decisiones de Arquitectura (ADR) — Estrategia de Memoria Conversacional

Estado: Aceptado  
Fecha: 29 de agosto de 2026  
Autores: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## ADR-003: Memoria Conversacional de Doble Nivel y Extracción de Hechos

### Contexto
En agentes de asistencia deportiva como el Wellness Coach Agent 2.0, los usuarios interactúan en sesiones continuas o intermitentes donde mencionan limitaciones físicas (ej. dolor lumbar), preferencias y progresos de entrenamiento. Mantener un historial ilimitado en cada llamada al LLM resulta ineficiente y costoso en tokens, mientras que no mantener memoria produce respuestas descontextualizadas.

### Decisión
Se adoptó una arquitectura de **Memoria Conversacional de Doble Nivel** coordinada por `ConversationMemoryManager`:

1. **Buffer a Corto Plazo (Short-Term Memory)**: Mantiene una ventana deslizante de los últimos 10 turnos de conversación para inyección directa en el prompt del LLM.
2. **Persistencia a Largo Plazo (Long-Term Persistence)**: Guarda en JSON local (`data/memory/{user_id}_memory.json`) el historial completo sin truncar y los hechos extraídos, con diseño extensible hacia Google Cloud Firestore para entornos multinodo.
3. **Extracción Automática de Hechos (Fact Extraction)**: Analiza el texto del usuario para identificar condiciones de salud o marcas de peso y almacenarlas de forma estructurada.

### Consecuencias
- Positivas: Respuestas consistentes y seguras en diálogos multi-turno.
- Positivas: Reducción del consumo de tokens al limitar la ventana del prompt a corto plazo mientras se preservan hechos clave a largo plazo.
- Positivas: Pruebas automatizadas 100% reproducibles.
