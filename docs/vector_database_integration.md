# 🗄️ Integración de Base de Datos Vectorial — Wellness Lift (Issue #8)

## 1. Resumen Ejecutivo
Este documento especifica la integración, indexación, persistencia y recuperación por similitud vectorial de la **Base de Datos Vectorial** implementada para el motor RAG de la plataforma **Wellness Lift**, en cumplimiento directo del requerimiento **[S1-04 - Integrar base de datos vectorial] (Issue #8)** y su integración con las representaciones vectoriales generadas en **[S1-03 - Generación de embeddings] (Issue #7)**.

---

## 2. Selección de la Tecnología y Arquitectura Vectorial

Se implementó el motor vectorial **In-Memory Dense Cosine Vector Database Store** (`src/backend/app/vector_store.py`):
- **Representación Vectorial Principal**: Vectores densos de **384 dimensiones** generados por `EmbeddingsGenerator` (`local-deterministic-hashing-384d` con SHA-256 y normalización $L_2$, o Gemini `text-embedding-004`).
- **Motor de Búsqueda Vectorial**: Similitud del Coseno (*Cosine Similarity*) sobre las representaciones vectoriales de 384d:
  $$\text{sim}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \|\mathbf{d}\|_2}$$
- **Mecanismo Baseline / Respaldo**: Soporte alternativo para vectores ralos TF-IDF normalizados $L_2$, disponible mediante el parámetro `mode="tfidf"`, utilizado con propósitos comparativos y de auditoría.
- **Indexación y Persistencia**: Serialización determinista en formato JSON estructurado (`data/vector_store/vector_index.json`).
- **Soporte de Ingesta Dual S1-03**: Carga nativa desde `data/processed_chunks/rag_chunks_with_embeddings.json` y fallback compatible con la estructura `metadata -> vectors` de `data/vector_store/embeddings.json`.
- **Trazabilidad Integral**: Conserva la relación directa:
  $$\text{chunk\_id} \longrightarrow \text{embedding (384d)} \longrightarrow \text{vector\_store (índice)}$$

---

## 3. Diagrama de Flujo del Pipeline RAG Integrado

```
[Documentos RAG (.md)] (S1-01)
         │
         ▼
[Chunking Híbrido Markdown] (S1-02) ──> data/processed_chunks/rag_chunks.json
         │
         ▼
[EmbeddingsGenerator (384d)] (S1-03) ──> data/processed_chunks/rag_chunks_with_embeddings.json
         │                                (o data/vector_store/embeddings.json)
         ▼
[VectorDatabaseStore] (S1-04) ───────> data/vector_store/vector_index.json
         │
         ├─────────────────────────────────────────┐
         │ (Modo Principal: Dense 384d)             │ (Modo Baseline: TF-IDF)
         ▼                                         ▼
[Consulta Atleta] ──> [Query Vector (384d)] ────> [Similitud Coseno] ──> [Top-K Chunks Relevantes]
```

---

## 4. Pruebas de Recuperación por Similitud Vectorial

Se ejecutaron consultas de prueba en `scripts/index_vector_store.py` sobre los 8 chunks del corpus científico:

| # | Consulta | Chunk Top-1 Recuperado | Similitud Coseno (384d) | Baseline TF-IDF |
|---|----------|------------------------|-------------------------|-----------------|
| 1 | *"¿Qué ejercicios debo reemplazar si tengo hernia discal lumbar L4-L5?"* | `medical_adaptations.md#2._matriz_de_sustitución_por_lesión_/_condición-0` | **0.2252** | 0.1519 |
| 2 | *"¿Cómo se aplica el principio de sobrecarga progresiva e hipertrofia?"* | `hypertrophy_periodization.md#2._mecanismos_de_hipertrofia-0` | **0.3398** | 0.1245 |
| 3 | *"Alineación articular y prevención de valgo de rodilla en sentadilla"* | `biomechanics_and_safety.md#2._principios_biomecánicos_fundamentales-0` | **0.5137** | 0.2926 |

---

## 5. Verificación Automatizada

La suite de pruebas unitarias en `tests/test_vector_store.py` valida:
1. `test_indexing_dense_embeddings`: Integración dimensional y metadatos de vectores de 384d.
2. `test_direct_s103_embeddings_preservation`: Preservación exacta de representaciones precalculadas en S1-03 sin recalcular.
3. `test_fallback_embeddings_json_structure_compatibility`: Compatibilidad de ingesta con la estructura `metadata -> vectors` de `embeddings.json`.
4. `test_dense_similarity_search_retrieval`: Recuperación Top-1 por similitud coseno sobre representaciones vectoriales densas.
5. `test_dense_similarity_search_rodilla`: Recuperación de adaptaciones articulares de rodilla.
6. `test_vector_query_search`: Búsqueda directa pasando vectores numéricos `List[float]`.
7. `test_baseline_tfidf_search`: Operación correcta del motor baseline TF-IDF.
8. `test_save_and_load_index`: Serialización y deserialización sin pérdida de precisión.
9. `test_persisted_vector_index_integrity`: Integridad estructural de `data/vector_store/vector_index.json`.

```bash
python -m unittest tests/test_vector_store.py
# Ran 9 tests in 0.040s - OK
```
