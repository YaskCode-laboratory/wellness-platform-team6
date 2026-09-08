# 🧪 Guía Técnica de Evaluación RAG — Wellness Lift

Documentación técnica del evaluador de desempeño de recuperación del motor RAG (*Wellness Lift RAG Evaluator*).

---

## 📌 1. Arquitectura del Evaluador (`rag_evaluator.py`)

El evaluador RAG (`src/backend/app/rag_evaluator.py`) proporciona un conjunto de herramientas programáticas y CLI para medir de forma reproducible la calidad del motor de búsqueda vectorial sobre la base de conocimiento de dominio.

### Módulos Principales:
- `RAGEvaluator`: Clase principal responsable de cargar `embeddings.json`, ejecutar la similitud coseno y evaluar el benchmark.
- `evaluate_query(query_item, top_k)`: Evalúa un caso individual retornando Precision@K, Recall@K, MRR y verificaciones de cobertura médica.
- `evaluate_all(test_queries, top_k)`: Ejecuta la evaluación agregada calculando promedios globales y `medical_safety_accuracy`.

---

## 📐 2. Fórmulas y Criterios de Evaluación

### A. Calidad de Recuperación (*Retrieval Quality*)
1. **Precision@K**: $\text{Precision@K} = \frac{|\text{Chunks Recuperados Relevantes en Top-K}|}{K}$
2. **Recall@K**: $\text{Recall@K} = \frac{|\text{Chunks Recuperados Relevantes en Top-K}|}{|\text{Total Chunks Relevantes Esperados}|}$
3. **MRR (Mean Reciprocal Rank)**: $\text{MRR} = \frac{1}{\text{rank}_{\text{primer chunk relevante}}}$

### B. Precisión en Seguridad Médica (*Medical Safety Accuracy*)
- **Filtro de Ámbito**: Se calcula **únicamente** sobre las consultas clasificadas bajo la categoría `Medical Substitutions` ($N_{medical} = 4$).
- **Fórmula**: $\text{Medical Safety Accuracy} = \frac{\sum \text{Consultas Médicas con } safety\_passed = True}{N_{medical}}$
- **Criterio de Aprobación (`safety_passed`)**: Requiere que los chunks recuperados en el Top-K contengan tanto los ejercicios prohibidos como los sustitutos seguros esperados ($unwarned\_contraindications = \emptyset \land missing\_substitutes = \emptyset$).

---

## 🚀 3. Instrucciones de Ejecución

### Ejecutar Benchmark CLI:
```bash
python scripts/evaluate_rag.py
```
Este script genera el informe JSON reproducible en `data/evaluation/evaluation_results.json`.

### Ejecutar Pruebas Automatizadas (Pytest):
```bash
python -m pytest tests/test_rag_evaluation.py -v
```
