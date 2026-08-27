"""
Pruebas Automatizadas del Pipeline RAG End-to-End — Wellness Lift (Issue #9)
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.rag_pipeline import RAGPipeline

class TestRAGPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = RAGPipeline()

    def test_context_retrieval(self):
        chunks = self.pipeline.retrieve_context("hernia discal lumbar L4-L5", top_k=2)
        self.assertGreaterEqual(len(chunks), 1)
        self.assertIn("source_file", chunks[0])

    def test_augmented_prompt_construction(self):
        chunks = self.pipeline.retrieve_context("hipertrofia y tension mecanica", top_k=2)
        prompt = self.pipeline.build_augmented_prompt("hipertrofia", chunks, user_profile={"name": "Test User"})
        self.assertIn("BASE DE CONOCIMIENTO RAG RECUPERADA", prompt)
        self.assertIn("PERFIL DEL ATLETA", prompt)

    def test_full_pipeline_execution(self):
        result = self.pipeline.run_pipeline("ejercicios seguros para hernia lumbar", user_profile={"name": "Ana", "health_conditions": "Lumbar"})
        self.assertEqual(result["retrieved_chunks_count"], 3)
        self.assertIn("rag_response", result)
        self.assertGreaterEqual(len(result["sources"]), 1)

if __name__ == "__main__":
    unittest.main()
