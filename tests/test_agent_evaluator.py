"""
Pruebas Automatizadas de la Suite de Evaluación del Agente — Wellness Lift (Issue #17)
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.agent_evaluator import AgentQualityEvaluator

class TestAgentQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = AgentQualityEvaluator()

    def test_evaluator_suite_execution(self):
        report = self.evaluator.run_suite()
        self.assertEqual(report["total_test_cases"], 5)
        self.assertEqual(report["overall_accuracy_pct"], 100.0)
        self.assertGreater(len(report["limitations_identified"]), 0)
        self.assertGreater(len(report["proposed_improvements"]), 0)

if __name__ == "__main__":
    unittest.main()
