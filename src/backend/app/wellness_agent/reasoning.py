"""
Módulo de Razonamiento y Construcción de Prompts (ReasoningEngine).
Orquesta la integración con RAG, la memoria de datos extraídos y construye mensajes del sistema.
"""

import json
import logging
import random
from typing import Dict, List, Any, Optional

from app import database
from app.wellness_agent.catalog import EXERCISE_CATALOG, SPLIT_TEMPLATES, get_set_rep_scheme
from app.wellness_agent.tools import AgentToolRegistry

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    Motor de Razonamiento RAG-Augmented para la generación de rutinas y respuesta a consultas.
    """

    def __init__(self, tool_registry: Optional[AgentToolRegistry] = None):
        self.tools = tool_registry or AgentToolRegistry()

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

    def generate_local_chat_response(self, user_id: str, message: str, extracted_facts: Optional[List[str]] = None) -> str:
        """Responde la consulta del usuario analizando perfil, reglas, intenciones y memoria de hechos."""
        msg = message.lower().strip()
        profile = database.get_user_profile(user_id)
        fitness = profile.get("fitness_profile", {})
        personal = profile.get("personal_info", {})
        metrics = profile.get("physical_metrics", {})

        name = personal.get("name", "Atleta")
        weight = metrics.get("weight", 70)
        level = fitness.get("level", "basico")
        goal = fitness.get("goal", "hipertrofia")
        days = fitness.get("training_days", [])
        sessions = database.get_workout_sessions(user_id)

        # 1. Alternativas de Ejercicio
        if any(k in msg for k in ["alternativa", "reemplaz", "cambiar", "ocupad", "sustitui"]):
            for group in EXERCISE_CATALOG.keys():
                if group.lower() in msg or (group == "Pecho" and "banca" in msg) or (group == "Piernas" and "sentadilla" in msg):
                    alt_data = self.tools.get_exercise_alternative(group)
                    if alt_data.get("status") == "success":
                        return (
                            f"Sugerencia Local: Ya que la máquina puede estar ocupada, te sugiero cambiar por {alt_data['name']}. "
                            f"Trabaja el patrón muscular de {group}."
                        )
            return "Sugerencia Local: No logré identificar el ejercicio. Intenta con una variante con mancuernas."

        # 2. Progresión de Carga
        if any(k in msg for k in ["peso", "progresar", "subir", "carga", "progresión"]):
            if sessions:
                last = sessions[0]
                return f"En tu última sesión levantaste un volumen total de {last.get('total_volume', 0)} kg. Intenta aumentarle 1.25kg o 2.5kg a tu primer ejercicio."
            base_weight = round(weight * 0.4) if goal == "hipertrofia" else round(weight * 0.5)
            return (
                f"{name}, recomendaciones iniciales de carga:\n"
                f"- Multiarticulares (sentadilla, press de banca): comenza con {base_weight} kg\n"
                f"- Aislamiento (curl, extensiones): comenza con {round(base_weight * 0.4)} kg\n"
                f"Sube 2.5 kg en multiarticulares y 1.25 kg en aislamiento semanalmente."
            )

        # 3. Dolor o Lesión
        if any(k in msg for k in ["duele", "dolor", "lesion", "lesión", "molest"]):
            return (
                "Advertencia de Seguridad:\n"
                f"{name}, nunca entrenes sobre dolor agudo o articular.\n"
                "1. Detén el ejercicio\n"
                "2. Aplica hielo 15 min\n"
                "3. Consulta a un fisioterapeuta si persiste 48 horas."
            )

        # 4. Nutrición
        if any(k in msg for k in ["macro", "calor", "nutri", "proteín", "protein", "dieta", "comer"]):
            macros_data = self.tools.calculate_nutrition_macros(user_id)
            if macros_data["tdee"]:
                return (
                    f"Plan Nutricional para {name}:\n"
                    f"TDEE estimado: {macros_data['tdee']} kcal/día\n"
                    f"- Proteínas: {macros_data['protein']}g\n"
                    f"- Carbohidratos: {macros_data['carbs']}g\n"
                    f"- Grasas: {macros_data['fats']}g"
                )
            return "Para calcular tus macronutrientes, completa tu perfil en la sección de Perfil."

        # 5. Información sobre Rutina
        if any(k in msg for k in ["rutina", "plan", "programa", "día", "dias", "semana"]):
            days_str = ", ".join(days) if days else "no configurados"
            sets, reps = get_set_rep_scheme(level, goal)
            return (
                f"Tu Plan de Entrenamiento Actual, {name}:\n"
                f"- Objetivo: {goal}\n"
                f"- Nivel: {level}\n"
                f"- Días: {days_str} ({len(days)} días/semana)\n"
                f"- Esquema: {sets} series x {reps} repeticiones"
            )

        # 6. Saludo / Contexto Recordado
        facts_summary = ""
        if extracted_facts:
            facts_summary = f"\n\nTengo registradas estas observaciones de conversaciones anteriores:\n- " + "\n- ".join(extracted_facts)

        return (
            f"Hola {name}, soy tu Wellness Coach inteligente.\n"
            f"Puedo ayudarte con alternativas de ejercicios, progresión de cargas, nutrición y alertas de seguridad.{facts_summary}\n\n"
            f"¿En qué te puedo ayudar hoy?"
        )
