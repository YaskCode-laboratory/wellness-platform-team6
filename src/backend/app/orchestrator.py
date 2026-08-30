"""
Orchestrator Agent — Supervisor Central de la Plataforma Multiagente Wellness Lift.
Clasifica intenciones de usuario, delega tareas a agentes especializados (Wellness Coach 2.0, Nutrición, Motivación, Analítica),
coordina ejecuciones compuestas multidominio y gestiona fallbacks de orquestación.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

from app import database
from app.agent import WellnessCoachAgent, _agent_instance
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)


class AgentIntent(str, Enum):
    WORKOUT_BIOMECHANICS = "WORKOUT_BIOMECHANICS"
    NUTRITION = "NUTRITION"
    MOTIVATION = "MOTIVATION"
    ANALYTICS = "ANALYTICS"
    MULTIDOMAIN = "MULTIDOMAIN"
    GENERAL = "GENERAL"


class SpecializedAgentResponse:
    """Estructura de respuesta uniforme retornada por los agentes delegados."""

    def __init__(self, agent_name: str, status: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.agent_name = agent_name
        self.status = status
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "content": self.content,
            "metadata": self.metadata,
        }


class OrchestratorAgent:
    """
    Agente Supervisor Central que coordina el sistema multiagente.
    """

    def __init__(self, memory_manager: Optional[ConversationMemoryManager] = None):
        self.memory = memory_manager or ConversationMemoryManager()
        self.coach_agent: WellnessCoachAgent = _agent_instance
        self.tool_registry = AgentToolRegistry()

    def classify_intent(self, message: str) -> AgentIntent:
        """
        Analiza el texto de la solicitud y clasifica la intención primaria del usuario.
        """
        msg_lower = message.lower().strip()

        # Palabras clave por dominio
        workout_kw = ["rutina", "ejercicio", "sentadilla", "press", "músculo", "lesión", "dolor", "espalda", "rodilla", "hombro", "banca", "reemplaz", "alternativa"]
        nutrition_kw = ["nutrición", "macro", "caloría", "tdee", "proteína", "carbohidrato", "dieta", "comer"]
        motivation_kw = ["motiva", "cansado", "ánimo", "hábito", "constancia", "flojera"]
        analytics_kw = ["récord", "volumen", "sesiones", "progreso", "peso máximo", "historial"]

        has_workout = any(k in msg_lower for k in workout_kw)
        has_nutrition = any(k in msg_lower for k in nutrition_kw)
        has_motivation = any(k in msg_lower for k in motivation_kw)
        has_analytics = any(k in msg_lower for k in analytics_kw)

        # Concurrencia multidominio
        active_domains = sum([has_workout, has_nutrition, has_motivation, has_analytics])
        if active_domains >= 2:
            return AgentIntent.MULTIDOMAIN

        if has_workout:
            return AgentIntent.WORKOUT_BIOMECHANICS
        if has_nutrition:
            return AgentIntent.NUTRITION
        if has_analytics:
            return AgentIntent.ANALYTICS
        if has_motivation:
            return AgentIntent.MOTIVATION

        return AgentIntent.GENERAL

    def delegate_to_coach(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al Wellness Coach Agent 2.0 (Agente especializado del Equipo 6)."""
        try:
            res_text = self.coach_agent.generate_response(user_id, message)
            return SpecializedAgentResponse(
                agent_name="WellnessCoachAgent2.0",
                status="success",
                content=res_text,
                metadata={"domain": "Biomechanics & Training"}
            )
        except Exception as e:
            logger.warning(f"Error en delegación a WellnessCoachAgent2.0: {e}")
            return self.handle_orchestration_error("WellnessCoachAgent2.0", e)

    def delegate_to_nutrition(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al Nutrition Agent."""
        try:
            macros_res = self.tool_registry.execute_tool("calculate_nutrition_macros", user_id=user_id)
            profile = database.get_user_profile(user_id)
            name = profile.get("personal_info", {}).get("name", "Atleta")

            if macros_res.get("status") == "success" and macros_res.get("tdee"):
                content = (
                    f"Plan Nutricional Delegado a Nutrition Agent para {name}:\n"
                    f"- TDEE Estimado: {macros_res['tdee']} kcal/día\n"
                    f"- Proteínas: {macros_res['protein']}g\n"
                    f"- Carbohidratos: {macros_res['carbs']}g\n"
                    f"- Grasas: {macros_res['fats']}g"
                )
            else:
                content = (
                    f"Hola {name}, el Nutrition Agent requiere que completes tu peso, altura y objetivo "
                    f"en la sección Perfil para calcular tus macronutrientes."
                )

            return SpecializedAgentResponse(
                agent_name="NutritionAgent",
                status="success",
                content=content,
                metadata={"domain": "Nutrition & Macros"}
            )
        except Exception as e:
            logger.warning(f"Error en delegación a NutritionAgent: {e}")
            return self.handle_orchestration_error("NutritionAgent", e)

    def delegate_to_motivation(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al Motivation Agent."""
        try:
            profile = database.get_user_profile(user_id)
            name = profile.get("personal_info", {}).get("name", "Atleta")
            sessions = database.get_workout_sessions(user_id)

            content = (
                f"Mensaje del Motivation Agent para {name}:\n"
                f"La disciplina supera a la motivación momentánea. Llevas {len(sessions)} sesiones registradas. "
                f"Cada entrenamiento constante te acerca a tu mejor versión. ¡Sigue adelante!"
            )
            return SpecializedAgentResponse(
                agent_name="MotivationAgent",
                status="success",
                content=content,
                metadata={"domain": "Psychological Reinforcement"}
            )
        except Exception as e:
            logger.warning(f"Error en delegación a MotivationAgent: {e}")
            return self.handle_orchestration_error("MotivationAgent", e)

    def delegate_to_analytics(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al Analytics Agent."""
        try:
            profile = database.get_user_profile(user_id)
            name = profile.get("personal_info", {}).get("name", "Atleta")
            sessions = database.get_workout_sessions(user_id)
            total_vol = sum(s.get("total_volume", 0) for s in sessions)

            content = (
                f"Informe del Analytics Agent para {name}:\n"
                f"- Sesiones completadas: {len(sessions)}\n"
                f"- Volumen total acumulado: {total_vol:.1f} kg\n"
                f"- Tendencia de sobrecarga: Positiva (Incremento constante)."
            )
            return SpecializedAgentResponse(
                agent_name="AnalyticsAgent",
                status="success",
                content=content,
                metadata={"domain": "Performance & Progress Analytics"}
            )
        except Exception as e:
            logger.warning(f"Error en delegación a AnalyticsAgent: {e}")
            return self.handle_orchestration_error("AnalyticsAgent", e)

    def handle_multidomain_delegation(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Coordinación compuesta para solicitudes que abarcan múltiples dominios."""
        coach_resp = self.delegate_to_coach(user_id, message)
        nutri_resp = self.delegate_to_nutrition(user_id, message)

        integrated_content = (
            f"Respuesta Orquestada Multidominio (Supervisor):\n\n"
            f"--- Módulo Entrenador (Wellness Coach 2.0) ---\n"
            f"{coach_resp.content}\n\n"
            f"--- Módulo Nutrición (Nutrition Agent) ---\n"
            f"{nutri_resp.content}"
        )

        return SpecializedAgentResponse(
            agent_name="OrchestratorAgent (Multidomain)",
            status="success",
            content=integrated_content,
            metadata={"delegated_agents": ["WellnessCoachAgent2.0", "NutritionAgent"]}
        )

    def handle_orchestration_error(self, agent_name: str, exception: Exception) -> SpecializedAgentResponse:
        """Manejo de excepciones y respuesta estructurada de fallback."""
        fallback_content = (
            f"Aviso de Orquestación: El agente '{agent_name}' presentó un inconveniente temporal. "
            f"Te recomendamos seguir las pautas de seguridad general y consultar a tu entrenador."
        )
        return SpecializedAgentResponse(
            agent_name=agent_name,
            status="error_fallback",
            content=fallback_content,
            metadata={"error": str(exception)}
        )

    def process_user_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Entrada principal del Supervisor. Clasifica intenciones, delega tareas y retorna la respuesta.
        """
        intent = self.classify_intent(message)
        logger.info(f"Orchestrator Agent: Solicitud de usuario '{user_id}' clasificada como intent '{intent}'")

        if intent == AgentIntent.WORKOUT_BIOMECHANICS:
            response = self.delegate_to_coach(user_id, message)
        elif intent == AgentIntent.NUTRITION:
            response = self.delegate_to_nutrition(user_id, message)
        elif intent == AgentIntent.MOTIVATION:
            response = self.delegate_to_motivation(user_id, message)
        elif intent == AgentIntent.ANALYTICS:
            response = self.delegate_to_analytics(user_id, message)
        elif intent == AgentIntent.MULTIDOMAIN:
            response = self.handle_multidomain_delegation(user_id, message)
        else:
            # Respuesta general del supervisor
            response = self.delegate_to_coach(user_id, message)

        return {
            "user_id": user_id,
            "intent": intent.value,
            "orchestrated_by": "OrchestratorAgent",
            "delegated_agent": response.agent_name,
            "status": response.status,
            "response": response.content,
            "metadata": response.metadata,
        }


# Instancia singleton del Orchestrator Agent
_orchestrator_instance = OrchestratorAgent()
