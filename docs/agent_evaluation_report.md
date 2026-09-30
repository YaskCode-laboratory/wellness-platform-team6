# Informe de Evaluación de Comportamiento y Calidad — Wellness Coach Agent 2.0 (Issue #17)

## 1. Resumen Ejecutivo
Este documento detalla la metodología de evaluación cuantitativa, la matriz de contraste de comportamiento esperado vs obtenido, la validación estricta de llamadas a herramientas, la puntuación de relevancia derivada y las evidencias registradas en `data/agent_evaluation_results.json` para el **Wellness Coach Agent 2.0**, respondiendo a la revisión **[S2-06 - Evaluar comportamiento y calidad del agente] (Issue #17)**.

---

## 2. Metodología de Evaluación y Criterios de Validación

1. **Validación Estricta de Herramientas**:
   - Para casos con `expected_tool = None` (respuestas conversacionales directas), se exige que **no se ejecute ninguna herramienta previa a `FINAL_ANSWER`**. Si el agente invoca herramientas innecesarias, el caso falla automáticamente.
   - Para casos con `expected_tool_sequence`, se valida que las herramientas requeridas sean invocadas en el orden exacto especificado.
   - Para casos con `expected_tool`, se verifica la invocación correcta de la herramienta objetivo.

2. **Memoria Conversacional Multiturno & Retención de Hechos (TC-02)**:
   - Se evalúa la conservación y recuperación de información a través de una secuencia de 3 turnos conversacionales sobre el flujo real del agente utilizando `ConversationMemoryManager`.
   - **Criterios de Validación Estricta**: La evaluación distingue explícitamente entre tres componentes fundamentales:
     - **Riesgo correctamente identificado**: El agente debe identificar `risk_level: HIGH` y contraindicación explícita para sentadilla libre con barra por patología lumbar.
     - **Grupo muscular correcto**: La herramienta de alternativas debe consultar el grupo muscular `Piernas`.
     - **Alternativa realmente coherente con la restricción**: El ejercicio sustituto devuelto por `get_exercise_alternative` no debe contradecir la contraindicación detectada (debe evitar variantes de sentadilla o compresión axial como `Sentadilla Goblet con Mancuerna` o `Sentadilla con Barra`, priorizando ejercicios con soporte lumbar como `Prensa de Piernas`).
   - Si la herramienta de alternativa devuelve un ejercicio inconsistente con la patología detectada, el caso se califica objetivamente como **FAILED** y se documenta como limitación del agente.

3. **Derivación del Puntaje de Relevancia (`relevance_score`)**:
   - El puntaje se calcula en una escala de 1.0 a 5.0 basada en la exactitud en la selección de herramientas, la validez del flujo ReAct, la coherencia biomecánica y la completitud de la respuesta.
   - Si se detectan inconsistencias en herramientas o recomendaciones contradictorias, se aplica una penalización de 2.5 puntos y el caso pasa a estado `FAILED`.

---

## 3. Matriz de Casos de Prueba Evaluados (`TC-01` a `TC-05`)

| ID Caso | Categoría | Prompt / Secuencia de Turnos | Comportamiento Esperado | Comportamiento Obtenido | Herramientas Ejecutadas | Puntaje Relevancia | Estado |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Respuesta Directa | *Hola, buenos días, gracias por la recomendación* | Respuesta conversacional directa sin invocar herramientas. | Respuesta directa generada sin llamadas a herramientas innecesarias. | `FINAL_ANSWER` | `5.0 / 5.0` | **PASSED** |
| **TC-02** | Conversación Multiturno & Retención de Hechos | *T1: Hola, sufro de hernia discal lumbar L4-L5. -> T2: ¿Qué ejercicios de piernas puedo hacer hoy? -> T3: ¿La sentadilla libre con barra es recomendable para mi rutina?* | Retener patología en T1; en T3 identificar riesgo HIGH contraindicando sentadilla libre y seleccionar alternativa de piernas coherente y no contraindicada. | Inconsistencia detectada: la herramienta `get_exercise_alternative` seleccionó 'Sentadilla Goblet con Mancuerna', la cual contradice la contraindicación de compresión axial lumbar identificada por `assess_injury_risk`. [Riesgo identificado: SÍ \| Grupo muscular correcto: SÍ \| Alternativa coherente con restricción: NO]. | `assess_injury_risk`, `get_exercise_alternative`, `FINAL_ANSWER` | `2.5 / 5.0` | **FAILED** |
| **TC-03** | Secuencia Multipaso ReAct | *Tengo molestias en la espalda baja, evalúa el riesgo y sugiere sustitutos de ejercicio.* | Ejecutar la secuencia ordenada: `assess_injury_risk` -> `get_exercise_alternative` -> `FINAL_ANSWER`. | Secuencia requerida (`assess_injury_risk` -> `get_exercise_alternative`) ejecutada en el orden exacto. | `assess_injury_risk`, `get_exercise_alternative`, `FINAL_ANSWER` | `5.0 / 5.0` | **PASSED** |
| **TC-04** | Tool Calling Exactitud | *Calcula mis macronutrientes y calorías para entrenamiento* | Invocar la herramienta de cálculo de macronutrientes `calculate_nutrition_macros`. | Herramienta requerida `calculate_nutrition_macros` ejecutada correctamente. | `calculate_nutrition_macros`, `FINAL_ANSWER` | `5.0 / 5.0` | **PASSED** |
| **TC-05** | Recuperación RAG ReAct | *Evalúa la evidencia científica RAG sobre periodización de hipertrofia* | Invocar `retrieve_rag_knowledge` y sintetizar respuesta final ReAct. | Herramienta `retrieve_rag_knowledge` ejecutada y respuesta sintetizada. | `retrieve_rag_knowledge`, `FINAL_ANSWER` | `5.0 / 5.0` | **PASSED** |

---

## 4. Resultados Cuantitativos del Benchmark

- **Total Casos de Prueba**: 5
- **Casos Aprobados (PASSED)**: 4
- **Casos Fallidos (FAILED)**: 1
- **Tasa de Éxito (Accuracy)**: `80.0%`
- **Puntaje Promedio de Relevancia**: `4.5 / 5.0`
- **Archivo de Resultados**: `data/agent_evaluation_results.json`

---

## 5. Limitaciones Identificadas

1. **Selección Estocástica de Alternativas sin Filtrado Biomecánico**: La herramienta `get_exercise_alternative` selecciona aleatoriamente ejercicios del catálogo por grupo muscular sin considerar las patologías previas o contraindicaciones identificadas por `assess_injury_risk` (p. ej., sugiriendo sentadilla goblet a un usuario con hernia discal lumbar).
2. **Latencia Acumulada**: El encadenamiento de múltiples herramientas secuenciales en el ciclo ReAct incrementa el tiempo total de respuesta.
3. **Persistencia entre Sesiones HTTP**: La memoria episódica en memoria local requiere sincronización con Google Cloud Firestore para persistir sesiones entre reinicios del servidor.

---

## 6. Propuestas de Mejora Concretas

1. **Filtrado Contextual de Patologías en Alternativas**: Enriquecer `get_exercise_alternative` para aceptar parámetros opcionales de contraindicaciones biomecánicas o conectar un middleware de filtrado que descarte variantes lesivas (como ejercicios axiales ante hernias lumbares).
2. **Caché LRU de Consultas Biomecánicas**: Reducir latencia almacenando en caché resultados de herramientas frecuentemente invocadas.
3. **Persistencia Episódica NoSQL**: Integrar almacenamiento persistente en Google Cloud Firestore para mantener el historial de conversaciones de forma permanente.
