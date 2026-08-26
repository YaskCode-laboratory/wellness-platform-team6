# 📐 Estrategia e Implementación de Chunking para el Sistema RAG — Wellness Lift

## 1. Resumen Ejecutivo
Este documento describe el diseño, la justificación de parámetros y la implementación de la estrategia de segmentación (**Chunking Strategy**) utilizada para procesar la base de conocimiento especializada del dominio deportivo y biomecánico en **Wellness Lift**.

---

## 2. Análisis de Estructura y Características de los Documentos
Los documentos del dominio (`docs/rag_knowledge_base/*.md`) presentan una estructura semántica jerárquica:
- Encabezados Markdown de nivel 1 (`#`), 2 (`##`) y 3 (`###`).
- Tablas comparativas de sustitución muscular y contraindicaciones médicas.
- Listas con viñetas de reglas biomecánicas y rangos de repeticiones.

---

## 3. Estrategia de Segmentación Seleccionada: Híbrida Semántica-Markdown con Ventana Deslizante

Se seleccionó un enfoque **Híbrido Semántico-Markdown con Ventana Deslizante (Sliding Window Overlap)**:
1. **Fase 1 (Segmentación Jerárquica por Encabezados)**: Preserva la unidad temática del concepto (ej. *Hernia Discal L4-L5*).
2. **Fase 2 (Ventana Deslizante con Solapamiento)**: Para secciones extensas que superan el tamaño máximo de ventana, se aplica una división con solapamiento (*overlap*) para evitar la fragmentación abrupta de frases al final de cada bloque.

---

## 4. Justificación y Matriz de Pruebas de Parámetros

Se realizaron pruebas empíricas evaluando 3 configuraciones de segmentación:

| Configuración | Tamaños Probados (`chunk_size` / `overlap`) | Coherencia Semántica | Fragmentación de Tablas | Configuración Seleccionada |
| :--- | :--- | :--- | :--- | :--- |
| **Opción A (Pequeña)** | 256 tokens / 32 overlap | Deficiente (Frases cortadas) | Alta (Tablas divididas por la mitad) | No |
| **Opción B (Óptima)** | **512 tokens / 64 overlap** | **Excelente (Contexto completo)** | **Nula (Mantiene tablas intactas)** | **SI (SELECCIONADA)** |
| **Opción C (Grande)** | 1024 tokens / 128 overlap | Excesivo ruido impreciso | Nula | No |

### Justificación de Parámetros Seleccionados:
- **`chunk_size = 512` tokens (~350-400 palabras)**: Coincide exactamente con la ventana de contexto óptima para modelos de embeddings modernos (ej. OpenAI `text-embedding-3-small`, Google `text-embedding-004`).
- **`chunk_overlap = 64` tokens (~12.5% del tamaño del chunk)**: Garantiza que los conceptos fronterizos entre dos bloques adyacentes conserven la ilación lógica sin duplicar excesivamente el índice vectorial.

---

## 5. Implementación en Código (`src/backend/app/rag_chunker.py`)

El módulo `MarkdownSemanticChunker` procesa los archivos `.md`, extrae el contexto del encabezado superior e inyecta el metadato `heading_context` en el cuerpo del chunk.

```python
# Ejemplo de chunk generado en data/processed_chunks/sample_chunks.json
{
  "chunk_id": "medical_adaptations.md#matriz_de_sustitución_por_lesión_/_condición-0",
  "source_file": "medical_adaptations.md",
  "heading_context": "Matriz de Sustitución por Lesión / Condición",
  "token_count": 210,
  "text": "### Contexto: Matriz de Sustitución por Lesión / Condición\n| Condición Registrada | Ejercicios Contraindicados | Ejercicios Sustitutos Seguros | ..."
}
```
