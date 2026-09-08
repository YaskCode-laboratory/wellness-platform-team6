"""
Script de Indexación y Prueba de Búsqueda Semántica Vectorial — Wellness Lift (Issue #8)
Indexa los chunks producidos en S1-03 (data/processed_chunks/rag_chunks_with_embeddings.json)
o calcula los embeddings de 384 dimensiones en la Vector Database Store.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.vector_store import VectorDatabaseStore
from app.embeddings_generator import EmbeddingsGenerator

def run_vector_indexing():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    chunks_with_emb_file = os.path.join(base_dir, 'data', 'processed_chunks', 'rag_chunks_with_embeddings.json')
    embeddings_file = os.path.join(base_dir, 'data', 'vector_store', 'embeddings.json')
    chunks_raw_file = os.path.join(base_dir, 'data', 'processed_chunks', 'rag_chunks.json')
    vector_dir = os.path.join(base_dir, 'data', 'vector_store')
    os.makedirs(vector_dir, exist_ok=True)

    # 1. Carga prioritaria de chunks con embeddings generados en S1-03
    chunks = []
    source_origin = ""

    if os.path.exists(chunks_with_emb_file):
        with open(chunks_with_emb_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        source_origin = "rag_chunks_with_embeddings.json (S1-03)"
    elif os.path.exists(embeddings_file):
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        source_origin = "embeddings.json (S1-03)"
    elif os.path.exists(chunks_raw_file):
        with open(chunks_raw_file, 'r', encoding='utf-8') as f:
            raw_chunks = json.load(f)
        gen = EmbeddingsGenerator()
        chunks = gen.generate_batch_embeddings(raw_chunks)
        source_origin = "rag_chunks.json (enriquecido con EmbeddingsGenerator)"
    else:
        print(f"[ERROR] No se encontraron archivos de chunks en data/processed_chunks/")
        return

    print(f"[+] Origen de datos: {source_origin}")
    print(f"[+] Cargando {len(chunks)} chunks con representaciones vectoriales densas...")

    vstore = VectorDatabaseStore(collection_name="wellness_rag_knowledge")
    vstore.fit_and_index(chunks)

    output_index = os.path.join(vector_dir, 'vector_index.json')
    vstore.save_index(output_index)
    print(f"[SUCCESS] Base de datos vectorial indexada (Dim: {vstore.embedding_dim}, Modelo: '{vstore.embedding_model}')")
    print(f"[SUCCESS] Índice persistido en: {output_index}")

    # Pruebas de Consulta por Similitud Semántica (Dense Embeddings 384d)
    test_queries = [
        "¿Qué ejercicios debo reemplazar si tengo hernia discal lumbar L4-L5?",
        "¿Cómo se aplica el principio de sobrecarga progresiva e hipertrofia?",
        "Alineación articular y prevención de valgo de rodilla en sentadilla"
    ]

    print("\n" + "=" * 70)
    print("--- PRUEBAS DE RECUPERACION POR SIMILITUD VECTORIAL (DENSE 384d) ---")
    print("=" * 70)
    for q in test_queries:
        print(f"\n[QUERY] Consulta: '{q}'")
        results = vstore.search_similarity(q, k=2, mode="dense")
        for i, (doc, score) in enumerate(results, 1):
            print(f"  [{i}] (Similitud Coseno: {score:.4f}) ID: {doc['chunk_id']}")
            print(f"      Fuente: {doc['source_file']} | Contexto: {doc['heading_context']}")
            print(f"      Modelo: {doc.get('embedding_model', 'N/A')} | Dimensión: {len(doc.get('embedding', []))}")

    print("\n" + "=" * 70)
    print("--- PRUEBA BASELINE TF-IDF COMPARATIVA ---")
    print("=" * 70)
    for q in test_queries[:1]:
        print(f"\n[BASELINE TF-IDF] Consulta: '{q}'")
        results_tfidf = vstore.search_similarity(q, k=2, mode="tfidf")
        for i, (doc, score) in enumerate(results_tfidf, 1):
            print(f"  [{i}] (Similitud TF-IDF: {score:.4f}) ID: {doc['chunk_id']}")
            print(f"      Fuente: {doc['source_file']} | Contexto: {doc['heading_context']}")

if __name__ == "__main__":
    run_vector_indexing()
