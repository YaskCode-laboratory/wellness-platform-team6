"""
Módulo Wellness Coach Agent 2.0 — Patrón ReAct y Flujo de Razonamiento (Issue #16 & Issue #18).
Implementa el ciclo de razonamiento Thought -> Action -> Observation -> Final Answer integrado con AgentToolRegistry
y protección contra bucles infinitos.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.wellness_agent.tools import AgentToolRegistry
except ModuleNotFoundError:
    try:
        from wellness_agent.tools import AgentToolRegistry
    except ModuleNotFoundError:
        from .wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)


class ReActAgent:
    """
    Agente ReAct (Reasoning and Acting) que coordina pensamientos, selección dinámica de herramientas
    (AgentToolRegistry) y síntesis de respuestas finales con prevención de bucles infinitos.
    """

    def __init__(self, tool_registry: Optional[AgentToolRegistry] = None):
        self.tool_registry = tool_registry or AgentToolRegistry()

    def run_react_loop(
        self,
        user_prompt: str,
        athlete_id: str = "user123",
        max_iterations: int = 5,
        force_repeat_action: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta el bucle ReAct adaptando las herramientas a la solicitud del usuario
        y detectando activamente ciclos duplicados de herramientas.
        """
        steps: List[Dict[str, Any]] = []
        executed_tool_calls = set()
        loop_detected = False
        final_answer = ""
        msg_lower = user_prompt.lower().strip()

        for iteration in range(1, max_iterations + 1):
            current_thought = ""
            action_name = ""
            action_input: Any = None

            # Si se fuerza la repetición para prueba explícita de bucle
            if force_repeat_action:
                action_name = force_repeat_action
                action_input = {"muscle_group": "Pecho"} if action_name == "get_exercise_alternative" else {"user_id": athlete_id}
                current_thought = f"PENSAMIENTO [{iteration}]: Ejecutando herramienta de prueba '{action_name}'."
            else:
                # Detección dinámica basada en la intencionalidad del mensaje y observaciones previas
                if iteration == 1:
                    if any(k in msg_lower for k in ["hola", "buenos días", "gracias", "saludos", "buenas"]):
                        current_thought = f"PENSAMIENTO [{iteration}]: El usuario envía un saludo o agradecimiento directo. Generando respuesta sin herramientas."
                        action_name = "FINAL_ANSWER"
                        action_input = None
                    elif any(k in msg_lower for k in ["macro", "calor", "nutri", "dieta", "comer"]):
                        current_thought = f"PENSAMIENTO [{iteration}]: El usuario consulta sobre nutrición y macronutrientes. Usaré calculate_nutrition_macros."
                        action_name = "calculate_nutrition_macros"
                        action_input = {"user_id": athlete_id}
                    elif any(k in msg_lower for k in ["alternativa", "reemplaz", "cambiar", "ocupad", "sustitui"]):
                        muscle = "Pecho" if "pecho" in msg_lower else ("Espalda" if "espalda" in msg_lower else "Pecho")
                        current_thought = f"PENSAMIENTO [{iteration}]: El usuario busca sustitutos de ejercicio. Usaré get_exercise_alternative para {muscle}."
                        action_name = "get_exercise_alternative"
                        action_input = {"muscle_group": muscle}
                    elif any(k in msg_lower for k in ["periodización", "periodizacion", "hipertrofia", "ciencia", "evidencia"]):
                        current_thought = f"PENSAMIENTO [{iteration}]: El usuario requiere evidencia científica RAG. Consultaré la base de conocimiento con retrieve_rag_knowledge."
                        action_name = "retrieve_rag_knowledge"
                        action_input = {"query_text": user_prompt}
                    else:
                        current_thought = f"PENSAMIENTO [{iteration}]: El usuario reporta dolor o consulta de seguridad. Usaré assess_injury_risk para evaluar el perfil del atleta."
                        action_name = "assess_injury_risk"
                        action_input = {"user_id": athlete_id, "exercise_name": "Sentadilla con Barra"}

                elif iteration == 2:
                    last_action = steps[-1]["action"] if steps else ""
                    if last_action == "assess_injury_risk":
                        target_muscle = "Piernas" if any(k in msg_lower for k in ["sentadilla", "pierna", "piernas", "cuádriceps", "cuadriceps", "rodilla"]) else ("Espalda" if "espalda" in msg_lower else "Pecho")
                        current_thought = f"PENSAMIENTO [{iteration}]: Tras evaluar el riesgo biomecánico, buscaré alternativas seguras para {target_muscle} en el catálogo."
                        action_name = "get_exercise_alternative"
                        action_input = {"muscle_group": target_muscle}
                    elif last_action == "get_exercise_alternative":
                        current_thought = f"PENSAMIENTO [{iteration}]: Consultaré la evidencia RAG para respaldar la sustitución de ejercicios."
                        action_name = "retrieve_rag_knowledge"
                        action_input = {"query_text": f"sustitución ejercicio {user_prompt}"}
                    else:
                        current_thought = f"PENSAMIENTO [{iteration}]: Dispongo de la información necesaria para responder al usuario."
                        action_name = "FINAL_ANSWER"
                        action_input = None

                else:
                    current_thought = f"PENSAMIENTO [{iteration}]: Secuencia de razonamiento ReAct completada. Sintetizando respuesta final."
                    action_name = "FINAL_ANSWER"
                    action_input = None

            # Verificación de bucle repetitivo (anti-loop protection)
            tool_signature = f"{action_name}:{json.dumps(action_input, sort_keys=True)}"
            if tool_signature in executed_tool_calls and action_name != "FINAL_ANSWER":
                loop_detected = True
                current_thought += " (Detección de ciclo duplicado: la herramienta ya fue ejecutada previamente. Forzando respuesta final para prevenir bucle infinito)."
                action_name = "FINAL_ANSWER"
                action_input = None

            executed_tool_calls.add(tool_signature)

            if action_name == "FINAL_ANSWER":
                final_answer = self._synthesize_final_answer(user_prompt, steps)
                steps.append({
                    "iteration": iteration,
                    "thought": current_thought,
                    "action": "FINAL_ANSWER",
                    "observation": "Flujo ReAct finalizado."
                })
                break
            else:
                observation = self.tool_registry.execute_tool(action_name, **(action_input if isinstance(action_input, dict) else {}))
                steps.append({
                    "iteration": iteration,
                    "thought": current_thought,
                    "action": action_name,
                    "action_input": action_input,
                    "observation": observation
                })

        return {
            "user_prompt": user_prompt,
            "total_iterations": len(steps),
            "loop_detected": loop_detected,
            "steps": steps,
            "final_answer": final_answer
        }

    def _synthesize_final_answer(self, prompt: str, steps: List[Dict[str, Any]]) -> str:
        observations_summary = []
        for s in steps:
            if s["action"] != "FINAL_ANSWER":
                obs_json = json.dumps(s["observation"], ensure_ascii=False)
                observations_summary.append(f"- Herramienta {s['action']}: {obs_json}")

        obs_str = "\n".join(observations_summary) if observations_summary else "Sin herramientas ejecutadas."
        return (
            f"**Síntesis ReAct ReActAgent**\n"
            f"Consulta: '{prompt}'\n\n"
            f"Evidencia de Herramientas Ejecutadas:\n{obs_str}\n\n"
            f"Recomendación: Plan ajustado respetando los datos obtenidos."
        )
