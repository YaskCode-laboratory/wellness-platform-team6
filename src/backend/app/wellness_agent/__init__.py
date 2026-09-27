"""
Paquete Wellness Agent — Arquitectura Modular para Agentes Inteligentes.
Incluye catálogo de ejercicios, proveedores LLM, memoria conversacional, registro de herramientas y motor de razonamiento.
"""

from app.wellness_agent.catalog import EXERCISE_CATALOG, SPLIT_TEMPLATES, get_set_rep_scheme
from app.wellness_agent.providers import LLMProviderManager
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.tools import AgentToolRegistry
from app.wellness_agent.reasoning import ReasoningEngine

__all__ = [
    "EXERCISE_CATALOG",
    "SPLIT_TEMPLATES",
    "get_set_rep_scheme",
    "LLMProviderManager",
    "ConversationMemoryManager",
    "AgentToolRegistry",
    "ReasoningEngine",
]
