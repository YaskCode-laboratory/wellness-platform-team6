#!/usr/bin/env python3
"""
Script CLI para la generación de embeddings y almacenamiento vectorial del sistema RAG Wellness Lift.
Transforma los chunks generados en data/processed_chunks/rag_chunks.json en representaciones vectoriales.
"""

import json
import os
import sys
from pathlib import Path

# Configurar stdout para UTF-8 si aplica
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.embeddings_generator import EmbeddingsGenerator


def main():
    print("=" * 70)
    print("INICIANDO GENERACION DE EMBEDDINGS Y ALMACENAMIENTO VECTORIAL (RAG)")
    print("=" * 70)

    chunks_file = ROOT_DIR / "data" / "processed_chunks" / "rag_chunks.json"
    vector_store_dir = ROOT_DIR / "data" / "vector_store"
    enriched_chunks_file = ROOT_DIR / "data" / "processed_chunks" / "rag_chunks_with_embeddings.json"
    vector_store_file = vector_store_dir / "embeddings.json"

    if not chunks_file.exists():
        print(f"Error: No se encontro el archivo de chunks en {chunks_file}")
        sys.exit(1)

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Se cargaron {len(chunks)} chunks desde {chunks_file.name}")

    generator = EmbeddingsGenerator()
    enriched_chunks = generator.generate_batch_embeddings(chunks)

    # Crear directorios de destino si no existen
    vector_store_dir.mkdir(parents=True, exist_ok=True)
    enriched_chunks_file.parent.mkdir(parents=True, exist_ok=True)

    # Guardar en data/processed_chunks/rag_chunks_with_embeddings.json
    with open(enriched_chunks_file, "w", encoding="utf-8") as f:
        json.dump(enriched_chunks, f, indent=2, ensure_ascii=False)

    # Guardar índice en data/vector_store/embeddings.json
    vector_store_data = {
        "metadata": {
            "total_chunks": len(enriched_chunks),
            "embedding_model": enriched_chunks[0]["embedding_model"] if enriched_chunks else "N/A",
            "vector_dimension": enriched_chunks[0]["embedding_dim"] if enriched_chunks else 0,
            "generated_at_version": "1.0.0"
        },
        "vectors": [
            {
                "chunk_id": item["chunk_id"],
                "source_file": item["source_file"],
                "heading_context": item["heading_context"],
                "text": item["text"],
                "vector": item["embedding"]
            }
            for item in enriched_chunks
        ]
    }

    with open(vector_store_file, "w", encoding="utf-8") as f:
        json.dump(vector_store_data, f, indent=2, ensure_ascii=False)

    print("\nGENERACION COMPLETADA EXITOSAMENTE")
    print("-" * 70)
    print(f"Chunks procesados: {len(enriched_chunks)}")
    print(f"Modelo de embeddings: {enriched_chunks[0]['embedding_model']}")
    print(f"Dimensionalidad del vector: {enriched_chunks[0]['embedding_dim']}")
    print(f"Vector Store guardado en: {vector_store_file}")
    print(f"Chunks enriquecidos en: {enriched_chunks_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
