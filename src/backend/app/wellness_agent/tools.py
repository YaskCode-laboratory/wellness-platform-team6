"""
Módulo de Registro de Herramientas del Agente (AgentToolRegistry).
Define y ejecuta herramientas específicas (Tool Calling / Function Calling) para consultar ejercicios, nutrición, prevención de lesiones y recuperación RAG.
"""

import logging
import random
from typing import Dict, Any, Callable, List, Optional
from app import database
from app.wellness_agent.catalog import EXERCISE_CATALOG

try:
    from app.rag_evaluator import RAGEvaluator
except ImportError:
    RAGEvaluator = None

logger = logging.getLogger(__name__)


class AgentToolRegistry:
    """
    Registro centralizado de herramientas ejecutables por el Wellness Agent.
    """

    def __init__(self):
        self.rag_evaluator = RAGEvaluator() if RAGEvaluator else None
        self._tools: Dict[str, Callable] = {
            "get_exercise_alternative": self.get_exercise_alternative,
            "calculate_nutrition_macros": self.calculate_nutrition_macros,
            "assess_injury_risk": self.assess_injury_risk,
            "retrieve_rag_knowledge": self.retrieve_rag_knowledge,
        }

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Retorna las declaraciones formales de herramientas en formato JSON Schema (Tool Declarations)."""
        return [
            {
                "name": "get_exercise_alternative",
                "description": "Obtiene un ejercicio sustituto seguro para el mismo grupo muscular si una máquina está ocupada.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "muscle_group": {
                            "type": "string",
                            "description": "Grupo muscular objetivo (ej. Pecho, Espalda, Piernas, Hombros, Bíceps, Tríceps)"
                        }
                    },
                    "required": ["muscle_group"]
                }
            },
            {
                "name": "calculate_nutrition_macros",
                "description": "Calcula el TDEE y desglose de macronutrientes recomendados para el atleta.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Identificador del usuario en la plataforma"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "assess_injury_risk",
                "description": "Evalúa el riesgo biomecánico de un ejercicio según las condiciones de salud del usuario.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "Identificador del usuario"
                        },
                        "exercise_name": {
                            "type": "string",
                            "description": "Nombre del ejercicio a evaluar (ej. Sentadilla con Barra, Press Militar)"
                        }
                    },
                    "required": ["user_id", "exercise_name"]
                }
            },
            {
                "name": "retrieve_rag_knowledge",
                "description": "Realiza búsqueda semántica vectorial en la base de conocimiento RAG de fisioterapia y periodización.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "Consulta o duda técnica biomecánica a buscar en el Vector Store"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Cantidad de fragmentos más relevantes a recuperar (default: 2)"
                        }
                    },
                    "required": ["query_text"]
                }
            }
        ]

    def get_exercise_alternative(self, muscle_group: str) -> Dict[str, Any]:
        """Retorna un ejercicio alternativo del catálogo para el grupo muscular especificado."""
        if not muscle_group or not isinstance(muscle_group, str):
            return {"status": "error", "message": "Parámetro muscle_group inválido."}

        # Normalizar capitalización
        group_map = {k.lower(): k for k in EXERCISE_CATALOG.keys()}
        target_key = group_map.get(muscle_group.lower(), muscle_group)

        catalog = EXERCISE_CATALOG.get(target_key, [])
        if not catalog:
            return {"status": "not_found", "message": f"No hay ejercicios en el catálogo para {muscle_group}."}

        selected = random.choice(catalog)
        return {
            "status": "success",
            "muscle_group": target_key,
            "exercise_id": selected["exercise_id"],
            "name": selected["name"]
        }

    def calculate_nutrition_macros(self, user_id: str) -> Dict[str, Any]:
        """Calcula el perfil nutricional y desglose de macronutrientes para el usuario."""
        if not user_id:
            return {"status": "error", "message": "Identificador user_id requerido."}

        profile = database.get_user_profile(user_id)
        nutrition = profile.get("nutrition_profile", {})
        tdee = nutrition.get("tdee", 0)
        macros = nutrition.get("macros", {})

        return {
            "status": "success",
            "user_id": user_id,
            "tdee": tdee,
            "protein": macros.get("protein", 0),
            "carbs": macros.get("carbs", 0),
            "fats": macros.get("fats", 0)
        }

    def assess_injury_risk(self, user_id: str, exercise_name: str) -> Dict[str, Any]:
        """Evalúa si un ejercicio presenta riesgos según las condiciones de salud del usuario."""
        if not exercise_name:
            return {"status": "error", "message": "Nombre del ejercicio requerido."}

        profile = database.get_user_profile(user_id)
        fitness = profile.get("fitness_profile", {})
        health_conditions = [h.lower() for h in fitness.get("health_conditions", [])]

        is_lumbar_risk = any("hernia" in h or "lumbar" in h for h in health_conditions)
        is_squat_or_deadlift = any(k in exercise_name.lower() for k in ["sentadilla con barra", "peso muerto"])

        if is_lumbar_risk and is_squat_or_deadlift:
            return {
                "status": "success",
                "risk_level": "HIGH",
                "warning": "Ejercicio contraindicado por lesión/hernia lumbar.",
                "safe_recommendation": "Utilizar Prensa Inclinada a 45° o Sentadilla Goblet asistida."
            }

        return {
            "status": "success",
            "risk_level": "LOW",
            "warning": "Sin contraindicación directa registrada.",
            "safe_recommendation": "Ejecutar con técnica neutra y rango de movimiento controlado."
        }

    def retrieve_rag_knowledge(self, query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Consulta la base de conocimiento RAG mediante búsqueda semántica vectorial."""
        if not query_text:
            return []

        if not self.rag_evaluator:
            return []

        try:
            return self.rag_evaluator.retrieve_top_k(query_text, top_k=top_k)
        except Exception as e:
            logger.warning(f"Error consultando RAG evaluator: {e}")
            return []

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Ejecuta una herramienta registrada dinámicamente con control de errores."""
        tool = self._tools.get(tool_name)
        if not tool:
            return {"status": "error", "message": f"Herramienta '{tool_name}' no registrada."}
        try:
            return tool(**kwargs)
        except Exception as e:
            logger.warning(f"Error ejecutando herramienta {tool_name}: {e}")
            return {"status": "error", "message": f"Fallo al ejecutar herramienta {tool_name}: {str(e)}"}
