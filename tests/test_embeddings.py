"""
Suite de Pruebas Unitarias e Integración para la Generación de Embeddings (Issue #7 - S1-03).
Verifica dimensionalidad, consistencia vectorial, norma L2, determinismo inter-proceso con SHA-256,
búsqueda semántica por similitud coseno y metadatos explícitos del Vector Store.
"""

import json
import math
import sys
import os
import unittest
from pathlib import Path

# Agregar src/backend a sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

try:
    from app.embeddings_generator import EmbeddingsGenerator, cosine_similarity
except ModuleNotFoundError:
    try:
        from embeddings_generator import EmbeddingsGenerator, cosine_similarity
    except ModuleNotFoundError:
        from .embeddings_generator import EmbeddingsGenerator, cosine_similarity


class TestEmbeddings(unittest.TestCase):
    def setUp(self):
        self.generator = EmbeddingsGenerator(model_name="local-deterministic-hashing-384d", vector_dim=384)

    def test_embedding_dimensionality(self):
        """Verifica que el vector generado tenga exactamente 384 dimensiones."""
        text = "Sentadilla libre con barra y técnica de alineación articular neutra."
        emb_data = self.generator.generate_embedding(text)

        self.assertEqual(emb_data["dimension"], 384)
        self.assertEqual(len(emb_data["vector"]), 384)
        self.assertEqual(emb_data["model"], "local-deterministic-hashing-384d")
        self.assertIsInstance(emb_data["vector"], list)

    def test_embedding_l2_normalization(self):
        """Verifica que la norma L2 del vector generado sea aproximadamente 1.0 (vector unitario)."""
        text = "Hipertrofia muscular y sobrecarga progresiva."
        emb_data = self.generator.generate_embedding(text)
        vector = emb_data["vector"]

        norm = math.sqrt(sum(x * x for x in vector))
        self.assertAlmostEqual(norm, 1.0, places=3)

    def test_deterministic_reproducibility(self):
        """Verifica que dos invocaciones independientes generen exactamente el mismo vector (determinismo SHA-256)."""
        text = "Rehabilitación de hernia discal lumbar con ejercicios de cadena posterior."
        vec1 = self.generator.generate_embedding(text)["vector"]
        vec2 = self.generator.generate_embedding(text)["vector"]

        self.assertEqual(vec1, vec2)

    def test_empty_text_embedding(self):
        """Verifica el comportamiento seguro al procesar cadenas vacías."""
        emb_data = self.generator.generate_embedding("")

        self.assertEqual(emb_data["dimension"], 384)
        self.assertEqual(len(emb_data["vector"]), 384)
        self.assertTrue(all(x == 0.0 for x in emb_data["vector"]))

    def test_cosine_similarity_identical_vectors(self):
        """Verifica que la similitud coseno de vectores idénticos sea 1.0."""
        vec_a = [0.6, 0.8, 0.0]
        vec_b = [0.6, 0.8, 0.0]
        sim = cosine_similarity(vec_a, vec_b)
        self.assertAlmostEqual(sim, 1.0, places=3)

    def test_semantic_similarity_relevance(self):
        """Verifica que una consulta médica coincida mejor con el chunk de hernia discal que con uno ortogonal."""
        query = "Hernia discal lumbar y ejercicios prohibidos"
        chunk_hernia = "### Contexto: 2. Matriz de Sustitución\nHernia Discal L4-L5 Lumbar contraindica Sentadilla Libre con Barra."
        chunk_hipertrofia = "### Contexto: 3. Periodización\nFase de Hipertrofia: Rangos de 6 a 12 repeticiones."

        vec_query = self.generator.generate_embedding(query)["vector"]
        vec_hernia = self.generator.generate_embedding(chunk_hernia)["vector"]
        vec_hipertrofia = self.generator.generate_embedding(chunk_hipertrofia)["vector"]

        sim_hernia = cosine_similarity(vec_query, vec_hernia)
        sim_hipertrofia = cosine_similarity(vec_query, vec_hipertrofia)

        self.assertGreater(sim_hernia, sim_hipertrofia)

    def test_vector_store_file_integrity(self):
        """Verifica la existencia y esquema JSON del archivo data/vector_store/embeddings.json."""
        vector_store_file = ROOT_DIR / "data" / "vector_store" / "embeddings.json"
        self.assertTrue(vector_store_file.exists(), "El archivo data/vector_store/embeddings.json debe existir")

        with open(vector_store_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("metadata", data)
        self.assertIn("vectors", data)
        self.assertEqual(data["metadata"]["total_chunks"], len(data["vectors"]))
        self.assertEqual(data["metadata"]["vector_dimension"], 384)
        self.assertEqual(data["metadata"]["embedding_model"], "local-deterministic-hashing-384d")

        for item in data["vectors"]:
            self.assertIn("chunk_id", item)
            self.assertIn("source_file", item)
            self.assertIn("text", item)
            self.assertIn("vector", item)
            self.assertEqual(len(item["vector"]), 384)


if __name__ == "__main__":
    unittest.main()
