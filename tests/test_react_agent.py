"""
Pruebas Automatizadas del Patrón ReAct — Wellness Coach Agent 2.0 (Issue #16 & Issue #18)
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.react_agent import ReActAgent
except ModuleNotFoundError:
    try:
        from react_agent import ReActAgent
    except ModuleNotFoundError:
        from .react_agent import ReActAgent

class TestReActAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ReActAgent()

    def test_react_loop_injury_query(self):
        """Verifica que consultas de dolor/lesión invoquen assess_injury_risk y alternativas seguras."""
        result = self.agent.run_react_loop("Ajusta mi rutina por dolor lumbar", athlete_id="user123")
        actions = [s["action"] for s in result["steps"]]
        self.assertIn("assess_injury_risk", actions)
        self.assertIn("FINAL_ANSWER", actions)
        self.assertTrue(len(result["final_answer"]) > 0)

    def test_react_loop_nutrition_query(self):
        """Verifica que las acciones dependan de la consulta (nutrición llama a calculate_nutrition_macros)."""
        result = self.agent.run_react_loop("Calcula mis macronutrientes y calorías", athlete_id="user123")
        actions = [s["action"] for s in result["steps"]]
        self.assertIn("calculate_nutrition_macros", actions)
        self.assertNotIn("assess_injury_risk", actions)  # Evita llamadas innecesarias
        self.assertIn("FINAL_ANSWER", actions)

    def test_react_loop_rag_query(self):
        """Verifica que consultas sobre periodización/ciencia invoquen retrieve_rag_knowledge."""
        result = self.agent.run_react_loop("¿Qué dice la ciencia sobre la periodización de hipertrofia?", athlete_id="user123")
        actions = [s["action"] for s in result["steps"]]
        self.assertIn("retrieve_rag_knowledge", actions)
        self.assertIn("FINAL_ANSWER", actions)

    def test_anti_loop_protection(self):
        """Demuestra explícitamente que la detección de ciclo duplicado interrumpe la iteración y fuerza FINAL_ANSWER."""
        result = self.agent.run_react_loop(
            user_prompt="Consulta para forzar bucle",
            athlete_id="user123",
            max_iterations=5,
            force_repeat_action="get_exercise_alternative"
        )
        self.assertTrue(result["loop_detected"])
        self.assertIn("FINAL_ANSWER", [s["action"] for s in result["steps"]])
        # El ciclo debe haber finalizado antes del máximo de iteraciones
        self.assertLess(result["total_iterations"], 5)
        # La observación del pensamiento debe confirmar la detección del ciclo
        thoughts_str = " ".join([s["thought"] for s in result["steps"]])
        self.assertIn("ciclo duplicado", thoughts_str.lower())

if __name__ == "__main__":
    unittest.main()
