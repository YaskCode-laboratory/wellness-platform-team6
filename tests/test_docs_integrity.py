"""
Suite de Pruebas Automatizadas para la Integridad de la Documentación de Arquitectura (Issue #11 - S1-07).
Verifica que los archivos de arquitectura existan, no estén vacíos y contengan los diagramas y secciones requeridas.
"""

from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent


def test_rag_architecture_doc_integrity():
    """Verifica que docs/architecture/rag-architecture.md exista y contenga diagramas Mermaid."""
    doc_path = ROOT_DIR / "docs" / "architecture" / "rag-architecture.md"
    assert doc_path.exists(), "El archivo rag-architecture.md debe existir"

    content = doc_path.read_text(encoding="utf-8")
    assert len(content) > 500, "El documento rag-architecture.md debe tener contenido detallado"
    assert "```mermaid" in content, "El documento debe contener diagramas Mermaid"
    assert "MarkdownSemanticChunker" in content
    assert "EmbeddingsGenerator" in content
    assert "RAGEvaluator" in content


def test_adr_doc_integrity():
    """Verifica que el registro de decisiones de arquitectura ADR exista."""
    adr_path = ROOT_DIR / "docs" / "architecture" / "adr" / "001-rag-architecture-decisions.md"
    assert adr_path.exists(), "El archivo 001-rag-architecture-decisions.md debe existir"

    content = adr_path.read_text(encoding="utf-8")
    assert "ADR-001" in content
    assert "ADR-002" in content
    assert "ADR-003" in content


def test_system_overview_doc_integrity():
    """Verifica que el resumen del sistema system-overview.md esté actualizado."""
    overview_path = ROOT_DIR / "docs" / "architecture" / "system-overview.md"
    assert overview_path.exists(), "El archivo system-overview.md debe existir"

    content = overview_path.read_text(encoding="utf-8")
    assert "Wellness Lift SaaS" in content
    assert "rag-architecture.md" in content
