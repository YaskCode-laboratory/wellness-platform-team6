"""
Suite de Pruebas Automatizadas para el Orchestrator Agent (Issue #20 - S3-02).
Verifica clasificación de intenciones, delegación individual y compuesta, manejo de errores y respuestas de FastAPI.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.orchestrator import OrchestratorAgent, AgentIntent, SpecializedAgentResponse


@pytest.fixture
def orchestrator():
    """Fixture para obtener una instancia limpia del Orchestrator Agent."""
    return OrchestratorAgent()


def test_intent_classification(orchestrator):
    """Verifica la clasificación precisa de intenciones en diversos dominios del usuario."""
    assert orchestrator.classify_intent("Necesito una rutina para piernas adaptada") == AgentIntent.WORKOUT_BIOMECHANICS
    assert orchestrator.classify_intent("Calcula mis macronutrientes y TDEE calórico") == AgentIntent.NUTRITION
    assert orchestrator.classify_intent("No tengo ánimo ni constancia para entrenar") == AgentIntent.MOTIVATION
    assert orchestrator.classify_intent("¿Cuántas sesiones e historial de volumen llevo?") == AgentIntent.ANALYTICS
    assert orchestrator.classify_intent("Dame una rutina de ejercicios y mis macros de nutrición") == AgentIntent.MULTIDOMAIN
    assert orchestrator.classify_intent("Hola buenos días") == AgentIntent.GENERAL


def test_single_agent_delegation(orchestrator):
    """Verifica la delegación individual hacia los agentes especializados."""
    user_id = "test_user_orch_01"

    # 1. Delegación a Wellness Coach 2.0
    coach_res = orchestrator.delegate_to_coach(user_id, "Recomiéndame un ejercicio de Pecho")
    assert coach_res.agent_name == "WellnessCoachAgent2.0"
    assert coach_res.status == "success"
    assert len(coach_res.content) > 0

    # 2. Delegación a Nutrition Agent
    nutri_res = orchestrator.delegate_to_nutrition(user_id, "Ver mis macros")
    assert nutri_res.agent_name == "NutritionAgent"
    assert nutri_res.status == "success"
    assert "Nutrition Agent" in nutri_res.content

    # 3. Delegación a Motivation Agent
    moti_res = orchestrator.delegate_to_motivation(user_id, "Necesito motivación")
    assert moti_res.agent_name == "MotivationAgent"
    assert moti_res.status == "success"
    assert "Motivation Agent" in moti_res.content

    # 4. Delegación a Analytics Agent
    analy_res = orchestrator.delegate_to_analytics(user_id, "Ver mi volumen acumulado")
    assert analy_res.agent_name == "AnalyticsAgent"
    assert analy_res.status == "success"
    assert "Analytics Agent" in analy_res.content


def test_multidomain_delegation(orchestrator):
    """Verifica la orquestación compuesta para solicitudes que abarcan múltiples dominios."""
    user_id = "test_user_orch_multi"
    res = orchestrator.handle_multidomain_delegation(user_id, "Dame una rutina de hombros y mis macros de comida")

    assert res.agent_name == "OrchestratorAgent (Multidomain)"
    assert res.status == "success"
    assert "Wellness Coach 2.0" in res.content
    assert "Nutrition Agent" in res.content


def test_orchestration_error_handling(orchestrator):
    """Verifica la captura controlada de errores y generación de respuesta estructurada de fallback."""
    res = orchestrator.handle_orchestration_error("FaultyAgent", Exception("Conexión interrumpida"))

    assert res.agent_name == "FaultyAgent"
    assert res.status == "error_fallback"
    assert "Aviso de Orquestación" in res.content
    assert "Conexión interrumpida" in res.metadata["error"]


def test_process_user_request_end_to_end(orchestrator):
    """Verifica el flujo completo process_user_request retornado al backend."""
    result = orchestrator.process_user_request("test_user_e2e", "¿Qué ejercicios puedo hacer para triceps?")

    assert result["user_id"] == "test_user_e2e"
    assert result["intent"] == AgentIntent.WORKOUT_BIOMECHANICS.value
    assert result["orchestrated_by"] == "OrchestratorAgent"
    assert result["delegated_agent"] == "WellnessCoachAgent2.0"
    assert result["status"] == "success"
    assert len(result["response"]) > 0
