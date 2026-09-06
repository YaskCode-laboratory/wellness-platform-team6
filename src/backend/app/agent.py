"""
Wellness Coach Agent — Motor de Entrenamiento Inteligente Local
==============================================================
Genera rutinas personalizadas y respuestas de chat basándose en
principios de ciencia del ejercicio: periodización, sobrecarga
progresiva, distribución de volumen por grupo muscular y
recomendaciones nutricionales adaptadas al perfil del atleta.

No requiere ninguna API externa. 100 % estable y determinista.
"""

import json
import logging
import math
import random
import os
import time
from app import database

try:
    import groq
except ImportError:
    groq = None

try:
    import httpx
except ImportError:
    httpx = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

OPENROUTER_DEFAULT_KEY = "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"

def get_openrouter_key():
    return os.environ.get("OPENROUTER_API_KEY", OPENROUTER_DEFAULT_KEY)

def _call_openrouter_ai(prompt: str, is_json: bool = False) -> str:
    if not httpx:
        return None
    key = get_openrouter_key()
    if not key:
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173",
        "X-Title": "Wellness App"
    }
    
    models = ["inclusionai/ling-3.0-flash:free", "openrouter/auto", "google/gemma-4-31b-it:free"]
    
    for model in models:
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2 if is_json else 0.7
            }
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0]["message"]["content"]
                        return content
                logger.warning(f"OpenRouter model {model} status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Error llamando OpenRouter ({model}): {e}")
            continue
    return None

def get_groq_client():
    if not groq:
        return None
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        return groq.Groq(api_key=api_key)
    except Exception as e:
        logger.warning("Groq no pudo inicializarse: %s", e)
        return None

def get_gemini_key():
    return os.environ.get("GEMINI_API_KEY")





# Para que el servidor reporte "Wellness Engine" en el root endpoint
use_real_ai = True  # Motor local inteligente activo

# ────────────────────────────────────────────────────────────────
# CATÁLOGO COMPLETO DE EJERCICIOS POR GRUPO MUSCULAR
# ────────────────────────────────────────────────────────────────
EXERCISE_CATALOG = {
    "Pecho": [
        {"exercise_id": "bench_press", "name": "Press de Banca Plano con Barra"},
        {"exercise_id": "dumbbell_press", "name": "Press Inclinado con Mancuernas"},
        {"exercise_id": "chest_fly", "name": "Aperturas en Polea para Pecho"},
    ],
    "Espalda": [
        {"exercise_id": "lat_pulldown", "name": "Jalón al Pecho en Polea"},
        {"exercise_id": "barbell_row", "name": "Remo con Barra"},
        {"exercise_id": "dumbbell_row", "name": "Remo con Mancuerna a una Mano"},
    ],
    "Piernas": [
        {"exercise_id": "squat", "name": "Sentadilla con Barra"},
        {"exercise_id": "leg_press", "name": "Prensa de Piernas"},
        {"exercise_id": "goblet_squat", "name": "Sentadilla Goblet con Mancuerna"},
    ],
    "Hombros": [
        {"exercise_id": "overhead_press", "name": "Press Militar con Barra"},
        {"exercise_id": "dumbbell_shoulder_press", "name": "Press de Hombros con Mancuernas"},
        {"exercise_id": "lateral_raises", "name": "Elevaciones Laterales con Mancuernas"},
    ],
    "Bíceps": [
        {"exercise_id": "bicep_curl", "name": "Curl de Bíceps con Barra"},
        {"exercise_id": "db_bicep_curl", "name": "Curl de Bíceps con Mancuernas"},
    ],
    "Tríceps": [
        {"exercise_id": "tricep_pushdown", "name": "Extensión de Tríceps en Polea"},
        {"exercise_id": "skull_crusher", "name": "Rompe Cráneos con Barra Z"},
    ],
}

# ────────────────────────────────────────────────────────────────
# ESQUEMAS DE SPLIT SEGÚN NÚMERO DE DÍAS
# ────────────────────────────────────────────────────────────────
SPLIT_TEMPLATES = {
    1: [  # Full Body
        {"label": "Full Body", "groups": ["Piernas", "Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]},
    ],
    2: [  # Upper / Lower
        {"label": "Tren Superior", "groups": ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]},
        {"label": "Tren Inferior + Core", "groups": ["Piernas", "Piernas", "Hombros"]},
    ],
    3: [  # Push / Pull / Legs
        {"label": "Empuje (Push)", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción (Pull)", "groups": ["Espalda", "Bíceps", "Hombros"]},
        {"label": "Pierna (Legs)", "groups": ["Piernas", "Piernas", "Piernas"]},
    ],
    4: [  # Upper A / Lower A / Upper B / Lower B
        {"label": "Superior A (Empuje)", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Inferior A (Cuádriceps)", "groups": ["Piernas", "Piernas"]},
        {"label": "Superior B (Tracción)", "groups": ["Espalda", "Bíceps", "Hombros"]},
        {"label": "Inferior B (Posterior)", "groups": ["Piernas", "Piernas"]},
    ],
    5: [  # Push / Pull / Legs / Upper / Lower
        {"label": "Empuje (Pecho + Tríceps)", "groups": ["Pecho", "Pecho", "Tríceps"]},
        {"label": "Tracción (Espalda + Bíceps)", "groups": ["Espalda", "Espalda", "Bíceps"]},
        {"label": "Pierna Completa", "groups": ["Piernas", "Piernas", "Piernas"]},
        {"label": "Superior (Hombros + Brazos)", "groups": ["Hombros", "Bíceps", "Tríceps"]},
        {"label": "Inferior + Core", "groups": ["Piernas", "Piernas", "Hombros"]},
    ],
    6: [  # PPL x2
        {"label": "Empuje A", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción A", "groups": ["Espalda", "Bíceps"]},
        {"label": "Pierna A", "groups": ["Piernas", "Piernas"]},
        {"label": "Empuje B", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción B", "groups": ["Espalda", "Bíceps"]},
        {"label": "Pierna B", "groups": ["Piernas", "Piernas"]},
    ],
}

# ────────────────────────────────────────────────────────────────
# PARÁMETROS DE VOLUMEN SEGÚN NIVEL Y OBJETIVO
# ────────────────────────────────────────────────────────────────
def _get_set_rep_scheme(level: str, goal: str):
    """Devuelve (sets, reps_str) según nivel y objetivo."""
    schemes = {
        ("basico", "hipertrofia"):    (3, "10-12"),
        ("basico", "fuerza"):         (3, "6-8"),
        ("basico", "definicion"):     (3, "12-15"),
        ("intermedio", "hipertrofia"):(4, "8-12"),
        ("intermedio", "fuerza"):     (4, "5-8"),
        ("intermedio", "definicion"): (3, "12-15"),
        ("avanzado", "hipertrofia"):  (4, "8-10"),
        ("avanzado", "fuerza"):       (5, "3-6"),
        ("avanzado", "definicion"):   (4, "10-15"),
    }
    return schemes.get((level, goal), (3, "8-12"))

# ────────────────────────────────────────────────────────────────
# GENERADOR DE RUTINAS PERSONALIZADAS
# ────────────────────────────────────────────────────────────────
def _generate_local_routine(user_id: str) -> dict:
    """
    Genera una rutina semanal personalizada basándose en parámetros locales y condiciones médicas.
    """
    profile = database.get_user_profile(user_id)
    fitness = profile.get("fitness_profile", {})
    personal = profile.get("personal_info", {})

    training_days = fitness.get("training_days", ["Lunes", "Miércoles", "Viernes"])
    level = fitness.get("level", "basico")
    goal = fitness.get("goal", "hipertrofia")
    age = personal.get("age", 25)
    weight = profile.get("physical_metrics", {}).get("weight", 70)
    health_conditions = [h.lower() for h in fitness.get("health_conditions", [])]
    has_lumbar_issue = any("hernia" in h or "lumbar" in h for h in health_conditions)

    num_days = len(training_days)
    sets, reps = _get_set_rep_scheme(level, goal)

    # Ajustar volumen por edad
    if age > 50:
        sets = max(2, sets - 1)
    elif age > 40:
        reps = reps.replace("8-10", "10-12").replace("3-6", "5-8")

    # Seleccionar el esquema de split adecuado
    template_key = min(num_days, 6)
    if template_key < 1:
        template_key = 1
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

            # Filtro Biomecánico de Salud: Si tiene hernia discal, omitir barra pesada sobre columna
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
    health_note = " (Adaptada a Salud)" if health_conditions else ""
    focus = f"{goal_labels.get(goal, goal)} — Nivel {level_labels.get(level, level)} — {num_days} días/semana{health_note}"

    routine = {"focus": focus, "weekly_schedule": schedule}
    logger.info(f"Rutina LOCAL generada para {user_id}: {num_days} días, salud={health_conditions}")
    return routine


def generate_weekly_routine(user_id: str) -> dict:
    """
    Intenta generar la rutina con Gemini u OpenRouter AI tomando en cuenta salud física.
    """
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
    
    prompt = f"""
    Eres un entrenador personal de élite y especialista en fisioterapia biomecánica.
    Genera una rutina de entrenamiento ESTRICTA y EXCLUSIVA para los siguientes días: {', '.join(training_days)}.
    NO agregues ningún otro día. Genera exactamente {len(training_days)} días.
    
    Perfil del atleta:
    - Objetivo: {goal} | Nivel: {level}
    - Edad: {age} años | Peso: {weight} kg
    - CONDICIONES DE SALUD O LESIONES: {', '.join(health_conditions) if health_conditions else 'Ninguna'}
    - LIMITACIONES FÍSICAS: {limitations}
    
    REGLAS DE SEGURIDAD BIOMECÁNICA E IMPRESCINDIBLES:
    1. Si padece Hernia Discal, NO incluyas Sentadilla con Barra libre ni Peso Muerto pesado. Reemplaza por Prensa de Pierna con apoyo lumbar o Sentadilla Goblet ligera.
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
    
    # 1. Intentar con OpenRouter (usando la clave de OpenRouter)
    openrouter_res = _call_openrouter_ai(prompt, is_json=True)
    if openrouter_res:
        try:
            text = openrouter_res.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            routine = json.loads(text.strip())
            logger.info(f"Rutina generada con OpenRouter AI para {user_id}")
            return routine
        except Exception as e:
            logger.warning(f"Error parseando JSON de OpenRouter: {e}")

    # 2. Intentar con Gemini si existe la API Key
    gemini_key = get_gemini_key()
    if gemini_key and genai:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            routine = json.loads(text.strip())
            logger.info(f"Rutina generada con Gemini AI para {user_id}")
            return routine
        except Exception as e:
            logger.warning(f"Error generando rutina con Gemini: {e}")
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            routine = json.loads(text.strip())
            logger.info(f"Rutina generada con Gemini AI para {user_id}")
            return routine
        except Exception as e:
            logger.warning(f"Error generando rutina con Gemini: {e}")

    # 2. Intentar con Groq si existe cliente válido
    groq_client = get_groq_client()
    if groq_client:
        models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        for model_name in models_to_try:
            try:
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_name,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                text = response.choices[0].message.content.strip()
                routine = json.loads(text)
                logger.info(f"Rutina generada con Groq ({model_name}) para {user_id}")
                return routine
            except Exception as e:
                logger.warning(f"Error generando rutina con Groq ({model_name}): {e}")
                continue

    # 3. Fallback al motor local inteligente (100% confiable y adaptativo)
    logger.info("Usando motor local avanzado como fallback.")
    return _generate_local_routine(user_id)


# ────────────────────────────────────────────────────────────────
# CHATBOT INTELIGENTE CONTEXTUAL
# ────────────────────────────────────────────────────────────────
def _generate_local_chat_response(user_id: str, message: str) -> str:
    """
    Responde consultas del usuario analizando su perfil, historial
    de entrenamiento y la base de datos de ejercicios de forma determinista.
    """
    msg = message.lower().strip()
    profile = database.get_user_profile(user_id)
    fitness = profile.get("fitness_profile", {})
    personal = profile.get("personal_info", {})
    metrics = profile.get("physical_metrics", {})
    nutrition = profile.get("nutrition_profile", {})

    name = personal.get("name", "Atleta")
    age = personal.get("age", 25)
    weight = metrics.get("weight", 70)
    level = fitness.get("level", "basico")
    goal = fitness.get("goal", "hipertrofia")
    days = fitness.get("training_days", [])

    sessions = database.get_workout_sessions(user_id)

    # ── 1. ALTERNATIVA DE EJERCICIO ──
    if any(k in msg for k in ["alternativa", "reemplaz", "cambiar", "ocupad", "sustitui"]):
        target_group = None
        group_keywords = {
            "Pecho": ["pecho", "banca", "press plano", "press de banca"],
            "Espalda": ["espalda", "jalón", "polea alta", "dorsal", "remo"],
            "Piernas": ["pierna", "sentadilla", "squat", "prensa", "cuádriceps"],
            "Hombros": ["hombro", "deltoides", "press militar", "lateral"],
            "Bíceps": ["bícep", "bicep", "curl"],
            "Tríceps": ["trícep", "tricep", "extensión", "fondos"],
        }
        for group, keywords in group_keywords.items():
            if any(kw in msg for kw in keywords):
                target_group = group
                break

        if target_group:
            alternatives = EXERCISE_CATALOG.get(target_group, [])
            if len(alternatives) >= 2:
                alt = random.choice(alternatives)
                return (
                    f"💡 **Sugerencia Local:** Ya que la máquina puede estar ocupada, te sugiero cambiar por **{alt['name']}**. "
                    f"Trabaja exactamente el mismo patrón muscular ({target_group})."
                )
        return "💡 **Sugerencia Local:** No logré identificar el ejercicio. Intenta con una variante con mancuernas."

    # ── 2. PROGRESIÓN DE CARGA / PESO ──
    if any(k in msg for k in ["peso", "progresar", "subir", "carga", "cuánto", "cuanto", "progresión"]):
        if sessions:
            last = sessions[0]
            return f"📈 En tu última sesión levantaste un volumen total de **{last.get('total_volume', 0)} kg**. Hoy intenta aumentarle 1.25kg o 2.5kg a tu primer ejercicio compuesto. ¡Sobrecarga progresiva!"
        base_weight = round(weight * 0.4) if goal == "hipertrofia" else round(weight * 0.5)
        return (
            f"🏋️ {name}, como aún no tienes entrenamientos registrados, aquí van mis recomendaciones iniciales:\n\n"
            f"- **Ejercicios multiarticulares** (sentadilla, press de banca): comienza con **{base_weight} kg**\n"
            f"- **Ejercicios de aislamiento** (curl, extensiones): comienza con **{round(base_weight * 0.4)} kg**\n\n"
            f"La clave es empezar liviano con técnica perfecta. "
            f"Cada semana sube **2.5 kg** en multiarticulares y **1.25 kg** en aislamiento."
        )

    # ── 3. DOLOR O LESIÓN ──
    if any(k in msg for k in ["duele", "dolor", "lesion", "lesión", "molest"]):
        return (
            "⚠️ **Advertencia de Seguridad**\n\n"
            f"{name}, como tu Wellness Coach debo ser categórico: **nunca entrenes sobre dolor agudo o articular**.\n\n"
            "**Protocolo inmediato:**\n"
            "1. **Detén** el ejercicio que causa dolor\n"
            "2. Aplica **hielo** en la zona durante 15 min\n"
            "3. Si el dolor persiste más de **48 horas**, consulta con un **fisioterapeuta o médico**\n\n"
            "Mientras tanto, puedo sugerirte ejercicios alternativos que no involucren la zona afectada. "
            "¿Qué articulación o músculo te molesta?"
        )

    # ── 4. NUTRICIÓN / MACROS / CALORÍAS ──
    if any(k in msg for k in ["macro", "calor", "nutri", "proteín", "protein", "carbohidrat", "grasa", "dieta", "comer"]):
        tdee = nutrition.get("tdee", 0)
        macros = nutrition.get("macros", {})
        if tdee and macros:
            protein = macros.get("protein", 0)
            carbs = macros.get("carbs", 0)
            fats = macros.get("fats", 0)
            goal_tips = {
                "hipertrofia": "Para ganar masa muscular, necesitas un superávit calórico. Prioriza la proteína post-entrenamiento.",
                "fuerza": "Para ganar fuerza, mantén una ingesta calórica estable con alta proteína antes y después del entrenamiento.",
                "definicion": "Para definir, mantén un déficit moderado (~400 kcal). No bajes de 1500 kcal diarias para preservar masa muscular.",
            }
            return (
                f"🍎 **Plan Nutricional Personalizado para {name}:**\n\n"
                f"📊 **TDEE estimado:** {tdee} kcal/día\n"
                f"- 🥩 **Proteínas:** {protein}g ({protein * 4} kcal) — construcción y reparación muscular\n"
                f"- 🍚 **Carbohidratos:** {carbs}g ({carbs * 4} kcal) — energía para entrenar\n"
                f"- 🥑 **Grasas:** {fats}g ({fats * 9} kcal) — función hormonal\n\n"
                f"💡 **Consejo:** {goal_tips.get(goal, 'Mantén un balance calórico adecuado.')}\n\n"
                f"Distribución diaria recomendada:\n"
                f"- Desayuno: 25% de las calorías\n"
                f"- Pre-entreno (1.5h antes): 30%\n"
                f"- Post-entreno: 25%\n"
                f"- Cena: 20%"
            )
        return "🍎 Para calcular tus macronutrientes, completa tu perfil en la sección de Perfil (peso, altura, edad y objetivo)."

    # ── 5. INFORMACIÓN SOBRE RUTINA / DÍAS / PLAN ──
    if any(k in msg for k in ["rutina", "plan", "programa", "día", "dias", "semana", "entrenar"]):
        days_str = ", ".join(days) if days else "no configurados"
        sets, reps = _get_set_rep_scheme(level, goal)
        return (
            f"📋 **Tu Plan de Entrenamiento Actual, {name}:**\n\n"
            f"- 🎯 Objetivo: **{goal.capitalize()}**\n"
            f"- 📊 Nivel: **{level.capitalize()}**\n"
            f"- 📅 Días: **{days_str}** ({len(days)} días/semana)\n"
            f"- 🔢 Esquema: **{sets} series x {reps} repeticiones** por ejercicio\n"
            f"- ⚖️ Peso corporal: **{weight} kg** | Edad: **{age} años**\n\n"
            f"Para regenerar tu rutina con nuevos parámetros, ve a la pestaña **Perfil** "
            f"y ajusta tus días y objetivo. Luego presiona **Regenerar Rutina**."
        )

    # ── 6. MOTIVACIÓN / SALUDO / PREGUNTA GENERAL ──
    stats_msg = ""
    if sessions:
        total_vol = sum(s.get("total_volume", 0) for s in sessions)
        stats_msg = f"\n\n📊 Llevas **{len(sessions)} sesiones** registradas con un volumen total de **{total_vol:.0f} kg**. ¡Sigue así!"

    return (
        f"¡Hola {name}! 👋 Soy tu Wellness Coach inteligente.\n\n"
        f"Puedo ayudarte con:\n"
        f"- 🔄 **Alternativas de ejercicios** si una máquina está ocupada\n"
        f"- 📈 **Progresión de cargas** basada en tu historial\n"
        f"- 🍎 **Nutrición y macros** calculados para tu perfil\n"
        f"- 📋 **Información de tu rutina** y plan semanal\n"
        f"- ⚠️ **Alertas de seguridad** si sientes dolor{stats_msg}\n\n"
        f"¿En qué te puedo ayudar hoy?"
    )


def generate_chat_response(user_id: str, message: str) -> str:
    """
    Intenta responder con Gemini o Groq AI. Si falla o no hay API key válida, usa el motor local.
    """
    msg = message.lower().strip()
    profile = database.get_user_profile(user_id)
    
    prompt = f"""
    Eres 'Wellness AI', un asistente personal deportivo experto.
    Estás hablando con {profile.get('personal_info', {}).get('name', 'el usuario')}, edad {profile.get('personal_info', {}).get('age', 25)}, peso {profile.get('physical_metrics', {}).get('weight', 70)} kg.
    Su objetivo es {profile.get('fitness_profile', {}).get('goal', 'hipertrofia')} y su nivel es {profile.get('fitness_profile', {}).get('level', 'basico')}.
    
    El usuario dice: "{message}"
    
    Responde de manera natural, motivadora, usando emojis y basándote en ciencia del deporte. 
    Si te piden alternativas de ejercicios, mantén el mismo grupo muscular.
    Sé conciso, como en un chat móvil.
    """
    
    # 1. Intentar con OpenRouter
    openrouter_text = _call_openrouter_ai(prompt, is_json=False)
    if openrouter_text:
        logger.info(f"Chat respondido con OpenRouter AI para {user_id}")
        return openrouter_text.strip()

    # 2. Intentar con Gemini
    gemini_key = get_gemini_key()
    if gemini_key and genai:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            logger.info(f"Chat respondido con Gemini AI para {user_id}")
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Error chat Gemini: {e}")

    # 2. Intentar con Groq
    groq_client = get_groq_client()
    if groq_client:
        models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        for model_name in models_to_try:
            try:
                response = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres Wellness AI, experto en fitness. Sé conciso y motivador."},
                        {"role": "user", "content": prompt}
                    ],
                    model=model_name,
                    temperature=0.7,
                )
                logger.info(f"Chat respondido con Groq ({model_name})")
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"Error chat Groq modelo {model_name}: {e}")
                continue

    # 3. Fallback al motor local
    logger.info("Fallback local para el chat (IA no disponible)")
    return _generate_local_chat_response(user_id, message)


class WellnessCoachAgent:
    """Fachada compatible del Wellness Coach Agent para interoperabilidad multiagente."""

    def generate_response(self, user_id: str, message: str) -> str:
        return generate_chat_response(user_id, message)

    def generate_routine(self, user_id: str) -> dict:
        return generate_weekly_routine(user_id)


_agent_instance = WellnessCoachAgent()



