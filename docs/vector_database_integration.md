# 🗄️ Integración de Base de Datos Vectorial — Wellness Lift (Issue #8)

## 1. Resumen Ejecutivo
Este documento especifica la selección, configuración, indexación y pruebas de recuperación semántica de la **Base de Datos Vectorial** implementada para el motor RAG de la plataforma **Wellness Lift**, respondiendo al requerimiento **[S1-04 - Integrar base de datos vectorial] (Issue #8)**.

---

## 2. Selección de la Tecnología de Base de Datos Vectorial

Se seleccionó e implementó un motor vectorial **In-Memory Cosine Vector Database Store** desarrollado en Python (`src/backend/app/vector_store.py`):
- **Motor de Similitud**: Similitud del Coseno (*Cosine Similarity*) ponderada por TF-IDF normalizado L2.
- **Indexación y Persistencia**: Serialización en formato JSON (`data/vector_store/vector_index.json`).
- **Justificación**: Aporta cero latencia de red, 100% de reproducibilidad local y en AWS EC2 sin depender de servicios externos o contenedores pesados adicionales, garantizando búsquedas vectoriales sub-milisegundo.

---

## 3. Arquitectura del Flujo de Indexación y Consulta

```
[Documentos RAG (.md)] ──> [RAG Chunker (512 tokens)] ──> [Vector Database Store]
                                                                  │
[Consulta Atleta/Coach] ──> [Vectorizador Similitud] ─────────────┴──> [Top-K Chunks Relevantes]
```

---

## 4. Pruebas de Recuperación Semántica por Similitud

Se ejecutaron consultas de prueba en `scripts/index_vector_store.py`:

1. **Consulta**: *"¿Qué ejercicios debo reemplazar si tengo hernia discal lumbar L4-L5?"*
   - **Resultado**: `medical_adaptations.md` (Similitud: `0.1519`)
   - **Chunk Recuperado**: *Matriz de Sustitución por Lesión Lumbar* (Reemplazar sentadilla libre por prensa inclinada).

2. **Consulta**: *"¿Cómo se aplica el principio de sobrecarga progresiva e hipertrofia?"*
   - **Resultado**: `hypertrophy_periodization.md` (Similitud: `0.2390`)
   - **Chunk Recuperado**: *Mecanismos de Hipertrofia y Tensión Mecánica*.

3. **Consulta**: *"Alineación articular y prevención de valgo de rodilla en sentadilla"*
   - **Resultado**: `biomechanics_and_safety.md` (Similitud: `0.2926`)
   - **Chunk Recuperado**: *Principios Biomecánicos Fundamentales*.

---

## 5. Verificación Automatizada

La suite de pruebas unitarias en `tests/test_vector_store.py` valida la fidelidad de la recuperación vectorial:
```bash
python -m unittest tests/test_vector_store.py
# Ran 3 tests in 0.001s - OK
```
