# Informe de Evaluación de Comportamiento y Calidad — Wellness Coach Agent 2.0 (Issue #17)

## 1. Resumen Ejecutivo
Este documento detalla la metodología de evaluación cuantitativa, la matriz de contraste de comportamiento esperados vs obtenidos, la validación estricta de llamadas a herramientas, la puntuación de relevancia derivada y las evidencias registradas en `data/agent_evaluation_results.json` para el **Wellness Coach Agent 2.0**, respondiendo al requerimiento **[S2-06 - Evaluar comportamiento y calidad del agente] (Issue #17)**.

---

## 2. Metodología de Evaluación y Criterios de Validación

1. **Validación Estricta de Herramientas**:
   - Para casos con `expected_tool = None` (respuestas conversacionales directas), se exige que **no se ejecute ninguna herramienta**. Si el agente invoca herramientas innecesarias, el caso falla automáticamente.
   - Para casos que requieren herramientas específicas o un conjunto de herramientas válidas, se verifica que la invocación coincida con la intención de la consulta.

2. **Derivación del Puntaje de Relevancia (`relevance_score`)**:
   - El puntaje se calcula sobre una escala de 1.0 a 5.0 basada en la exactitud en la selección de herramientas, la completitud de la respuesta final y la presencia de términos clave requeridos por el dominio biomecánico/nutricional.

3. **Contraste de Comportamiento Esperado vs Obtenido**:
   - Se registra explícitamente el resultado de cada prueba en la matriz de evaluación.

---

## 3. Matriz de Casos de Prueba Evaluados (`TC-01` a `TC-05`)

| ID Caso | Categoría | Prompt de Entrada | Comportamiento Esperado | Comportamiento Obtenido | Herramientas Ejecutadas | Puntaje Relevancia | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Respuesta Directa | *Hola, buenos días, gracias por la recomendación* | Respuesta directa sin herramientas innecesarias. | Respuesta directa sin llamadas a herramientas. | `FINAL_ANSWER` | `5.0 / 5.0` | **PASSED** |
| **TC-02** | Conversación Multiturno | *Quiero mejorar mi sentadilla libre pero me duele la zona baja de la espalda al bajar.* | Identificar dolor lumbar y evaluar riesgo biomecánico / contraindicaciones. | Evaluación de riesgo biomecánico y alternativas ejecutadas. | `assess_injury_risk`, `get_exercise_alternative` | `5.0 / 5.0` | **PASSED** |
| **TC-03** | Memoria y Hechos | *Tengo una hernia discal en L4-L5 y me molesta la zona lumbar.* | Retención de Hernia L4-L5 y evaluación de contraindicaciones. | Evaluación de riesgo y búsqueda de sustituto seguro. | `assess_injury_risk`, `get_exercise_alternative` | `5.0 / 5.0` | **PASSED** |
| **TC-04** | Tool Calling | *Calcula mis macronutrientes y calorías para entrenamiento* | Invocación de la herramienta de nutrición `calculate_nutrition_macros`. | Herramienta `calculate_nutrition_macros` invocada y procesada. | `calculate_nutrition_macros` | `5.0 / 5.0` | **PASSED** |
| **TC-05** | Razonamiento ReAct | *Evalúa la evidencia científica RAG sobre periodización de hipertrofia* | Invocación de RAG y síntesis final ReAct. | Herramienta `retrieve_rag_knowledge` ejecutada y respuesta sintetizada. | `retrieve_rag_knowledge` | `5.0 / 5.0` | **PASSED** |

---

## 4. Resultados Cuantitativos del Benchmark

- **Total Casos de Prueba**: 5
- **Casos Aprobados (PASSED)**: 5
- **Casos Fallidos (FAILED)**: 0
- **Tasa de Éxito (Accuracy)**: `100.0%`
- **Puntaje Promedio de Relevancia**: `5.0 / 5.0`
- **Archivo de Resultados**: `data/agent_evaluation_results.json`

---

## 5. Limitaciones Identificadas

1. **Latencia Acumulada**: El encadenamiento secuencial de 2 a 3 herramientas en el ciclo ReAct incrementa el tiempo de respuesta total.
2. **Persistencia entre Sesiones HTTP**: La memoria episódica requiere sincronización constante con la base NoSQL Cloud Firestore para mantener el contexto cuando se reinicia el cliente.

---

## 6. Propuestas de Mejora Concretas

1. **Implementación de Caché LRU de Herramientas**: Almacenar en caché respuestas para consultas biomecánicas frecuentes, reduciendo llamadas redundantes.
2. **Persistencia Episódica NoSQL**: Almacenar entidades y hechos extraídos directamente en Google Cloud Firestore.
