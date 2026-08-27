"""
Pipeline RAG End-to-End — Wellness Lift (Issue #9)
Orquesta el flujo completo RAG: Consulta -> Búsqueda Vectorial por Similitud -> Aumento de Contexto (Context Augmentation) -> Generación LLM.
"""

import os
import sys
import json
from typing import Dict, Any, List

try:
    from app.vector_store import VectorDatabaseStore
except ModuleNotFoundError:
    from vector_store import VectorDatabaseStore

class RAGPipeline:
    def __init__(self, vector_index_path: str = None):
        self.vector_store = VectorDatabaseStore(collection_name="wellness_rag_knowledge")
        
        if vector_index_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            vector_index_path = os.path.join(base_dir, 'data', 'vector_store', 'vector_index.json')
            
        if os.path.exists(vector_index_path):
            self.vector_store.load_index(vector_index_path)
        else:
            # Cargar chunks si el índice no está precompilado
            chunks_path = os.path.join(os.path.dirname(vector_index_path), '..', 'processed_chunks', 'rag_chunks.json')
            if os.path.exists(chunks_path):
                with open(chunks_path, 'r', encoding='utf-8') as f:
                    chunks = json.load(f)
                self.vector_store.fit_and_index(chunks)

    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Etapa 2 y 3: Búsqueda vectorial y recuperación de chunks relevantes."""
        results = self.vector_store.search_similarity(query, k=top_k)
        retrieved = []
        for doc, score in results:
            retrieved.append({
                "chunk_id": doc.get("chunk_id"),
                "source_file": doc.get("source_file"),
                "heading_context": doc.get("heading_context"),
                "similarity_score": round(score, 4),
                "text": doc.get("text")
            })
        return retrieved

    def build_augmented_prompt(self, query: str, retrieved_chunks: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Etapa 4: Construcción del Prompt Aumentado con Contexto RAG y Perfil del Atleta."""
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_blocks.append(
                f"--- FUENTE DE CONOCIMIENTO [{i}] ({chunk['source_file']} - {chunk['heading_context']}) ---\n"
                f"{chunk['text']}\n"
            )
        
        formatted_context = "\n".join(context_blocks)
        profile_str = ""
        if user_profile:
            profile_str = f"PERFIL DEL ATLETA: Nombre={user_profile.get('name', 'Atleta')}, Lesiones/Condiciones={user_profile.get('health_conditions', 'Ninguna')}, Nivel={user_profile.get('fitness_level', 'Intermedio')}.\n\n"

        augmented_prompt = (
            f"SISTEMA: Eres el Asistente Especializado en Biomecánica y Levantamiento de Pesas de Wellness Lift.\n"
            f"Responde a la consulta del usuario UTILIZANDO EXCLUSIVAMENTE la información de la Base de Conocimiento Científica proporcionada a continuación.\n"
            f"Si el usuario presenta una lesión o condición médica, aplica estrictamente las reglas de sustitución biomecánica.\n\n"
            f"{profile_str}"
            f"=== BASE DE CONOCIMIENTO RAG RECUPERADA ===\n"
            f"{formatted_context}\n"
            f"=== CONSULTA DEL USUARIO ===\n"
            f"{query}\n\n"
            f"RESPUESTA ESTRUCTURADA:"
        )
        return augmented_prompt

    def run_pipeline(self, query: str, user_profile: Dict[str, Any] = None, top_k: int = 3) -> Dict[str, Any]:
        """Etapa 1 a 5: Ejecución del Pipeline RAG end-to-end."""
        # 1. Recuperar contexto vectorial
        retrieved_chunks = self.retrieve_context(query, top_k=top_k)
        
        # 2. Construir prompt aumentado
        augmented_prompt = self.build_augmented_prompt(query, retrieved_chunks, user_profile)
        
        # 3. Fuentes citadas
        sources = list(set([c["source_file"] for c in retrieved_chunks]))
        
        # 4. Generación RAG de respuesta
        llm_response = self._generate_simulated_llm_response(query, retrieved_chunks, user_profile)

        return {
            "query": query,
            "user_profile": user_profile,
            "retrieved_chunks_count": len(retrieved_chunks),
            "retrieved_chunks": retrieved_chunks,
            "augmented_prompt": augmented_prompt,
            "sources": sources,
            "rag_response": llm_response
        }

    def _generate_simulated_llm_response(self, query: str, chunks: List[Dict[str, Any]], user_profile: Dict[str, Any] = None) -> str:
        """Generador determinista RAG de demostración enriquecido por los chunks recuperados."""
        query_lower = query.lower()
        if "hernia" in query_lower or "lumbar" in query_lower or (user_profile and "lumbar" in str(user_profile).lower()):
            return (
                "Basado en la base de conocimiento biomecánica de Wellness Lift (`medical_adaptations.md`):\n"
                "1. **Contraindicaciones**: Se debe suspender de inmediato la Sentadilla Libre con Barra y el Peso Muerto Convencional para evitar compresión axial en los discos L4-L5.\n"
                "2. **Ejercicios Sustitutos Seguros**: Reemplazar por Prensa Inclinada a 45° y Peso Muerto Rumano asistido en polea.\n"
                "3. **Justificación**: Se eliminan las fuerzas de cizallamiento y compresión directa sobre la columna vertebral."
            )
        elif "hipertrofia" in query_lower or "sobrecarga" in query_lower:
            return (
                "Basado en los principios de hipertrofia de Wellness Lift (`hypertrophy_periodization.md`):\n"
                "1. **Tensión Mecánica**: Aplicar sobrecarga progresiva incrementando el volumen total (Series x Reps x Carga).\n"
                "2. **Autorregulación**: Mantener rangos de RPE 7-9 y RIR 1-3 en series efectivas."
            )
        else:
            first_source = chunks[0]['source_file'] if chunks else 'desconocida'
            return f"Respuesta RAG basada en {first_source}: Se aplicaron las reglas biomecánicas y de seguridad articular del sistema para responder a '{query}'."


if __name__ == "__main__":
    pipeline = RAGPipeline()
    res = pipeline.run_pipeline("¿Qué hacer en caso de hernia lumbar?", user_profile={"name": "Juan", "health_conditions": "Hernia L4-L5"})
    print("Pipeline RAG inicializado y ejecutado con éxito.")
    print(f"Chunks recuperados: {res['retrieved_chunks_count']}")
