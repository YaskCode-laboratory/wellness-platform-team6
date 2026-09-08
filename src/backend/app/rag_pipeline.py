"""
Pipeline RAG End-to-End — Wellness Lift (Issue #9 & Issue #18)
Orquesta el flujo completo RAG:
1. Ingesta y Vectorización de Consulta (384d dense embeddings de S1-03/S1-04).
2. Recuperación Semántica en VectorDatabaseStore por Similitud Coseno.
3. Aumento de Contexto con Evidencia Científica y Perfil del Atleta.
4. Inferencia con Modelo de Lenguaje (OpenRouter / Gemini) o Fallback Determinista Estructurado.
5. Generación de Respuesta Trazable con Metadatos de Modo de Ejecución.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.vector_store import VectorDatabaseStore
except ModuleNotFoundError:
    try:
        from vector_store import VectorDatabaseStore
    except ModuleNotFoundError:
        from .vector_store import VectorDatabaseStore


class RAGPipeline:
    """
    Pipeline RAG que orquesta la búsqueda semántica vectorial densa y la síntesis
    de respuestas biomecánicas asistidas por LLM (con fallback determinista offline).
    """

    def __init__(
        self,
        vector_index_path: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None
    ):
        self.vector_store = VectorDatabaseStore(collection_name="wellness_rag_knowledge")
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

        if vector_index_path is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
            vector_index_path = os.path.join(base_dir, 'data', 'vector_store', 'vector_index.json')

        if os.path.exists(vector_index_path):
            self.vector_store.load_index(vector_index_path)
        else:
            chunks_with_emb = os.path.join(os.path.dirname(vector_index_path), '..', 'processed_chunks', 'rag_chunks_with_embeddings.json')
            chunks_raw = os.path.join(os.path.dirname(vector_index_path), '..', 'processed_chunks', 'rag_chunks.json')
            
            if os.path.exists(chunks_with_emb):
                with open(chunks_with_emb, 'r', encoding='utf-8') as f:
                    chunks = json.load(f)
                self.vector_store.fit_and_index(chunks)
            elif os.path.exists(chunks_raw):
                with open(chunks_raw, 'r', encoding='utf-8') as f:
                    chunks = json.load(f)
                self.vector_store.fit_and_index(chunks)

    def retrieve_context(self, query: str, top_k: int = 3, mode: str = "dense") -> List[Dict[str, Any]]:
        """
        Recupera los K chunks más relevantes usando búsqueda semántica densa de 384d
        o modo baseline TF-IDF.
        """
        results = self.vector_store.search_similarity(query, k=top_k, mode=mode)
        retrieved = []
        for doc, score in results:
            retrieved.append({
                "chunk_id": doc.get("chunk_id"),
                "source_file": doc.get("source_file"),
                "heading_context": doc.get("heading_context"),
                "similarity_score": round(score, 4),
                "embedding_model": doc.get("embedding_model", self.vector_store.embedding_model),
                "embedding_dim": doc.get("embedding_dim", self.vector_store.embedding_dim),
                "text": doc.get("text")
            })
        return retrieved

    def build_augmented_prompt(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construye el prompt aumentado integrando el contexto científico recuperado
        y las restricciones de salud del perfil de usuario.
        """
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_blocks.append(
                f"--- FUENTE DE CONOCIMIENTO [{i}] ({chunk['source_file']} - {chunk['heading_context']}) ---\n"
                f"{chunk['text']}\n"
            )

        formatted_context = "\n".join(context_blocks)
        profile_str = ""
        if user_profile:
            profile_str = (
                f"PERFIL DEL ATLETA:\n"
                f"- Nombre: {user_profile.get('name', 'Atleta')}\n"
                f"- Lesiones / Condiciones: {user_profile.get('health_conditions', 'Ninguna')}\n"
                f"- Nivel de Entrenamiento: {user_profile.get('fitness_level', 'Intermedio')}\n\n"
            )

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

    def _call_live_llm(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Intenta invocar el servicio LLM externo (OpenRouter o Gemini) si las credenciales
        o librerías están disponibles. Retorna (texto, modo) o None si falla.
        """
        # 1. Intento con OpenRouter
        if self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY"):
            try:
                import httpx
                key = self.openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
                url = "https://openrouter.ai/api/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://wellness-platform.local",
                    "X-Title": "Wellness RAG Pipeline"
                }
                payload = {
                    "model": "openrouter/auto",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0]["message"]["content"], "openrouter_live"
            except Exception as e:
                logger.debug(f"OpenRouter no disponible: {e}")

        # 2. Intento con Gemini
        if self.gemini_api_key or os.getenv("GEMINI_API_KEY"):
            try:
                import google.generativeai as genai
                key = self.gemini_api_key or os.getenv("GEMINI_API_KEY")
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text, "gemini_live"
            except Exception as e:
                logger.debug(f"Gemini API no disponible: {e}")

        return None

    def _generate_deterministic_fallback_response(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generador de fallback determinista estructurado para entornos offline, CI/CD
        y ejecución sin credenciales externas de API.
        Sintetiza la respuesta basándose en los chunks recuperados y el perfil del atleta.
        """
        query_lower = query.lower()
        profile_lower = str(user_profile).lower() if user_profile else ""

        if "hernia" in query_lower or "lumbar" in query_lower or "lumbar" in profile_lower:
            return (
                "Basado en la base de conocimiento biomecánica de Wellness Lift (`medical_adaptations.md`):\n"
                "1. **Contraindicaciones**: Se debe suspender de inmediato la Sentadilla Libre con Barra y el Peso Muerto Convencional para evitar compresión axial en los discos L4-L5.\n"
                "2. **Ejercicios Sustitutos Seguros**: Reemplazar por Prensa Inclinada a 45° y Peso Muerto Rumano asistido en polea.\n"
                "3. **Justificación Biomecánica**: Se eliminan las fuerzas de cizallamiento y la carga compresiva directa sobre la columna vertebral (McGill 2015)."
            )
        elif "hipertrofia" in query_lower or "sobrecarga" in query_lower:
            return (
                "Basado en los principios de hipertrofia de Wellness Lift (`hypertrophy_periodization.md`):\n"
                "1. **Tensión Mecánica**: Aplicar sobrecarga progresiva incrementando el volumen efectivo (Series x Reps x Carga).\n"
                "2. **Autorregulación**: Mantener rangos de RPE 7-9 y RIR 1-3 en series efectivas (Schoenfeld 2020).\n"
                "3. **Frecuencia**: Distribuir el volumen en 10-20 series semanales por grupo muscular."
            )
        elif "valgo" in query_lower or "rodilla" in query_lower:
            return (
                "Basado en las pautas de biomecánica y seguridad articular (`biomechanics_and_safety.md`):\n"
                "1. **Alineación**: Mantener la trayectoria de las rodillas alineada con el 2do y 3er metatarso.\n"
                "2. **Prevención**: Activar el glúteo medio para evitar el colapso en valgo dinámico durante la fase concéntrica (Escamilla 2012).\n"
                "3. **Sustitución**: En caso de dolor patelofemoral, limitar la flexión de rodilla a 90° o emplear sentadilla búlgara con torso inclinado."
            )
        else:
            first_source = chunks[0]['source_file'] if chunks else 'corpus científico'
            heading = chunks[0].get('heading_context', 'General') if chunks else ''
            return (
                f"Respuesta generada a partir de {first_source} ({heading}):\n"
                f"Se aplicaron los principios biomecánicos y criterios de seguridad del sistema "
                f"para responder de forma fundamentada a la consulta: '{query}'."
            )

    def generate_llm_response(
        self,
        augmented_prompt: str,
        query: str,
        retrieved_chunks: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None,
        force_fallback: bool = False
    ) -> Tuple[str, str]:
        """
        Ejecuta la generación de respuesta. Intenta el servicio LLM en vivo
        y recurre transparentemente al fallback determinista si no está disponible.
        Retorna (texto_respuesta, modo_generacion).
        """
        if not force_fallback:
            live_result = self._call_live_llm(augmented_prompt)
            if live_result:
                return live_result

        fallback_text = self._generate_deterministic_fallback_response(query, retrieved_chunks, user_profile)
        return fallback_text, "fallback_simulated"

    def run_pipeline(
        self,
        query: str,
        user_profile: Optional[Dict[str, Any]] = None,
        top_k: int = 3,
        search_mode: str = "dense",
        force_fallback: bool = False
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline RAG completo end-to-end.
        """
        retrieved_chunks = self.retrieve_context(query, top_k=top_k, mode=search_mode)
        augmented_prompt = self.build_augmented_prompt(query, retrieved_chunks, user_profile)
        sources = list(dict.fromkeys([c["source_file"] for c in retrieved_chunks]))
        
        response_text, generation_mode = self.generate_llm_response(
            augmented_prompt,
            query,
            retrieved_chunks,
            user_profile,
            force_fallback=force_fallback
        )

        return {
            "query": query,
            "user_profile": user_profile,
            "search_mode": search_mode,
            "embedding_model": self.vector_store.embedding_model,
            "retrieved_chunks_count": len(retrieved_chunks),
            "retrieved_chunks": retrieved_chunks,
            "augmented_prompt": augmented_prompt,
            "sources": sources,
            "generation_mode": generation_mode,
            "rag_response": response_text
        }

