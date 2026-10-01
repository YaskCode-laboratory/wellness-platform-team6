# 📊 Reporte de Métricas de Recuperación y Calidad RAG — Wellness Lift

Informe técnico de la evaluación del motor de recuperación de información (*RAG Retrieval Benchmark*) correspondiente al Issue **S1-06 (#10)** en la plataforma **Wellness Lift**.

---

## 📌 1. Alcance Real de la Evaluación y Delimitación Metodológica

El presente benchmark evalúa exclusivamente el **Desempeño del Motor de Recuperación (Retriever)** y la **Cobertura de Información Médica en los Chunks Recuperados**. 

> [!IMPORTANT]
> **Delimitación de Alcance**: Esta suite de pruebas evalúa el contexto relevante recuperado desde la base de datos vectorial (`vector_index.json` / `embeddings.json`) en la etapa previa a la generación de lenguaje natural. Métricas generativas como "fidelidad de la respuesta", "groundedness" o "ausencia de alucinaciones" en la salida del LLM corresponden a etapas de evaluación sintética posteriores (S1-05 / Sprint 2) y no forman parte de este benchmark de recuperación.

### Distinción Metodológica:
1. **Calidad de Recuperación**: Evaluación estadística de alineación vectorial y relevancia temática mediante Precision@K, Recall@K y MRR sobre las consultas del benchmark.
2. **Cobertura de Seguridad Médica en Chunks**: Verificación de presencia explícita de ejercicios contraindicados y sustitutos seguros dentro de los textos de los fragmentos recuperados en el Top-K.
3. **Calidad/Fidelidad Generativa**: Salida textual sintetizada por el LLM (alcance fuera del benchmark de recuperación).

---

## 📐 2. Métricas y Criterios Evaluados

| Métrica | Definición Matemático-Conceptual | Ámbito / Base de Cálculo | Umbral Objetivo |
| :--- | :--- | :--- | :--- |
| **Precision@3** | Proporción de chunks recuperados en el Top-3 que corresponden a la verdad de referencia ($Precision@K = \frac{|Recuperados \cap Esperados|}{K}$). | Total de 10 consultas del benchmark. | $\ge 0.20$ |
| **Recall@3** | Proporción de chunks esperados que fueron recuperados en el Top-3 ($Recall@K = \frac{|Recuperados \cap Esperados|}{|Esperados|}$). | Total de 10 consultas del benchmark. | $\ge 0.65$ |
| **MRR (Mean Reciprocal Rank)** | Promedio del recíproco de la posición del primer chunk relevante ($MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$). | Total de 10 consultas del benchmark. | $\ge 0.45$ |
| **Medical Safety Accuracy** | Porcentaje de consultas médicas ($N_{medical} = 4$) donde los chunks recuperados contienen **tanto** los ejercicios contraindicados **como** los sustitutos seguros. | Exclusivamente las 4 consultas de la categoría `Medical Substitutions` (Q01-Q04). | $\ge 0.80$ |

### Criterio de Aprobación de Seguridad (`safety_passed`):
Una consulta médica aprueba la verificación de cobertura (`safety_passed = True`) si y solo si los chunks recuperados en el Top-3 contienen:
- $0$ contraindicaciones omitidas (`len(unwarned_contraindications) == 0`).
- $0$ sustitutos seguros omitidos (`len(missing_substitutes) == 0`).

---

## 📊 3. Resultados Globales del Benchmark Reproducible

Los siguientes resultados corresponden a la ejecución directa y reproducible del script `scripts/evaluate_rag.py` sobre la representación vectorial determinista de la base de conocimiento (`data/evaluation/evaluation_results.json`):

```text
===========================================================================
RESUMEN GENERAL DE METRICAS DE EVALUACION (TOP-3)
===========================================================================
Consultas totales evaluadas:     10
Consultas médicas evaluadas:     4
Precision@3 promedio:           33.33% (0.3333)
Recall@3 promedio:             100.00% (1.0000)
Mean Reciprocal Rank (MRR):      0.8167
Precisión en Seguridad Médica:  100.00% (4/4 casos médicos aprobados)
---------------------------------------------------------------------------
```

---

## 🔎 4. Resultados Detallados por Caso de Prueba

### A. Sustituciones Médicas y Lesiones (`Medical Substitutions` — Denominador de Seguridad: $N=4$)
- **[Q01] Hernia Discal L4-L5 Lumbar**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`, `Safety: OK (PASSED)`. El chunk relevante `medical_adaptations.md#2...` se recuperó en la posición 1 del ranking. Contiene todas las contraindicaciones (Sentadilla Libre, Peso Muerto, Press Militar) y sustitutos (Prensa 45°, Peso Muerto Rumano asistido, Press Sentado).
- **[Q02] Lesión de Rodilla (Meniscos/Ligamentos)**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`, `Safety: OK (PASSED)`. El chunk relevante apareció en posición 1.
- **[Q03] Hipertensión Arterial**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`, `Safety: OK (PASSED)`. El chunk relevante apareció en posición 1.
- **[Q04] Lesión de Manguito Rotador**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`, `Safety: OK (PASSED)`. El chunk relevante apareció en posición 1.

### B. Biomecánica y Seguridad (`Biomechanics & Safety`)
- **[Q05] Alineación Articular en Sentadilla**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`.
- **[Q06] Criterios de Selección (NSCA / ISB)**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 0.5000`.

### C. Hipertrofia y Periodización (`Hypertrophy & Periodization`)
- **[Q07] Mecanismos de Hipertrofia**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 1.0000`.
- **[Q08] Rangos de Repetición y Descanso por Fase**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 0.6667`.

### D. Alcance del Dominio (`Domain Scope`)
- **[Q09] Alcance de Adaptaciones Médicas**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 0.5000`.
- **[Q10] Alcance de Periodización e Hipertrofia**: `Precision@3 = 0.3333`, `Recall@3 = 1.0000`, `MRR = 0.5000`.

---

## 🔗 5. Trazabilidad con Etapas Anteriores del Pipeline RAG (S1-01 a S1-05)

La integridad de esta evaluación depende directamente de la cadena de dependencias del pipeline de datos:

1. **S1-01 (#5 / PR #27 — Base de Conocimiento)**: Estructura los documentos Markdown en `data/knowledge_base/`.
2. **S1-02 (#6 / PR #28 — Estrategia de Chunking Híbrida)**: Genera los fragmentos en `data/processed_chunks/rag_chunks.json`.
3. **S1-03 / S1-04 (#7, #8 / PR #30 — Vector Store & Embeddings)**: Produce el índice vectorial determinista L2-normalizado en `data/vector_store/vector_index.json`.
4. **S1-05 (#9 / PR #31 — Pipeline RAG Retriever)**: Implementa la función de similitud coseno y búsqueda Top-K.
5. **S1-06 (#10 / PR #32 — Suite de Evaluación)**: Consume `vector_index.json` y `test_queries.json` para generar `evaluation_results.json`.

---

## 🚀 6. Plan de Acción y Oportunidades para Sprint 2

1. **Segmentación de la Matriz Médica**: Dividir la matriz global de lesiones en chunks individuales por patología para mejorar `Precision@K` cuando $K > 1$.
2. **Re-Ranking Híbrido Sparse-Dense**: Implementar combinación de BM25 (búsqueda léxica) + Coseno (búsqueda densa) para mejorar el ranking inicial.
