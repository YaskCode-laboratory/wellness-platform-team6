"""
Módulo de Catálogo de Ejercicios, Plantillas de División Semanal y Esquemas de Volumen.
"""

from typing import Dict, List, Tuple

EXERCISE_CATALOG: Dict[str, List[Dict[str, str]]] = {
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

SPLIT_TEMPLATES: Dict[int, List[Dict[str, any]]] = {
    1: [
        {"label": "Full Body", "groups": ["Piernas", "Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]},
    ],
    2: [
        {"label": "Tren Superior", "groups": ["Pecho", "Espalda", "Hombros", "Bíceps", "Tríceps"]},
        {"label": "Tren Inferior + Core", "groups": ["Piernas", "Piernas", "Hombros"]},
    ],
    3: [
        {"label": "Empuje (Push)", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción (Pull)", "groups": ["Espalda", "Bíceps", "Hombros"]},
        {"label": "Pierna (Legs)", "groups": ["Piernas", "Piernas", "Piernas"]},
    ],
    4: [
        {"label": "Superior A (Empuje)", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Inferior A (Cuádriceps)", "groups": ["Piernas", "Piernas"]},
        {"label": "Superior B (Tracción)", "groups": ["Espalda", "Bíceps", "Hombros"]},
        {"label": "Inferior B (Posterior)", "groups": ["Piernas", "Piernas"]},
    ],
    5: [
        {"label": "Empuje (Pecho + Tríceps)", "groups": ["Pecho", "Pecho", "Tríceps"]},
        {"label": "Tracción (Espalda + Bíceps)", "groups": ["Espalda", "Espalda", "Bíceps"]},
        {"label": "Pierna Completa", "groups": ["Piernas", "Piernas", "Piernas"]},
        {"label": "Superior (Hombros + Brazos)", "groups": ["Hombros", "Bíceps", "Tríceps"]},
        {"label": "Inferior + Core", "groups": ["Piernas", "Piernas", "Hombros"]},
    ],
    6: [
        {"label": "Empuje A", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción A", "groups": ["Espalda", "Bíceps"]},
        {"label": "Pierna A", "groups": ["Piernas", "Piernas"]},
        {"label": "Empuje B", "groups": ["Pecho", "Hombros", "Tríceps"]},
        {"label": "Tracción B", "groups": ["Espalda", "Bíceps"]},
        {"label": "Pierna B", "groups": ["Piernas", "Piernas"]},
    ],
}


def get_set_rep_scheme(level: str, goal: str) -> Tuple[int, str]:
    """Retorna la cantidad de series y repeticiones formateadas según nivel y objetivo."""
    schemes = {
        ("basico", "hipertrofia"): (3, "10-12"),
        ("basico", "fuerza"): (3, "6-8"),
        ("basico", "definicion"): (3, "12-15"),
        ("intermedio", "hipertrofia"): (4, "8-12"),
        ("intermedio", "fuerza"): (4, "5-8"),
        ("intermedio", "definicion"): (3, "12-15"),
        ("avanzado", "hipertrofia"): (4, "8-10"),
        ("avanzado", "fuerza"): (5, "3-6"),
        ("avanzado", "definicion"): (4, "10-15"),
    }
    return schemes.get((level, goal), (3, "8-12"))
