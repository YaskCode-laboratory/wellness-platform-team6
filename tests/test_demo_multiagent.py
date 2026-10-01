"""
Suite de Pruebas Automatizadas de la Demo y Documentación del Sprint 3 (Issue #25 - S3-07).
Verifica que el script de demostración ejecute exitosamente y que toda la documentación técnica requerida exista y tenga contenido válido.
"""

import unittest
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestSprint3DemoAndDocs(unittest.TestCase):
    def test_demo_multiagent_execution(self):
        """Verifica que scripts/demo_multiagent.py ejecute de principio a fin con código de salida 0."""
        demo_script = ROOT_DIR / "scripts" / "demo_multiagent.py"
        self.assertTrue(demo_script.exists(), "El script scripts/demo_multiagent.py debe existir")

        result = subprocess.run(
            [sys.executable, str(demo_script)],
            capture_output=True,
            text=True,
            cwd=str(ROOT_DIR),
            timeout=120
        )
        self.assertEqual(result.returncode, 0, f"La demo falló con error:\n{result.stderr}")
        self.assertIn("Demostracion completada exitosamente", result.stdout)
        self.assertIn("Tasa de Acierto en Delegacion  : 100.0%", result.stdout)

    def test_sprint3_documentation_files_integrity(self):
        """Verifica que todos los documentos arquitectónicos y reportes del Sprint 3 existan y no estén vacíos."""
        required_docs = [
            ROOT_DIR / "docs" / "architecture" / "multiagent-architecture.md",
            ROOT_DIR / "docs" / "orchestration" / "orchestrator-agent.md",
            ROOT_DIR / "docs" / "agents" / "interagent-communication.md",
            ROOT_DIR / "docs" / "multiagent_data_integration.md",
            ROOT_DIR / "docs" / "evaluation" / "multiagent-evaluation.md",
            ROOT_DIR / "docs" / "reports" / "sprint-3-report.md",
            ROOT_DIR / "README.md",
        ]

        for doc in required_docs:
            self.assertTrue(doc.exists(), f"El archivo {doc} debe existir")
            content = doc.read_text(encoding="utf-8")
            self.assertGreater(len(content.strip()), 100, f"El archivo {doc} debe contener documentación descriptiva")


if __name__ == "__main__":
    unittest.main()
