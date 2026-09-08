"""
Módulo Vector Database Store — Wellness Lift (Issue #8 & Issue #18)
Implementa el motor de base de datos vectorial in-memory con soporte nativo para
embeddings densos de 384 dimensiones (S1-03 / EmbeddingsGenerator), búsqueda Top-K
mediante Similitud del Coseno, persistencia JSON y mecanismo baseline TF-IDF.
"""

import os
import sys
import json
import math
import re
from typing import List, Dict, Any, Tuple, Union, Optional

try:
    from app.embeddings_generator import EmbeddingsGenerator, cosine_similarity
except ModuleNotFoundError:
    try:
        from .embeddings_generator import EmbeddingsGenerator, cosine_similarity
    except (ImportError, ValueError):
        from embeddings_generator import EmbeddingsGenerator, cosine_similarity


class VectorDatabaseStore:
    """
    Motor de almacenamiento e indexación vectorial para el sistema RAG de Wellness Lift.
    Indexa chunks de texto vinculados con sus representaciones vectoriales densas (384d)
    y permite recuperación semántica de alta precisión por Similitud del Coseno.
    """

    def __init__(
        self,
        collection_name: str = "wellness_rag_knowledge",
        embedding_generator: Optional[EmbeddingsGenerator] = None
    ):
        self.collection_name = collection_name
        self.embedding_generator = embedding_generator or EmbeddingsGenerator()
        self.embedding_model = self.embedding_generator.model_name
        self.embedding_dim = self.embedding_generator.vector_dim
        self.documents: List[Dict[str, Any]] = []
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        """Tokenizador para el mecanismo baseline TF-IDF."""
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = [w for w in text_clean.split() if len(w) > 2]
        return words

    def _compute_tfidf_vector(self, text: str) -> Dict[str, float]:
        """Calcula el vector ralo TF-IDF normalizado L2 (mecanismo baseline)."""
        tokens = self._tokenize(text)
        if not tokens:
            return {}

        tf: Dict[str, int] = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1

        vector: Dict[str, float] = {}
        norm_sq = 0.0
        for token, count in tf.items():
            val = (1.0 + math.log(count)) * self.idf.get(token, 1.0)
            vector[token] = val
            norm_sq += val * val

        norm = math.sqrt(norm_sq) if norm_sq > 0 else 1.0
        return {k: round(v / norm, 6) for k, v in vector.items()}

    def _sparse_cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Similitud coseno entre vectores ralos TF-IDF."""
        dot_product = sum(val * vec2.get(term, 0.0) for term, val in vec1.items())
        return float(dot_product)

    def fit_and_index(self, chunks: List[Dict[str, Any]], compute_tfidf_baseline: bool = True) -> None:
        """
        Indexa una lista de chunks conservando o generando sus representaciones vectoriales densas (384d).
        Conserva la trazabilidad completa: chunk_id -> embedding -> vector_index.
        """
        num_docs = len(chunks)
        if num_docs == 0:
            self.documents = []
            return

        indexed_docs = []
        doc_counts: Dict[str, int] = {}

        for doc in chunks:
            doc_copy = dict(doc)

            # 1. Integración de embeddings densos de S1-03
            if "embedding" not in doc_copy or not doc_copy["embedding"]:
                emb_info = self.embedding_generator.generate_embedding(doc_copy.get("text", ""))
                doc_copy["embedding"] = emb_info["vector"]
                doc_copy["embedding_model"] = emb_info["model"]
                doc_copy["embedding_dim"] = emb_info["dimension"]
            else:
                if "embedding_model" not in doc_copy:
                    doc_copy["embedding_model"] = self.embedding_model
                if "embedding_dim" not in doc_copy:
                    doc_copy["embedding_dim"] = len(doc_copy["embedding"])

            # 2. Conteo para baseline TF-IDF
            if compute_tfidf_baseline:
                tokens = set(self._tokenize(doc_copy.get("text", "")))
                for token in tokens:
                    doc_counts[token] = doc_counts.get(token, 0) + 1

            indexed_docs.append(doc_copy)

        # 3. Cálculo de IDF para baseline
        if compute_tfidf_baseline and doc_counts:
            self.idf = {
                token: math.log((num_docs + 1) / (count + 1)) + 1.0
                for token, count in doc_counts.items()
            }
            for doc_copy in indexed_docs:
                tfidf_vec = self._compute_tfidf_vector(doc_copy.get("text", ""))
                doc_copy["vector_tfidf"] = tfidf_vec
                doc_copy["vector"] = tfidf_vec  # Compatibilidad con código previo

        self.documents = indexed_docs

    def search_similarity(
        self,
        query: Union[str, List[float]],
        k: int = 3,
        mode: str = "dense"
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Realiza búsqueda semántica Top-K por Similitud del Coseno.
        
        Parámetros:
            query: Texto de la consulta (str) o vector embedding numérico (List[float]).
            k: Número de documentos más relevantes a retornar.
            mode: 'dense' para búsqueda semántica con embeddings de 384d (por defecto),
                  'tfidf' para búsqueda rala baseline.
        """
        if not self.documents:
            return []

        scored_results: List[Tuple[Dict[str, Any], float]] = []

        if mode == "dense":
            if isinstance(query, str):
                query_emb = self.embedding_generator.generate_embedding(query)["vector"]
            elif isinstance(query, list):
                query_emb = query
            else:
                raise ValueError("Query debe ser una cadena de texto o una lista de floats")

            for doc in self.documents:
                doc_emb = doc.get("embedding", [])
                score = cosine_similarity(query_emb, doc_emb)
                scored_results.append((doc, score))

        elif mode in ("tfidf", "sparse"):
            if isinstance(query, str):
                query_tfidf = self._compute_tfidf_vector(query)
            else:
                query_tfidf = {}

            for doc in self.documents:
                doc_tfidf = doc.get("vector_tfidf", doc.get("vector", {}))
                score = self._sparse_cosine_similarity(query_tfidf, doc_tfidf)
                scored_results.append((doc, score))
        else:
            raise ValueError(f"Modo de búsqueda desconocido: '{mode}'. Use 'dense' o 'tfidf'.")

        scored_results.sort(key=lambda x: x[1], reverse=True)
        return scored_results[:k]

    def save_index(self, filepath: str) -> None:
        """Serializa y persiste el índice vectorial estructurado en disco en formato JSON."""
        data = {
            "collection_name": self.collection_name,
            "embedding_model": self.embedding_model,
            "embedding_dim": self.embedding_dim,
            "total_documents": len(self.documents),
            "documents": [
                {
                    "chunk_id": d["chunk_id"],
                    "source_file": d["source_file"],
                    "heading_context": d["heading_context"],
                    "token_count": d.get("token_count", 0),
                    "text": d["text"],
                    "embedding_model": d.get("embedding_model", self.embedding_model),
                    "embedding_dim": d.get("embedding_dim", self.embedding_dim),
                    "embedding": d.get("embedding", []),
                    "vector_tfidf": d.get("vector_tfidf", d.get("vector", {}))
                }
                for d in self.documents
            ],
            "baseline_tfidf": {
                "idf": self.idf
            }
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_index(self, filepath: str) -> None:
        """Carga un índice vectorial persistido en formato JSON a memoria."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.collection_name = data.get("collection_name", self.collection_name)
        self.embedding_model = data.get("embedding_model", self.embedding_model)
        self.embedding_dim = data.get("embedding_dim", self.embedding_dim)
        self.documents = data.get("documents", [])
        
        baseline = data.get("baseline_tfidf", {})
        self.idf = baseline.get("idf", data.get("idf", {}))

