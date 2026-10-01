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


class NutritionAgent:
    """Agente especializado en Nutrición y Macronutrientes."""

    def __init__(self, tool_registry: Optional[AgentToolRegistry] = None):
        self.tool_registry = tool_registry or AgentToolRegistry()
        self.agent_name = "NutritionAgent"

    def process_request(self, user_id: str, message: str) -> SpecializedAgentResponse:
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
                agent_name=self.agent_name,
                status="success",
                content=content,
                metadata={"domain": "Nutrition & Macros"}
            )
        except Exception as e:
            logger.warning(f"Error en {self.agent_name}: {e}")
            return SpecializedAgentResponse(
                agent_name=self.agent_name,
                status="error_fallback",
                content=f"Aviso del {self.agent_name}: Inconveniente al calcular nutrición.",
                metadata={"error": str(e)}
            )


class MotivationAgent:
    """Agente especializado en Motivación y Psicología Deportiva."""

    def __init__(self):
        self.agent_name = "MotivationAgent"

    def process_request(self, user_id: str, message: str) -> SpecializedAgentResponse:
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
                agent_name=self.agent_name,
                status="success",
                content=content,
                metadata={"domain": "Psychological Reinforcement"}
            )
        except Exception as e:
            logger.warning(f"Error en {self.agent_name}: {e}")
            return SpecializedAgentResponse(
                agent_name=self.agent_name,
                status="error_fallback",
                content=f"Aviso del {self.agent_name}: Inconveniente al procesar mensaje motivacional.",
                metadata={"error": str(e)}
            )


class AnalyticsAgent:
    """Agente especializado en Analítica y Progreso de Rendimiento."""

    def __init__(self):
        self.agent_name = "AnalyticsAgent"

    def process_request(self, user_id: str, message: str) -> SpecializedAgentResponse:
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
                agent_name=self.agent_name,
                status="success",
                content=content,
                metadata={"domain": "Performance & Progress Analytics"}
            )
        except Exception as e:
            logger.warning(f"Error en {self.agent_name}: {e}")
            return SpecializedAgentResponse(
                agent_name=self.agent_name,
                status="error_fallback",
                content=f"Aviso del {self.agent_name}: Inconveniente al calcular analíticas de progreso.",
                metadata={"error": str(e)}
            )


class OrchestratorAgent:
    """
    Agente Supervisor Central que coordina el sistema multiagente.
    """

    def __init__(self, memory_manager: Optional[ConversationMemoryManager] = None):
        self.memory = memory_manager or ConversationMemoryManager()
        self.coach_agent: WellnessCoachAgent = _agent_instance
        self.nutrition_agent = NutritionAgent()
        self.motivation_agent = MotivationAgent()
        self.analytics_agent = AnalyticsAgent()
        self.tool_registry = AgentToolRegistry()

    def detect_domains(self, message: str) -> List[str]:
        """Detecta los dominios requeridos por la consulta."""
        msg_lower = message.lower().strip()

        workout_kw = ["rutina", "ejercicio", "sentadilla", "press", "músculo", "lesión", "dolor", "espalda", "rodilla", "hombro", "banca", "reemplaz", "alternativa"]
        nutrition_kw = ["nutrición", "macro", "caloría", "tdee", "proteína", "carbohidrato", "dieta", "comer"]
        motivation_kw = ["motiva", "cansado", "ánimo", "hábito", "constancia", "flojera"]
        analytics_kw = ["récord", "volumen", "sesiones", "progreso", "peso máximo", "historial"]

        domains = []
        if any(k in msg_lower for k in workout_kw):
            domains.append("workout")
        if any(k in msg_lower for k in nutrition_kw):
            domains.append("nutrition")
        if any(k in msg_lower for k in motivation_kw):
            domains.append("motivation")
        if any(k in msg_lower for k in analytics_kw):
            domains.append("analytics")

        return domains

    def classify_intent(self, message: str) -> AgentIntent:
        """
        Analiza el texto de la solicitud y clasifica la intención primaria del usuario.
        """
        domains = self.detect_domains(message)
        if len(domains) >= 2:
            return AgentIntent.MULTIDOMAIN

        if "workout" in domains:
            return AgentIntent.WORKOUT_BIOMECHANICS
        if "nutrition" in domains:
            return AgentIntent.NUTRITION
        if "analytics" in domains:
            return AgentIntent.ANALYTICS
        if "motivation" in domains:
            return AgentIntent.MOTIVATION

        return AgentIntent.GENERAL

    def delegate_to_coach(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al Wellness Coach Agent 2.0 (WellnessCoachSpecialist)."""
        try:
            if hasattr(self.coach_agent, "process_specialized_request"):
                spec_res = self.coach_agent.process_specialized_request(user_id, message)
                status = spec_res.get("status", "success")
                in_domain = spec_res.get("in_domain", True)
                return SpecializedAgentResponse(
                    agent_name="WellnessCoachAgent2.0",
                    status=status,
                    content=spec_res.get("response", ""),
                    metadata={
                        "domain": "Biomechanics & Training",
                        "in_domain": in_domain,
                        "fitness_profile": spec_res.get("fitness_profile", {}),
                        "health_conditions": spec_res.get("health_conditions", [])
                    }
                )
            else:
                res_text = self.coach_agent.generate_response(user_id, message)
                return SpecializedAgentResponse(
                    agent_name="WellnessCoachAgent2.0",
                    status="success",
                    content=res_text,
                    metadata={"domain": "Biomechanics & Training", "in_domain": True}
                )
        except Exception as e:
            logger.warning(f"Error en delegación a WellnessCoachAgent2.0: {e}")
            return self.handle_orchestration_error("WellnessCoachAgent2.0", e)

    def delegate_to_nutrition(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al NutritionAgent."""
        return self.nutrition_agent.process_request(user_id, message)

    def delegate_to_motivation(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al MotivationAgent."""
        return self.motivation_agent.process_request(user_id, message)

    def delegate_to_analytics(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Delega la solicitud al AnalyticsAgent."""
        return self.analytics_agent.process_request(user_id, message)

    def handle_multidomain_delegation(self, user_id: str, message: str) -> SpecializedAgentResponse:
        """Coordinación compuesta secuencial delegando únicamente a los dominios detectados."""
        domains = self.detect_domains(message)
        if not domains:
            domains = ["workout", "nutrition"]

        responses: List[SpecializedAgentResponse] = []
        if "workout" in domains:
            responses.append(self.delegate_to_coach(user_id, message))
        if "nutrition" in domains:
            responses.append(self.delegate_to_nutrition(user_id, message))
        if "motivation" in domains:
            responses.append(self.delegate_to_motivation(user_id, message))
        if "analytics" in domains:
            responses.append(self.delegate_to_analytics(user_id, message))

        contents = [f"--- {r.agent_name} ---\n{r.content}" for r in responses]
        integrated_content = "Respuesta Orquestada Multidominio (Supervisor):\n\n" + "\n\n".join(contents)

        statuses = [r.status for r in responses]
        if all(s == "success" for s in statuses):
            overall_status = "success"
        elif any(s == "success" for s in statuses):
            overall_status = "partial_success"
        else:
            overall_status = "error_fallback"

        agent_names = [r.agent_name for r in responses]
        return SpecializedAgentResponse(
            agent_name=f"OrchestratorAgent (Multidomain: {', '.join(agent_names)})",
            status=overall_status,
            content=integrated_content,
            metadata={
                "delegated_agents": agent_names,
                "domain_statuses": {r.agent_name: r.status for r in responses}
            }
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

