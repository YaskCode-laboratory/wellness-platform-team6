"""
Script Reproducible de Comparación Empírica de Configuraciones de Chunking (Issue #6 - S1-02).
Evalúa y documenta métricas cuantitativas reales para las 3 configuraciones de segmentación
(256/32, 512/64 y 1024/128 palabras) sobre el corpus de la base de conocimiento y textos extensos controlados.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Configurar sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.rag_chunker import MarkdownSemanticChunker


def run_benchmark() -> Dict[str, Any]:
    kb_dir = ROOT_DIR / "docs" / "rag_knowledge_base"
    output_dir = ROOT_DIR / "data" / "processed_chunks"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Corpus Real de la Base de Conocimiento
    kb_files = [f for f in kb_dir.glob("*.md") if f.name != "README.md"]

    # 2. Documento de Prueba Extenso Controlado (1,200 palabras) para validar Ventana Deslizante
    long_section_words = [f"palabra_{i}" for i in range(1, 1201)]
    controlled_long_content = (
        "# Documento Clínico Extenso Controlado\n\n"
        "## Protocolo Integral de Rehabilitación y Adaptación Lumbar\n\n" +
        " ".join(long_section_words)
    )

    configs = [
        {"id": "Config_A_256_32", "name": "Opción A (Pequeña: 256/32)", "chunk_size": 256, "chunk_overlap": 32},
        {"id": "Config_B_512_64", "name": "Opción B (Óptima Seleccionada: 512/64)", "chunk_size": 512, "chunk_overlap": 64},
        {"id": "Config_C_1024_128", "name": "Opción C (Grande: 1024/128)", "chunk_size": 1024, "chunk_overlap": 128}
    ]

    benchmark_results = {
        "benchmark_description": "Comparación empírica reproducible de estrategias de chunking en Wellness Lift (Issue #6)",
        "unit_of_measure": "words (palabras) con estimación de tokens",
        "configurations": {}
    }

    for cfg in configs:
        chunker = MarkdownSemanticChunker(chunk_size=cfg["chunk_size"], chunk_overlap=cfg["chunk_overlap"])
        
        # Procesar corpus real
        real_chunks = []
        for file_path in kb_files:
            real_chunks.extend(chunker.process_file(str(file_path)))

        # Procesar documento de prueba extenso
        long_sections = chunker.split_markdown_by_headings(controlled_long_content)
        long_chunks = []
        for sec in long_sections:
            long_chunks.extend(chunker.chunk_section(sec, "controlled_long_doc.md"))

        # Validar solapamiento efectivo en el documento extenso
        overlap_verifications = []
        for i in range(len(long_chunks) - 1):
            c1_body_words = long_chunks[i]["text"].split("\n", 1)[1].split()
            c2_body_words = long_chunks[i+1]["text"].split("\n", 1)[1].split()
            
            c1_tail = c1_body_words[-cfg["chunk_overlap"]:]
            c2_head = c2_body_words[:cfg["chunk_overlap"]]
            
            overlap_exact_match = (c1_tail == c2_head)
            overlap_verifications.append({
                "transition": f"Chunk {i+1} -> Chunk {i+2}",
                "expected_overlap_words": cfg["chunk_overlap"],
                "actual_overlap_words": len(c2_head),
                "exact_match": overlap_exact_match
            })

        avg_words_real = sum(c["word_count"] for c in real_chunks) / len(real_chunks) if real_chunks else 0
        avg_tokens_real = sum(c["token_count"] for c in real_chunks) / len(real_chunks) if real_chunks else 0

        benchmark_results["configurations"][cfg["id"]] = {
            "name": cfg["name"],
            "chunk_size_words": cfg["chunk_size"],
            "chunk_overlap_words": cfg["chunk_overlap"],
            "real_corpus_metrics": {
                "total_chunks": len(real_chunks),
                "avg_words_per_chunk": round(avg_words_real, 1),
                "avg_estimated_tokens_per_chunk": round(avg_tokens_real, 1),
                "min_words": min(c["word_count"] for c in real_chunks) if real_chunks else 0,
                "max_words": max(c["word_count"] for c in real_chunks) if real_chunks else 0,
            },
            "controlled_long_doc_metrics": {
                "total_subchunks_generated": len(long_chunks),
                "sliding_window_activated": len(long_chunks) > 1,
                "overlap_validations": overlap_verifications,
                "all_overlaps_verified": all(v["exact_match"] for v in overlap_verifications)
            }
        }

    # Guardar resultados del benchmark en JSON
    results_path = output_dir / "chunking_benchmark_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Benchmark empírico completado y guardado en {results_path}")
    return benchmark_results


if __name__ == "__main__":
    run_benchmark()
