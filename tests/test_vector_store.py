"""
Pruebas Automatizadas de la Base de Datos Vectorial — Wellness Lift (Issue #8)
Valida la integración con S1-03 (representaciones vectoriales de 384 dimensiones), trazabilidad
chunk_id -> embedding -> vector_store, recuperación por similitud coseno,
persistencia JSON y soporte para baseline TF-IDF.
"""

import unittest
import os
import sys
import json
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.vector_store import VectorDatabaseStore
from app.embeddings_generator import EmbeddingsGenerator


class TestVectorDatabaseStore(unittest.TestCase):
    def setUp(self):
        self.generator = EmbeddingsGenerator()
        self.store = VectorDatabaseStore(
            collection_name="test_collection",
            embedding_generator=self.generator
        )
        self.sample_chunks = [
            {
                "chunk_id": "doc1#lumbar",
                "source_file": "medical_adaptations.md",
                "heading_context": "Lesion Lumbar",
                "token_count": 50,
                "text": "Sentadilla libre contraindicada para hernia lumbar discal L4-L5. Sustituir por prensa inclinada."
            },
            {
                "chunk_id": "doc2#rodilla",
                "source_file": "medical_adaptations.md",
                "heading_context": "Lesion Rodilla",
                "token_count": 40,
                "text": "Prensa profunda contraindicada para menisco. Sustituir por extension de rodilla."
            }
        ]
        self.store.fit_and_index(self.sample_chunks)

    def test_indexing_dense_embeddings(self):
        """Verifica que los documentos indexados contengan representaciones vectoriales densas de 384 dimensiones."""
        self.assertEqual(len(self.store.documents), 2)
        for doc in self.store.documents:
            self.assertIn("embedding", doc)
            self.assertEqual(len(doc["embedding"]), 384)
            self.assertEqual(doc.get("embedding_dim"), 384)
            self.assertEqual(doc.get("embedding_model"), "local-deterministic-hashing-384d")

    def test_direct_s103_embeddings_preservation(self):
        """Verifica que los embeddings precalculados en S1-03 se preserven sin recalcular."""
        custom_emb = [0.5] + [0.0] * 383
        precomputed_chunk = [
            {
                "chunk_id": "doc_s103#test",
                "source_file": "test.md",
                "heading_context": "Precomputed",
                "token_count": 10,
                "text": "Texto de prueba con embedding preexistente",
                "embedding": custom_emb,
                "embedding_model": "local-deterministic-hashing-384d",
                "embedding_dim": 384
            }
        ]
        test_store = VectorDatabaseStore(collection_name="s103_test")
        test_store.fit_and_index(precomputed_chunk)
        self.assertEqual(test_store.documents[0]["embedding"], custom_emb)
        self.assertEqual(test_store.documents[0]["chunk_id"], "doc_s103#test")

    def test_fallback_embeddings_json_structure_compatibility(self):
        """Verifica que la estructura 'metadata -> vectors' de embeddings.json se adapte e indexe correctamente."""
        embeddings_json_data = {
            "metadata": {
                "total_chunks": 1,
                "embedding_model": "local-deterministic-hashing-384d",
                "vector_dimension": 384
            },
            "vectors": [
                {
                    "chunk_id": "fallback#01",
                    "source_file": "fallback.md",
                    "heading_context": "Fallback",
                    "text": "Texto en formato embeddings.json",
                    "vector": [0.2] * 384
                }
            ]
        }
        meta = embeddings_json_data["metadata"]
        converted_chunks = []
        for item in embeddings_json_data["vectors"]:
            c = dict(item)
            c["embedding"] = item["vector"]
            c["embedding_model"] = meta["embedding_model"]
            c["embedding_dim"] = meta["vector_dimension"]
            converted_chunks.append(c)

        fallback_store = VectorDatabaseStore(collection_name="fallback_test")
        fallback_store.fit_and_index(converted_chunks)
        self.assertEqual(len(fallback_store.documents), 1)
        self.assertEqual(fallback_store.documents[0]["chunk_id"], "fallback#01")
        self.assertEqual(len(fallback_store.documents[0]["embedding"]), 384)

    def test_dense_similarity_search_retrieval(self):
        """Verifica la recuperación por similitud vectorial Top-1 usando similitud coseno sobre representaciones densas."""
        results = self.store.search_similarity("hernia discal lumbar", k=1, mode="dense")
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc1#lumbar")
        self.assertGreater(score, 0.0)

    def test_dense_similarity_search_rodilla(self):
        """Verifica la recuperación por similitud vectorial en adaptación de rodilla."""
        results = self.store.search_similarity("menisco rodilla extension", k=1, mode="dense")
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc2#rodilla")
        self.assertGreater(score, 0.0)

    def test_vector_query_search(self):
        """Verifica que search_similarity acepte directamente un vector de 384 dimensiones."""
        query_vec = self.generator.generate_embedding("hernia lumbar")["vector"]
        results = self.store.search_similarity(query_vec, k=1, mode="dense")
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc1#lumbar")

    def test_baseline_tfidf_search(self):
        """Verifica que el modo baseline TF-IDF funcione como alternativa de respaldo."""
        results = self.store.search_similarity("hernia discal", k=1, mode="tfidf")
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc1#lumbar")
        self.assertGreater(score, 0.0)

    def test_save_and_load_index(self):
        """Verifica la serialización y deserialización del índice vectorial en JSON."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            self.store.save_index(temp_path)
            self.assertTrue(os.path.exists(temp_path))

            new_store = VectorDatabaseStore(collection_name="loaded_collection")
            new_store.load_index(temp_path)

            self.assertEqual(len(new_store.documents), 2)
            self.assertEqual(new_store.documents[0]["chunk_id"], "doc1#lumbar")
            self.assertEqual(len(new_store.documents[0]["embedding"]), 384)

            # Probar búsqueda sobre el store cargado
            results = new_store.search_similarity("hernia discal lumbar", k=1)
            self.assertEqual(results[0][0]["chunk_id"], "doc1#lumbar")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_persisted_vector_index_integrity(self):
        """Verifica que el archivo persistido en data/vector_store/vector_index.json sea válido."""
        index_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'vector_store', 'vector_index.json'
        ))
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assertIn("documents", data)
            self.assertGreater(len(data["documents"]), 0)
            for doc in data["documents"]:
                self.assertIn("chunk_id", doc)
                self.assertIn("embedding", doc)
                self.assertEqual(len(doc["embedding"]), 384)


if __name__ == "__main__":
    unittest.main()
