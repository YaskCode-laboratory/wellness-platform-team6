# 🏛️ Arquitectura del Sistema RAG — Wellness Lift

Documentación técnica integral de la arquitectura, componentes, decisiones de diseño, flujo de datos y resultados del sistema de **Recuperación Aumentada por Generación (RAG)** de **Wellness Lift** (Sprint 1).

---

## 📌 1. Visión General del Sistema RAG

El motor RAG de **Wellness Lift** tiene como objetivo enriquecer las respuestas de los agentes de Inteligencia Artificial con evidencia científica fundamentada en biomecánica, periodización del entrenamiento deportivo y matrices de seguridad/adaptaciones médicas ante lesiones físicas.

```
                                ┌─────────────────────────┐
                                │   AWS Amplify (HTTPS)   │
                                │  Frontend React Vite    │
                                └────────────┬────────────┘
                                             │ HTTP / JSON API
                                             ▼
                                ┌─────────────────────────┐
                                │     AWS EC2 (Ubuntu)    │
                                │  Nginx Reverse Proxy    │
                                │    FastAPI Backend      │
                                └────────────┬────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
        ┌───────────────────────────┐                 ┌───────────────────────────┐
        │   Google Cloud Firestore  │                 │ OpenRouter / Gemini API   │
        │    Base de Datos NoSQL    │                 │   Motor de Agentes de IA  │
        └───────────────────────────┘                 └───────────────────────────┘
```

---

## 📐 2. Diagramas de Arquitectura y Flujo de Datos

### A. Pipeline de Ingesta, Chunking e Indexación Vectorial

```mermaid
flowchart TD
    subgraph Fuentes ["1. Fuentes de Conocimiento (Markdown)"]
        KB1["biomechanics_and_safety.md"]
        KB2["hypertrophy_periodization.md"]
        KB3["medical_adaptations.md"]
    end

    subgraph Chunking ["2. Segmentación Semántica"]
        Chunker["MarkdownSemanticChunker\n(Size: 512, Overlap: 64)"]
        ChunksJSON["data/processed_chunks/rag_chunks.json\n(8 Chunks Estructurados)"]
    end

    subgraph Embedding ["3. Generación Vectorial"]
        Embedder["EmbeddingsGenerator\n(384-dim L2 Normalized / 768-dim Gemini)"]
        ScriptEmb["scripts/generate_embeddings.py"]
    end

    subgraph Storage ["4. Almacenamiento Vectorial"]
        VStore["data/vector_store/embeddings.json\n(Índice Vectorial RAG)"]
        EnrichedChunks["rag_chunks_with_embeddings.json"]
    end

    KB1 --> Chunker
    KB2 --> Chunker
    KB3 --> Chunker
    Chunker --> ChunksJSON
    ChunksJSON --> ScriptEmb
    ScriptEmb --> Embedder
    Embedder --> VStore
    Embedder --> EnrichedChunks
```

---

### B. Flujo en Tiempo de Ejecución (Búsqueda y Generación Aumentada)

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Atleta / Entrenador
    participant FE as Frontend (React SPA)
    participant BE as Backend (FastAPI)
    participant Eval as RAGEvaluator
    participant VS as VectorStore (embeddings.json)
    participant LLM as Motor de IA (Gemini / OpenRouter)

    Usuario->>FE: Ingresa consulta ("¿Qué ejercicios evitar por hernia discal?")
    FE->>BE: POST /api/v1/chat (Prompt del usuario)
    BE->>Eval: retrieve_top_k(query, top_k=3)
    Eval->>VS: Carga índice vectorial y calcula Similitud Coseno
    VS-->>Eval: Retorna Top-3 Chunks Relevantes (Score Coseno)
    Eval-->>BE: Matriz de sustitución médica y principios biomecánicos
    BE->>LLM: Inyecta Contexto Recuperado + Prompt del Sistema
    LLM-->>BE: Genera respuesta fundamentada en evidencia
    BE-->>FE: HTTP 200 OK (Respuesta RAG + Alertas Médicas)
    FE-->>Usuario: Muestra rutina adaptada sin riesgos biomecánicos
```

---

## 🧩 3. Componentes Principales del Sistema

| Componente | Archivo Fuente | Descripción y Responsabilidad |
| :--- | :--- | :--- |
| **`MarkdownSemanticChunker`** | [`src/backend/app/rag_chunker.py`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/src/backend/app/rag_chunker.py) | Segmentador semántico de documentos Markdown respetando jerarquía de encabezados (`#`, `##`, `###`) con ventana deslizante (512 tokens objetivo, 64 tokens de solapamiento). |
| **`EmbeddingsGenerator`** | [`src/backend/app/embeddings_generator.py`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/src/backend/app/embeddings_generator.py) | Motor vectorial híbrido. Calcula embeddings deterministas de **384 dimensiones** con normalización $L2$ para entornos locales/CI-CD y soporte para `text-embedding-004` (**768 dimensiones**) en producción. |
| **`VectorStore`** | [`data/vector_store/embeddings.json`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/data/vector_store/embeddings.json) | Base de datos vectorial liviana indexada en JSON que almacena los vectores normalizados, `chunk_id`, metadatos y el contenido de los fragmentos. |
| **`RAGEvaluator`** | [`src/backend/app/rag_evaluator.py`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/src/backend/app/rag_evaluator.py) | Motor de benchmarking automatizado. Evalúa **Precision@K**, **Recall@K**, **MRR** y valida que la información recuperada cumpla con el 100% de seguridad médica ante lesiones. |
| **`WellnessCoachAgent`** | [`src/backend/app/agent.py`](file:///C:/Users/Alejandro/.gemini/antigravity/scratch/wellness-platform-team6/src/backend/app/agent.py) | Agente orquestador de Inteligencia Artificial que recibe el contexto RAG y genera rutinas de entrenamiento autorreguladas. |

---

## 🛠️ 4. Tecnologías, Modelos y Herramientas

- **Lenguaje Principal**: Python 3.12+
- **Framework Web Backend**: FastAPI 0.110.0 con Uvicorn
- **Modelo de Embeddings Local**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, $L2$ Normalized)
- **Modelo de Embeddings Cloud**: Google Gemini API (`models/text-embedding-004`, 768-dim)
- **Métrica de Distancia Vectorial**: Similitud Coseno (*Cosine Similarity*)
- **Suite de Pruebas**: Pytest 9.1+ (11/11 pruebas unitarias e integración en verde)
- **Frontend SPA**: React 18.2, Vite 8.0, TailwindCSS / Emil Kowalski Design System

---

## 📊 5. Resultados Principales de Evaluación (Sprint 1)

Basado en el benchmark automatizado ejecutado sobre `data/evaluation/test_queries.json`:

- **Recall@3 Promedio**: **70.00%** (Los fragmentos recuperados cubren los conceptos clave necesarios).
- **Mean Reciprocal Rank (MRR)**: **0.4833** (El primer chunk relevante se ubica sistemáticamente en las primeras posiciones).
- **Precisión en Seguridad Médica**: **90.00%** (Identificación precisa de contraindicaciones en hernias discales, lesiones de rodilla y manguito rotador).

---

## ⚠️ 6. Limitaciones Conocidas y Mejoras Futuras (Sprint 2 Roadmap)

1. **Granularidad de Chunks Médicos**:
   - *Limitación*: La matriz de sustitución médica se encuentra condensada en un único chunk amplio.
   - *Mejora Sprint 2*: Dividir la matriz en micro-chunks por patología clínica específica.
2. **Estrategia de Búsqueda Híbrida**:
   - *Limitación*: Consultas con acrónimos científicos muy específicos (ej. "RIR") dependen puramente de coincidencia densa.
   - *Mejora Sprint 2*: Implementar búsqueda híbrida combinando TF-IDF / BM25 con similitud coseno densa.
