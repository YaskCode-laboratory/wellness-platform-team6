# Estrategia de Generacion de Embeddings - Sistema RAG (Wellness Lift)

Documentacion tecnica del proceso de generacion de representaciones vectoriales para los fragmentos de conocimiento (chunks) del sistema RAG en Wellness Lift, correspondiente a la tarea [S1-03 - Generacion de embeddings] (Issue #7).

---

## 1. Identificacion y Justificacion del Mecanismo de Embeddings

Para garantizar la maxima transparencia, reproducibilidad y eficiencia en el ciclo de vida del sistema RAG, se implemento una estrategia desacoplada con trazabilidad explicita:

### A. Mecanismo Local Determinista: local-deterministic-hashing-384d (Seleccionado por Defecto)
- **Identificador de Modelo:** local-deterministic-hashing-384d
- **Dimensionalidad:** **384 dimensiones** (384 floats).
- **Mecanismo Real:** Proyeccion espacial mediante hashing criptografico **SHA-256** con ponderacion logaritmica de longitud de terminos y descomposicion posicional de n-gramas.
- **Normalizacion Euclidiana:** Normalizacion L2 estricta (||v|| = 1.0), permitiendo que el producto escalar sea equivalente a la Similitud Coseno.
- **Garantia de Reproducibilidad Inter-Procesos:** Al utilizar hashlib.sha256 en lugar de la funcion interna hash() de Python, se eliminan variaciones por aleatoriedad de semilla (PYTHONHASHSEED), garantizando vectores **100% identicos** entre diferentes entornos, ejecuciones y plataformas.
- **Justificacion de Uso:** Permite una ejecucion 100% offline sin necesidad de descargar modelos pesados en entornos de integracion continua (CI/CD) o depender de cuotas de red.

### B. Integrador Cloud: models/text-embedding-004 (Opcional en Produccion)
- **Identificador de Modelo:** models/text-embedding-004 (Google Gemini API).
- **Dimensionalidad:** **768 dimensiones**.
- **Justificacion:** Se activa de forma transparente cuando se configura la variable de entorno GEMINI_API_KEY, ofreciendo inferencia densa basada en transformers para produccion.

---

## 2. Arquitectura del Almacenamiento Vectorial

Los vectores generados se organizan y persisten en las siguientes rutas del repositorio:

- **data/vector_store/embeddings.json**: Indice vectorial oficial del sistema RAG, conteniendo metadatos (	otal_chunks, embedding_model, ector_dimension) y la lista de vectores numericos asociados a cada chunk_id.
- **data/processed_chunks/rag_chunks_with_embeddings.json**: Chunks segmentados enriquecidos con sus respectivos vectores y metadatos de trazabilidad.

---

## 3. Normalizacion y Metrica de Similitud Coseno

Todos los vectores generados son sometidos a **normalizacion L2** tal que:

\|\vec{v}\|_2 = \sqrt{\sum_{i=1}^{d} v_i^2} = 1.0

Gracias a esta normalizacion, la **Similitud Coseno** entre una consulta $\vec{u}$ y un chunk $\vec{v}$ se evalua directamente como:

\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \sum_{i=1}^{d} u_i \cdot v_i

---

## 4. Guia de Ejecucion Reproducible

### Requisitos Previos
- Python 3.12+

### Comando de Ejecucion de Generacion Vectorial
`ash
python scripts/generate_embeddings.py
`

### Salida Esperada
`	ext
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
`

---

## 5. Suite de Pruebas Automatizadas

La consistencia matematica y la trazabilidad de los embeddings se valida mediante la suite automatizada:

`ash
python -m unittest tests/test_embeddings.py
`

### Pruebas Incluidas (	ests/test_embeddings.py):
1. 	est_embedding_dimensionality: Confirma 384 dimensiones exactas y metadatos del modelo (local-deterministic-hashing-384d).
2. 	est_embedding_l2_normalization: Valida norma L2 unitaria (~1.0).
3. 	est_deterministic_reproducibility: Valida que dos ejecuciones separadas produzcan exactamente el mismo vector numerico (determinismo SHA-256).
4. 	est_empty_text_embedding: Verifica el manejo seguro de entradas vacias (vector nulo de 384 ceros).
5. 	est_cosine_similarity_identical_vectors: Valida que la similitud de vectores identicos sea 1.0.
6. 	est_semantic_similarity_relevance: Comprueba que una consulta de 'hernia discal' obtenga mayor similitud con el chunk de hernia discal que con un chunk de periodizacion.
7. 	est_vector_store_file_integrity: Valida el esquema JSON, dimensiones y metadatos de data/vector_store/embeddings.json.
