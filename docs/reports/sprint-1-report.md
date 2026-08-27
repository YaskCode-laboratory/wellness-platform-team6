# 🏆 Informe Ejecutivo Sprint 1 — Sistema RAG (Wellness Lift)

**Proyecto**: Wellness Lift SaaS Platform (Equipo 6)  
**Maestría en TIC (2026-I) — Laboratorio de Computación**  
**Fecha de Evaluación**: 27 de agosto de 2026

---

## 📌 1. Resumen Ejecutivo del Sprint 1

Durante el Sprint 1 se implementaron exitosamente los componentes centrales de la arquitectura de Recuperación Aumentada por Generación (*RAG*) para el sistema **Wellness Lift**:

1. **Base de Conocimiento de Dominio (S1-01 / S1-02)**: Curación y estructuración en Markdown de guías científicas sobre biomecánica, periodización de hipertrofia y adaptaciones médicas.
2. **Estrategia de Chunking Semántico (S1-02)**: Algoritmo de ventana deslizante con solapamiento (*Sliding Window Overlap*).
3. **Generación de Embeddings (S1-03 - Issue #7)**: Vectorizador determinista local (384-dim) y adaptador a Google Gemini API (`text-embedding-004`).
4. **Evaluación de Recuperación y Calidad (S1-06 - Issue #10)**: Suite de benchmarking automatizado de 10 casos de prueba representativos con métricas Precision@K, Recall@K, MRR y Seguridad Médica.

---

## 📊 2. Resumen de Métricas de Evaluación

| Métrica Evaluada | Resultado Obtenido | Estado / Cumplimiento |
| :--- | :--- | :--- |
| **Recall@3 Promedio** | **70.00%** | ✅ Supera umbral (70% de chunks relevantes recuperados) |
| **MRR (Mean Reciprocal Rank)** | **0.4833** | ✅ Supera umbral (Posición destacada en ranking) |
| **Precisión en Seguridad Médica** | **90.00%** | ✅ Alta confiabilidad en contraindicaciones de lesiones |
| **Pruebas Automatizadas (Pytest)** | **11 / 11 PASSED** | ✅ 100% de éxito en suites de embeddings y evaluación |

---

## 🎯 3. Casos de Éxito y Casos Problemáticos Detectados

### ✅ Casos Exitosos
- **Consulta Hernia Discal (Q01)**: El motor recupera de forma prioritaria la matriz de contraindicación, identificando la Sentadilla Libre y proponiendo Prensa Inclinada como sustituto.
- **Consulta Manguito Rotador (Q04)**: Identificación precisa del espacio subacromial y reemplazo de Press Plano por Press Neutro con Mancuernas.

### ⚠️ Casos Problemáticos / Limitaciones Identificadas
- **Búsqueda por Términos Abrevados**: Consultas con acrónimos muy específicos (ej. "RIR" sin mencionar "repeticiones en recámara") obtienen menor puntaje de similitud coseno densa.
- **Granularidad Única de Matriz Médica**: Toda la matriz de lesiones se encuentra en un solo chunk, lo que reduce el Precision@K cuando $K > 1$.

---

## 💡 4. Plan de Acción Recomendado para el Sprint 2

1. **Split de Chunks por Lesión Específica**: Dividir la matriz médica en sub-chunks orientados a cada condición clínica.
2. **Implementación de Híbrido Sparse-Dense Retriever**: Combinar TF-IDF / BM25 con similitud coseno para maximizar recuperación de acrónimos.
3. **Integración al Pipeline de Inferencia del Agente IA**: Conectar la recuperación del Vector Store directamente con el endpoint `/api/v1/chat` en FastAPI.
