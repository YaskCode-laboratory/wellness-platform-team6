"""
Módulo de Razonamiento y Construcción de Prompts (ReasoningEngine).
Orquesta la integración con RAG, la memoria de datos extraídos, la detección de intenciones e invocación de herramientas (Tool Calling).
"""

import json
import logging
import random
from typing import Dict, List, Any, Optional, Tuple

from app import database
from app.wellness_agent.catalog import EXERCISE_CATALOG, SPLIT_TEMPLATES, get_set_rep_scheme
from app.wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Motor de Razonamiento RAG-Augmented y Orquestador de Tool Calling.
    """

    def __init__(self, tool_registry: Optional[AgentToolRegistry] = None):
        self.tools = tool_registry or AgentToolRegistry()

    def detect_and_execute_tools(self, user_id: str, message: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Analiza si el mensaje del usuario requiere la invocación de herramientas.
        Retorna (nombre_herramienta, resultado_herramienta) o (None, None) si no se requieren herramientas.
        """
        msg_lower = message.lower().strip()

        # 1. Detección de Alternativas de Ejercicio
        if any(k in msg_lower for k in ["alternativa", "reemplaz", "cambiar", "ocupad", "sustitui"]):
            target_group = None
            group_keywords = {
                "Pecho": ["pecho", "banca", "press plano"],
                "Espalda": ["espalda", "jalón", "polea alta", "dorsal", "remo"],
                "Piernas": ["pierna", "sentadilla", "squat", "prensa"],
                "Hombros": ["hombro", "deltoides", "press militar"],
                "Bíceps": ["bícep", "bicep", "curl"],
                "Tríceps": ["trícep", "tricep", "extensión"],
            }
            for group, keywords in group_keywords.items():
                if any(kw in msg_lower for kw in keywords):
                    target_group = group
                    break
            target_group = target_group or "Pecho"
            result = self.tools.execute_tool("get_exercise_alternative", muscle_group=target_group)
            return "get_exercise_alternative", result

        # 2. Detección de Nutrición / Macros
        if any(k in msg_lower for k in ["macro", "calor", "nutri", "proteín", "protein", "tdee", "dieta"]):
            result = self.tools.execute_tool("calculate_nutrition_macros", user_id=user_id)
            return "calculate_nutrition_macros", result

        # 3. Detección de Evaluación de Riesgo de Lesión / Dolor
        if any(k in msg_lower for k in ["duele", "dolor", "lesion", "lesión", "molest", "riesgo"]):
            exercise_eval = "Sentadilla con Barra" if "sentadilla" in msg_lower else "Ejercicio General"
            result = self.tools.execute_tool("assess_injury_risk", user_id=user_id, exercise_name=exercise_eval)
            return "assess_injury_risk", result

        # 4. Detección de Consulta Científica / RAG
        if any(k in msg_lower for k in ["ciencia", "estudio", "evidencia", "mecanismo", "fisioterapia", "periodización"]):
            result = self.tools.execute_tool("retrieve_rag_knowledge", query_text=message, top_k=2)
            return "retrieve_rag_knowledge", result

        return None, None

    def build_routine_prompt(self, user_id: str, extracted_facts: Optional[List[str]] = None) -> str:
        """Construye el prompt estructurado para la generación de rutinas enriquecido con hechos conversacionales."""
        profile = database.get_user_profile(user_id)
        fitness = profile.get("fitness_profile", {})
        personal = profile.get("personal_info", {})
        metrics = profile.get("physical_metrics", {})

        training_days = fitness.get("training_days", ["Lunes", "Miércoles", "Viernes"])
        level = fitness.get("level", "basico")
        goal = fitness.get("goal", "hipertrofia")
        age = personal.get("age", 25)
        weight = metrics.get("weight", 70)
        health_conditions = fitness.get("health_conditions", [])
        limitations = fitness.get("limitations", "Ninguna")

        facts_text = "\n".join(extracted_facts) if extracted_facts else "Sin hechos adicionales extraídos del chat."

        # RAG Context Augmentation
        rag_context_blocks = self.tools.retrieve_rag_knowledge(
            f"periodizacion {goal} adaptaciones lesiones {', '.join(health_conditions)}", top_k=2
        )
        rag_text = "\n".join([item["text"] for item in rag_context_blocks]) if rag_context_blocks else "Sin contexto RAG"

        return f"""
        Eres un entrenador personal de élite y especialista en fisioterapia biomecánica.
        Genera una rutina de entrenamiento ESTRICTA y EXCLUSIVA para los siguientes días: {', '.join(training_days)}.
        NO agregues ningún otro día. Genera exactamente {len(training_days)} días.
        
        Perfil del atleta:
        - Objetivo: {goal} | Nivel: {level}
        - Edad: {age} años | Peso: {weight} kg
        - CONDICIONES DE SALUD O LESIONES REGISTRADAS: {', '.join(health_conditions) if health_conditions else 'Ninguna'}
        - LIMITACIONES FÍSICAS: {limitations}
        - HECHOS EXTRAÍDOS DE MEMORIA CONVERSACIONAL:
        {facts_text}
        
        CONTEXTO DE CONOCIMIENTO CIENTÍFICO RAG:
        {rag_text}
        
        REGLAS DE SEGURIDAD BIOMECÁNICA E IMPRESCINDIBLES:
        1. Si padece Hernia Discal o molestia lumbar, NO incluyas Sentadilla con Barra libre ni Peso Muerto pesado. Reemplaza por Prensa de Pierna con apoyo lumbar o Sentadilla Goblet ligera.
        2. Si padece Lesión de Rodilla, evita flexiones profundas con alto impacto.
        3. Diseña ejercicios biomecánicamente seguros y efectivos.
        
        Responde ÚNICAMENTE con un JSON válido usando esta estructura exacta (SIN MARKDOWN, SIN COMENTARIOS, SOLO EL JSON PURO):
        {{
          "focus": "Descripción breve del enfoque (ej. Hipertrofia para intermedio - {len(training_days)} días (Protección Lumbar))",
          "weekly_schedule": [
            {{
              "day": "Nombre del Día (ej. Lunes (Torso Protegido))",
              "exercises": [
                {{ "name": "Nombre del Ejercicio", "sets": 3, "reps": "8-12" }}
              ]
            }}
          ]
        }}
        """

    def generate_local_routine(self, user_id: str, extracted_facts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Genera una rutina semanal basada en el motor determinista local y memoria de hechos."""
        profile = database.get_user_profile(user_id)
        fitness = profile.get("fitness_profile", {})
        personal = profile.get("personal_info", {})

        training_days = fitness.get("training_days", ["Lunes", "Miércoles", "Viernes"])
        level = fitness.get("level", "basico")
        goal = fitness.get("goal", "hipertrofia")
        age = personal.get("age", 25)
        health_conditions = [h.lower() for h in fitness.get("health_conditions", [])]
        
        if extracted_facts:
            for fact in extracted_facts:
                if "lumbar" in fact.lower() or "hernia" in fact.lower():
                    health_conditions.append("hernia discal")
                if "rodilla" in fact.lower():
                    health_conditions.append("lesión de rodilla")

        has_lumbar_issue = any("hernia" in h or "lumbar" in h for h in health_conditions)

        num_days = len(training_days)
        sets, reps = get_set_rep_scheme(level, goal)

        if age > 50:
            sets = max(2, sets - 1)
        elif age > 40:
            reps = reps.replace("8-10", "10-12").replace("3-6", "5-8")

        template_key = min(max(num_days, 1), 6)
        split = SPLIT_TEMPLATES[template_key]

        while len(split) < num_days:
            split = split + SPLIT_TEMPLATES[template_key]
        split = split[:num_days]

        schedule = []
        used_exercises_by_group = {}

        for idx, day_name in enumerate(training_days):
            template = split[idx]
            day_label = f"{day_name} ({template['label']})"
            exercises = []

            for group_name in template["groups"]:
                catalog = list(EXERCISE_CATALOG.get(group_name, []))
                if not catalog:
                    continue

                if has_lumbar_issue:
                    catalog = [ex for ex in catalog if "Sentadilla con Barra" not in ex["name"]]

                random.shuffle(catalog)
                used_idx = used_exercises_by_group.get(group_name, 0)
                exercise = catalog[used_idx % len(catalog)]
                used_exercises_by_group[group_name] = used_idx + 1

                exercises.append({
                    "exercise_id": exercise["exercise_id"],
                    "name": exercise["name"],
                    "sets": sets,
                    "reps": reps,
                })

            schedule.append({
                "day": day_label,
                "exercises": exercises,
            })

        goal_labels = {"hipertrofia": "Hipertrofia", "fuerza": "Fuerza Máxima", "definicion": "Definición Corporal"}
        level_labels = {"basico": "Principiante", "intermedio": "Intermedio", "avanzado": "Avanzado"}
        health_note = " (Adaptada a Salud/Memoria)" if health_conditions else ""
        focus = f"{goal_labels.get(goal, goal)} — Nivel {level_labels.get(level, level)} — {num_days} días/semana{health_note}"

        return {"focus": focus, "weekly_schedule": schedule}

    def generate_local_chat_response(
        self, user_id: str, message: str, extracted_facts: Optional[List[str]] = None
    ) -> str:
        """Responde la consulta del usuario invocando herramientas registradas o respondiendo de forma determinista."""
        msg = message.lower().strip()
        profile = database.get_user_profile(user_id)
        personal = profile.get("personal_info", {})

        name = personal.get("name", "Atleta")

        # 1. Detección e Invocación de Herramientas
        tool_name, tool_result = self.detect_and_execute_tools(user_id, message)

        if tool_name and tool_result:
            if tool_name == "get_exercise_alternative" and tool_result.get("status") == "success":
                return (
                    f"Sugerencia de Herramienta [{tool_name}]: Ya que la máquina de {tool_result['muscle_group']} puede estar ocupada, "
                    f"te sugiero cambiar por {tool_result['name']}."
                )
            elif tool_name == "calculate_nutrition_macros" and tool_result.get("status") == "success":
                return (
                    f"Plan Nutricional Calculado por Herramienta [{tool_name}] para {name}:\n"
                    f"- TDEE Estimado: {tool_result['tdee']} kcal/día\n"
                    f"- Proteínas: {tool_result['protein']}g\n"
                    f"- Carbohidratos: {tool_result['carbs']}g\n"
                    f"- Grasas: {tool_result['fats']}g"
                )
            elif tool_name == "assess_injury_risk" and tool_result.get("status") == "success":
                return (
                    f"Evaluación de Riesgo [{tool_name}]: Nivel {tool_result['risk_level']}.\n"
                    f"- Advertencia: {tool_result['warning']}\n"
                    f"- Recomendación Segura: {tool_result['safe_recommendation']}"
                )
            elif tool_name == "retrieve_rag_knowledge" and isinstance(tool_result, list):
                snippets = "\n\n".join([c.get("text", "") for c in tool_result]) if tool_result else "Sin evidencia recuperada."
                return f"Consulta de Base de Conocimiento RAG [{tool_name}]:\n\n{snippets}"

        # 2. Respuestas Generales (Sin Herramientas)
        facts_summary = ""
        if extracted_facts:
            facts_summary = f"\n\nObservaciones registradas de conversaciones anteriores:\n- " + "\n- ".join(extracted_facts)

        return (
            f"Hola {name}, soy tu Wellness Coach inteligente 2.0.\n"
            f"Puedo ayudarte con alternativas de ejercicios, progresión de cargas, nutrición, alertas de seguridad y consulta RAG.{facts_summary}\n\n"
            f"¿En qué te puedo ayudar hoy?"
        )
