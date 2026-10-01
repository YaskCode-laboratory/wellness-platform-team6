"""
Pruebas Automatizadas de Verificación de Documentación del Sprint 2 — Wellness Lift (Issue #18)
"""

import unittest
import os

class TestSprint2Documentation(unittest.TestCase):
    def setUp(self):
        self.docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
        self.required_docs = [
            "agent_architecture_sprint2.md",
            "react_agent_architecture.md",
            "agent_evaluation_report.md",
            "vector_database_integration.md",
            "chunking_strategy.md",
            "README.md"
        ]

    def test_all_sprint2_docs_exist_and_non_empty(self):
        for doc in self.required_docs:
            doc_path = os.path.join(self.docs_dir, doc)
            self.assertTrue(os.path.exists(doc_path), f"Falta el documento requerido: {doc}")
            self.assertGreater(os.path.getsize(doc_path), 100, f"El documento {doc} está vacío o incompleto.")

if __name__ == "__main__":
    unittest.main()
