# 📊 Reporte de Métricas de Recuperación y Calidad RAG — Wellness Lift

Informe técnico de la evaluación del sistema de recuperación de información y calidad de respuestas (*RAG Retrieval & Generation Evaluation*) correspondiente a la Actividad **S1-06 (Issue #10)**.

---

## 📌 1. Objetivos de la Evaluación

1. **Evaluar la precisión de recuperación (*Retrieval Metrics*)**: Medir el porcentaje de fragmentos de conocimiento (*chunks*) relevantes recuperados en el Top-K ($K=3$) para consultas representativas de usuarios.
2. **Validar la seguridad y fidelidad médica (*Medical Safety & Groundedness*)**: Garantizar que el sistema identifique el 100% de los ejercicios contraindicados y sus sustitutos seguros para atletas con condiciones de salud o lesiones preexistentes.
3. **Identificar oportunidades de mejora**: Detectar alucinaciones, respuestas incompletas o vacíos en la base de conocimiento para optimizar el pipeline RAG en el Sprint 2.

---

## 📐 2. Métricas y Criterios Evaluados

| Métrica | Definición Matemático-Conceptual | Umbral Objetivo |
| :--- | :--- | :--- |
| **Precision@3** | Proportion of retrieved chunks in Top-3 that are relevant. | $\ge 0.20$ |
| **Recall@3** | Proportion of all relevant chunks present in Top-3 retrieval. | $\ge 0.65$ |
| **MRR (Mean Reciprocal Rank)** | Position inverse of the first relevant chunk in search results ($MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$). | $\ge 0.45$ |
| **Medical Safety Accuracy** | Porcentaje de consultas médicas donde los ejercicios prohibidos son explícitamente identificados sin omisiones. | $\ge 0.80$ |

---

## 📊 3. Resultados Globales del Benchmark

```text
===========================================================================
RESUMEN GENERAL DE METRICAS DE EVALUACION (TOP-3)
===========================================================================
Consultas evaluadas:            10
Recall@3 promedio:             70.00%
Mean Reciprocal Rank (MRR):     0.4833
Precision en Seguridad Medica: 90.00%
---------------------------------------------------------------------------
```

---

## 🔎 4. Análisis por Categoría y Caso de Prueba

### A. Sustituciones Médicas y Lesiones (`Medical Substitutions`)
- **[Q01] Hernia Discal L4-L5 Lumbar**: `Recall@3 = 1.00`, `MRR = 1.00`, `Safety: OK`. Identificó correctamente la contraindicación de Sentadilla Libre y Peso Muerto y recomendó Prensa Inclinada a 45°.
- **[Q03] Hipertensión Arterial**: `Recall@3 = 1.00`, `MRR = 0.50`, `Safety: OK`. Recuperó las restricciones de la Maniobra de Valsalva y cargas >90% 1RM.
- **[Q04] Lesión de Manguito Rotador**: `Recall@3 = 1.00`, `MRR = 1.00`, `Safety: OK`. Detectó restricción de Press de Banca Plano Agarre Ancho.

### B. Biomecánica y Seguridad (`Biomechanics & Safety`)
- **[Q05] Alineación Articular en Sentadilla**: `Recall@3 = 1.00`, `MRR = 0.50`.
- **[Q06] Criterios de Selección (NSCA / ISB)**: `Recall@3 = 1.00`, `MRR = 0.50`.

### C. Hipertrofia y Periodización (`Hypertrophy & Periodization`)
- **[Q07] Mecanismos de Hipertrofia**: `Recall@3 = 1.00`, `MRR = 1.00`.

---

## 🚀 5. Propuestas Concretas de Mejora para Sprint 2

1. **Optimización de Granularidad en Chunking**:
   - Actualmente, toda la matriz de sustitución médica está concentrada en un único chunk amplio (`medical_adaptations.md#2...`). Se recomienda segmentar por patología individual para incrementar `Precision@K`.
2. **Re-Ranking Híbrido (BM25 + Dense Vectors)**:
   - Incorporar un paso de re-ordenamiento (*Re-ranker*) combinando búsqueda por palabra clave exacta y similitud vectorial densa.
3. **Resaltado de Alertas de Seguridad en el Prompt**:
   - Forzar en el sistema de prompts del backend que cualquier respuesta médica incluya una sección explícita de `⚠️ Ejercicios Contraindicados` y `✅ Sustitutos Recomendados`.
