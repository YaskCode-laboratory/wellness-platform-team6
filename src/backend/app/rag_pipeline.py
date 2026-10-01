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
        Generador de fallback determinista estructurado y fundamentado (grounded)
        para entornos offline, CI/CD y ejecución sin credenciales externas de API.
        
        Sintetiza la respuesta extrayendo directamente evidencia técnica, reglas de
        sustitución y directrices de los fragmentos recuperados (retrieved_chunks).
        """
        if not chunks:
            return (
                f"No se encontraron fragmentos de conocimiento relevantes en el índice "
                f"para responder a la consulta: '{query}'."
            )

        extracted_guidelines: List[str] = []
        sources_list: List[str] = []
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        profile_str = str(user_profile).lower() if user_profile else ""

        for idx, chunk in enumerate(chunks, 1):
            source = chunk.get("source_file", "corpus")
            heading = chunk.get("heading_context", "")
            text = chunk.get("text", "")
            sources_list.append(f"{source} ({heading})" if heading else source)

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines:
                if line.startswith("### Contexto:") or line.startswith("| :---"):
                    continue

                # Procesar filas de tablas Markdown (ej. matrices de adaptaciones médicas)
                if line.startswith("|") and line.endswith("|"):
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    if len(cells) >= 4 and "Condición" not in cells[0]:
                        cond, contra, sust, just = cells[0], cells[1], cells[2], cells[3]
                        line_lower = line.lower()
                        is_relevant = any(t in line_lower for t in query_terms) or (
                            profile_str and any(t in line_lower for t in profile_str.split() if len(t) > 3)
                        )
                        if is_relevant or len(extracted_guidelines) < 3:
                            entry = (
                                f"Condición '{cond}': Contraindicaciones: {contra}. "
                                f"Sustitutos Seguros: {sust}. Justificación Biomecánica: {just}"
                            )
                            if entry not in extracted_guidelines:
                                extracted_guidelines.append(entry)
                    continue

                # Procesar viñetas o directrices
                clean_line = line
                if clean_line.startswith(("- ", "* ", "• ")):
                    clean_line = clean_line[2:].strip()
                elif clean_line.startswith(("-", "*", "•")):
                    clean_line = clean_line[1:].strip()

                if len(clean_line) > 10 and not clean_line.startswith("#"):
                    if clean_line not in extracted_guidelines:
                        extracted_guidelines.append(clean_line)

        # Si no se extrajeron líneas específicas, utilizar fragmentos textuales del chunk
        if not extracted_guidelines:
            for chunk in chunks[:2]:
                extracted_guidelines.append(chunk.get("text", "")[:200])

        selected_points = extracted_guidelines[:5]
        evidence_formatted = "\n".join([f"{i+1}. {pt}" for i, pt in enumerate(selected_points)])

        unique_sources = list(dict.fromkeys(sources_list))
        sources_header = ", ".join([f"`{s}`" for s in unique_sources])

        profile_addon = ""
        if user_profile:
            conds = user_profile.get("health_conditions", "Ninguna")
            if conds and conds.lower() not in ("ninguna", "none", "healthy"):
                profile_addon = f"\n- **Adaptación al Perfil**: Se aplican restricciones para condición: {conds}."

        response = (
            f"Basado en la base de conocimiento de Wellness Lift ({sources_header}):\n"
            f"{evidence_formatted}"
            f"{profile_addon}\n\n"
            f"**Fundamentación**: Síntesis construida a partir de los {len(chunks)} fragmentos recuperados para responder: '{query}'."
        )
        return response

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

