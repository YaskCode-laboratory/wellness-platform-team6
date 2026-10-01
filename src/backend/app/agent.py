"""
Wellness Coach Agent — Motor de Entrenamiento Inteligente Local y Orquestador de Agentes (Refactorizado).
Mantiene fachada de compatibilidad retrocompatible 100% delegando en el paquete modular app.wellness_agent.
"""

import json
import logging
from typing import Dict, Any, Optional

from app import database
from app.wellness_agent.catalog import EXERCISE_CATALOG, SPLIT_TEMPLATES, get_set_rep_scheme
from app.wellness_agent.providers import LLMProviderManager
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.tools import AgentToolRegistry
from app.wellness_agent.reasoning import ReasoningEngine
from app.react_agent import ReActAgent

logger = logging.getLogger(__name__)

use_real_ai = True

provider_manager = LLMProviderManager()
memory_manager = ConversationMemoryManager()
tool_registry = AgentToolRegistry()
reasoning_engine = ReasoningEngine(tool_registry=tool_registry)
react_agent = ReActAgent(tool_registry=tool_registry)


class WellnessCoachAgent:
    """
    Agente Orquestador Inteligente para Wellness Lift.
    Integrado con memoria conversacional de doble nivel, registro de herramientas y motor de razonamiento ReAct.
    """

    def __init__(self):
        self.providers = provider_manager
        self.memory = memory_manager
        self.tools = tool_registry
        self.reasoning = reasoning_engine
        self.react = react_agent

    def generate_routine(self, user_id: str) -> Dict[str, Any]:
        """Genera una rutina de entrenamiento semanal balanceada considerando historial y memoria."""
        extracted_facts = self.memory.get_extracted_facts(user_id)
        prompt = self.reasoning.build_routine_prompt(user_id, extracted_facts=extracted_facts)
        completion = self.providers.generate_completion(prompt, is_json=True)

        if completion:
            try:
                text = completion.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                routine = json.loads(text.strip())
                logger.info(f"Rutina generada exitosamente con proveedor LLM para {user_id}")
                return routine
            except Exception as e:
                logger.warning(f"Error parseando JSON del proveedor LLM: {e}")

        logger.info(f"Usando motor local determinista para rutina de {user_id}")
        return self.reasoning.generate_local_routine(user_id, extracted_facts=extracted_facts)

    def generate_response(self, user_id: str, message: str) -> str:
        """Genera una respuesta en la conversación considerando historial de memoria y ejecutando el ciclo ReAct."""
        self.memory.add_message(user_id, "user", message)
        profile = database.get_user_profile(user_id)
        name = profile.get("personal_info", {}).get("name", "Atleta")
        history_text = self.memory.get_formatted_history(user_id)
        extracted_facts = self.memory.get_extracted_facts(user_id)
        facts_text = "\n".join(extracted_facts) if extracted_facts else "Sin hechos adicionales extraídos."

        prompt = f"""
        Eres Wellness AI, un asistente personal deportivo experto.
        Hablas con {name}.
        
        HISTORIAL DE CONVERSACIÓN (MEMORIA A CORTO PLAZO):
        {history_text}
        
        HECHOS Y OBSERVACIONES EXTRAÍDAS (MEMORIA A LARGO PLAZO):
        {facts_text}
        
        MENSAJE ACTUAL DEL USUARIO:
        "{message}"
        
        Responde de manera natural, motivadora y basándote en ciencia del deporte.
        Si te piden alternativas de ejercicios, mantén el mismo grupo muscular.
        Sé conciso. No utilices emojis.
        """

        completion = self.providers.generate_completion(prompt, is_json=False)
        if completion:
            response_text = completion.strip()
            self.memory.add_message(user_id, "assistant", response_text)
            logger.info(f"Respuesta generada con proveedor LLM para usuario {user_id}")
            return response_text

        # Integración funcional del ciclo ReAct en el flujo principal del agente
        react_result = self.react.run_react_loop(message, athlete_id=user_id)
        response_text = react_result["final_answer"]
        self.memory.add_message(user_id, "assistant", response_text)
        logger.info(f"Respuesta generada con ciclo ReAct para usuario {user_id}")
        return response_text


_agent_instance = WellnessCoachAgent()


# ────────────────────────────────────────────────────────────────
# FUNCIONES PÚBLICAS RETROCOMPATIBLES
# ────────────────────────────────────────────────────────────────

def get_openrouter_key() -> Optional[str]:
    return provider_manager.get_openrouter_key()


def get_gemini_key() -> Optional[str]:
    return provider_manager.get_gemini_key()


def get_groq_client() -> Optional[Any]:
    groq_key = provider_manager.get_groq_key()
    if groq_key:
        try:
            import groq
            return groq.Groq(api_key=groq_key)
        except Exception:
            return None
    return None


def _generate_local_routine(user_id: str) -> Dict[str, Any]:
    return reasoning_engine.generate_local_routine(user_id, extracted_facts=memory_manager.get_extracted_facts(user_id))


def generate_weekly_routine(user_id: str) -> Dict[str, Any]:
    return _agent_instance.generate_routine(user_id)


def _generate_local_chat_response(user_id: str, message: str) -> str:
    return reasoning_engine.generate_local_chat_response(user_id, message, extracted_facts=memory_manager.get_extracted_facts(user_id))


def generate_chat_response(user_id: str, message: str) -> str:
    return _agent_instance.generate_response(user_id, message)
