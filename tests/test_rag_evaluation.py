"""
Suite de Pruebas Unitarias e Integración para la Evaluación del Motor RAG (Issue #10 - S1-06).
Verifica métricas de recuperación (Precision@K, Recall@K, MRR) y precisión de seguridad médica.
"""

import json
import os
import sys
import unittest
from pathlib import Path

# Agregar src/backend a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.rag_evaluator import RAGEvaluator


class TestRAGEvaluation(unittest.TestCase):
    def setUp(self):
        self.evaluator = RAGEvaluator()

    def test_evaluator_vector_store_loaded(self):
        """Verifica que el evaluador cargue correctamente el almacén de vectores."""
        self.assertGreater(len(self.evaluator.vector_data), 0, "El almacén de vectores no debe estar vacío")

    def test_retrieve_top_k(self):
        """Verifica que retrieve_top_k retorne exactamente K elementos ordenados por similitud descendente."""
        query = "Sentadilla libre y valgo de rodilla"
        results = self.evaluator.retrieve_top_k(query, top_k=3)

        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(results[0]["similarity_score"], results[1]["similarity_score"])
        self.assertGreaterEqual(results[1]["similarity_score"], results[2]["similarity_score"])

    def test_single_query_evaluation(self):
        """Verifica la evaluación de un caso individual de prueba."""
        query_item = {
            "query_id": "TEST_01",
            "category": "Medical Substitutions",
            "query": "Hernia discal L4-L5 lumbar contraindicaciones",
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

        res = self.evaluator.evaluate_query(query_item, top_k=3)

        self.assertEqual(res["query_id"], "TEST_01")
        self.assertEqual(res["recall_at_k"], 1.0)
        self.assertTrue(res["safety_passed"])
        self.assertGreater(res["mrr"], 0.0)

    def test_missing_safe_substitute_fails_safety(self):
        """Verifica que una consulta médica con un sustituto seguro faltante produzca safety_passed = False."""
        query_item = {
            "query_id": "TEST_MISSING_SUB",
            "category": "Medical Substitutions",
            "query": "Hernia discal L4-L5 lumbar contraindicaciones",
            "expected_relevant_chunk_ids": [
                "medical_adaptations.md#2._matriz_de_sustitución_por_lesión_/_condición-0"
            ],
            "contraindicated_exercises": [
                "Sentadilla Libre con Barra"
            ],
            "safe_substitutes": [
                "Ejercicio Inexistente Inalcanzable 9000"
            ]
        }

        res = self.evaluator.evaluate_query(query_item, top_k=3)

        self.assertFalse(res["safety_passed"])
        self.assertIn("Ejercicio Inexistente Inalcanzable 9000", res["missing_substitutes"])

    def test_medical_safety_accuracy_denominator_exclusive_to_medical_queries(self):
        """Verifica que medical_safety_accuracy utilice exclusivamente las consultas médicas como denominador."""
        mixed_queries = [
            # 2 consultas médicas: 1 pasa, 1 falla (seguridad médica esperada = 1/2 = 50%)
            {
                "query_id": "MED_01",
                "category": "Medical Substitutions",
                "query": "Hernia discal L4-L5",
                "expected_relevant_chunk_ids": ["medical_adaptations.md#2._matriz_de_sustitución_por_lesión_/_condición-0"],
                "contraindicated_exercises": ["Sentadilla Libre con Barra"],
                "safe_substitutes": ["Prensa Inclinada a 45°"]
            },
            {
                "query_id": "MED_02",
                "category": "Medical Substitutions",
                "query": "Hernia discal lumbar",
                "expected_relevant_chunk_ids": ["medical_adaptations.md#2._matriz_de_sustitución_por_lesión_/_condición-0"],
                "contraindicated_exercises": ["Sentadilla Libre con Barra"],
                "safe_substitutes": ["Sustituto No Presente En Corpus XYZ"]
            },
            # 3 consultas no médicas
            {
                "query_id": "NON_MED_01",
                "category": "Biomechanics & Safety",
                "query": "Alineación articular y valgo de rodilla",
                "expected_relevant_chunk_ids": ["biomechanics_and_safety.md#2._principios_biomecánicos_fundamentales-0"]
            },
            {
                "query_id": "NON_MED_02",
                "category": "Hypertrophy & Periodization",
                "query": "Mecanismos de hipertrofia muscular",
                "expected_relevant_chunk_ids": ["hypertrophy_periodization.md#2._mecanismos_de_hipertrofia-0"]
            },
            {
                "query_id": "NON_MED_03",
                "category": "Domain Scope",
                "query": "Alcance del conocimiento",
                "expected_relevant_chunk_ids": ["biomechanics_and_safety.md#1._dominio_y_alcance-0"]
            }
        ]

        report = self.evaluator.evaluate_all(mixed_queries, top_k=3)
        summary = report["summary"]

        self.assertEqual(summary["total_queries"], 5)
        self.assertEqual(summary["medical_queries_evaluated"], 2)
        # 1 de 2 pasó -> 0.50 (si fuera sobre el total de 5 daría 0.20)
        self.assertEqual(summary["medical_safety_accuracy"], 0.50)

    def test_full_evaluation_suite(self):
        """Verifica la ejecución del suite completo de 10 consultas de prueba."""
        test_queries_file = ROOT_DIR / "data" / "evaluation" / "test_queries.json"
        with open(test_queries_file, "r", encoding="utf-8") as f:
            test_queries = json.load(f)

        report = self.evaluator.evaluate_all(test_queries, top_k=3)
        summary = report["summary"]

        self.assertEqual(summary["total_queries"], 10)
        self.assertEqual(summary["medical_queries_evaluated"], 4)
        self.assertGreaterEqual(summary["mean_recall_at_k"], 0.50, "Recall@3 debe ser al menos 50%")
        self.assertGreaterEqual(summary["medical_safety_accuracy"], 0.70, "Precisión médica debe ser al menos 70%")

    def test_evaluation_results_file_integrity(self):
        """Verifica que el archivo de resultados data/evaluation/evaluation_results.json exista y sea válido."""
        results_file = ROOT_DIR / "data" / "evaluation" / "evaluation_results.json"
        self.assertTrue(results_file.exists(), "El archivo data/evaluation/evaluation_results.json debe existir")

        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("summary", data)
        self.assertIn("detailed_results", data)
        self.assertEqual(len(data["detailed_results"]), 10)


if __name__ == "__main__":
    unittest.main()
