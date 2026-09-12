# Estrategia de Generación de Representaciones Vectoriales — Sistema RAG (Wellness Lift)

Documentación técnica del proceso de generación de representaciones vectoriales para los fragmentos de conocimiento (chunks) del sistema RAG en Wellness Lift, correspondiente a la tarea **[S1-03 - Generación de embeddings] (Issue #7)**.

---

## 1. Identificación y Justificación del Mecanismo de Representación Vectorial

Para garantizar la máxima transparencia, reproducibilidad y eficiencia en el ciclo de vida del sistema RAG, se implementó una estrategia desacoplada con trazabilidad explícita:

### A. Mecanismo Local Determinista: local-deterministic-hashing-384d (Seleccionado por Defecto)
- **Identificador:** `local-deterministic-hashing-384d`
- **Dimensionalidad:** **384 dimensiones** (384 floats).
- **Mecanismo Real:** Representación vectorial determinista mediante proyección espacial por hashing criptográfico **SHA-256**, con ponderación logarítmica de longitud de términos y descomposición posicional de n-gramas.
- **Normalización Euclidiana:** Normalización L2 estricta ($\|\mathbf{v}\|_2 = 1.0$), permitiendo que el producto escalar sea equivalente a la Similitud Coseno.
- **Garantía de Reproducibilidad Inter-Procesos:** Al utilizar `hashlib.sha256` en lugar de la función interna `hash()` de Python, se eliminan variaciones por aleatoriedad de semilla (`PYTHONHASHSEED`), garantizando vectores **100% idénticos** entre diferentes entornos, ejecuciones y plataformas.
- **Alcance Técnico:** Genera representaciones vectoriales deterministas que permiten calcular similitud coseno para comparar textos con términos relacionados, operando de manera 100% offline y sin requerir pesos de transformers ni cuotas de red.

### B. Integrador Cloud: models/text-embedding-004 (Opcional en Producción)
- **Identificador de Modelo:** `models/text-embedding-004` (Google Gemini API).
- **Dimensionalidad:** **768 dimensiones**.
- **Justificación:** Se activa de forma transparente cuando se configura la variable de entorno `GEMINI_API_KEY`, ofreciendo inferencia densa basada en transformers para producción.

---

## 2. Arquitectura del Almacenamiento Vectorial

Los vectores generados se organizan y persisten en las siguientes rutas del repositorio:

- **`data/vector_store/embeddings.json`**: Índice vectorial oficial del sistema RAG, conteniendo metadatos (`total_chunks`, `embedding_model`, `vector_dimension`) y la lista de vectores numéricos asociados a cada `chunk_id`.
- **`data/processed_chunks/rag_chunks_with_embeddings.json`**: Chunks segmentados enriquecidos con sus respectivos vectores y metadatos de trazabilidad.

---

## 3. Normalización y Métrica de Similitud Coseno entre Representaciones

Todos los vectores generados son sometidos a **normalización L2** tal que:

$$\|\vec{v}\|_2 = \sqrt{\sum_{i=1}^{d} v_i^2} = 1.0$$

Gracias a esta normalización, la **Similitud Coseno** entre una consulta $\vec{u}$ y un chunk $\vec{v}$ se evalúa directamente como:

$$\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \sum_{i=1}^{d} u_i \cdot v_i$$

---

## 4. Guía de Ejecución Reproducible

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
Modelo de embeddings: local-deterministic-hashing-384d
Dimensionalidad del vector: 384
Vector Store guardado en: data/vector_store/embeddings.json
Chunks enriquecidos en: data/processed_chunks/rag_chunks_with_embeddings.json
======================================================================
```

---

## 5. Suite de Pruebas Automatizadas

La consistencia matemática y la trazabilidad de las representaciones vectoriales se valida mediante la suite automatizada:

```bash
python -m unittest tests/test_embeddings.py
```

### Pruebas Incluidas (`tests/test_embeddings.py`):
1. `test_embedding_dimensionality`: Confirma 384 dimensiones exactas y metadatos del modelo (`local-deterministic-hashing-384d`).
2. `test_embedding_l2_normalization`: Valida norma L2 unitaria (~1.0).
3. `test_deterministic_reproducibility`: Valida que dos ejecuciones separadas produzcan exactamente el mismo vector numérico (determinismo SHA-256).
4. `test_empty_text_embedding`: Verifica el manejo seguro de entradas vacías (vector nulo de 384 ceros).
5. `test_cosine_similarity_identical_vectors`: Valida que la similitud de vectores idénticos sea 1.0.
6. `test_vector_similarity_relevance`: Comprueba la relevancia basada en la representación local (mayor similitud coseno entre consulta de hernia discal y chunk temáticamente afín vs. periodización).
7. `test_vector_store_file_integrity`: Valida el esquema JSON, dimensiones y metadatos de `data/vector_store/embeddings.json`.

