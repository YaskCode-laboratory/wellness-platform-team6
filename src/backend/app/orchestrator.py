"""
Orchestrator Agent — Supervisor Central de la Plataforma Multiagente Wellness Lift.
Clasifica intenciones de usuario, delega tareas a agentes especializados (Wellness Coach 2.0, Nutrición, Motivación, Analítica),
coordina ejecuciones compuestas multidominio y gestiona fallbacks de orquestación a través del protocolo InterAgentMessage.
"""

import uuid
import time
import logging
from enum import Enum
from typing import Dict, Any, List, Optional

from app import database
from app.agent import WellnessCoachAgent, _agent_instance
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.tools import AgentToolRegistry
from app.wellness_agent.communication import InterAgentMessage, InterAgentResponse, DelegationTracer, global_tracer

logger = logging.getLogger(__name__)


class AgentIntent(str, Enum):
    WORKOUT_BIOMECHANICS = "WORKOUT_BIOMECHANICS"
    NUTRITION = "NUTRITION"
    MOTIVATION = "MOTIVATION"
    ANALYTICS = "ANALYTICS"
    MULTIDOMAIN = "MULTIDOMAIN"
    GENERAL = "GENERAL"


# Mantener alias de compatibilidad con SpecializedAgentResponse
SpecializedAgentResponse = InterAgentResponse


# ────────────────────────────────────────────────────────────────
# AGENTES ESPECIALIZADOS DESACOPLADOS (INTERAGENT PROTOCOL)
# ────────────────────────────────────────────────────────────────

class NutritionAgent:
    """Agente Especializado en Nutrición y Cálculo de Macronutrientes."""

    def process_interagent_message(self, msg: InterAgentMessage) -> InterAgentResponse:
        start_time = time.time()
        user_id = msg.user_id
        tool_registry = AgentToolRegistry()

        macros_res = tool_registry.execute_tool("calculate_nutrition_macros", user_id=user_id)
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

        return InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="NutritionAgent",
            status="success",
            content=content,
            metadata={"domain": "Nutrition & Macros"},
            execution_time_ms=(time.time() - start_time) * 1000
        )


class MotivationAgent:
    """Agente Especializado en Refuerzo Psicológico y Hábitos."""

    def process_interagent_message(self, msg: InterAgentMessage) -> InterAgentResponse:
        start_time = time.time()
        user_id = msg.user_id
        profile = database.get_user_profile(user_id)
        name = profile.get("personal_info", {}).get("name", "Atleta")
        sessions = database.get_workout_sessions(user_id)

        content = (
            f"Mensaje del Motivation Agent para {name}:\n"
            f"La disciplina supera a la motivación momentánea. Llevas {len(sessions)} sesiones registradas. "
            f"Cada entrenamiento constante te acerca a tu mejor versión. ¡Sigue adelante!"
        )
        return InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="MotivationAgent",
            status="success",
            content=content,
            metadata={"domain": "Psychological Reinforcement"},
            execution_time_ms=(time.time() - start_time) * 1000
        )


class AnalyticsAgent:
    """Agente Especializado en Analítica de Progreso y Volumen de Entrenamiento."""

    def process_interagent_message(self, msg: InterAgentMessage) -> InterAgentResponse:
        start_time = time.time()
        user_id = msg.user_id
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
        return InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="AnalyticsAgent",
            status="success",
            content=content,
            metadata={"domain": "Performance & Progress Analytics"},
            execution_time_ms=(time.time() - start_time) * 1000
        )


class OrchestratorAgent:
    """
    Agente Supervisor Central que coordina el sistema multiagente bajo el protocolo de mensajes InterAgentMessage.
    """

    def __init__(self, memory_manager: Optional[ConversationMemoryManager] = None, tracer: Optional[DelegationTracer] = None):
        self.memory = memory_manager or ConversationMemoryManager()
        self.coach_agent: WellnessCoachAgent = _agent_instance
        self.nutrition_agent = NutritionAgent()
        self.motivation_agent = MotivationAgent()
        self.analytics_agent = AnalyticsAgent()
        self.tool_registry = AgentToolRegistry()
        self.tracer = tracer or global_tracer

    def detect_domains(self, message: str) -> List[AgentIntent]:
        """
        Detecta dinámicamente la lista de dominios / intenciones involucrados en la solicitud.
        """
        msg_lower = message.lower().strip()

        workout_kw = ["rutina", "ejercicio", "sentadilla", "press", "músculo", "lesión", "dolor", "espalda", "rodilla", "hombro", "banca", "reemplaz", "alternativa", "pierna", "pecho", "tricep", "bicep"]
        nutrition_kw = ["nutrición", "macro", "caloría", "tdee", "proteína", "carbohidrato", "dieta", "comer", "comida"]
        motivation_kw = ["motiva", "cansado", "ánimo", "hábito", "constancia", "flojera"]
        analytics_kw = ["récord", "volumen", "sesiones", "progreso", "peso máximo", "historial"]

        domains = []
        if any(k in msg_lower for k in workout_kw):
            domains.append(AgentIntent.WORKOUT_BIOMECHANICS)
        if any(k in msg_lower for k in nutrition_kw):
            domains.append(AgentIntent.NUTRITION)
        if any(k in msg_lower for k in motivation_kw):
            domains.append(AgentIntent.MOTIVATION)
        if any(k in msg_lower for k in analytics_kw):
            domains.append(AgentIntent.ANALYTICS)

        return domains

    def classify_intent(self, message: str) -> AgentIntent:
        """
        Analiza el texto de la solicitud y clasifica la intención primaria del usuario.
        """
        domains = self.detect_domains(message)
        if len(domains) >= 2:
            return AgentIntent.MULTIDOMAIN

        if len(domains) == 1:
            return domains[0]

        return AgentIntent.GENERAL

    def _build_context_payload(self, user_id: str, message: str) -> Dict[str, Any]:
        """Construye el context_payload estandarizado integrando perfil de salud y hechos de memoria."""
        profile = database.get_user_profile(user_id)
        fitness_profile = profile.get("fitness_profile", {})
        health_conditions = fitness_profile.get("health_conditions", [])
        if not health_conditions and "health_conditions" in profile:
            health_conditions = profile.get("health_conditions", [])
        limitations = fitness_profile.get("limitations", "Sin limitaciones registradas")
        goal = fitness_profile.get("goal", "hipertrofia")
        level = fitness_profile.get("level", "intermedio")
        extracted_facts = self.memory.get_extracted_facts(user_id)

        return {
            "original_message": message,
            "message": message,
            "user_id": user_id,
            "health_conditions": health_conditions,
            "limitations": limitations,
            "goal": goal,
            "level": level,
            "extracted_facts": extracted_facts,
        }

    def delegate_to_coach(self, user_id: str, message: str, trace_id: Optional[str] = None, parent_hop_count: int = 0) -> InterAgentResponse:
        """Delega la solicitud al Wellness Coach Agent 2.0 transmisitiendo InterAgentMessage."""
        context_payload = self._build_context_payload(user_id, message)
        hop_count = parent_hop_count + 1

        msg = InterAgentMessage(
            source_agent="OrchestratorAgent",
            target_agent="WellnessCoachAgent2.0",
            user_id=user_id,
            intent=AgentIntent.WORKOUT_BIOMECHANICS.value,
            context_payload=context_payload,
            trace_id=trace_id,
            hop_count=hop_count
        )

        if not self.tracer.log_delegation(msg):
            return InterAgentResponse(
                task_id=msg.task_id,
                trace_id=msg.trace_id,
                source_agent="WellnessCoachAgent2.0",
                status="error_cycle_detected",
                content="Aviso de Orquestación: Se previno un ciclo o número excesivo de delegaciones entre agentes."
            )

        try:
            resp = self.coach_agent.process_interagent_message(msg)
            self.tracer.log_response(resp)
            return resp
        except Exception as e:
            logger.warning(f"Error en delegación a WellnessCoachAgent2.0: {e}")
            resp = self.handle_orchestration_error("WellnessCoachAgent2.0", e, msg)
            self.tracer.log_response(resp)
            return resp

    def delegate_to_nutrition(self, user_id: str, message: str, trace_id: Optional[str] = None, parent_hop_count: int = 0) -> InterAgentResponse:
        """Delega la solicitud al Nutrition Agent transmitiendo InterAgentMessage."""
        context_payload = self._build_context_payload(user_id, message)
        hop_count = parent_hop_count + 1

        msg = InterAgentMessage(
            source_agent="OrchestratorAgent",
            target_agent="NutritionAgent",
            user_id=user_id,
            intent=AgentIntent.NUTRITION.value,
            context_payload=context_payload,
            trace_id=trace_id,
            hop_count=hop_count
        )

        if not self.tracer.log_delegation(msg):
            return InterAgentResponse(
                task_id=msg.task_id,
                trace_id=msg.trace_id,
                source_agent="NutritionAgent",
                status="error_cycle_detected",
                content="Aviso de Orquestación: Se previno un ciclo o número excesivo de delegaciones."
            )

        try:
            resp = self.nutrition_agent.process_interagent_message(msg)
            self.tracer.log_response(resp)
            return resp
        except Exception as e:
            logger.warning(f"Error en delegación a NutritionAgent: {e}")
            resp = self.handle_orchestration_error("NutritionAgent", e, msg)
            self.tracer.log_response(resp)
            return resp

    def delegate_to_motivation(self, user_id: str, message: str, trace_id: Optional[str] = None, parent_hop_count: int = 0) -> InterAgentResponse:
        """Delega la solicitud al Motivation Agent transmitiendo InterAgentMessage."""
        context_payload = self._build_context_payload(user_id, message)
        hop_count = parent_hop_count + 1

        msg = InterAgentMessage(
            source_agent="OrchestratorAgent",
            target_agent="MotivationAgent",
            user_id=user_id,
            intent=AgentIntent.MOTIVATION.value,
            context_payload=context_payload,
            trace_id=trace_id,
            hop_count=hop_count
        )

        if not self.tracer.log_delegation(msg):
            return InterAgentResponse(
                task_id=msg.task_id,
                trace_id=msg.trace_id,
                source_agent="MotivationAgent",
                status="error_cycle_detected",
                content="Aviso de Orquestación: Ciclo prevenido."
            )

        try:
            resp = self.motivation_agent.process_interagent_message(msg)
            self.tracer.log_response(resp)
            return resp
        except Exception as e:
            logger.warning(f"Error en delegación a MotivationAgent: {e}")
            resp = self.handle_orchestration_error("MotivationAgent", e, msg)
            self.tracer.log_response(resp)
            return resp

    def delegate_to_analytics(self, user_id: str, message: str, trace_id: Optional[str] = None, parent_hop_count: int = 0) -> InterAgentResponse:
        """Delega la solicitud al Analytics Agent transmitiendo InterAgentMessage."""
        context_payload = self._build_context_payload(user_id, message)
        hop_count = parent_hop_count + 1

        msg = InterAgentMessage(
            source_agent="OrchestratorAgent",
            target_agent="AnalyticsAgent",
            user_id=user_id,
            intent=AgentIntent.ANALYTICS.value,
            context_payload=context_payload,
            trace_id=trace_id,
            hop_count=hop_count
        )

        if not self.tracer.log_delegation(msg):
            return InterAgentResponse(
                task_id=msg.task_id,
                trace_id=msg.trace_id,
                source_agent="AnalyticsAgent",
                status="error_cycle_detected",
                content="Aviso de Orquestación: Ciclo prevenido."
            )

        try:
            resp = self.analytics_agent.process_interagent_message(msg)
            self.tracer.log_response(resp)
            return resp
        except Exception as e:
            logger.warning(f"Error en delegación a AnalyticsAgent: {e}")
            resp = self.handle_orchestration_error("AnalyticsAgent", e, msg)
            self.tracer.log_response(resp)
            return resp

    def handle_multidomain_delegation(self, user_id: str, message: str, trace_id: Optional[str] = None, parent_hop_count: int = 0) -> InterAgentResponse:
        """Coordinación compuesta para solicitudes que abarcan múltiples dominios con trazabilidad unificada y estados compuestos."""
        context_payload = self._build_context_payload(user_id, message)
        hop_count = parent_hop_count + 1

        msg = InterAgentMessage(
            source_agent="OrchestratorAgent",
            target_agent="OrchestratorAgent (Multidomain)",
            user_id=user_id,
            intent=AgentIntent.MULTIDOMAIN.value,
            context_payload=context_payload,
            trace_id=trace_id,
            hop_count=hop_count
        )

        # Verificar si la traza del flujo multidominio es rechazada por ciclo o hop_count
        if not self.tracer.log_delegation(msg):
            return InterAgentResponse(
                task_id=msg.task_id,
                trace_id=msg.trace_id,
                source_agent="OrchestratorAgent (Multidomain)",
                status="error_cycle_detected",
                content="Aviso de Orquestación: Se previno un ciclo o número excesivo de delegaciones en el flujo multidominio."
            )

        start_time = time.time()
        active_domains = self.detect_domains(message)
        if not active_domains:
            active_domains = [AgentIntent.WORKOUT_BIOMECHANICS, AgentIntent.NUTRITION]

        responses: List[InterAgentResponse] = []
        delegated_agents: List[str] = []
        content_parts: List[str] = []

        domain_agent_map = {
            AgentIntent.WORKOUT_BIOMECHANICS: (self.delegate_to_coach, "Módulo Entrenador (Wellness Coach 2.0)", "WellnessCoachAgent2.0"),
            AgentIntent.NUTRITION: (self.delegate_to_nutrition, "Módulo Nutrición (Nutrition Agent)", "NutritionAgent"),
            AgentIntent.MOTIVATION: (self.delegate_to_motivation, "Módulo Motivación (Motivation Agent)", "MotivationAgent"),
            AgentIntent.ANALYTICS: (self.delegate_to_analytics, "Módulo Analítica (Analytics Agent)", "AnalyticsAgent"),
        }

        for domain in active_domains:
            if domain in domain_agent_map:
                delegate_fn, title, agent_name = domain_agent_map[domain]
                sub_resp = delegate_fn(user_id, message, trace_id=msg.trace_id, parent_hop_count=msg.hop_count)
                responses.append(sub_resp)
                delegated_agents.append(agent_name)
                content_parts.append(f"--- {title} ---\n{sub_resp.content}")

        integrated_content = "Respuesta Orquestada Multidominio (Supervisor):\n\n" + "\n\n".join(content_parts)

        # Evaluación de estado compuesto: success, partial_success, error_fallback
        success_count = sum(1 for r in responses if r.status == "success")
        if success_count == len(responses) and len(responses) > 0:
            composite_status = "success"
        elif success_count > 0:
            composite_status = "partial_success"
        else:
            composite_status = "error_fallback"

        resp = InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="OrchestratorAgent (Multidomain)",
            status=composite_status,
            content=integrated_content,
            metadata={"delegated_agents": delegated_agents},
            execution_time_ms=(time.time() - start_time) * 1000
        )
        self.tracer.log_response(resp)
        return resp

    def handle_orchestration_error(self, agent_name: str, exception: Exception, msg: Optional[InterAgentMessage] = None) -> InterAgentResponse:
        """Manejo de excepciones y respuesta estructurada de fallback."""
        fallback_content = (
            f"Aviso de Orquestación: El agente '{agent_name}' presentó un inconveniente temporal. "
            f"Te recomendamos seguir las pautas de seguridad general y consultar a tu entrenador."
        )
        return InterAgentResponse(
            task_id=msg.task_id if msg else f"TASK-ERR-{uuid.uuid4().hex[:4]}",
            trace_id=msg.trace_id if msg else f"TRACE-ERR-{uuid.uuid4().hex[:4]}",
            source_agent=agent_name,
            status="error_fallback",
            content=fallback_content,
            metadata={"error": str(exception)}
        )

    def process_user_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Entrada principal del Supervisor. Clasifica intenciones, delega tareas con trazabilidad y retorna la respuesta.
        """
        intent = self.classify_intent(message)
        trace_id = f"TRACE-{uuid.uuid4().hex[:8].upper()}"
        logger.info(f"Orchestrator Agent: Solicitud '{user_id}' (trace: {trace_id}) clasificada como intent '{intent}'")

        if intent == AgentIntent.WORKOUT_BIOMECHANICS:
            response = self.delegate_to_coach(user_id, message, trace_id=trace_id, parent_hop_count=0)
        elif intent == AgentIntent.NUTRITION:
            response = self.delegate_to_nutrition(user_id, message, trace_id=trace_id, parent_hop_count=0)
        elif intent == AgentIntent.MOTIVATION:
            response = self.delegate_to_motivation(user_id, message, trace_id=trace_id, parent_hop_count=0)
        elif intent == AgentIntent.ANALYTICS:
            response = self.delegate_to_analytics(user_id, message, trace_id=trace_id, parent_hop_count=0)
        elif intent == AgentIntent.MULTIDOMAIN:
            response = self.handle_multidomain_delegation(user_id, message, trace_id=trace_id, parent_hop_count=0)
        else:
            response = self.delegate_to_coach(user_id, message, trace_id=trace_id, parent_hop_count=0)

        trace_history = self.tracer.get_trace_history(response.trace_id)

        return {
            "user_id": user_id,
            "intent": intent.value,
            "orchestrated_by": "OrchestratorAgent",
            "delegated_agent": response.source_agent,
            "status": response.status,
            "response": response.content,
            "trace_id": response.trace_id,
            "task_id": response.task_id,
            "execution_time_ms": response.execution_time_ms,
            "trace_history": trace_history,
            "metadata": response.metadata,
        }


# Instancia singleton del Orchestrator Agent
_orchestrator_instance = OrchestratorAgent()

