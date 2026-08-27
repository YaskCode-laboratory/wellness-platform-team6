"""
Pruebas Automatizadas de la Base de Datos Vectorial — Wellness Lift (Issue #8)
"""

import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.vector_store import VectorDatabaseStore

class TestVectorDatabaseStore(unittest.TestCase):
    def setUp(self):
        self.store = VectorDatabaseStore(collection_name="test_collection")
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

    def test_indexing_and_vocabulary(self):
        self.assertGreater(len(self.store.idf), 0)
        self.assertEqual(len(self.store.documents), 2)

    def test_similarity_search_retrieval(self):
        results = self.store.search_similarity("hernia discal lumbar", k=1)
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc1#lumbar")
        self.assertGreater(score, 0.0)

    def test_similarity_search_rodilla(self):
        results = self.store.search_similarity("dolor menisco rodilla", k=1)
        self.assertEqual(len(results), 1)
        top_doc, score = results[0]
        self.assertEqual(top_doc["chunk_id"], "doc2#rodilla")
        self.assertGreater(score, 0.0)

if __name__ == "__main__":
    unittest.main()
