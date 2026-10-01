"""
Suite de Pruebas Automatizadas de Evaluación y Observabilidad Multiagente (Issue #24 - S3-06).
Verifica clasificación de intenciones, precisión de delegación, colaboración inter-agente,
medición de latencia y trazabilidad estructurada de extremo a extremo.
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.multiagent_evaluator import MultiAgentFlowEvaluator
    from app.orchestrator import OrchestratorAgent, AgentIntent
except ModuleNotFoundError:
    try:
        from multiagent_evaluator import MultiAgentFlowEvaluator
        from orchestrator import OrchestratorAgent, AgentIntent
    except ModuleNotFoundError:
        from .multiagent_evaluator import MultiAgentFlowEvaluator
        from .orchestrator import OrchestratorAgent, AgentIntent


class TestMultiAgentEvaluation(unittest.TestCase):
    def setUp(self):
        os.environ["DISABLE_EXTERNAL_LLM"] = "true"
        self.evaluator = MultiAgentFlowEvaluator()
        self.orchestrator = OrchestratorAgent()

    def test_intent_classification_coverage(self):
        """Verifica que el supervisor clasifique correctamente los 4 dominios y el caso multidominio."""
        self.assertEqual(
            self.orchestrator.classify_intent("Recomiéndame una rutina para hipertrofia de pecho"),
            AgentIntent.WORKOUT_BIOMECHANICS
        )
        self.assertEqual(
            self.orchestrator.classify_intent("Calcula mis macronutrientes y calorías de mi dieta"),
            AgentIntent.NUTRITION
        )
        self.assertEqual(
            self.orchestrator.classify_intent("Hoy me siento muy desanimado y con flojera para entrenar"),
            AgentIntent.MOTIVATION
        )
        self.assertEqual(
            self.orchestrator.classify_intent("Muestra mi récord de sesiones y volumen total acumulado"),
            AgentIntent.ANALYTICS
        )
        self.assertEqual(
            self.orchestrator.classify_intent("Ajusta mi rutina de pierna y calcula mis calorías y macros"),
            AgentIntent.MULTIDOMAIN
        )

    def test_single_agent_delegation(self):
        """Verifica la delegación directa a agentes especializados individuales."""
        res_coach = self.orchestrator.process_user_request("user_01", "¿Qué ejercicio hago para espalda?")
        self.assertEqual(res_coach["delegated_agent"], "WellnessCoachAgent2.0")
        self.assertIn("trace_id", res_coach)

        res_nutri = self.orchestrator.process_user_request("user_02", "Calcula mis macros y calorías")
        self.assertEqual(res_nutri["delegated_agent"], "NutritionAgent")
        self.assertIn("trace_id", res_nutri)

        res_moti = self.orchestrator.process_user_request("user_03", "No tengo ganas ni ánimo de entrenar hoy")
        self.assertEqual(res_moti["delegated_agent"], "MotivationAgent")
        self.assertIn("trace_id", res_moti)

        res_ana = self.orchestrator.process_user_request("user_04", "Muestra mi volumen total y progreso")
        self.assertEqual(res_ana["delegated_agent"], "AnalyticsAgent")
        self.assertIn("trace_id", res_ana)

    def test_interagent_collaboration_multidomain(self):
        """Verifica el escenario de colaboración inter-agente multidominio."""
        prompt = "Quiero planificar mi rutina de entrenamiento de piernas y mis macros de nutrición"
        res = self.orchestrator.process_user_request("user_collab", prompt)

        self.assertEqual(res["intent"], AgentIntent.MULTIDOMAIN.value)
        self.assertEqual(res["delegated_agent"], "OrchestratorAgent (Multidomain)")
        self.assertIn("WellnessCoachAgent2.0", res["metadata"]["delegated_agents"])
        self.assertIn("NutritionAgent", res["metadata"]["delegated_agents"])
        self.assertIn("trace_id", res)
        self.assertGreater(len(res["response"]), 50)

    def test_observability_and_traces_generation(self):
        """Verifica que se generen trazas completas de orquestación con trace_id y registros."""
        res = self.orchestrator.process_user_request("user_trace_01", "Hola, ¿cómo estás?")
        self.assertTrue(res["trace_id"].startswith("TRACE-"))
        self.assertGreater(len(res["trace_history"]), 0)

    def test_trace_id_uniqueness_and_continuity(self):
        """
        Verifica que solicitudes diferentes generen trace_id distintos y que las delegaciones
        de un mismo flujo multidominio mantengan el mismo trace_id.
        """
        res1 = self.orchestrator.process_user_request("user_uq_01", "¿Qué ejercicios puedo hacer para bíceps?")
        res2 = self.orchestrator.process_user_request("user_uq_02", "¿Qué ejercicios puedo hacer para tríceps?")
        
        # Unicidad
        self.assertNotEqual(res1["trace_id"], res2["trace_id"])

        # Continuidad en flujo multidominio
        res_multi = self.orchestrator.process_user_request("user_uq_03", "Diseña mi rutina de pierna y calcula mis calorías")
        shared_trace_id = res_multi["trace_id"]
        
        trace_history = self.orchestrator.tracer.get_trace_history(shared_trace_id)
        self.assertGreaterEqual(len(trace_history), 3)
        for entry in trace_history:
            self.assertEqual(entry["task_id"].startswith("TASK-"), True)

    def test_latency_measurement_presence(self):
        """Verifica que se mida y registre el tiempo de respuesta (latencia en ms)."""
        res = self.orchestrator.process_user_request("user_lat_01", "¿Qué alternativas tengo para sentadilla?")
        self.assertIn("execution_time_ms", res)
        self.assertGreaterEqual(res["execution_time_ms"], 0.0)

    def test_multiagent_evaluator_suite_execution(self):
        """Verifica la ejecución integral del MultiAgentFlowEvaluator y sus métricas consolidadas."""
        summary = self.evaluator.run_suite()

        self.assertEqual(summary["total_test_cases"], 7)
        self.assertEqual(summary["intent_accuracy_pct"], 100.0)
        self.assertEqual(summary["delegation_accuracy_pct"], 100.0)
        self.assertEqual(summary["collaboration_success_pct"], 100.0)
        self.assertGreater(summary["average_latency_ms"], 0.0)
        self.assertGreaterEqual(summary["overall_quality_score_pct"], 0.0)
        self.assertGreater(len(summary["limitations_identified"]), 0)
        self.assertGreater(len(summary["proposed_improvements"]), 0)

    def test_error_and_fallback_handling(self):
        """Verifica el manejo de errores/fallbacks cuando faltan datos antropométricos o se previenen ciclos."""
        res_fallback = self.orchestrator.process_user_request("unregistered_user_99", "Calcula mis calorías y macronutrientes")
        self.assertEqual(res_fallback["delegated_agent"], "NutritionAgent")
        self.assertIn("Perfil", res_fallback["response"])


if __name__ == "__main__":
    unittest.main()
