"""
Suite de Pruebas Automatizadas para la Arquitectura Multiagente (Issue #19 - S3-01).
Verifica la presencia y estructura de la documentación arquitectónica, la inclusión de diagramas Mermaid y la justificación del patrón Supervisor.
"""

from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_multiagent_architecture_doc_integrity():
    """Verifica que docs/architecture/multiagent-architecture.md exista y contenga diagramas Mermaid y justificaciones."""
    doc_path = ROOT_DIR / "docs" / "architecture" / "multiagent-architecture.md"
    assert doc_path.exists(), "El archivo multiagent-architecture.md debe existir"

    content = doc_path.read_text(encoding="utf-8")
    assert len(content) > 1000, "El documento multiagent-architecture.md debe contener diseño detallado"
    assert "```mermaid" in content, "El documento debe contener diagramas Mermaid"
    assert "Orchestrator Agent" in content, "Debe definir al Orchestrator Agent"
    assert "Wellness Coach Agent 2.0" in content, "Debe hacer referencia al agente especializado del equipo"
    assert "Supervisor" in content, "Debe justificar el patrón Supervisor"


def test_adr_005_integrity():
    """Verifica que docs/architecture/adr/005-multiagent-orchestration-pattern.md exista y registre la decisión ADR 005."""
    adr_path = ROOT_DIR / "docs" / "architecture" / "adr" / "005-multiagent-orchestration-pattern.md"
    assert adr_path.exists(), "El archivo 005-multiagent-orchestration-pattern.md debe existir"

    content = adr_path.read_text(encoding="utf-8")
    assert "ADR-005" in content
    assert "Patrón Supervisor" in content or "Supervisor" in content
    assert "Orchestrator Agent" in content
    assert "Hierarchical" in content, "ADR-005 debe incluir el patrón Hierarchical en la comparativa de patrones evaluados"
