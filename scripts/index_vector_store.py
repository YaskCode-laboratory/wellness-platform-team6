"""
Script de Indexación y Prueba de Búsqueda Semántica Vectorial — Wellness Lift (Issue #8)
Indexa los chunks producidos en data/processed_chunks/rag_chunks.json en la Vector DB.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.vector_store import VectorDatabaseStore

def run_vector_indexing():
    chunks_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed_chunks', 'rag_chunks.json'))
    vector_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'vector_store'))
    os.makedirs(vector_dir, exist_ok=True)

    if not os.path.exists(chunks_file):
        print(f"[ERROR] No se encontro el archivo de chunks: {chunks_file}")
        return

    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print(f"[+] Cargando {len(chunks)} chunks para indexacion vectorial...")
    vstore = VectorDatabaseStore(collection_name="wellness_rag_knowledge")
    vstore.fit_and_index(chunks)

    output_index = os.path.join(vector_dir, 'vector_index.json')
    vstore.save_index(output_index)
    print(f"[SUCCESS] Base de datos vectorial indexada y guardada en: {output_index}")

    # Prueba de Consulta por Similitud
    test_queries = [
        "¿Qué ejercicios debo reemplazar si tengo hernia discal lumbar L4-L5?",
        "¿Cómo se aplica el principio de sobrecarga progresiva e hipertrofia?",
        "Alineación articular y prevención de valgo de rodilla en sentadilla"
    ]

    print("\n--- PRUEBAS DE RECUPERACION POR SIMILITUD VECTORIAL ---")
    for q in test_queries:
        print(f"\n[QUERY] Consulta: '{q}'")
        results = vstore.search_similarity(q, k=2)
        for i, (doc, score) in enumerate(results, 1):
            print(f"  [{i}] (Similitud: {score:.4f}) ID: {doc['chunk_id']}")
            print(f"      Fuente: {doc['source_file']} | Contexto: {doc['heading_context']}")

if __name__ == "__main__":
    run_vector_indexing()
