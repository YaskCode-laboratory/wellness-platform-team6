"""
Script de Prueba End-to-End del Pipeline RAG — Wellness Lift (Issue #9)
Ejecuta el pipeline RAG completo demostrando la ingesta, búsqueda vectorial, aumento de contexto y generación.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.rag_pipeline import RAGPipeline

def run_rag_pipeline_demo():
    print("[START] === INICIANDO DEMOSTRACION DEL PIPELINE RAG END-TO-END ===\n")
    pipeline = RAGPipeline()

    test_cases = [
        {
            "query": "¿Qué ejercicios debo reemplazar si sufro de una hernia discal lumbar L4-L5?",
            "profile": {"name": "Carlos Atleta", "health_conditions": "Hernia Discal L4-L5", "fitness_level": "Intermedio"}
        },
        {
            "query": "¿Cuáles son las reglas de sobrecarga progresiva para maximizar la hipertrofia muscular?",
            "profile": {"name": "María Pérez", "health_conditions": "Ninguna", "fitness_level": "Avanzado"}
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"==================================================")
        print(f"[CASE #{i}] Usuario: {test['profile']['name']} ({test['profile']['health_conditions']})")
        print(f"[QUERY] Consulta: '{test['query']}'")
        print(f"--------------------------------------------------")

        result = pipeline.run_pipeline(test["query"], user_profile=test["profile"], top_k=2)

        print(f"[CHUNKS] Chunks Recuperados ({result['retrieved_chunks_count']}):")
        for chunk in result['retrieved_chunks']:
            print(f"  - [{chunk['source_file']}] {chunk['heading_context']} (Similitud: {chunk['similarity_score']})")

        print(f"\n[SOURCES] Fuentes Utilizadas: {', '.join(result['sources'])}")
        print(f"\n[RESPONSE] Respuesta Generada por el Pipeline RAG:\n{result['rag_response']}")
        print(f"==================================================\n")

if __name__ == "__main__":
    run_rag_pipeline_demo()
