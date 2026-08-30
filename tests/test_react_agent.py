"""
Pruebas Automatizadas del Patrón ReAct — Wellness Coach Agent 2.0 (Issue #16)
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.react_agent import ReActAgent

class TestReActAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ReActAgent()

    def test_react_loop_lumbar_condition(self):
        result = self.agent.run_react_loop("Ajusta mi rutina por dolor lumbar", athlete_id="user123")
        self.assertGreaterEqual(result["total_iterations"], 3)
        self.assertIn("FINAL_ANSWER", [s["action"] for s in result["steps"]])
        self.assertIn("Hernia Discal L4-L5", result["final_answer"])

    def test_react_loop_knee_condition(self):
        result = self.agent.run_react_loop("Revisa lesión de menisco", athlete_id="user456")
        self.assertGreaterEqual(result["total_iterations"], 3)
        self.assertIn("Lesión de Rodilla", result["final_answer"])

    def test_anti_loop_protection(self):
        # Verificar que el bucle no supere el límite de iteraciones (max 5)
        result = self.agent.run_react_loop("Consulta repetitiva", athlete_id="user123", max_iterations=5)
        self.assertLessEqual(result["total_iterations"], 5)

if __name__ == "__main__":
    unittest.main()
