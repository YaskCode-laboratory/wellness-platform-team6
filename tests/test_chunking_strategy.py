"""
Suite de Pruebas Automatizadas para la Estrategia de Chunking y Ventana Deslizante (Issue #6 - S1-02).
Verifica la segmentación Markdown, la activación de la ventana deslizante sobre textos extensos,
la coincidencia exacta del solapamiento (overlap) y la reproducibilidad del benchmark empírico.
"""

import unittest
import os
import sys
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.rag_chunker import MarkdownSemanticChunker


class TestChunkingStrategy(unittest.TestCase):
    def setUp(self):
        self.chunker = MarkdownSemanticChunker(chunk_size=512, chunk_overlap=64)

    def test_markdown_heading_segmentation(self):
        """Verifica que el segmentador divida el documento respetando los encabezados Markdown."""
        markdown_text = (
            "# Título Principal\n"
            "Contenido introductorio del documento.\n\n"
            "## Sección A\n"
            "Detalle de la sección A.\n\n"
            "## Sección B\n"
            "Detalle de la sección B."
        )
        sections = self.chunker.split_markdown_by_headings(markdown_text)
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]["heading"], "Título Principal")
        self.assertEqual(sections[1]["heading"], "Sección A")
        self.assertEqual(sections[2]["heading"], "Sección B")

    def test_sliding_window_activation_on_long_content(self):
        """Verifica que una sección con más de 512 palabras active la ventana deslizante y genere múltiples subchunks."""
        # Generar un contenido controlado de 800 palabras
        words = [f"token_{i}" for i in range(1, 801)]
        long_section = {
            "heading": "Protocolo Extenso Controlado",
            "content": " ".join(words)
        }

        chunks = self.chunker.chunk_section(long_section, "test_doc.md")
        
        # Con 800 palabras, chunk_size=512 y overlap=64:
        # Chunk 1: palabras [0:512] (512 palabras)
        # Siguiente inicio: 512 - 64 = 448
        # Chunk 2: palabras [448:800] (352 palabras)
        self.assertEqual(len(chunks), 2)
        self.assertIn("Parte 1", chunks[0]["text"])
        self.assertIn("Parte 2", chunks[1]["text"])
        self.assertEqual(chunks[0]["word_count"], 512)
        self.assertEqual(chunks[1]["word_count"], 352)

    def test_overlap_exact_words_matching(self):
        """Verifica matemáticamente que las últimas 64 palabras del Chunk 1 sean idénticas a las primeras 64 del Chunk 2."""
        words = [f"w_{i}" for i in range(1, 801)]
        long_section = {
            "heading": "Sección de Verificación de Solapamiento",
            "content": " ".join(words)
        }

        chunks = self.chunker.chunk_section(long_section, "test_overlap.md")
        self.assertGreaterEqual(len(chunks), 2)

        # Extraer las palabras del contenido de cada chunk (omitiendo la cabecera '### Contexto: ...')
        c1_content_words = chunks[0]["text"].split("\n", 1)[1].split()
        c2_content_words = chunks[1]["text"].split("\n", 1)[1].split()

        # Las últimas 64 palabras de c1
        c1_tail_overlap = c1_content_words[-64:]
        # Las primeras 64 palabras de c2
        c2_head_overlap = c2_content_words[:64]

        self.assertEqual(len(c1_tail_overlap), 64)
        self.assertEqual(len(c2_head_overlap), 64)
        self.assertEqual(c1_tail_overlap, c2_head_overlap)

    def test_unit_and_token_estimation_consistency(self):
        """Verifica que se registre word_count y token_count de forma consistente."""
        sample_text = "Sentadilla con barra libre y alineacion neutra de la columna lumbar"
        words = sample_text.split()
        short_section = {
            "heading": "Biomecánica",
            "content": sample_text
        }
        chunks = self.chunker.chunk_section(short_section, "bio.md")
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["word_count"], len(words))
        self.assertGreaterEqual(chunks[0]["token_count"], len(words))

    def test_benchmark_results_file_integrity(self):
        """Verifica que data/processed_chunks/chunking_benchmark_results.json exista y contenga los datos empíricos."""
        benchmark_file = ROOT_DIR / "data" / "processed_chunks" / "chunking_benchmark_results.json"
        self.assertTrue(benchmark_file.exists(), "El archivo de benchmark empírico debe existir")

        with open(benchmark_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("configurations", data)
        self.assertIn("Config_A_256_32", data["configurations"])
        self.assertIn("Config_B_512_64", data["configurations"])
        self.assertIn("Config_C_1024_128", data["configurations"])
        
        # Validar que todos los solapamientos del documento controlado estén verificados
        for cfg_id, cfg_data in data["configurations"].items():
            self.assertTrue(cfg_data["controlled_long_doc_metrics"]["all_overlaps_verified"])


if __name__ == "__main__":
    unittest.main()
