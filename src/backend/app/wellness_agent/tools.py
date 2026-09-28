"""
Módulo de Registro de Herramientas del Agente (AgentToolRegistry).
Define y ejecuta herramientas específicas (Tool Calling / Function Calling) para consultar ejercicios, nutrición, prevención de lesiones y recuperación RAG.
"""

import random
from typing import Dict, Any, Callable, List, Optional
from app import database
from app.wellness_agent.catalog import EXERCISE_CATALOG

try:
    from app.rag_evaluator import RAGEvaluator
except ImportError:
    RAGEvaluator = None


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

    def get_exercise_alternative(self, muscle_group: str) -> Dict[str, Any]:
        """Retorna un ejercicio alternativo del catálogo para el grupo muscular especificado."""
        catalog = EXERCISE_CATALOG.get(muscle_group, [])
        if not catalog:
            return {"status": "not_found", "message": f"No hay ejercicios en el catálogo para {muscle_group}"}

        selected = random.choice(catalog)
        return {
            "status": "success",
            "muscle_group": muscle_group,
            "exercise_id": selected["exercise_id"],
            "name": selected["name"]
        }

    def calculate_nutrition_macros(self, user_id: str) -> Dict[str, Any]:
        """Calcula el perfil nutricional y desglose de macronutrientes para el usuario."""
        profile = database.get_user_profile(user_id)
        nutrition = profile.get("nutrition_profile", {})
        tdee = nutrition.get("tdee", 0)
        macros = nutrition.get("macros", {})

        return {
            "user_id": user_id,
            "tdee": tdee,
            "protein": macros.get("protein", 0),
            "carbs": macros.get("carbs", 0),
            "fats": macros.get("fats", 0)
        }

    def assess_injury_risk(self, user_id: str, exercise_name: str) -> Dict[str, Any]:
        """Evalúa si un ejercicio presenta riesgos según las condiciones de salud del usuario."""
        profile = database.get_user_profile(user_id)
        fitness = profile.get("fitness_profile", {})
        health_conditions = [h.lower() for h in fitness.get("health_conditions", [])]

        is_lumbar_risk = any("hernia" in h or "lumbar" in h for h in health_conditions)
        is_squat_or_deadlift = any(k in exercise_name.lower() for k in ["sentadilla con barra", "peso muerto"])

        if is_lumbar_risk and is_squat_or_deadlift:
            return {
                "risk_level": "HIGH",
                "warning": "Ejercicio contraindicado por lesión/hernia lumbar.",
                "safe_recommendation": "Utilizar Prensa Inclinada a 45° o Sentadilla Goblet asistida."
            }

        return {
            "risk_level": "LOW",
            "warning": "Sin contraindicación directa registrada.",
            "safe_recommendation": "Ejecutar con técnica neutra y rango de movimiento controlado."
        }

    def retrieve_rag_knowledge(self, query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Consulta la base de conocimiento RAG mediante búsqueda semántica vectorial."""
        if not self.rag_evaluator:
            return []

        return self.rag_evaluator.retrieve_top_k(query_text, top_k=top_k)

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Ejecuta una herramienta registrada dinámicamente."""
        tool = self._tools.get(tool_name)
        if not tool:
            return {"status": "error", "message": f"Herramienta '{tool_name}' no registrada."}
        return tool(**kwargs)
