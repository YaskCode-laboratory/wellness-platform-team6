"""
Wellness Coach Specialist — Agente Especializado del Equipo 6.
Dominio: Biomecánica, Selección de Ejercicios, Adaptación Médica por Lesiones y Generación de Rutinas.
Integra Motor RAG, Memoria Conversacional de Doble Nivel, Tool Calling y Delimitación de Dominio.
"""

import json
import logging
from typing import Dict, Any, Optional

from app import database
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.providers import LLMProviderManager
from app.wellness_agent.reasoning import ReasoningEngine
from app.wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)


class WellnessCoachSpecialist:
    """
    Agente Especializado del Equipo 6 para la Plataforma Multiagente Wellness Lift.
    Responsabilidad exclusiva: Biomecánica del Ejercicio, Rutinas Adaptativas y Seguridad Médica.
    """

    def __init__(
        self,
        memory_manager: Optional[ConversationMemoryManager] = None,
        tool_registry: Optional[AgentToolRegistry] = None,
        reasoning_engine: Optional[ReasoningEngine] = None,
        llm_provider: Optional[LLMProviderManager] = None,
    ):
        self.memory = memory_manager or ConversationMemoryManager()
        self.tools = tool_registry or AgentToolRegistry()
        self.reasoning = reasoning_engine or ReasoningEngine(tool_registry=self.tools)
        self.llm = llm_provider or LLMProviderManager()

    def is_query_in_domain(self, query: str) -> bool:
        """
        Verifica si la consulta pertenece al dominio del agente especializado (Biomecánica & Entrenamiento).
        """
        q_lower = query.lower()
        # Términos que identifican el dominio del coach
        coach_keywords = [
            "rutina", "ejercicio", "entrenamiento", "sentadilla", "press", "banca", "peso muerto",
            "lesión", "dolor", "espalda", "hernia", "rodilla", "hombro", "reemplaz", "alternativa",
            "músculo", "pecho", "espalda", "piernas", "biceps", "triceps", "hipertrofia", "fuerza",
            "serie", "repetición", "rpe", "rir", "descanso", "calentamiento", "postura", "técnica"
        ]

        # Términos ajenos
        out_keywords = ["receta de cocina", "menú semanal", "dieta keto", "receta vegetal", "terapia psicología", "depresión clínica"]

        has_coach_kw = any(kw in q_lower for kw in coach_keywords)
        has_out_kw = any(kw in q_lower for kw in out_keywords)

        if has_out_kw and not has_coach_kw:
            return False
        return True

    def process_specialized_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Procesa una solicitud especializada validando la frontera de dominio.
        """
        # Cargar perfil de usuario para extraer lesiones y nivel
        profile = database.get_user_profile(user_id)
        name = profile.get("personal_info", {}).get("name", "Atleta")
        health_conds = profile.get("health_conditions", [])

        # Verificar frontera de dominio
        if not self.is_query_in_domain(message):
            logger.info(f"Wellness Coach Specialist: Consulta de usuario '{user_id}' está fuera de dominio directo.")
            redirect_msg = (
                f"Hola {name}, como especialista en Biomecánica y Entrenamiento Adaptativo de Wellness Lift, "
                f"mi enfoque principal son los ejercicios, técnicas y adaptaciones de seguridad. "
                f"Para recomendaciones detalladas de cocina o dieta, he notificado al Nutrition Agent. "
                f"En cuanto a tu entrenamiento, recuerda mantener buena postura y técnica."
            )
            self.memory.add_message(user_id, "user", message)
            self.memory.add_message(user_id, "assistant", redirect_msg)
            return {
                "user_id": user_id,
                "agent_name": "WellnessCoachAgent2.0",
                "in_domain": False,
                "status": "out_of_domain_redirect",
                "response": redirect_msg,
            }

        # Registrar mensaje de entrada en la memoria conversacional
        self.memory.add_message(user_id, "user", message)
        extracted_facts = self.memory.get_extracted_facts(user_id)

        history_text = self.memory.get_formatted_history(user_id)
        facts_text = "\n".join(extracted_facts) if extracted_facts else "Sin hechos adicionales extraídos."

        prompt = f"""
        Eres Wellness Coach Agent 2.0, el agente especializado del Equipo 6 en Biomecánica y Entrenamiento Adaptativo.
        Hablas con {name}.
        
        HISTORIAL DE CONVERSACIÓN (MEMORIA A CORTO PLAZO):
        {history_text}
        
        HECHOS Y OBSERVACIONES EXTRAÍDAS (MEMORIA A LARGO PLAZO):
        {facts_text}
        
        MENSAJE ACTUAL DEL USUARIO:
        "{message}"
        
        Responde de manera natural, motivadora y basándote en ciencia del deporte.
        Si te piden alternativas de ejercicios, mantén el mismo grupo muscular y respeta las lesiones.
        Sé conciso. No utilices emojis.
        """

        completion = self.llm.generate_completion(prompt, is_json=False)
        if completion:
            response_text = completion.strip()
        else:
            response_text = self.reasoning.generate_local_chat_response(user_id, message, extracted_facts=extracted_facts)

        self.memory.add_message(user_id, "assistant", response_text)

        return {
            "user_id": user_id,
            "agent_name": "WellnessCoachAgent2.0",
            "in_domain": True,
            "status": "success",
            "health_conditions": health_conds,
            "response": response_text,
        }

    def generate_adaptive_routine(self, user_id: str) -> Dict[str, Any]:
        """Genera una rutina semanal adaptada a las lesiones y perfil del atleta."""
        extracted_facts = self.memory.get_extracted_facts(user_id)
        prompt = self.reasoning.build_routine_prompt(user_id, extracted_facts=extracted_facts)
        completion = self.llm.generate_completion(prompt, is_json=True)

        if completion:
            try:
                text = completion.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                return json.loads(text.strip())
            except Exception as e:
                logger.warning(f"Error parseando JSON de rutina en coach_specialist: {e}")

        return self.reasoning.generate_local_routine(user_id, extracted_facts=extracted_facts)

    def process_interagent_message(self, msg: Any) -> Any:
        """
        Procesa una solicitud formal InterAgentMessage y retorna un InterAgentResponse.
        """
        import time
        from app.wellness_agent.communication import InterAgentResponse
        start_time = time.time()

        message_text = msg.context_payload.get("original_message") or msg.context_payload.get("message", "")
        user_id = msg.user_id

        res = self.process_specialized_request(user_id, message_text)

        status = res.get("status", "success")
        return InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="WellnessCoachAgent2.0",
            status=status,
            content=res.get("response", ""),
            metadata={
                "domain": "Biomechanics & Training",
                "in_domain": res.get("in_domain", True),
                "fitness_profile": res.get("fitness_profile", {}),
                "health_conditions": res.get("health_conditions", [])
            },
            execution_time_ms=(time.time() - start_time) * 1000
        )


# Instancia singleton del Agente Especializado
_specialist_instance = WellnessCoachSpecialist()
