"""
Suite de Pruebas Automatizadas para Integración de Herramientas mediante Tool Calling (Issue #15 - S2-04).
Verifica esquemas JSON, detección de intenciones con y sin herramientas, procesamiento de resultados y control de errores.
"""

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app import agent
from app.wellness_agent.tools import AgentToolRegistry
from app.wellness_agent.reasoning import ReasoningEngine


def test_tool_schemas_validity():
    """Verifica que get_tool_schemas devuelva esquemas JSON válidos para las 4 herramientas."""
    registry = AgentToolRegistry()
    schemas = registry.get_tool_schemas()

    assert len(schemas) == 4
    tool_names = [s["name"] for s in schemas]
    assert "get_exercise_alternative" in tool_names
    assert "calculate_nutrition_macros" in tool_names
    assert "assess_injury_risk" in tool_names
    assert "retrieve_rag_knowledge" in tool_names

    for schema in schemas:
        assert "name" in schema
        assert "description" in schema
        assert "parameters" in schema
        assert "required" in schema["parameters"]


def test_intent_detection_with_tools():
    """Escenario CON Herramientas: Verifica la detección e invocación cuando la consulta lo requiere."""
    engine = ReasoningEngine()

    # 1. Alternativas de ejercicio
    name, res = engine.detect_and_execute_tools("user123", "La máquina de pecho está ocupada, ¿qué alternativa me das?")
    assert name == "get_exercise_alternative"
    assert res["status"] == "success"
    assert "exercise_id" in res

    # 2. Nutrición y macros
    name, res = engine.detect_and_execute_tools("user123", "Calcula mis macronutrientes y calorías")
    assert name == "calculate_nutrition_macros"
    assert res["status"] == "success"
    assert "tdee" in res

    # 3. Evaluación de riesgo de lesión
    name, res = engine.detect_and_execute_tools("user123", "Me duele la espalda al hacer sentadilla")
    assert name == "assess_injury_risk"
    assert res["status"] == "success"
    assert "risk_level" in res

    # 4. Consulta de evidencia RAG
    name, res = engine.detect_and_execute_tools("user123", "¿Qué dice la ciencia sobre la periodización de hipertrofia?")
    assert name == "retrieve_rag_knowledge"
    assert isinstance(res, list)


def test_intent_detection_without_tools():
    """Escenario SIN Herramientas: Verifica que mensajes generales no invoquen herramientas innecesarias."""
    engine = ReasoningEngine()

    name, res = engine.detect_and_execute_tools("user123", "Hola, buenos días")
    assert name is None
    assert res is None

    name, res = engine.detect_and_execute_tools("user123", "Muchas gracias por la recomendación")
    assert name is None
    assert res is None


def test_tool_error_handling():
    """Verifica la gestión controlada de errores cuando una herramienta recibe parámetros inválidos."""
    registry = AgentToolRegistry()

    # Invocación de herramienta inexistente
    res1 = registry.execute_tool("unregistered_tool_name")
    assert res1["status"] == "error"
    assert "no registrada" in res1["message"]

    # Invocación con parámetros inválidos
    res2 = registry.execute_tool("get_exercise_alternative", muscle_group=None)
    assert res2["status"] == "error"
    assert "inválido" in res2["message"]


def test_end_to_end_tool_response_synthesis():
    """Verifica que el resultado de la herramienta se incorpore adecuadamente en la respuesta final del agente."""
    response = agent._generate_local_chat_response("user123", "¿Qué alternativa me sugieres para ejercicio de espalda?")
    assert isinstance(response, str)
    assert "get_exercise_alternative" in response or "Espalda" in response
