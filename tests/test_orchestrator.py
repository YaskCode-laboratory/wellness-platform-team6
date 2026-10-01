"""
Suite de Pruebas Automatizadas para el Orchestrator Agent (Issue #20 - S3-02).
Verifica clasificación de intenciones, delegación individual y compuesta, manejo de errores e integración del endpoint FastAPI.
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
    """Verifica la orquestación compuesta dinámica para solicitudes que abarcan múltiples dominios detectados."""
    user_id = "test_user_orch_multi"
    res = orchestrator.handle_multidomain_delegation(user_id, "Dame una rutina de hombros y mis macros de comida")

    assert "Multidomain" in res.agent_name
    assert res.status == "success"
    assert "WellnessCoachAgent2.0" in res.metadata["delegated_agents"]
    assert "NutritionAgent" in res.metadata["delegated_agents"]


def test_multidomain_motivation_analytics_delegation(orchestrator):
    """Verifica la delegación dinámica multidominio para motivación y analítica."""
    user_id = "test_user_orch_multi_moti_analy"
    res = orchestrator.handle_multidomain_delegation(user_id, "No tengo ánimo y quiero ver mis sesiones e historial de volumen")

    assert "Multidomain" in res.agent_name
    assert res.status == "success"
    assert "MotivationAgent" in res.metadata["delegated_agents"]
    assert "AnalyticsAgent" in res.metadata["delegated_agents"]


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


def test_detect_domains(orchestrator):
    """Verifica la detección dinámica de múltiples dominios activos."""
    domains = orchestrator.detect_domains("Quiero una rutina de piernas y calcular mis macronutrientes de nutrición")
    assert AgentIntent.WORKOUT_BIOMECHANICS in domains
    assert AgentIntent.NUTRITION in domains
    assert len(domains) == 2


def test_multidomain_composite_statuses(orchestrator, monkeypatch):
    """Verifica el cálculo de estados compuestos (success, partial_success, error_fallback)."""
    from app.wellness_agent.communication import InterAgentResponse

    user_id = "test_composite"
    msg = "Rutina de piernas y nutrición"

    # 1. Caso success (ambos tienen éxito)
    res_success = orchestrator.handle_multidomain_delegation(user_id, msg)
    assert res_success.status == "success"

    # 2. Caso partial_success (coach falla, nutrición pasa)
    def mock_faulty_coach(*args, **kwargs):
        return InterAgentResponse("t1", "tr1", "WellnessCoachAgent2.0", "error_fallback", "Error temporal coach")

    monkeypatch.setattr(orchestrator, "delegate_to_coach", mock_faulty_coach)
    res_partial = orchestrator.handle_multidomain_delegation(user_id, msg)
    assert res_partial.status == "partial_success"

    # 3. Caso error_fallback (ambos fallan)
    def mock_faulty_nutri(*args, **kwargs):
        return InterAgentResponse("t2", "tr2", "NutritionAgent", "error_fallback", "Error temporal nutri")

    monkeypatch.setattr(orchestrator, "delegate_to_nutrition", mock_faulty_nutri)
    res_error = orchestrator.handle_multidomain_delegation(user_id, msg)
    assert res_error.status == "error_fallback"


def test_fastapi_chat_endpoint_integration():
    """Verifica la integración real del endpoint POST /api/v1/ai/chat/{user_id} mediante TestClient de FastAPI."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    user_id = "test_user_fastapi_endpoint"
    payload = {"message": "Dame una rutina para piernas y mis macros de nutrición"}

    response = client.post(f"/api/v1/ai/chat/{user_id}", json=payload)
    assert response.status_code == 200, f"Respuesta esperada 200, obtenido {response.status_code}"

    data = response.json()
    assert "response" in data, "La respuesta debe contener la clave 'response'"
    assert "intent" in data, "La respuesta debe contener la clave 'intent'"
    assert "delegated_agent" in data, "La respuesta debe contener la clave 'delegated_agent'"
    assert "status" in data, "La respuesta debe contener la clave 'status'"
    assert data["intent"] == AgentIntent.MULTIDOMAIN.value
    assert data["status"] in ("success", "partial_success", "error_fallback")
