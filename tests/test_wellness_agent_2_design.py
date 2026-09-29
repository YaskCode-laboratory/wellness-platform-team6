"""
Suite de Pruebas Automatizadas para el Diseño del Wellness Coach Agent 2.0 (Issue #13 - S2-02).
Verifica la presencia, integridad y validez de la documentación, diagramas Mermaid y prompts de sistema.
"""

from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_wellness_agent_design_doc_integrity():
    """Verifica que docs/agents/wellness-agent.md exista y contenga diagramas Mermaid y secciones requeridas."""
    doc_path = ROOT_DIR / "docs" / "agents" / "wellness-agent.md"
    assert doc_path.exists(), "El archivo wellness-agent.md debe existir"

    content = doc_path.read_text(encoding="utf-8")
    assert len(content) > 500, "El documento wellness-agent.md debe contener diseño detallado"
    assert "```mermaid" in content, "El documento debe contener diagramas Mermaid"
    assert "ReAct" in content or "Tool Calling" in content
    assert "assess_injury_risk" in content
    assert "retrieve_rag_knowledge" in content


def test_tools_doc_integrity():
    """Verifica que docs/agents/tools.md contenga la especificación de herramientas del agente."""
    tools_path = ROOT_DIR / "docs" / "agents" / "tools.md"
    assert tools_path.exists(), "El archivo tools.md debe existir"

    content = tools_path.read_text(encoding="utf-8")
    assert "get_exercise_alternative" in content
    assert "calculate_nutrition_macros" in content
    assert "assess_injury_risk" in content
    assert "retrieve_rag_knowledge" in content


def test_system_prompt_coach_2_integrity():
    """Verifica que prompts/system_prompt_wellness_coach_2.0.txt exista y contenga los guardrails de seguridad."""
    prompt_path = ROOT_DIR / "prompts" / "system_prompt_wellness_coach_2.0.txt"
    assert prompt_path.exists(), "El archivo system_prompt_wellness_coach_2.0.txt debe existir"

    content = prompt_path.read_text(encoding="utf-8")
    assert "Wellness Coach AI 2.0" in content
    assert "Hernia Discal" in content
    assert "Rodilla" in content
    assert "Manguito Rotador" in content
