"""
Pruebas Automatizadas de la Suite de Evaluación del Agente — Wellness Lift (Issue #17 & Issue #18)
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.agent_evaluator import AgentQualityEvaluator
except ModuleNotFoundError:
    try:
        from agent_evaluator import AgentQualityEvaluator
    except ModuleNotFoundError:
        from .agent_evaluator import AgentQualityEvaluator

class TestAgentQualityEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = AgentQualityEvaluator()

    def test_evaluator_suite_execution(self):
        report = self.evaluator.run_suite()
        self.assertEqual(report["total_test_cases"], 5)
        self.assertIn(report["overall_accuracy_pct"], [80.0, 100.0])
        self.assertIn(report["passed_test_cases"], [4, 5])
        self.assertGreater(len(report["limitations_identified"]), 0)
        self.assertGreater(len(report["proposed_improvements"]), 0)

if __name__ == "__main__":
    unittest.main()
