# 🏆 Informe Ejecutivo Sprint 1 — Sistema RAG (Wellness Lift)

**Proyecto**: Wellness Lift SaaS Platform (Equipo 6)  
**Maestría en TIC (2026-I) — Laboratorio de Computación**  
**Fecha de Evaluación**: 27 de agosto de 2026 (Actualizado: 8 de septiembre de 2026)

---

## 📌 1. Resumen Ejecutivo del Sprint 1

Durante el Sprint 1 se implementaron exitosamente los componentes centrales de la arquitectura de Recuperación Aumentada por Generación (*RAG*) para el sistema **Wellness Lift**:

1. **Base de Conocimiento de Dominio (S1-01 / PR #27)**: Curación y estructuración en Markdown de guías científicas sobre biomecánica, periodización de hipertrofia y adaptaciones médicas.
2. **Estrategia de Chunking Semántico (S1-02 / PR #28)**: Algoritmo de ventana deslizante con solapamiento (*Sliding Window Overlap*).
3. **Generación de Embeddings y Vector Store (S1-03 / S1-04 / PR #30)**: Vectorizador determinista local (384-dim, normalización L2) e índice de almacenamiento vectorial.
4. **Pipeline RAG Retriever (S1-05 / PR #31)**: Motor de recuperación Top-K basado en similitud coseno.
5. **Evaluación de Recuperación y Calidad (S1-06 / PR #32)**: Suite de benchmarking automatizado con métricas Precision@K, Recall@K, MRR y Precisión en Seguridad Médica (cobertura en chunks).

---

## 📊 2. Resumen de Métricas de Evaluación Reproducibles

| Métrica Evaluada | Resultado Obtenido | Estado / Cumplimiento |
| :--- | :--- | :--- |
| **Precision@3 Promedio** | **30.00%** | ✅ Supera umbral ($\ge 20\%$) |
| **Recall@3 Promedio** | **90.00%** | ✅ Supera ampliamente umbral ($\ge 65\%$) |
| **MRR (Mean Reciprocal Rank)** | **0.7000** | ✅ Supera umbral ($\ge 0.45$) |
| **Precisión en Seguridad Médica** | **100.00%** | ✅ Cobertura completa de contraindicaciones y sustitutos ($4/4$ casos médicos) |
| **Pruebas Automatizadas (Pytest)** | **11 / 11 PASSED** | ✅ 100% de éxito en suites de embeddings y evaluación |

---

## 🎯 3. Casos de Éxito y Limitaciones Identificadas

### ✅ Casos Exitosos
- **Consultas Médicas (Q01, Q02, Q03, Q04)**: El motor recupera la matriz de sustitución médica identificando tanto las contraindicaciones como los sustitutos recomendados sin omisiones.
- **Consultas Biomecánicas (Q05, Q06)**: Recuperación efectiva de principios de alineación articular e instituciones científicas de referencia (NSCA / ISB).

### ⚠️ Limitaciones Identificadas
- **Consulta Q07 (Mecanismos de Hipertrofia)**: Requiere mayor alineación léxica para mejorar el ranking semántico cuando se utilizan términos conceptuales aislados.
- **Granularidad Única de Matriz Médica**: Toda la matriz de lesiones se encuentra concentrada en un solo chunk, lo que limita la precisión cuando se requiere especificidad clínica por patología.

---

## 💡 4. Plan de Acción Recomendado para el Sprint 2

1. **Split de Chunks por Lesión Específica**: Dividir la matriz médica en sub-chunks orientados a cada condición clínica.
2. **Implementación de Híbrido Sparse-Dense Retriever**: Combinar BM25 con similitud coseno densa para maximizar la recuperación.
3. **Integración al Pipeline de Inferencia del Agente IA**: Conectar la recuperación del Vector Store directamente con el endpoint `/api/v1/chat` en FastAPI.
