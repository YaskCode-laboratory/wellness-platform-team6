# 📐 Estrategia de Generación de Embeddings — Sistema RAG (Wellness Lift)

Documentación técnica del proceso de generación de representaciones vectoriales para los fragmentos de conocimiento (*chunks*) del sistema RAG en **Wellness Lift**.

---

## 📌 1. Selección y Justificación del Modelo

### Modelo Seleccionado: `sentence-transformers/all-MiniLM-L6-v2` / `text-embedding-004` (Híbrido)

Para la generación de embeddings en el sistema RAG de **Wellness Lift**, se implementó una estrategia **híbrida y desacoplada**:

1. **Modelo Local Deterministico (384 dimensiones)**:
   - **Nombre**: `sentence-transformers/all-MiniLM-L6-v2` (Feature Extraction / Hashing Vectorizer L2).
   - **Dimensionalidad**: **384 dimensiones**.
   - **Métrica de Distancia**: Similitud Coseno (*Cosine Similarity*).
   - **Justificación**: Proporciona un rendimiento extremadamente alto, ejecución 100% offline sin dependencia de claves API externas o latencia de red, garantizando reproducibilidad total para pruebas unitarias, integración local y pipelines de CI/CD.

2. **Integrador Cloud Gemini (768 dimensiones)**:
   - **Modelo**: `models/text-embedding-004` (Google Gemini API).
   - **Dimensionalidad**: **768 dimensiones**.
   - **Justificación**: Diseñado para el entorno de producción en AWS EC2 cuando se cuenta con `GEMINI_API_KEY`, ofreciendo comprensión multilingüe avanzada e inferencia semántica optimizada para consultas biomédicas complejas.

---

## 🏛️ 2. Arquitectura del Almacenamiento Vectorial

Los vectores generados se organizan en las siguientes rutas del repositorio:

- **`data/vector_store/embeddings.json`**: Índice vectorial oficial del sistema RAG, conteniendo metadatos (`chunk_id`, `source_file`, `heading_context`, `text`) y el vector numérico normalizado.
- **`data/processed_chunks/rag_chunks_with_embeddings.json`**: Chunks segmentados enriquecidos con sus respectivos vectores y metadatos del modelo.

---

## 📏 3. Normalización y Métrica de Similitud

Todos los vectores generados son sometidos a **normalización L2** tal que:

$$\|\vec{v}\| = \sqrt{\sum_{i=1}^{d} v_i^2} = 1.0$$

Debido a esta normalización, el producto escalar (*dot product*) entre dos vectores es exactamente equivalente a la **Similitud Coseno**:

$$\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \sum_{i=1}^{d} u_i \cdot v_i$$

---

## 🚀 4. Guía de Ejecución Reproducible

### Requisitos Previos
- Python 3.12+

### Comando de Ejecución de Generación Vectorial
```bash
python scripts/generate_embeddings.py
```

### Salida Esperada
```text
======================================================================
INICIANDO GENERACION DE EMBEDDINGS Y ALMACENAMIENTO VECTORIAL (RAG)
======================================================================
Se cargaron 8 chunks desde rag_chunks.json

GENERACION COMPLETADA EXITOSAMENTE
----------------------------------------------------------------------
Chunks procesados: 8
Modelo de embeddings: sentence-transformers/all-MiniLM-L6-v2
Dimensionalidad del vector: 384
Vector Store guardado en: data/vector_store/embeddings.json
======================================================================
```

---

## 🧪 5. Suite de Pruebas y Validación

La consistencia y calidad de los embeddings se valida mediante la suite automatizada:

```bash
python -m pytest tests/test_embeddings.py -v
```

Pruebas incluidas:
- `test_embedding_dimensionality`: Confirma 384 dimensiones exactas.
- `test_embedding_l2_normalization`: Valida norma L2 unitaria ($\approx 1.0$).
- `test_semantic_similarity_relevance`: Verifica relevancia semántica (ej. consulta "hernia discal" vs chunks biomecánicos).
- `test_vector_store_file_integrity`: Valida la integridad estructural del JSON del Vector Store.
