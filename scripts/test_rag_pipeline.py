"""
Script de Prueba End-to-End del Pipeline RAG — Wellness Lift (Issue #9)
Demuestra la cadena completa consolidada S1-03 -> S1-04 -> S1-05:
Ingesta, Búsqueda Semántica Densa 384d, Aumento de Contexto y Generación con trazabilidad de modo.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.rag_pipeline import RAGPipeline

def run_rag_pipeline_demo():
    print("=" * 75)
    print("=== DEMOSTRACION DEL PIPELINE RAG END-TO-END (S1-03 -> S1-04 -> S1-05) ===")
    print("=" * 75 + "\n")
    pipeline = RAGPipeline()

    test_cases = [
        {
            "query": "¿Qué ejercicios debo reemplazar si sufro de una hernia discal lumbar L4-L5?",
            "profile": {"name": "Carlos Atleta", "health_conditions": "Hernia Discal L4-L5", "fitness_level": "Intermedio"}
        },
        {
            "query": "¿Cuáles son las reglas de sobrecarga progresiva para maximizar la hipertrofia muscular?",
            "profile": {"name": "María Pérez", "health_conditions": "Ninguna", "fitness_level": "Avanzado"}
        },
        {
            "query": "Alineación articular y prevención de valgo de rodilla en sentadilla",
            "profile": {"name": "Luis Coach", "health_conditions": "Ninguna", "fitness_level": "Avanzado"}
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print("=" * 75)
        print(f"[CASO #{i}] Atleta: {test['profile']['name']} | Condición: {test['profile']['health_conditions']}")
        print(f"[QUERY] Consulta: '{test['query']}'")
        print("-" * 75)

        result = pipeline.run_pipeline(test["query"], user_profile=test["profile"], top_k=2)

        print(f"[VECTOR STORE] Modelo: {result['embedding_model']} | Modo Búsqueda: {result['search_mode']}")
        print(f"[CHUNKS RECUPERADOS] Total: {result['retrieved_chunks_count']}")
        for chunk in result['retrieved_chunks']:
            print(f"  • ID: {chunk['chunk_id']}")
            print(f"    Fuente: {chunk['source_file']} | Sección: {chunk['heading_context']}")
            print(f"    Similitud Coseno: {chunk['similarity_score']} | Dim: {chunk.get('embedding_dim', 384)}")

        print(f"\n[FUENTES CITADAS]: {', '.join(result['sources'])}")
        print(f"[MODO DE GENERACION]: {result['generation_mode']}")
        print(f"\n[RESPUESTA RAG GENERADA]:\n{result['rag_response']}")
        print("=" * 75 + "\n")

if __name__ == "__main__":
    run_rag_pipeline_demo()
