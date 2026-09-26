"""
Módulo Evaluador de Desempeño del Sistema RAG (Wellness Lift).
Calcula métricas de recuperación (Precision@K, Recall@K, MRR) y evalúa fidelidad y seguridad médica.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Garantizar que src/backend esté en sys.path
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.embeddings_generator import EmbeddingsGenerator, cosine_similarity

logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Evaluador de Recuperación y Calidad para el motor RAG.
    """

    def __init__(self, vector_store_path: Optional[Path] = None):
        self.vector_store_path = vector_store_path or (ROOT_DIR / "data" / "vector_store" / "embeddings.json")
        self.generator = EmbeddingsGenerator()
        self.vector_data = self._load_vector_store()

    def _load_vector_store(self) -> List[Dict[str, Any]]:
        """Carga los vectores y metadatos del índice vectorial."""
        if not self.vector_store_path.exists():
            logger.warning(f"Vector Store no encontrado en {self.vector_store_path}")
            return []

        with open(self.vector_store_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("vectors", [])

    def retrieve_top_k(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Recupera los top_k chunks más semejantes a la consulta según Similitud Coseno.
        """
        if not self.vector_data:
            return []

        query_emb = self.generator.generate_embedding(query_text)["vector"]
        scored_chunks = []

        for item in self.vector_data:
            doc_emb = item["vector"]
            score = cosine_similarity(query_emb, doc_emb)
            scored_chunks.append({
                "chunk_id": item["chunk_id"],
                "source_file": item["source_file"],
                "heading_context": item["heading_context"],
                "text": item["text"],
                "similarity_score": score
            })

        # Ordenar por puntaje descendente
        scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_chunks[:top_k]

    def evaluate_query(self, query_item: Dict[str, Any], top_k: int = 3) -> Dict[str, Any]:
        """
        Evalúa un caso de prueba individual calculando Precision@K, Recall@K, MRR y verificaciones de seguridad.
        """
        query_id = query_item.get("query_id", "Q00")
        query_text = query_item.get("query", "")
        expected_ids = set(query_item.get("expected_relevant_chunk_ids", []))
        contraindicated = query_item.get("contraindicated_exercises", [])
        safe_substitutes = query_item.get("safe_substitutes", [])

        retrieved = self.retrieve_top_k(query_text, top_k=top_k)
        retrieved_ids = [item["chunk_id"] for item in retrieved]

        # 1. Precision@K = (Chunks recuperados relevantes en Top-K) / K
        relevant_in_top_k = sum(1 for cid in retrieved_ids if cid in expected_ids)
        precision_at_k = round(relevant_in_top_k / top_k, 4) if top_k > 0 else 0.0

        # 2. Recall@K = (Chunks recuperados relevantes en Top-K) / (Total de Chunks Relevantes Esperados)
        recall_at_k = round(relevant_in_top_k / len(expected_ids), 4) if expected_ids else 1.0

        # 3. MRR (Mean Reciprocal Rank)
        mrr = 0.0
        for rank, cid in enumerate(retrieved_ids, start=1):
            if cid in expected_ids:
                mrr = round(1.0 / rank, 4)
                break

        # 4. Evaluación de Cobertura de Seguridad Médica en Contexto Recuperado
        retrieved_text_block = "\n".join([item["text"] for item in retrieved])
        safety_passed = True
        missing_substitutes = []
        unwarned_contraindications = []

        is_medical_query = bool(contraindicated or safe_substitutes or query_item.get("category") == "Medical Substitutions")

        if contraindicated:
            for exercise in contraindicated:
                if exercise.lower() not in retrieved_text_block.lower():
                    unwarned_contraindications.append(exercise)

        if safe_substitutes:
            for sub in safe_substitutes:
                if sub.lower() not in retrieved_text_block.lower():
                    missing_substitutes.append(sub)

        if is_medical_query:
            # Una consulta médica aprueba la verificación de cobertura de seguridad si se recuperan
            # tanto las contraindicaciones como los sustitutos seguros especificados.
            if unwarned_contraindications or missing_substitutes:
                safety_passed = False

        return {
            "query_id": query_id,
            "category": query_item.get("category", "General"),
            "query": query_text,
            "top_k": top_k,
            "precision_at_k": precision_at_k,
            "recall_at_k": recall_at_k,
            "mrr": mrr,
            "retrieved_chunk_ids": retrieved_ids,
            "top_score": retrieved[0]["similarity_score"] if retrieved else 0.0,
            "safety_passed": safety_passed,
            "unwarned_contraindications": unwarned_contraindications,
            "missing_substitutes": missing_substitutes,
            "retrieved_chunks": [
                {
                    "chunk_id": item["chunk_id"],
                    "similarity_score": item["similarity_score"],
                    "heading_context": item["heading_context"]
                }
                for item in retrieved
            ]
        }

    def evaluate_all(self, test_queries: List[Dict[str, Any]], top_k: int = 3) -> Dict[str, Any]:
        """
        Evalúa un conjunto completo de consultas y calcula promedios globales.
        `medical_safety_accuracy` se calcula exclusivamente sobre las consultas médicas.
        """
        results = [self.evaluate_query(q, top_k=top_k) for q in test_queries]

        avg_precision = round(sum(r["precision_at_k"] for r in results) / len(results), 4) if results else 0.0
        avg_recall = round(sum(r["recall_at_k"] for r in results) / len(results), 4) if results else 0.0
        avg_mrr = round(sum(r["mrr"] for r in results) / len(results), 4) if results else 0.0

        # Filtrar únicamente consultas médicas para el cálculo de medical_safety_accuracy
        medical_results = [r for r in results if r["category"] == "Medical Substitutions"]
        if medical_results:
            safety_score = round(sum(1 for r in medical_results if r["safety_passed"]) / len(medical_results), 4)
            total_medical_queries = len(medical_results)
        else:
            safety_score = 1.0
            total_medical_queries = 0

        return {
            "summary": {
                "total_queries": len(results),
                "medical_queries_evaluated": total_medical_queries,
                "top_k_evaluated": top_k,
                "mean_precision_at_k": avg_precision,
                "mean_recall_at_k": avg_recall,
                "mean_mrr": avg_mrr,
                "medical_safety_accuracy": safety_score
            },
            "detailed_results": results
        }
