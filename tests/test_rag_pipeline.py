"""
Pruebas Automatizadas del Pipeline RAG End-to-End — Wellness Lift (Issue #9)
Valida la integración S1-03 -> S1-04 -> S1-05: recuperación semántica densa (384d),
construcción de prompt aumentado, trazabilidad de modo de generación (live vs fallback),
y síntesis de respuestas fundamentadas en la base de conocimiento científico.
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.rag_pipeline import RAGPipeline


class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = RAGPipeline()

    def test_context_retrieval_dense_384d(self):
        """Valida que la recuperación semántica consuma los embeddings densos de 384d."""
        chunks = self.pipeline.retrieve_context("hernia discal lumbar L4-L5", top_k=2, mode="dense")
        self.assertGreaterEqual(len(chunks), 1)
        self.assertIn("source_file", chunks[0])
        self.assertIn("similarity_score", chunks[0])
        self.assertEqual(chunks[0].get("embedding_dim"), 384)
        self.assertGreater(chunks[0]["similarity_score"], 0.0)

    def test_context_retrieval_tfidf_mode(self):
        """Valida la recuperación mediante el modo baseline TF-IDF."""
        chunks = self.pipeline.retrieve_context("hernia lumbar", top_k=2, mode="tfidf")
        self.assertGreaterEqual(len(chunks), 1)
        self.assertIn("similarity_score", chunks[0])

    def test_augmented_prompt_construction(self):
        """Valida la construcción del prompt aumentado con perfil del atleta y bloques científicos."""
        chunks = self.pipeline.retrieve_context("hipertrofia y tension mecanica", top_k=2)
        prompt = self.pipeline.build_augmented_prompt(
            "¿Cómo maximizar hipertrofia?",
            chunks,
            user_profile={"name": "Carlos", "health_conditions": "Ninguna", "fitness_level": "Avanzado"}
        )
        self.assertIn("BASE DE CONOCIMIENTO RAG RECUPERADA", prompt)
        self.assertIn("PERFIL DEL ATLETA", prompt)
        self.assertIn("Carlos", prompt)
        self.assertIn("FUENTE DE CONOCIMIENTO [1]", prompt)

    def test_full_pipeline_execution_metadata(self):
        """Valida que el resultado del pipeline contenga todos los metadatos y trazabilidad de modo."""
        result = self.pipeline.run_pipeline(
            "ejercicios seguros para hernia lumbar",
            user_profile={"name": "Ana", "health_conditions": "Lumbar"},
            top_k=3
        )
        self.assertEqual(result["retrieved_chunks_count"], 3)
        self.assertIn("rag_response", result)
        self.assertIn("generation_mode", result)
        self.assertIn(result["generation_mode"], ["openrouter_live", "gemini_live", "fallback_simulated"])
        self.assertGreaterEqual(len(result["sources"]), 1)
        self.assertEqual(result["search_mode"], "dense")
        self.assertEqual(result["embedding_model"], "local-deterministic-hashing-384d")

    def test_lumbar_contraindications_synthesis(self):
        """Valida la síntesis biomecánica de sustituciones para patologías lumbares."""
        result = self.pipeline.run_pipeline(
            "hernia lumbar L4-L5",
            user_profile={"name": "Mario", "health_conditions": "Hernia L4-L5"},
            force_fallback=True
        )
        self.assertEqual(result["generation_mode"], "fallback_simulated")
        self.assertIn("Contraindicaciones", result["rag_response"])
        self.assertIn("Prensa Inclinada", result["rag_response"])

    def test_hypertrophy_principles_synthesis(self):
        """Valida la síntesis de principios de hipertrofia y sobrecarga progresiva."""
        result = self.pipeline.run_pipeline(
            "reglas de sobrecarga progresiva e hipertrofia",
            force_fallback=True
        )
        self.assertEqual(result["generation_mode"], "fallback_simulated")
        self.assertIn("Tensión Mecánica", result["rag_response"])
        self.assertIn("Autorregulación", result["rag_response"])


if __name__ == "__main__":
    unittest.main()
