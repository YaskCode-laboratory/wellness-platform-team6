# 📜 Registro de Decisiones de Arquitectura (ADR) — Sistema RAG (Wellness Lift)

**Estado**: Aceptado  
**Fecha**: 27 de agosto de 2026 (Actualizado: 8 de septiembre de 2026)  
**Autores**: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## 📌 ADR-001: Estrategia de Embeddings Híbrida (Local Deterministico 384-dim + Cloud Gemini 768-dim)

### Contexto
El sistema RAG requiere convertir textos biomédicos y guías de entrenamiento en vectores numéricos. Se necesitaba garantizar que el proyecto se pudiera ejecutar de manera 100% reproducible y offline en entornos de desarrollo local y CI/CD sin depender de claves de API externas ni inferencias pesadas de PyTorch, manteniendo al mismo tiempo compatibilidad con modelos Cloud para producción.

### Decisión
Adoptar una arquitectura de embeddings desacoplada en dos capas:
1. **Generador Local Determinístico (`EmbeddingsGenerator`)**: Genera vectores de 384 dimensiones mediante hashing determinista basado en SHA-256 y normalización $L2$, identificado como `local-deterministic-hashing-384d`, sin necesidad de cuotas o llamadas a APIs externas.
2. **Integrador Cloud Gemini (`models/text-embedding-004`)**: Genera vectores densos de 768 dimensiones cuando `GEMINI_API_KEY` está presente.

### Consecuencias
- ✅ **Positivas**: Pruebas unitarias e integración en CI/CD instantáneas, deterministas y 100% reproducibles offline.
- ⚠️ **Neutrales**: El generador local utiliza la representación determinista de 384 dimensiones `local-deterministic-hashing-384d` para garantizar reproducibilidad exacta y cero costo de API en ejecuciones locales.

---

## 📌 ADR-002: Chunking Semántico en Markdown con Ventana Deslizante (512 Tokens / 64 Overlap)

### Contexto
Los documentos de conocimiento (`data/knowledge_base/`) están estructurados en Markdown con tablas complejas y listas jerárquicas. Una fragmentación arbitraria por caracteres rompería las tablas de sustitución por lesiones médicas.

### Decisión
Implementar la clase `MarkdownSemanticChunker` en [`src/backend/app/rag_chunker.py`](../../../src/backend/app/rag_chunker.py) que:
- Respeta los bloques semánticos delimitados por encabezados Markdown (`#`, `##`, `###`).
- Aplica una ventana deslizante con un tamaño de chunk de **512 tokens** y **64 tokens de solapamiento** (*sliding window overlap*).

### Consecuencias
- ✅ **Positivas**: Las tablas médicas y explicaciones biomecánicas se conservan íntegras en bloques semánticos coherentes.
- ⚠️ **Neutrales**: El número total de chunks generados para la base de conocimiento actual es de 8 chunks condensados.

---

## 📌 ADR-003: Métrica de Similitud Coseno con Normalización L2 Vectorial

### Contexto
Para recuperar los fragmentos de conocimiento más relevantes en tiempo de ejecución ante la consulta de un atleta o entrenador, se requiere una métrica de distancia vectorial eficiente y matemáticamente robusta.

### Decisión
Establecer la **Similitud Coseno** (*Cosine Similarity*) como la métrica de distancia estándar, forzando la normalización $L2$ en todos los vectores generados tal que $\|\vec{v}\| = 1.0$.

$$\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \sum_{i=1}^{d} u_i \cdot v_i$$

### Consecuencias
- ✅ **Positivas**: Permite realizar búsquedas vectoriales por producto escalar directo en $\mathcal{O}(d)$, reduciendo la latencia de inferencia en `VectorDatabaseStore` y `RAGPipeline`.
