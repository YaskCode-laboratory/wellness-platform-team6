# 📜 Registro de Decisiones de Arquitectura (ADR) — Sistema RAG (Wellness Lift)

**Estado**: Aceptado  
**Fecha**: 27 de agosto de 2026  
**Autores**: Equipo 6 (Maestría en TIC — Proyecto Laboratorio de Computación)

---

## 📌 ADR-001: Estrategia de Embeddings Híbrida (Local 384-dim + Cloud Gemini 768-dim)

### Contexto
El sistema RAG requiere convertir textos biomédicos y guías de entrenamiento en vectores numéricos. Se necesitaba garantizar que el proyecto se pudiera ejecutar de manera 100% reproducible y offline en entornos de desarrollo local y CI/CD sin depender de claves de API externas, manteniendo al mismo tiempo compatibilidad con modelos Cloud de alta gama para producción en AWS EC2.

### Decisión
Adoptar una arquitectura de embeddings desacoplada en dos capas:
1. **Modelo Local Deterministico (`sentence-transformers/all-MiniLM-L6-v2`)**: Genera vectores de 384 dimensiones con normalización $L2$ sin necesidad de cuotas o llamadas a APIs externas.
2. **Integrador Cloud Gemini (`models/text-embedding-004`)**: Genera vectores de 768 dimensiones cuando `GEMINI_API_KEY` está presente.

### Consecuencias
- ✅ **Positivas**: Pruebas unitarias e integración en CI/CD instantáneas, deterministas y 100% reproducibles offline.
- ⚠️ **Neutrales**: El Vector Store almacena vectores de 384 dimensiones por defecto en el repositorio local.

---

## 📌 ADR-002: Chunking Semántico en Markdown con Ventana Deslizante (512 Tokens / 64 Overlap)

### Contexto
Los documentos de conocimiento (`docs/rag_knowledge_base/`) están estructurados en Markdown con tablas complejas y listas jerárquicas. Una fragmentación arbitraria por caracteres rompería las tablas de sustitución por lesiones médicas.

### Decisión
Implementar la clase `MarkdownSemanticChunker` en [`src/backend/app/rag_chunker.py`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/src/backend/app/rag_chunker.py) que:
- Respeta los bloques semánticos delimitados por encabezados Markdown (`#`, `##`, `###`).
- Aplica una ventana deslizante con un tamaño de chunk de **512 tokens** y **64 tokens de solapamiento** (*sliding window overlap*).

### Consecuencias
- ✅ **Positivas**: Las tablas médicas y explicaciones biomecánicas se conservan íntegras en bloques semánticos coherentes.
- ⚠️ **Neutrales**: El número total de chunks generados para la base de conocimiento actual es de 8 chunks altamente condensados.

---

## 📌 ADR-003: Métrica de Similitud Coseno con Normalización L2 Vectorial

### Contexto
Para recuperar los fragmentos de conocimiento más relevantes en tiempo de ejecución ante la consulta de un atleta o entrenador, se requiere una métrica de distancia vectorial eficiente y matemáticamente robusta.

### Decisión
Establecer la **Similitud Coseno** (*Cosine Similarity*) como la métrica de distancia estándar, forzando la normalización $L2$ en todos los vectores generados tal que $\|\vec{v}\| = 1.0$.

$$\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \sum_{i=1}^{d} u_i \cdot v_i$$

### Consecuencias
- ✅ **Positivas**: Permite realizar búsquedas vectoriales por producto escalar directo en $\mathcal{O}(d)$, reduciendo la latencia de inferencia en el backend FastAPI.
