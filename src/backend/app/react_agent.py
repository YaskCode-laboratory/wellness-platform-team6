"""
Módulo Wellness Coach Agent 2.0 — Patrón ReAct y Flujo de Razonamiento (Issue #16 & Issue #17)
Implementa el ciclo de razonamiento Thought -> Action -> Observation -> Final Answer con prevención de bucles infinitos.
"""

import os
import sys
import json
from typing import Dict, Any, List, Tuple

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from app.rag_pipeline import RAGPipeline
except ModuleNotFoundError:
    from rag_pipeline import RAGPipeline

class ReActAgent:
    def __init__(self):
        self.rag_pipeline = RAGPipeline()
        self.tool_registry = {
            "get_athlete_technical_file": self._tool_get_athlete_technical_file,
            "search_medical_contraindications": self._tool_search_medical_contraindications,
            "query_rag_vector_store": self._tool_query_rag_vector_store,
            "calculate_progressive_overload": self._tool_calculate_progressive_overload
        }

    # --- REGISTRO DE HERRAMIENTAS (TOOLS) ---
    def _tool_get_athlete_technical_file(self, athlete_id: str) -> Dict[str, Any]:
        """Herramienta 1: Consulta la Ficha Técnica Deportiva y Médica del Atleta."""
        mock_database = {
            "user123": {
                "id": "user123",
                "name": "Juan Pérez",
                "health_conditions": "Hernia Discal L4-L5",
                "fitness_level": "Intermedio",
                "current_routine": "Sentadilla Libre 4x10, Prensa 3x12",
                "assigned_coach": "coach_carlos"
            },
            "user456": {
                "id": "user456",
                "name": "María Fernández",
                "health_conditions": "Lesión de Rodilla (Menisco)",
                "fitness_level": "Avanzado",
                "current_routine": "Sentadilla Hack 4x8, Zancadas 3x10",
                "assigned_coach": "coach_maria"
            }
        }
        return mock_database.get(athlete_id, {
            "id": athlete_id,
            "name": "Atleta Registrado",
            "health_conditions": "Ninguna",
            "fitness_level": "Intermedio",
            "current_routine": "Rutina General 3x10"
        })

    def _tool_search_medical_contraindications(self, condition: str) -> Dict[str, Any]:
        """Herramienta 2: Busca contraindicaciones biomecánicas según patología médica."""
        condition_lower = condition.lower()
        if "lumbar" in condition_lower or "hernia" in condition_lower:
            return {
                "condition": condition,
                "contraindicated_exercises": ["Sentadilla Libre con Barra", "Peso Muerto Convencional", "Press Militar de Pie"],
                "recommended_substitutes": ["Prensa Inclinada a 45°", "Peso Muerto Rumano asistido en Polea"],
                "rationale": "Eliminación de compresión axial sobre discos L4-L5."
            }
        elif "rodilla" in condition_lower or "menisco" in condition_lower:
            return {
                "condition": condition,
                "contraindicated_exercises": ["Sentadilla Hack Profunda", "Extensión de Rodilla en Carga Máxima"],
                "recommended_substitutes": ["Prensa de Cadera", "Peso Muerto Rumano en Cadena Posterior"],
                "rationale": "Minimización de cizallamiento femororrotuliano."
            }
        return {
            "condition": condition,
            "contraindicated_exercises": [],
            "recommended_substitutes": ["Ejercicio General Adaptado"],
            "rationale": "Sin contraindicaciones severas registradas."
        }

    def _tool_query_rag_vector_store(self, query: str) -> Dict[str, Any]:
        """Herramienta 3: Ejecuta una consulta vectorial sobre la Base de Conocimiento RAG."""
        results = self.rag_pipeline.retrieve_context(query, top_k=2)
        return {
            "query": query,
            "retrieved_chunks": results
        }

    def _tool_calculate_progressive_overload(self, sets: int, reps: int, weight_kg: float) -> Dict[str, Any]:
        """Herramienta 4: Calcula el Volumen Total y sugiere incremento de sobrecarga progresiva."""
        volume = sets * reps * weight_kg
        new_weight = round(weight_kg * 1.05, 1)  # Incremento seguro del +5%
        return {
            "current_volume_kg": volume,
            "suggested_next_weight_kg": new_weight,
            "progression_rule": "Incremento de carga del +5% manteniendo RPE 8."
        }

    # --- CICLO DE RAZONAMIENTO REACT ---
    def run_react_loop(self, user_prompt: str, athlete_id: str = None, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Ejecuta el bucle ReAct (Thought -> Action -> Observation -> Final Answer).
        Incluye protección anti-bucles repetidos.
        """
        steps = []
        executed_tool_calls = set()
        
        current_thought = ""
        final_answer = ""
        
        for iteration in range(1, max_iterations + 1):
            if iteration == 1:
                current_thought = f"PENSAMIENTO [{iteration}]: El usuario solicita: '{user_prompt}'. Necesito consultar el expediente técnico del atleta para revisar condiciones de salud y rutina actual."
                action_name = "get_athlete_technical_file"
                action_input = athlete_id if athlete_id else "user123"
            elif iteration == 2:
                last_obs = steps[-1]["observation"]
                health_cond = last_obs.get("health_conditions", "Ninguna")
                if health_cond != "Ninguna":
                    current_thought = f"PENSAMIENTO [{iteration}]: El atleta presenta '{health_cond}'. Debo consultar la herramienta de contraindicaciones médicas para identificar ejercicios prohibidos y sustitutos seguros."
                    action_name = "search_medical_contraindications"
                    action_input = health_cond
                else:
                    current_thought = f"PENSAMIENTO [{iteration}]: No se registran lesiones médicas. Consultaré la base RAG para optimizar la rutina de hipertrofia."
                    action_name = "query_rag_vector_store"
                    action_input = user_prompt
            elif iteration == 3:
                current_thought = f"PENSAMIENTO [{iteration}]: Con la información biomecánica obtenida, calcularé el ajuste de sobrecarga progresiva."
                action_name = "calculate_progressive_overload"
                action_input = {"sets": 4, "reps": 10, "weight_kg": 80.0}
            else:
                current_thought = f"PENSAMIENTO [{iteration}]: Dispongo de toda la evidencia necesaria (Ficha Técnica, Contraindicaciones Biomecánicas y Sobrecarga). Procederé a sintetizar la respuesta final."
                action_name = "FINAL_ANSWER"
                action_input = None

            tool_call_signature = f"{action_name}:{json.dumps(action_input)}"
            if tool_call_signature in executed_tool_calls and action_name != "FINAL_ANSWER":
                current_thought += " (Detección de ciclo duplicado: forzando respuesta final)."
                action_name = "FINAL_ANSWER"

            executed_tool_calls.add(tool_call_signature)

            if action_name == "FINAL_ANSWER":
                final_answer = self._synthesize_final_answer(user_prompt, steps)
                steps.append({
                    "iteration": iteration,
                    "thought": current_thought,
                    "action": "FINAL_ANSWER",
                    "observation": "Flujo de razonamiento ReAct completado con éxito."
                })
                break
            else:
                tool_fn = self.tool_registry.get(action_name)
                if isinstance(action_input, dict):
                    observation = tool_fn(**action_input)
                else:
                    observation = tool_fn(action_input)

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
            "steps": steps,
            "final_answer": final_answer
        }

    def _synthesize_final_answer(self, prompt: str, steps: List[Dict[str, Any]]) -> str:
        """Sintetiza la respuesta final basándose en las observaciones acumuladas."""
        athlete_info = {}
        contraindications = {}
        for s in steps:
            if s["action"] == "get_athlete_technical_file":
                athlete_info = s["observation"]
            elif s["action"] == "search_medical_contraindications":
                contraindications = s["observation"]

        name = athlete_info.get("name", "Atleta")
        cond = athlete_info.get("health_conditions", "Sin lesiones")
        contra_ex = contraindications.get("contraindicated_exercises", [])
        subs = contraindications.get("recommended_substitutes", [])

        if contra_ex:
            return (
                f"**Plan Adaptado para {name} (Condición: {cond})**\n\n"
                f"1. **Análisis Biomecánico**: Se detectó {cond}. Por seguridad articular, quedan **contraindicados**: {', '.join(contra_ex)}.\n"
                f"2. **Ejercicios Sustitutos Recomendados**: Reemplazar por {', '.join(subs)}.\n"
                f"3. **Sobrecarga Progresiva**: Aplicar incremento del 5% manteniendo RPE 8 en la prensa inclinada."
            )
        else:
            return f"Plan de entrenamiento optimizado para {name}: Rutina aprobada con sobrecarga progresiva estándar."
