"""
Wellness Coach Specialist — Agente Especializado del Equipo 6.
Dominio: Biomecánica, Selección de Ejercicios, Adaptación Médica por Lesiones y Generación de Rutinas.
Integra Motor RAG, Memoria Conversacional de Doble Nivel, Tool Calling y Delimitación de Dominio.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from app import database
from app.wellness_agent.memory import ConversationMemoryManager
from app.wellness_agent.providers import LLMProviderManager
from app.wellness_agent.reasoning import ReasoningEngine
from app.wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)

# Nombre del archivo de System Prompt oficial
PROMPT_FILENAME = "system_prompt_wellness_coach_2.0.txt"


def load_system_prompt() -> str:
    """Carga el System Prompt especializado desde el archivo oficial prompts/system_prompt_wellness_coach_2.0.txt."""
    current_file = Path(__file__).resolve()
    # current_file: src/backend/app/wellness_agent/coach_specialist.py -> parents[4] es el repo_root
    repo_root = current_file.parents[4]
    official_path = repo_root / "prompts" / PROMPT_FILENAME

    possible_paths = [
        official_path,
        current_file.parent.parent.parent.parent / "prompts" / PROMPT_FILENAME,
        Path.cwd() / "prompts" / PROMPT_FILENAME,
        Path.cwd().parent / "prompts" / PROMPT_FILENAME,
    ]

    for path in possible_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        logger.info(f"System prompt cargado exitosamente desde {path}")
                        return content
            except Exception as e:
                logger.warning(f"Error al leer system prompt desde {path}: {e}")

    logger.error(f"No se pudo encontrar el archivo prompts/{PROMPT_FILENAME} en las rutas conocidas.")
    return (
        "Eres 'Wellness Coach AI 2.0', un entrenador personal deportivo de élite y especialista en fisioterapia biomecánica.\n"
        "Actúa de manera profesional, empática, concisa y basada en evidencia científica deportiva.\n"
        "Prioriza en todo momento la salud articular y la prevención de lesiones del atleta.\n"
        "Sé conciso y no utilices ningún tipo de emoji."
    )


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
        self.system_prompt = load_system_prompt()

    def is_query_in_domain(self, query: str) -> bool:
        """
        Verifica si la consulta pertenece explícitamente al dominio del agente especializado (Biomecánica & Entrenamiento).
        Rechaza consultas fuera de dominio (nutrición pura, recetas, finanzas, informática, medicina general, etc.).
        """
        if not query or not query.strip():
            return False

        q_lower = query.lower().strip()

        # Términos que identifican explícitamente el dominio del coach especializado
        coach_keywords = [
            "rutina", "ejercicio", "entrenamiento", "sentadilla", "press", "banca", "peso muerto",
            "lesión", "lesion", "dolor", "espalda", "hernia", "rodilla", "hombro", "reemplaz", "alternativa",
            "sustituto", "músculo", "musculo", "pecho", "espalda", "pierna", "piernas", "biceps", "triceps",
            "hipertrofia", "fuerza", "serie", "repetición", "repeticion", "rpe", "rir", "descanso",
            "calentamiento", "postura", "técnica", "tecnica", "cuádriceps", "cuadriceps", "femorales",
            "glúteos", "gluteos", "pantorrilla", "cardio", "mancuerna", "mancuernas", "barra", "polea",
            "gimnasio", "gym", "fisioterapia", "biomecánica", "biomecanica", "movilidad", "calistenia"
        ]

        # Términos explícitamente ajenos al dominio del entrenador
        out_keywords = [
            "receta", "menú", "menu", "dieta", "keto", "calorías", "calorias", "macro", "proteína para comer",
            "psicología", "psicologia", "depresión", "depresion", "ansiedad", "receta vegetal", "cocina",
            "programación", "programacion", "python", "javascript", "código", "codigo", "capital", "precio",
            "dólar", "dolar", "política", "politica", "clima", "tiempo libre", "película", "pelicula"
        ]

        has_coach_kw = any(kw in q_lower for kw in coach_keywords)
        has_out_kw = any(kw in q_lower for kw in out_keywords)

        if has_coach_kw:
            pure_non_fitness = ["receta de cocina", "código en python", "capital de", "precio del dólar", "cómo programar"]
            if any(p in q_lower for p in pure_non_fitness):
                return False
            return True

        if has_out_kw:
            return False

        return False

    def process_specialized_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Procesa una solicitud especializada validando la frontera de dominio,
        extrayendo la estructura real del perfil del usuario (fitness_profile y health_conditions),
        consultando la base RAG y herramientas de evaluación de riesgo.
        """
        # Cargar perfil de usuario usando la estructura real (fitness_profile)
        profile = database.get_user_profile(user_id)
        personal_info = profile.get("personal_info", {})
        name = personal_info.get("name", "Atleta")

        fitness_profile = profile.get("fitness_profile", {})
        health_conds = fitness_profile.get("health_conditions", [])
        if not health_conds and "health_conditions" in profile:
            health_conds = profile.get("health_conditions", [])

        goal = fitness_profile.get("goal", "entrenamiento")
        level = fitness_profile.get("level", "intermedio")
        limitations = fitness_profile.get("limitations", "Sin limitaciones registradas")

        # Verificar frontera de dominio
        if not self.is_query_in_domain(message):
            logger.info(f"Wellness Coach Specialist: Consulta de usuario '{user_id}' está fuera de dominio directo.")
            out_of_domain_msg = (
                f"Hola {name}, la consulta sobre '{message}' está fuera del dominio de Biomecánica y Entrenamiento Adaptativo de Wellness Coach 2.0. "
                f"Esta solicitud requiere la intervención de un agente especializado en dicho dominio."
            )
            self.memory.add_message(user_id, "user", message)
            self.memory.add_message(user_id, "assistant", out_of_domain_msg)
            return {
                "user_id": user_id,
                "agent_name": "WellnessCoachAgent2.0",
                "in_domain": False,
                "status": "out_of_domain",
                "response": out_of_domain_msg,
            }

        # Ejecución e integración RAG & Tool Calling
        rag_context = ""
        try:
            rag_chunks = self.tools.retrieve_rag_knowledge(message, top_k=2)
            if rag_chunks:
                rag_context = "\n".join(
                    [f"- Fragmento [{c.get('chunk_id', 'RAG')}]: {c.get('content', '')}" for c in rag_chunks]
                )
        except Exception as e:
            logger.warning(f"Coach Specialist: No se pudo consultar RAG context: {e}")

        injury_assessment = ""
        if health_conds or limitations != "Sin limitaciones registradas":
            try:
                risk = self.tools.assess_injury_risk(user_id, message)
                if risk and risk.get("risk_level") == "HIGH":
                    injury_assessment = f"ADVERTENCIA DE SEGURIDAD: {risk.get('warning')} Recomendación segura: {risk.get('safe_recommendation')}"
            except Exception as e:
                logger.warning(f"Error evaluando riesgo de lesión en coach_specialist: {e}")

        # Registrar mensaje de entrada en la memoria conversacional
        self.memory.add_message(user_id, "user", message)
        extracted_facts = self.memory.get_extracted_facts(user_id)

        history_text = self.memory.get_formatted_history(user_id)
        facts_text = "\n".join(extracted_facts) if extracted_facts else "Sin hechos adicionales extraídos."
        health_text = ", ".join(health_conds) if health_conds else "Sin condiciones médicas registradas."

        # Construcción del prompt usando el System Prompt oficial como Única Fuente de Verdad
        prompt = f"""
{self.system_prompt}

INFORMACIÓN Y PERFIL DEL ATLETA:
- Nombre: {name}
- Nivel de experiencia: {level}
- Objetivo principal: {goal}
- Condiciones de salud / Lesiones: {health_text}
- Limitaciones reportadas: {limitations}

CONTEXTO DE CONOCIMIENTO RAG RECUPERADO (BIOMECÁNICA Y SEGURIDAD):
{rag_context if rag_context else "No se recuperaron fragmentos RAG específicos para esta consulta."}

EVALUACIÓN DE RIESGO BIOMECÁNICO (HERRAMIENTAS):
{injury_assessment if injury_assessment else "Sin alertas de riesgo crítico detectadas."}

HISTORIAL DE CONVERSACIÓN (MEMORIA A CORTO PLAZO):
{history_text}

HECHOS Y OBSERVACIONES EXTRAÍDAS (MEMORIA A LARGO PLAZO):
{facts_text}

MENSAJE ACTUAL DEL USUARIO:
"{message}"

Responde de manera natural, motivadora y basándote en la evidencia RAG y el perfil del atleta.
Si te piden alternativas de ejercicios, mantén el mismo grupo muscular y respeta estrictamente las lesiones.
Sé conciso. No utilices ningún tipo de emoji.
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
            "fitness_profile": fitness_profile,
            "health_conditions": health_conds,
            "response": response_text,
        }

    def process_interagent_message(self, msg: Any) -> Any:
        """
        Procesa una solicitud formal InterAgentMessage y retorna un InterAgentResponse,
        preservando explícitamente el estado "out_of_domain" y "in_domain" para la propagación al Orchestrator.
        """
        import time
        from app.wellness_agent.communication import InterAgentResponse
        start_time = time.time()

        message_text = msg.context_payload.get("original_message") or msg.context_payload.get("message", "")
        user_id = msg.user_id

        res = self.process_specialized_request(user_id, message_text)

        status = res.get("status", "success")
        in_domain = res.get("in_domain", True)

        return InterAgentResponse(
            task_id=msg.task_id,
            trace_id=msg.trace_id,
            source_agent="WellnessCoachAgent2.0",
            status=status,
            content=res.get("response", ""),
            metadata={
                "domain": "Biomechanics & Training",
                "in_domain": in_domain,
                "fitness_profile": res.get("fitness_profile", {}),
                "health_conditions": res.get("health_conditions", [])
            },
            execution_time_ms=(time.time() - start_time) * 1000
        )

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


# Instancia singleton del Agente Especializado
_specialist_instance = WellnessCoachSpecialist()
