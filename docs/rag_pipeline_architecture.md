# ⚙️ Arquitectura del Pipeline RAG End-to-End — Wellness Lift (Issue #9)

## 1. Resumen Ejecutivo
Este documento describe el flujo completo, los componentes de software, la trazabilidad de la cadena consolidada **S1-03 $\rightarrow$ S1-04 $\rightarrow$ S1-05** y los mecanismos de generación (Live LLM vs. Fallback Determinista) del **Pipeline RAG End-to-End** implementado para la plataforma **Wellness Lift** ([Issue #9](https://github.com/YaskCode-laboratory/wellness-platform-team6/issues/9)).

---

## 2. Diagrama de Secuencia del Pipeline RAG

```mermaid
sequenceDiagram
    autonumber
    actor Usuario as Atleta / Coach
    participant Pipeline as RAGPipeline (src/backend/app/rag_pipeline.py)
    participant Embeddings as EmbeddingsGenerator (S1-03, 384d)
    participant VectorDB as VectorDatabaseStore (S1-04, Cosine Similarity)
    participant LLM as Motor LLM (OpenRouter / Gemini API)
    participant Fallback as Generador Determinista Offline

    Usuario->>Pipeline: run_pipeline(query, user_profile, top_k=2)
    Pipeline->>Embeddings: generate_embedding(query)
    Embeddings-->>Pipeline: Vector denso 384d (normalizado L2)
    Pipeline->>VectorDB: search_similarity(query_vector, k=2, mode="dense")
    VectorDB-->>Pipeline: Top-K Chunks Relevantes + Scores
    Pipeline->>Pipeline: build_augmented_prompt(Contexto + Perfil Atleta)
    
    alt Credenciales LLM Activas (OPENROUTER_API_KEY / GEMINI_API_KEY)
        Pipeline->>LLM: Invocación con Prompt Aumentado
        LLM-->>Pipeline: Respuesta Generada (mode: "openrouter_live" | "gemini_live")
    else Modo Offline / CI / Sin Credenciales
        Pipeline->>Fallback: Síntesis Basada en Evidencia y Reglas Científicas
        Fallback-->>Pipeline: Respuesta Estructurada (mode: "fallback_simulated")
    end

    Pipeline-->>Usuario: Payload RAG Estructurado (Respuesta + Fuentes + Metadatos)
```

---

## 3. Etapas del Pipeline RAG (`src/backend/app/rag_pipeline.py`)

1. **Etapa 1: Ingesta y Vectorización de Consulta (S1-03)**: Transforma la consulta en un vector denso de 384 dimensiones mediante `EmbeddingsGenerator` (`local-deterministic-hashing-384d`).
2. **Etapa 2: Recuperación Semántica en Vector DB (S1-04)**: Consulta `VectorDatabaseStore` (`data/vector_store/vector_index.json`) calculando Similitud del Coseno entre el vector de consulta y los vectores de los chunks indexados.
3. **Etapa 3: Aumento de Contexto (*Context Augmentation*)**: Inyecta el perfil de salud del atleta (ej. *Hernia Discal L4-L5*, nivel de entrenamiento) y los fragmentos científicos recuperados con sus fuentes bibliográficas dentro del prompt estructurado.
4. **Etapa 4: Inferencia y Generación**:
   - **Modo Producción (Live LLM)**: Si `OPENROUTER_API_KEY` o `GEMINI_API_KEY` están configuradas y disponibles, delega la inferencia al modelo externo.
   - **Modo Fallback / Simulado Determinista**: Si no hay conexión o claves de API configuradas, activa un motor determinista estructurado que sintetiza las sustituciones biomecánicas basándose en las directrices de los chunks recuperados, garantizando 100% de reproducibilidad y estabilidad en CI/CD.
5. **Etapa 5: Payload Trazable y Citado de Fuentes**: Retorna un objeto estructurado que incluye:
   - `retrieved_chunks`: Lista de chunks con scores de similitud y metadatos de embeddings.
   - `sources`: Archivos fuente citados (`medical_adaptations.md`, `biomechanics_and_safety.md`, etc.).
   - `generation_mode`: Indicador explícito del modo (`openrouter_live`, `gemini_live` o `fallback_simulated`).
   - `rag_response`: Texto final de la recomendación biomecánica.

---

## 4. Pruebas de Ejecución End-to-End

Resultados obtenidos mediante el script reproducible `scripts/test_rag_pipeline.py`:

| Caso de Prueba | Consulta | Fuentes Citadas | Modo de Generación |
|---|---|---|---|
| **Hernia Discal L4-L5** | *¿Qué ejercicios debo reemplazar si sufro de una hernia discal lumbar L4-L5?* | `medical_adaptations.md`, `biomechanics_and_safety.md` | `fallback_simulated` / `live` |
| **Sobrecarga Progresiva** | *¿Cuáles son las reglas de sobrecarga progresiva para maximizar la hipertrofia?* | `biomechanics_and_safety.md`, `hypertrophy_periodization.md` | `fallback_simulated` / `live` |
| **Valgo de Rodilla** | *Alineación articular y prevención de valgo de rodilla en sentadilla* | `medical_adaptations.md`, `biomechanics_and_safety.md` | `fallback_simulated` / `live` |

---

## 5. Verificación Automatizada

La suite de pruebas en `tests/test_rag_pipeline.py` valida:
1. `test_context_retrieval_dense_384d`: Recuperación semántica consumiendo los embeddings de 384d.
2. `test_context_retrieval_tfidf_mode`: Recuperación mediante baseline TF-IDF.
3. `test_augmented_prompt_construction`: Construcción del prompt aumentado con perfil y fuentes.
4. `test_full_pipeline_execution_metadata`: Trazabilidad completa de metadatos y modo de generación.
5. `test_lumbar_contraindications_synthesis`: Validación de sustituciones para patologías lumbares.
6. `test_hypertrophy_principles_synthesis`: Validación de principios de hipertrofia y sobrecarga.

```bash
python -m unittest tests/test_rag_pipeline.py
# Ran 6 tests in 0.012s - OK
```

