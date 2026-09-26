# 📐 Estrategia e Implementación de Chunking para el Sistema RAG — Wellness Lift (Issue #6)

## 1. Resumen Ejecutivo
Este documento describe el diseño, la justificación de parámetros, la unidad de medida y la validación empírica de la estrategia de segmentación (**Chunking Strategy**) utilizada para procesar la base de conocimiento especializada del dominio deportivo y biomecánico en **Wellness Lift**, respondiendo a la tarea **[S1-02 - Implementar estrategia de chunking] (Issue #6)**.

---

## 2. Definición y Alineación de Unidades de Medida

Para garantizar total transparencia y concordancia entre el código (src/backend/app/rag_chunker.py) y la documentación técnica:

- **Unidad Primaria de Segmentación:** **Palabras (words)**. La ventana deslizante opera dividiendo el contenido mediante content.split(), garantizando que ninguna palabra quede truncada ortográficamente.
- **Estimación de Tokens (_estimate_tokens):** Se computa mediante expresiones regulares (len(re.findall(r'\w+|\S', text))), proporcionando una estimación proporcional donde 1 palabra equivale aproximadamente a **1.3 – 1.4 tokens**.
- **Parámetros Nominales de la Configuración Seleccionada:**
  - chunk_size = 512 palabras (~650 – 700 tokens estimados).
  - chunk_overlap = 64 palabras (~80 – 90 tokens estimados, equivalente al **12.5%** de solapamiento).

---

## 3. Estrategia de Segmentación Híbrida: Jerárquica + Ventana Deslizante

La estrategia implementada consta de dos etapas complementarias:

1. **Fase 1 — Segmentación Jerárquica por Encabezados Markdown (split_markdown_by_headings):**
   - El documento se divide en secciones basadas en encabezados (#, ##, ###).
   - Cada sección preserva su contexto temático inyectando el metadato heading_context en el cuerpo del chunk.
   - Si la sección tiene $\le 512$ palabras, se genera un chunk atómico sin necesidad de fragmentación.

2. **Fase 2 — Ventana Deslizante con Solapamiento (chunk_section):**
   - Si una sección supera el umbral de chunk_size (512 palabras), se activa el algoritmo de ventana deslizante:
     	ext{Inicio}_{i+1} = 	ext{Inicio}_i + (	ext{chunk\_size} - 	ext{chunk\_overlap})
   - Los chunks consecutivos retienen exactamente chunk_overlap (64 palabras) en común, garantizando continuidad semántica entre transiciones.

---

## 4. Comparación Empírica Reproducible de Configuraciones

Para verificar cuantitativamente el impacto de los hiperparámetros de segmentación, se ejecutó el script de benchmark reproducible [scripts/benchmark_chunking_configs.py](../../scripts/benchmark_chunking_configs.py) sobre el corpus real de la base de conocimiento y sobre un documento de prueba controlado de 1,200 palabras.

Los resultados han sido persistidos en [data/processed_chunks/chunking_benchmark_results.json](../../data/processed_chunks/chunking_benchmark_results.json):

| Configuración Evaluada | chunk_size / overlap (palabras) | Tokens Estimados por Chunk | Chunks en Corpus Real | Subchunks en Doc Extenso (1,200 palabras) | Solapamiento Efectivo Verificado | Decisión de Selección |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Opción A (Pequeña)** | 256 / 32 | ~330 tokens | 8 chunks | 6 subchunks | ✅ 100% (32 palabras exactas) | Descartada (Excesiva fragmentación) |
| **Opción B (Óptima)** | **512 / 64** | **~650 tokens** | **8 chunks** | **3 subchunks** | **✅ 100% (64 palabras exactas)** | **SELECCIONADA** |
| **Opción C (Grande)** | 1024 / 128 | ~1300 tokens | 8 chunks | 2 subchunks | ✅ 100% (128 palabras exactas) | Descartada (Baja granularidad) |

### Justificación de la Configuración Seleccionada (512 / 64):
- **Preservación Atómica del Corpus:** Las secciones actuales de la base de conocimiento oscilan entre 23 y 185 palabras (promedio de 57.0 palabras / 76.9 tokens estimados), por lo que se mantienen como unidades conceptuales completas sin fragmentar tablas de contraindicaciones.
- **Preparación para Documentos Extensos:** Para protocolos clínicos de gran volumen, la ventana deslizante divide el texto en bloques de 512 palabras con 64 palabras compartidas, comprobado matemáticamente en las pruebas unitarias.

---

## 5. Evidencia de Solapamiento en Pruebas Automatizadas

El funcionamiento de la ventana deslizante y la exactitud del solapamiento están validados mediante la suite de pruebas unitarias [	ests/test_chunking_strategy.py](../../tests/test_chunking_strategy.py):

`python
# Verificación de coincidencia exacta de solapamiento en test_overlap_exact_words_matching
c1_tail_overlap = c1_content_words[-64:]
c2_head_overlap = c2_content_words[:64]
assert c1_tail_overlap == c2_head_overlap  # 64 palabras exactamente idénticas
`

---

## 6. Instrucciones de Reproducción

Para ejecutar y verificar la estrategia de chunking y el benchmark empírico:

`ash
# 1. Ejecutar el benchmark empírico de configuraciones
python scripts/benchmark_chunking_configs.py

# 2. Ejecutar el procesamiento de la base de conocimiento
python scripts/chunk_knowledge_base.py

# 3. Ejecutar las pruebas automatizadas de chunking
python -m unittest tests/test_chunking_strategy.py
`
