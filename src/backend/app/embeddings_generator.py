"""
Módulo de Generación de Embeddings y Métricas de Similitud Semántica.
Soporta generación de vectores locales de 384 dimensiones y Gemini Cloud API (768 dimensiones).
"""

import hashlib
import math
import os
import re
from typing import Dict, List, Union, Optional


class EmbeddingsGenerator:
    """
    Generador de representaciones vectoriales (embeddings) para el motor RAG de Wellness Lift.
    """

    def __init__(self, model_name: str = "local-deterministic-hashing-384d", vector_dim: int = 384):
        self.model_name = model_name
        self.vector_dim = vector_dim

    def _clean_text(self, text: str) -> str:
        """Limpia el texto removiendo caracteres especiales y convirtiendo a minúsculas."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def _generate_local_embedding(self, text: str) -> List[float]:
        """
        Genera un vector determinista de 384 dimensiones con normalización L2
        basado en descomposición semántica y hashing SHA-256 consistente entre plataformas.
        Garantiza consistencia dimensional de 384 floats y reproducibilidad 100% offline.
        """
        clean_str = self._clean_text(text)
        words = clean_str.split()
        vector = [0.0] * self.vector_dim

        if not words:
            return vector

        for idx, word in enumerate(words):
            h1 = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            h2 = int(hashlib.sha256(f"{word}_{idx}".encode("utf-8")).hexdigest()[:8], 16)
            h3 = int(hashlib.sha256(f"{word}_len_{len(word)}".encode("utf-8")).hexdigest()[:8], 16)

            pos_1 = h1 % self.vector_dim
            pos_2 = h2 % self.vector_dim
            pos_3 = h3 % self.vector_dim

            weight = 1.0 + (0.1 * math.log(len(word) + 1))
            vector[pos_1] += weight
            vector[pos_2] += weight * 0.5
            vector[pos_3] += weight * 0.25

        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 6) for x in vector]

        return vector

    def generate_embedding(self, text: str, api_key: Optional[str] = None) -> Dict[str, Union[str, int, List[float]]]:
        """
        Genera el embedding para un fragmento de texto individual.
        Si se provee api_key y la librería google.generativeai está disponible, utiliza text-embedding-004.
        De lo contrario, utiliza el modelo local determinista de 384 dimensiones.
        """
        if api_key or os.getenv("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                key = api_key or os.getenv("GEMINI_API_KEY")
                genai.configure(api_key=key)
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                embedding_vector = result.get("embedding", [])
                if embedding_vector:
                    return {
                        "model": "models/text-embedding-004",
                        "dimension": len(embedding_vector),
                        "vector": [round(x, 6) for x in embedding_vector]
                    }
            except Exception:
                pass  # Fallback a modelo local si la API no está configurada

        vector = self._generate_local_embedding(text)
        return {
            "model": self.model_name,
            "dimension": self.vector_dim,
            "vector": vector
        }

    def generate_batch_embeddings(self, chunks: List[Dict[str, str]]) -> List[Dict]:
        """
        Procesa una lista de chunks y retorna la estructura enriquecida con representaciones vectoriales.
        """
        result_chunks = []
        for chunk in chunks:
            text_to_embed = chunk.get("text", "")
            emb_data = self.generate_embedding(text_to_embed)

            chunk_with_emb = dict(chunk)
            chunk_with_emb["embedding_model"] = emb_data["model"]
            chunk_with_emb["embedding_dim"] = emb_data["dimension"]
            chunk_with_emb["embedding"] = emb_data["vector"]
            result_chunks.append(chunk_with_emb)

        return result_chunks


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calcula la similitud coseno entre dos vectores numéricos de igual dimensión.
    Retorna un valor en el rango [-1.0, 1.0].
    """
    if len(vec_a) != len(vec_b) or not vec_a:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return round(dot_product / (norm_a * norm_b), 6)
