"""
Suite de Pruebas Unitarias e Integración para la Evaluación del Motor RAG (Issue #10 - S1-06).
Verifica métricas de recuperación (Precision@K, Recall@K, MRR) y precisión de seguridad médica.
"""

import json
import sys
from pathlib import Path

import pytest

# Agregar src/backend a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.rag_evaluator import RAGEvaluator


@pytest.fixture
def evaluator():
    return RAGEvaluator()


def test_evaluator_vector_store_loaded(evaluator):
    """Verifica que el evaluador cargue correctamente el almacén de vectores."""
    assert len(evaluator.vector_data) > 0, "El almacén de vectores no debe estar vacío"


def test_retrieve_top_k(evaluator):
    """Verifica que retrieve_top_k retorne exactamente K elementos ordenados por similitud descendente."""
    query = "Sentadilla libre y valgo de rodilla"
    results = evaluator.retrieve_top_k(query, top_k=3)

    assert len(results) == 3
    assert results[0]["similarity_score"] >= results[1]["similarity_score"]
    assert results[1]["similarity_score"] >= results[2]["similarity_score"]


def test_single_query_evaluation(evaluator):
    """Verifica la evaluación de un caso individual de prueba."""
    query_item = {
        "query_id": "TEST_01",
        "category": "Medical Substitutions",
        "query": "¿Qué ejercicios están contraindicados si el atleta tiene hernia discal L4-L5 lumbar y cuáles son sus sustitutos seguros?",
        "expected_relevant_chunk_ids": [
            "medical_adaptations.md#2._matriz_de_sustitución_por_lesión_/_condición-0"
        ],
        "contraindicated_exercises": [
            "Sentadilla Libre con Barra"
        ],
        "safe_substitutes": [
            "Prensa Inclinada a 45°"
        ]
    }

    res = evaluator.evaluate_query(query_item, top_k=3)

    assert res["query_id"] == "TEST_01"
    assert res["recall_at_k"] == 1.0
    assert res["safety_passed"] is True
    assert res["mrr"] > 0.0


def test_full_evaluation_suite(evaluator):
    """Verifica la ejecución del suite completo de 10 consultas de prueba."""
    test_queries_file = ROOT_DIR / "data" / "evaluation" / "test_queries.json"
    with open(test_queries_file, "r", encoding="utf-8") as f:
        test_queries = json.load(f)

    report = evaluator.evaluate_all(test_queries, top_k=3)
    summary = report["summary"]

    assert summary["total_queries"] == 10
    assert summary["mean_recall_at_k"] >= 0.50, "Recall@3 debe ser al menos 50%"
    assert summary["medical_safety_accuracy"] >= 0.70, "Precisión médica debe ser al menos 70%"


def test_evaluation_results_file_integrity():
    """Verifica que el archivo de resultados data/evaluation/evaluation_results.json exista y sea válido."""
    results_file = ROOT_DIR / "data" / "evaluation" / "evaluation_results.json"
    assert results_file.exists(), "El archivo data/evaluation/evaluation_results.json debe existir"

    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "summary" in data
    assert "detailed_results" in data
    assert len(data["detailed_results"]) == 10
