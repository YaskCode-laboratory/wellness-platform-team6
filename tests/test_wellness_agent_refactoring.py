"""
Suite de Pruebas Unitarias e Integración para la Refactorización del Wellness Agent (Issue #12 - S2-01).
Verifica la modularidad del paquete app.wellness_agent, memoria, registro de herramientas y retrocompatibilidad de agent.py.
"""

import sys
from pathlib import Path

import pytest

# Agregar src/backend a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app import agent
from app.wellness_agent import (
    EXERCISE_CATALOG,
    SPLIT_TEMPLATES,
    LLMProviderManager,
    ConversationMemoryManager,
    AgentToolRegistry,
    ReasoningEngine,
)


def test_catalog_structure():
    """Verifica que el catálogo de ejercicios y las plantillas de división estén bien estructurados."""
    assert "Pecho" in EXERCISE_CATALOG
    assert "Espalda" in EXERCISE_CATALOG
    assert "Piernas" in EXERCISE_CATALOG
    assert 3 in SPLIT_TEMPLATES
    assert len(SPLIT_TEMPLATES[3]) == 3


def test_llm_provider_manager_initialization(monkeypatch):
    """Verifica la inicialización del administrador de proveedores LLM utilizando variable de entorno ficticia."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-mock-test-key-12345")
    manager = LLMProviderManager()
    key = manager.get_openrouter_key()
    assert key == "sk-or-v1-mock-test-key-12345"

    # Verificar que retorne None cuando no está configurada la variable de entorno
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert manager.get_openrouter_key() is None


def test_conversation_memory_manager():
    """Verifica el funcionamiento de la memoria conversacional multi-turno por usuario."""
    memory = ConversationMemoryManager(max_history_turns=5)
    user_id = "test_user_memory_01"

    memory.add_message(user_id, "user", "Hola, me duele la espalda.")
    memory.add_message(user_id, "assistant", "Te recomiendo evitar sentadillas con barra libre.")

    history = memory.get_history(user_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    formatted = memory.get_formatted_history(user_id)
    assert "Usuario:" in formatted
    assert "Asistente:" in formatted

    memory.clear_memory(user_id)
    assert len(memory.get_history(user_id)) == 0


def test_agent_tool_registry():
    """Verifica la ejecución de herramientas registradas en AgentToolRegistry."""
    registry = AgentToolRegistry()

    # 1. Herramienta de alternativas de ejercicios
    alt_res = registry.execute_tool("get_exercise_alternative", muscle_group="Pecho")
    assert alt_res["status"] == "success"
    assert alt_res["muscle_group"] == "Pecho"
    assert "exercise_id" in alt_res

    # 2. Herramienta de evaluación de riesgo de lesión
    risk_res = registry.execute_tool("assess_injury_risk", user_id="user123", exercise_name="Sentadilla con Barra")
    assert "risk_level" in risk_res

    # 3. Herramienta de consulta RAG
    rag_res = registry.execute_tool("retrieve_rag_knowledge", query_text="hernia discal", top_k=2)
    assert isinstance(rag_res, list)


def test_reasoning_engine_local_routine():
    """Verifica la generación de rutina determinista local en ReasoningEngine."""
    engine = ReasoningEngine()
    routine = engine.generate_local_routine("user123")

    assert "focus" in routine
    assert "weekly_schedule" in routine
    assert len(routine["weekly_schedule"]) > 0


def test_agent_facade_backward_compatibility():
    """Verifica que las funciones de la fachada agent.py sigan siendo retrocompatibles."""
    routine = agent.generate_weekly_routine("user123")
    assert "weekly_schedule" in routine
    assert len(routine["weekly_schedule"]) > 0

    chat_response = agent.generate_chat_response("user123", "Hola, ¿qué ejercicios puedo hacer para piernas?")
    assert isinstance(chat_response, str)
    assert len(chat_response) > 0
