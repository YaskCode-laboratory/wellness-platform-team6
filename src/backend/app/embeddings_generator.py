"""
Módulo de Generación de Representaciones Vectoriales y Similitud Coseno — Wellness Lift (Issue #7 - S1-03).
Implementa un generador vectorial determinista basado en proyección espacial por hashing SHA-256 (384 dimensiones)
con normalización L2, y soporte opcional para proveedores de embeddings en la nube (Google Gemini API).
"""

import math
import os
import re
import hashlib
from typing import Dict, List, Union, Optional


class EmbeddingsGenerator:
    """
    Generador de representaciones vectoriales (embeddings) para el motor RAG de Wellness Lift.
    """

    def __init__(self, model_name: str = "local-deterministic-hashing-384d", vector_dim: int = 384):
        """
        Inicializa el generador de representaciones vectoriales.
        :param model_name: Identificador formal del modelo/mecanismo ('local-deterministic-hashing-384d' o 'models/text-embedding-004').
        :param vector_dim: Dimensionalidad del espacio vectorial (384 dimensiones estándar para la representación local).
        """
        self.model_name = model_name
        self.vector_dim = vector_dim

    def _clean_text(self, text: str) -> str:
        """Limpia el texto removiendo caracteres especiales y convirtiendo a minúsculas."""
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    def _hash_word_sha256(self, term: str, seed: int = 0) -> int:
        """
        Genera un hash entero determinista y reproducible inter-procesos usando SHA-256.
        Garantiza que el valor sea idéntico en cualquier ejecución de Python, independiente de PYTHONHASHSEED.
        """
        payload = f"{term}_{seed}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        # Tomar los primeros 4 bytes como entero positivo
        return int.from_bytes(digest[:4], byteorder="big")

    def _generate_local_embedding(self, text: str) -> List[float]:
        """
        Genera una representación vectorial determinista de 384 dimensiones con normalización L2
        basada en hashing SHA-256 de términos, longitud y ponderación posicional.
        Garantiza consistencia dimensional estricta de 384 floats y reproducibilidad total offline.
        """
        clean_str = self._clean_text(text)
        words = clean_str.split()
        vector = [0.0] * self.vector_dim

        if not words:
            return vector

        # Proyección espacial determinista con ponderación n-gram y de posición
        for idx, word in enumerate(words):
            h1 = self._hash_word_sha256(word, seed=1)
            h2 = self._hash_word_sha256(f"{word}_{idx}", seed=2)
            h3 = self._hash_word_sha256(f"{word}_len_{len(word)}", seed=3)

            pos_1 = h1 % self.vector_dim
            pos_2 = h2 % self.vector_dim
            pos_3 = h3 % self.vector_dim

            weight = 1.0 + (0.1 * math.log(len(word) + 1))
            vector[pos_1] += weight
            vector[pos_2] += weight * 0.5
            vector[pos_3] += weight * 0.25

        # Normalización Euclidiana L2 para garantizar que ||v||_2 = 1.0 (vector unitario)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [round(x / norm, 6) for x in vector]

        return vector

    def generate_embedding(self, text: str, api_key: Optional[str] = None) -> Dict[str, Union[str, int, List[float]]]:
        """
        Genera el embedding para un fragmento de texto individual.
        Si se provee api_key o existe GEMINI_API_KEY en el entorno, intenta utilizar text-embedding-004.
        De lo contrario, utiliza el mecanismo local determinista de 384 dimensiones.
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
                pass  # Fallback automático a mecanismo local determinista

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
