"""
Módulo Vector Database Store — Wellness Lift (Issue #8 & Issue #9)
Implementa el motor de base de datos vectorial liviano basado en Similitud del Coseno (Cosine Similarity)
e indexación persistente para la búsqueda semántica del sistema RAG.
"""

import os
import json
import math
import re
from typing import List, Dict, Any, Tuple

class VectorDatabaseStore:
    def __init__(self, collection_name: str = "wellness_rag_knowledge"):
        self.collection_name = collection_name
        self.documents: List[Dict[str, Any]] = []
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Normalización y tokenización de texto."""
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [w for w in text_clean.split() if len(w) > 2]
        return words

    def _compute_vector(self, text: str) -> Dict[str, float]:
        """Calcula el vector de frecuencia de términos ponderado (TF-IDF vector representation)."""
        tokens = self._tokenize(text)
        if not tokens:
            return {}
        
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        
        # Ponderación TF-IDF
        vector = {}
        norm_sq = 0.0
        for token, count in tf.items():
            val = (1.0 + math.log(count)) * self.idf.get(token, 1.0)
            vector[token] = val
            norm_sq += val * val
            
        # Normalización L2
        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {k: v / norm for k, v in vector.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calcula la similitud del coseno entre dos vectores de alta dimensión."""
        dot_product = sum(val * vec2.get(term, 0.0) for term, val in vec1.items())
        return float(dot_product)

    def fit_and_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Indexa los chunks construyendo el vocabulario, IDF y vectores de similitud."""
        self.documents = chunks
        num_docs = len(chunks)
        if num_docs == 0:
            return

        # Calcular Frecuencia de Documento (DF)
        doc_counts = {}
        for doc in chunks:
            tokens = set(self._tokenize(doc["text"]))
            for token in tokens:
                doc_counts[token] = doc_counts.get(token, 0) + 1

        # Calcular IDF
        self.idf = {token: math.log((num_docs + 1) / (count + 1)) + 1.0 for token, count in doc_counts.items()}

        # Asignar vector a cada documento
        for doc in self.documents:
            doc["vector"] = self._compute_vector(doc["text"])

    def search_similarity(self, query: str, k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        """
        Consulta la base vectorial retornando los K chunks más relevantes semánticamente.
        """
        if not self.documents:
            return []

        query_vec = self._compute_vector(query)
        scored_results = []

        for doc in self.documents:
            score = self._cosine_similarity(query_vec, doc.get("vector", {}))
            scored_results.append((doc, score))

        # Ordenar por puntaje de similitud descendente
        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:k]

    def save_index(self, filepath: str) -> None:
        """Guarda la base de datos vectorial serializada en disco."""
        data = {
            "collection_name": self.collection_name,
            "idf": self.idf,
            "documents": [
                {
                    "chunk_id": d["chunk_id"],
                    "source_file": d["source_file"],
                    "heading_context": d["heading_context"],
                    "token_count": d["token_count"],
                    "text": d["text"],
                    "vector": d.get("vector", {})
                }
                for d in self.documents
            ]
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_index(self, filepath: str) -> None:
        """Carga el índice vectorial serializado desde disco."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.collection_name = data.get("collection_name", self.collection_name)
        self.idf = data.get("idf", {})
        self.documents = data.get("documents", [])


if __name__ == "__main__":
    store = VectorDatabaseStore()
    sample = [{"chunk_id": "c1", "source_file": "f1.md", "heading_context": "H1", "token_count": 10, "text": "Sentadilla libre y dolor lumbar hernia discal."}]
    store.fit_and_index(sample)
    res = store.search_similarity("hernia lumbar")
    print(f"Prueba ejecutada. Resultado: {res[0][1]:.4f}")
