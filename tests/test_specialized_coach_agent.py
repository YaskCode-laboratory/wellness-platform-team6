"""
Suite de Pruebas Automatizadas para el Agente Especializado del Equipo 6 (Issue #21 - S3-03).
Verifica responsabilidad de dominio, delimitación de fronteras fuera de dominio, herramientas integradas y orquestación.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.wellness_agent.coach_specialist import WellnessCoachSpecialist, _specialist_instance
from app.orchestrator import OrchestratorAgent


@pytest.fixture
def specialist():
    """Fixture para obtener una instancia limpia del Agente Especializado."""
    return WellnessCoachSpecialist()


def test_domain_boundary_verification(specialist):
    """Verifica la delimitación estricta de fronteras de dominio del especialista."""
    # Consultas dentro de dominio (Biomecánica y Entrenamiento Adaptativo)
    assert specialist.is_query_in_domain("Necesito una rutina para hipertrofia de piernas") is True
    assert specialist.is_query_in_domain("¿Qué alternativa tengo para press de banca con dolor de hombro?") is True
    assert specialist.is_query_in_domain("Tengo hernia discal L4-L5, ¿puedo hacer peso muerto?") is True

    # Consultas fuera de dominio (Nutrición/Cocina pura)
    assert specialist.is_query_in_domain("Dame una receta de cocina vegetal para la cena") is False
    assert specialist.is_query_in_domain("Menú semanal de dieta keto con lista de compras") is False


def test_in_domain_specialized_request(specialist):
    """Verifica el procesamiento dentro de dominio utilizando herramientas y razonamiento."""
    user_id = "test_spec_in_domain"
    result = specialist.process_specialized_request(user_id, "Tengo hernia discal, ¿qué alternativas seguras de piernas hay?")

    assert result["user_id"] == user_id
    assert result["agent_name"] == "WellnessCoachAgent2.0"
    assert result["in_domain"] is True
    assert result["status"] == "success"
    assert len(result["response"]) > 0


def test_out_of_domain_specialized_request(specialist):
    """Verifica la redirección respetuosa cuando la consulta está fuera de dominio."""
    user_id = "test_spec_out_domain"
    result = specialist.process_specialized_request(user_id, "Dame una receta de cocina vegetal paso a paso")

    assert result["user_id"] == user_id
    assert result["agent_name"] == "WellnessCoachAgent2.0"
    assert result["in_domain"] is False
    assert result["status"] == "out_of_domain_redirect"
    assert "Nutrition Agent" in result["response"]


def test_orchestrator_integration_with_specialist():
    """Verifica que el Orchestrator Agent invoque correctamente al agente especializado del equipo."""
    orch = OrchestratorAgent()
    res = orch.process_user_request("test_user_orch_spec", "Recomiéndame una rutina para cuádriceps")

    assert res["delegated_agent"] == "WellnessCoachAgent2.0"
    assert res["status"] == "success"
    assert len(res["response"]) > 0


def test_adaptive_routine_generation(specialist):
    """Verifica la generación de rutinas adaptativas por parte del agente especializado."""
    routine = specialist.generate_adaptive_routine("test_user_routine_spec")
    assert "weekly_schedule" in routine
    assert len(routine["weekly_schedule"]) >= 3
