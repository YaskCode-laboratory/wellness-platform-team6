"""
Script de Procesamiento e Ingesta RAG Chunker
Lee todos los documentos de docs/rag_knowledge_base/ y genera los chunks procesados en data/processed_chunks/
"""

import os
import sys
import json

# Agregar src/backend al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.rag_chunker import MarkdownSemanticChunker

def run_chunking_pipeline():
    kb_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs', 'rag_knowledge_base'))
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed_chunks'))
    os.makedirs(output_dir, exist_ok=True)

    chunker = MarkdownSemanticChunker(chunk_size=512, chunk_overlap=64)
    all_processed_chunks = []

    for file in os.listdir(kb_dir):
        if file.endswith('.md') and file != 'README.md':
            filepath = os.path.join(kb_dir, file)
            print(f"[+] Procesando documento: {file}...")
            file_chunks = chunker.process_file(filepath)
            all_processed_chunks.extend(file_chunks)

    # Guardar la totalidad de chunks
    output_file = os.path.join(output_dir, 'rag_chunks.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_processed_chunks, f, indent=2, ensure_ascii=False)

    # Guardar muestra representativa de ejemplo
    sample_file = os.path.join(output_dir, 'sample_chunks.json')
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(all_processed_chunks[:3], f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] Proceso de chunking completado. Total de chunks generados: {len(all_processed_chunks)}")
    print(f"[OUTPUT] Archivos guardados en:\n - {output_file}\n - {sample_file}")

if __name__ == "__main__":
    run_chunking_pipeline()
