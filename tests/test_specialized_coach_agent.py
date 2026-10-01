"""
Suite de Pruebas Automatizadas para el Agente Especializado del Equipo 6 (Issue #21 - S3-03).
Verifica responsabilidad de dominio, delimitación de fronteras fuera de dominio, lectura de fitness_profile, RAG/Tool Calling, System Prompt oficial y propagación de out_of_domain.
"""

import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.wellness_agent.coach_specialist import WellnessCoachSpecialist, load_system_prompt
from app.orchestrator import OrchestratorAgent


if pytest:
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
    assert specialist.is_query_in_domain("Recomiéndame una rutina para cuádriceps") is True

    # Consultas fuera de dominio (Nutrición/Cocina pura)
    assert specialist.is_query_in_domain("Dame una receta de cocina vegetal para la cena") is False
    assert specialist.is_query_in_domain("Menú semanal de dieta keto con lista de compras") is False

    # Consultas fuera de dominio generales (No relacionadas con el entrenamiento/biomecánica)
    assert specialist.is_query_in_domain("¿Cuál es la capital de Francia?") is False
    assert specialist.is_query_in_domain("¿Cómo programar un algoritmo en Python?") is False
    assert specialist.is_query_in_domain("¿Cuál es el precio del dólar hoy?") is False


def test_system_prompt_single_source_of_truth(specialist):
    """Verifica que el System Prompt provenga exactamente del archivo oficial prompts/system_prompt_wellness_coach_2.0.txt."""
    loaded = load_system_prompt()
    assert "Wellness Coach AI 2.0" in loaded or "entrenador" in loaded.lower()
    assert "REGLAS DE ACTUACIÓN" in loaded
    assert "GUARDRAILS DE SEGURIDAD BIOMECÁNICA" in loaded
    assert specialist.system_prompt == loaded


def test_in_domain_specialized_request(specialist):
    """Verifica el procesamiento dentro de dominio utilizando fitness_profile, RAG y herramientas."""
    user_id = "user123"  # Usuario en DB mock con fitness_profile completo
    result = specialist.process_specialized_request(user_id, "Tengo hernia discal, ¿qué alternativas seguras de piernas hay?")

    assert result["user_id"] == user_id
    assert result["agent_name"] == "WellnessCoachAgent2.0"
    assert result["in_domain"] is True
    assert result["status"] == "success"
    assert "fitness_profile" in result
    assert "health_conditions" in result
    assert len(result["response"]) > 0


def test_out_of_domain_specialized_request(specialist):
    """Verifica el retorno de estado out_of_domain cuando la consulta está fuera del dominio del coach."""
    user_id = "test_spec_out_domain"
    result = specialist.process_specialized_request(user_id, "Dame una receta de cocina vegetal paso a paso")

    assert result["user_id"] == user_id
    assert result["agent_name"] == "WellnessCoachAgent2.0"
    assert result["in_domain"] is False
    assert result["status"] == "out_of_domain"
    assert len(result["response"]) > 0


def test_out_of_domain_propagation_to_orchestrator():
    """Verifica que el estado out_of_domain y in_domain=False se propaguen formalmente hasta el Orchestrator."""
    orch = OrchestratorAgent()
    res = orch.process_user_request("test_user_out_domain_prop", "Dame una receta de cocina vegetal paso a paso")

    assert res["status"] == "out_of_domain" or res["metadata"].get("in_domain") is False
    assert res["delegated_agent"] == "WellnessCoachAgent2.0"


def test_orchestrator_integration_with_specialist():
    """Verifica que el Orchestrator Agent invoque correctamente al agente especializado del equipo."""
    orch = OrchestratorAgent()
    res = orch.process_user_request("test_user_orch_spec", "Recomiéndame una rutina para cuádriceps")

    assert res["delegated_agent"] == "WellnessCoachAgent2.0"
    assert res["status"] == "success"
    assert len(res["response"]) > 0


def test_adaptive_routine_generation(specialist):
    """Verifica la generación de rutinas adaptativas por parte del agente especializado."""
    routine = specialist.generate_adaptive_routine("user123")
    assert "weekly_schedule" in routine
    assert len(routine["weekly_schedule"]) >= 3


class TestSpecializedCoachAgent(unittest.TestCase):
    def setUp(self):
        self.specialist = WellnessCoachSpecialist()

    def test_domain_boundary_verification_unit(self):
        test_domain_boundary_verification(self.specialist)

    def test_system_prompt_single_source_of_truth_unit(self):
        test_system_prompt_single_source_of_truth(self.specialist)

    def test_in_domain_specialized_request_unit(self):
        test_in_domain_specialized_request(self.specialist)

    def test_out_of_domain_specialized_request_unit(self):
        test_out_of_domain_specialized_request(self.specialist)

    def test_out_of_domain_propagation_to_orchestrator_unit(self):
        test_out_of_domain_propagation_to_orchestrator()

    def test_orchestrator_integration_with_specialist_unit(self):
        test_orchestrator_integration_with_specialist()

    def test_adaptive_routine_generation_unit(self):
        test_adaptive_routine_generation(self.specialist)


if __name__ == "__main__":
    unittest.main()
