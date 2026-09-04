# 🗄️ Motor RAG y Base de Conocimiento — Wellness Lift

## 1. Introducción al Sistema RAG
El sistema de **Generación Aumentada por Recuperación (RAG)** de Wellness Lift permite al agente responder preguntas biomecánicas y deportivas fundamentándose exclusivamente en documentos de investigación validados, eliminando alucinaciones.

---

## 2. Estructura de la Base de Conocimiento
Los documentos están organizados en `docs/rag_knowledge_base/`:

- **`biomechanics_and_safety.md`**: Principios de alineación articular, vectores de fuerza, rango de movimiento (ROM) y prevención de valgo de rodilla o guiño de cadera (*butt wink*).
- **`hypertrophy_periodization.md`**: Ciencia de la hipertrofia, tensión mecánica, estrés metabólico, volumen por grupo muscular y autorregulación (RPE/RIR).
- **`medical_adaptations.md`**: Matriz completa de contraindicaciones médicas (Hernias discales, lesiones de menisco, pinzamiento subacromial) y tabla de ejercicios sustitutos seguros.

---

## 3. Estrategia de Segmentación Semántica (*Chunking*)
- **Enfoque**: Híbrido Semántico-Markdown con Ventana Deslizante.
- **Tamaño de Chunk (`chunk_size`)**: `512 tokens` (~350-400 palabras). Preserva tablas y bloques jerárquicos completos.
- **Solapamiento (`chunk_overlap`)**: `64 tokens` (~12.5%). Mantiene la continuidad entre bloques adyacentes.

---

## 4. Motor de Base de Datos Vectorial
- **Clase Principal**: `VectorDatabaseStore` (`src/backend/app/vector_store.py`).
- **Métrica de Similitud**: Similitud del Coseno (*Cosine Similarity*) sobre vectores TF-IDF con ponderación L2.
- **Persistencia**: Serialización JSON en `data/vector_store/vector_index.json`.
- **Rendimiento**: Búsquedas sub-milisegundo sin requerir bases vectoriales en contenedores externos.
