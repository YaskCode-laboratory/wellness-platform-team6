import os
import logging
import hashlib
from dotenv import load_dotenv
from google.cloud import firestore

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar inicializar Firestore
db = None
use_mock = True

# Si existe la variable de entorno para GCP o Firestore, intentamos conectar
# Para demos rápidos, se puede configurar GOOGLE_APPLICATION_CREDENTIALS o GCP_PROJECT_ID
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("FIRESTORE_EMULATOR_HOST") or os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID"):
    try:
        # Inicializa el cliente. Si no hay project_id explícito, Google Cloud SDK lo detecta del entorno
        db = firestore.Client()
        use_mock = False
        logger.info("Conectado con éxito a Google Cloud Firestore real.")
    except Exception as e:
        logger.warning(f"Error al conectar a Firestore real: {e}. Usando base de datos en memoria para el demo.")
else:
    logger.info("No se detectaron variables de entorno de GCP. Iniciando base de datos simulada en memoria.")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Base de datos en memoria para mock (soporte SaaS Multi-Rol)
mock_db = {
    "branches": [
        {"id": "branch_central", "name": "Wellness Fitness Center — Sucursal Central", "city": "Ciudad Central", "address": "Av. Principal #100"},
        {"id": "branch_norte", "name": "Wellness Fitness Center — Sucursal Norte", "city": "Distrito Norte", "address": "Plaza Comercial Norte #45"}
    ],
    "credentials": {
        "admin@wellnessgym.com": {
            "password_hash": hash_password("admin123"),
            "user_id": "user_admin"
        },
        "coach.carlos@wellnessgym.com": {
            "password_hash": hash_password("coach123"),
            "user_id": "coach_carlos"
        },
        "coach.maria@wellnessgym.com": {
            "password_hash": hash_password("coach123"),
            "user_id": "coach_maria"
        },
        "juan@wellness.com": {
            "password_hash": hash_password("password123"),
            "user_id": "user123"
        },
        "ana@wellness.com": {
            "password_hash": hash_password("password123"),
            "user_id": "user456"
        }
    },
    "users": {
        "user_admin": {
            "role": "admin",
            "is_active": True,
            "created_at": "2026-01-10T00:00:00Z",
            "gym_branch_id": "branch_central",
            "personal_info": {"name": "Administrador General", "age": 35, "gender": "Masculino"},
            "physical_metrics": {"weight": 75.0, "height": 175.0},
            "fitness_profile": {
                "goal": "hipertrofia", "level": "avanzado", "limitations": "Ninguna",
                "health_conditions": [], "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
                "training_days": ["Lunes", "Miércoles", "Viernes"]
            }
        },
        "coach_carlos": {
            "role": "coach",
            "is_active": True,
            "created_at": "2026-01-12T00:00:00Z",
            "gym_branch_id": "branch_central",
            "specialty": "Hipertrofia y Levantamiento de Pesas",
            "personal_info": {"name": "Coach Carlos Ruiz", "age": 30, "gender": "Masculino"},
            "physical_metrics": {"weight": 85.0, "height": 180.0},
            "fitness_profile": {
                "goal": "fuerza", "level": "avanzado", "limitations": "Ninguna",
                "health_conditions": [], "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
                "training_days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
            }
        },
        "coach_maria": {
            "role": "coach",
            "is_active": True,
            "created_at": "2026-02-01T00:00:00Z",
            "gym_branch_id": "branch_norte",
            "specialty": "Rehabilitación Biomecánica y Fuerza",
            "personal_info": {"name": "Coach María Fernández", "age": 29, "gender": "Femenino"},
            "physical_metrics": {"weight": 62.0, "height": 165.0},
            "fitness_profile": {
                "goal": "hipertrofia", "level": "avanzado", "limitations": "Ninguna",
                "health_conditions": [], "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
                "training_days": ["Lunes", "Miércoles", "Viernes"]
            }
        },
        "user123": {
            "role": "athlete",
            "is_active": True,
            "created_at": "2026-03-01T00:00:00Z",
            "gym_branch_id": "branch_central",
            "assigned_coach_id": "coach_carlos",
            "personal_info": {"name": "Juan Pérez", "age": 28, "gender": "Masculino"},
            "physical_metrics": {"weight": 80.0, "height": 178.0},
            "fitness_profile": {
                "goal": "hipertrofia", 
                "level": "intermedio", 
                "limitations": "Evitar compresión lumbar brusca", 
                "health_conditions": ["Hernia Discal L4-L5"],
                "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
                "training_days": ["Lunes", "Miércoles", "Viernes"]
            },
            "nutrition_profile": {
                "tdee": 2500,
                "macros": {"protein": 160, "carbs": 280, "fats": 80}
            }
        },
        "user456": {
            "role": "athlete",
            "is_active": True,
            "created_at": "2026-04-10T00:00:00Z",
            "gym_branch_id": "branch_central",
            "assigned_coach_id": "coach_carlos",
            "personal_info": {"name": "Ana Gómez", "age": 26, "gender": "Femenino"},
            "physical_metrics": {"weight": 60.0, "height": 165.0},
            "fitness_profile": {
                "goal": "definicion", 
                "level": "basico", 
                "limitations": "Dolor en rodilla derecha", 
                "health_conditions": ["Lesión de Rodilla (Menisco)"],
                "equipment": ["mancuernas", "poleas", "maquinas"],
                "training_days": ["Martes", "Jueves", "Sábado"]
            },
            "nutrition_profile": {
                "tdee": 1800,
                "macros": {"protein": 120, "carbs": 180, "fats": 50}
            }
        }
    },
    "routine_requests": [
        {
            "id": "req_1",
            "user_id": "user123",
            "athlete_name": "Juan Pérez",
            "coach_id": "coach_carlos",
            "requested_days": ["Lunes", "Martes", "Jueves", "Viernes"],
            "requested_goal": "fuerza",
            "notes": "Quiero subir el entrenamiento a 4 días cuidando mi hernia discal.",
            "health_conditions": ["Hernia Discal L4-L5"],
            "status": "pending",
            "created_at": "2026-08-05T10:00:00Z"
        }
    ],
    "master_exercises": [
        {"id": "squat", "name": "Sentadilla con Barra", "muscle_group": "Piernas", "equipment": "barra", "alternative_ids": ["leg_press", "goblet_squat"]},
        {"id": "leg_press", "name": "Prensa de Piernas Inclinada", "muscle_group": "Piernas", "equipment": "maquinas", "alternative_ids": ["squat", "lunges"]},
        {"id": "goblet_squat", "name": "Sentadilla Goblet con Mancuerna", "muscle_group": "Piernas", "equipment": "mancuernas", "alternative_ids": ["squat", "leg_press"]},
        {"id": "bench_press", "name": "Press de Banca Plano con Barra", "muscle_group": "Pecho", "equipment": "barra", "alternative_ids": ["dumbbell_press", "chest_fly"]},
        {"id": "dumbbell_press", "name": "Press Inclinado con Mancuernas", "muscle_group": "Pecho", "equipment": "mancuernas", "alternative_ids": ["bench_press", "push_ups"]},
        {"id": "chest_fly", "name": "Aperturas en Polea para Pecho", "muscle_group": "Pecho", "equipment": "poleas", "alternative_ids": ["bench_press", "dumbbell_press"]},
        {"id": "lat_pulldown", "name": "Jalón al Pecho en Polea", "muscle_group": "Espalda", "equipment": "poleas", "alternative_ids": ["barbell_row", "pull_ups"]},
        {"id": "barbell_row", "name": "Remo con Barra", "muscle_group": "Espalda", "equipment": "barra", "alternative_ids": ["lat_pulldown", "dumbbell_row"]},
        {"id": "dumbbell_row", "name": "Remo con Mancuerna a una Mano", "muscle_group": "Espalda", "equipment": "mancuernas", "alternative_ids": ["barbell_row", "lat_pulldown"]},
        {"id": "overhead_press", "name": "Press Militar con Barra", "muscle_group": "Hombros", "equipment": "barra", "alternative_ids": ["lateral_raises", "dumbbell_shoulder_press"]},
        {"id": "dumbbell_shoulder_press", "name": "Press de Hombros con Mancuernas", "muscle_group": "Hombros", "equipment": "mancuernas", "alternative_ids": ["overhead_press", "lateral_raises"]},
        {"id": "lateral_raises", "name": "Elevaciones Laterales con Mancuernas", "muscle_group": "Hombros", "equipment": "mancuernas", "alternative_ids": ["overhead_press", "dumbbell_shoulder_press"]},
        {"id": "bicep_curl", "name": "Curl de Bíceps con Barra", "muscle_group": "Bíceps", "equipment": "barra", "alternative_ids": ["db_bicep_curl", "hammer_curl"]},
        {"id": "db_bicep_curl", "name": "Curl de Bíceps con Mancuernas", "muscle_group": "Bíceps", "equipment": "mancuernas", "alternative_ids": ["bicep_curl", "hammer_curl"]},
        {"id": "tricep_pushdown", "name": "Extensión de Tríceps en Polea", "muscle_group": "Tríceps", "equipment": "poleas", "alternative_ids": ["skull_crusher", "overhead_tricep_extension"]},
        {"id": "skull_crusher", "name": "Rompe Cráneos con Barra Z", "muscle_group": "Tríceps", "equipment": "barra", "alternative_ids": ["tricep_pushdown", "overhead_tricep_extension"]}
    ],
    "workout_sessions": {
        "user123": [
            {
                "id": "sess_3",
                "date": "2026-08-04T18:00:00Z",
                "day_name": "Viernes (Pierna en Prensa)",
                "total_volume": 3200,
                "exercises": [
                    {
                        "exercise_id": "leg_press",
                        "exercise_name": "Prensa de Piernas Inclinada",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight": 120.0, "completed": True},
                            {"set_number": 2, "reps": 12, "weight": 120.0, "completed": True},
                            {"set_number": 3, "reps": 10, "weight": 130.0, "completed": True}
                        ]
                    },
                    {
                        "exercise_id": "goblet_squat",
                        "exercise_name": "Sentadilla Goblet con Mancuerna",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight": 24.0, "completed": True},
                            {"set_number": 2, "reps": 10, "weight": 28.0, "completed": True}
                        ]
                    }
                ]
            },
            {
                "id": "sess_2",
                "date": "2026-08-02T18:00:00Z",
                "day_name": "Miércoles (Tracción sin Carga Axel)",
                "total_volume": 2850,
                "exercises": [
                    {
                        "exercise_id": "lat_pulldown",
                        "exercise_name": "Jalón al Pecho en Polea",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 55.0, "completed": True},
                            {"set_number": 2, "reps": 10, "weight": 60.0, "completed": True},
                            {"set_number": 3, "reps": 8, "weight": 65.0, "completed": True}
                        ]
                    },
                    {
                        "exercise_id": "dumbbell_row",
                        "exercise_name": "Remo con Mancuerna a una Mano",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 26.0, "completed": True},
                            {"set_number": 2, "reps": 10, "weight": 28.0, "completed": True}
                        ]
                    }
                ]
            },
            {
                "id": "sess_1",
                "date": "2026-07-31T18:00:00Z",
                "day_name": "Lunes (Empuje Protegido)",
                "total_volume": 2400,
                "exercises": [
                    {
                        "exercise_id": "bench_press",
                        "exercise_name": "Press de Banca Plano con Barra",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 60.0, "completed": True},
                            {"set_number": 2, "reps": 10, "weight": 60.0, "completed": True},
                            {"set_number": 3, "reps": 8, "weight": 65.0, "completed": True}
                        ]
                    }
                ]
            }
        ],
        "user456": [
            {
                "id": "sess_ana_1",
                "date": "2026-08-03T17:00:00Z",
                "day_name": "Martes (Brazos y Core Guiado)",
                "total_volume": 1800,
                "exercises": [
                    {
                        "exercise_id": "lat_pulldown",
                        "exercise_name": "Jalón al Pecho en Polea",
                        "sets": [
                            {"set_number": 1, "reps": 12, "weight": 35.0, "completed": True},
                            {"set_number": 2, "reps": 12, "weight": 40.0, "completed": True}
                        ]
                    }
                ]
            }
        ]
    },
    "ai_routines": {
        "user123": {
            "focus": "Hipertrofia — Nivel Intermedio — 3 días/semana (Protección Lumbar)",
            "weekly_schedule": [
                {
                    "day": "Lunes (Empuje Protegido)",
                    "exercises": [
                        {"exercise_id": "dumbbell_press", "name": "Press Inclinado con Mancuernas", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "dumbbell_shoulder_press", "name": "Press de Hombros con Mancuernas", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "tricep_pushdown", "name": "Extensión de Tríceps en Polea", "sets": 4, "reps": "8-12"}
                    ]
                },
                {
                    "day": "Miércoles (Tracción sin Carga Axel)",
                    "exercises": [
                        {"exercise_id": "lat_pulldown", "name": "Jalón al Pecho en Polea", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "dumbbell_row", "name": "Remo con Mancuerna a una Mano", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "db_bicep_curl", "name": "Curl de Bíceps con Mancuernas", "sets": 4, "reps": "8-12"}
                    ]
                },
                {
                    "day": "Viernes (Pierna en Prensa)",
                    "exercises": [
                        {"exercise_id": "leg_press", "name": "Prensa de Piernas Inclinada", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "goblet_squat", "name": "Sentadilla Goblet con Mancuerna", "sets": 4, "reps": "8-12"},
                        {"exercise_id": "lateral_raises", "name": "Elevaciones Laterales con Mancuernas", "sets": 4, "reps": "8-12"}
                    ]
                }
            ]
        }
    }
}

# Funciones de utilidad para abstraer la base de datos
def get_user_profile(user_id: str) -> dict:
    if use_mock:
        return mock_db["users"].get(user_id, {})
    
    doc_ref = db.collection("users").document(user_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else {}

def save_user_profile(user_id: str, profile_data: dict) -> bool:
    if use_mock:
        if user_id not in mock_db["users"]:
            mock_db["users"][user_id] = {}
        mock_db["users"][user_id].update(profile_data)
        # Recalcular TDEE e inicializar macros de forma determinista para la demo
        weight = profile_data.get("physical_metrics", {}).get("weight", 70.0)
        goal = profile_data.get("fitness_profile", {}).get("goal", "hipertrofia")
        
        # Fórmula simplificada de TDEE para la demo
        tdee = int(weight * 32)
        if goal == "definicion":
            tdee -= 400
        elif goal == "fuerza" or goal == "hipertrofia":
            tdee += 300
            
        protein = int(weight * 2.0)
        fats = int(weight * 1.0)
        carbs = int((tdee - (protein * 4 + fats * 9)) / 4)
        
        mock_db["users"][user_id]["nutrition_profile"] = {
            "tdee": tdee,
            "macros": {"protein": protein, "carbs": carbs, "fats": fats}
        }
        return True
    
    # Cloud Firestore
    doc_ref = db.collection("users").document(user_id)
    # Calculo automático
    weight = profile_data.get("physical_metrics", {}).get("weight", 70.0)
    goal = profile_data.get("fitness_profile", {}).get("goal", "hipertrofia")
    tdee = int(weight * 32)
    if goal == "definicion":
        tdee -= 400
    elif goal == "fuerza" or goal == "hipertrofia":
        tdee += 300
    protein = int(weight * 2.0)
    fats = int(weight * 1.0)
    carbs = int((tdee - (protein * 4 + fats * 9)) / 4)
    
    profile_data["nutrition_profile"] = {
        "tdee": tdee,
        "macros": {"protein": protein, "carbs": carbs, "fats": fats}
    }
    
    doc_ref.set(profile_data, merge=True)
    return True

def get_master_exercises() -> list:
    if use_mock:
        return mock_db["master_exercises"]
    
    docs = db.collection("master_exercises").stream()
    exercises = []
    for doc in docs:
        ex = doc.to_dict()
        ex["id"] = doc.id
        exercises.append(ex)
    
    # Si la colección en Firestore está vacía (primer inicio), la inicializamos con datos por defecto
    if not exercises:
        logger.info("Colección master_exercises vacía en Firestore. Inicializando con catálogo por defecto...")
        for ex in mock_db["master_exercises"]:
            ex_id = ex["id"]
            data = ex.copy()
            del data["id"]
            db.collection("master_exercises").document(ex_id).set(data)
            data["id"] = ex_id
            exercises.append(data)
            
    return exercises

def get_exercise_history(user_id: str, exercise_id: str) -> list:
    sessions = get_workout_sessions(user_id)
    history = []
    for session in sessions:
        for ex in session.get("exercises", []):
            if ex.get("exercise_id") == exercise_id:
                history.append({
                    "date": session.get("date"),
                    "sets": ex.get("sets", [])
                })
    # Ordenar por fecha
    history.sort(key=lambda x: x["date"])
    return history[-5:]  # Retorna las últimas 5 sesiones de este ejercicio

def get_workout_sessions(user_id: str) -> list:
    if use_mock:
        return mock_db["workout_sessions"].get(user_id, [])
    
    docs = db.collection("users").document(user_id).collection("workout_sessions").order_by("date", direction=firestore.Query.DESCENDING).stream()
    sessions = []
    for doc in docs:
        sess = doc.to_dict()
        sess["id"] = doc.id
        sessions.append(sess)
    return sessions

def save_workout_session(user_id: str, session_data: dict) -> bool:
    # Calcular volumen total de forma segura
    total_volume = 0
    for ex in session_data.get("exercises", []):
        for s in ex.get("sets", []):
            if s.get("completed", False):
                total_volume += int(s.get("reps", 0)) * float(s.get("weight", 0.0))
    session_data["total_volume"] = total_volume

    if use_mock:
        if user_id not in mock_db["workout_sessions"]:
            mock_db["workout_sessions"][user_id] = []
        # Generar un ID simple
        session_data["id"] = f"sess_{len(mock_db['workout_sessions'][user_id]) + 1}"
        mock_db["workout_sessions"][user_id].insert(0, session_data)
        return True
    
    # Firestore
    coll_ref = db.collection("users").document(user_id).collection("workout_sessions")
    coll_ref.add(session_data)
    return True

def get_ai_routine(user_id: str) -> dict:
    if use_mock:
        return mock_db["ai_routines"].get(user_id, {})
    
    doc = db.collection("users").document(user_id).collection("ai_routines").document("active").get()
    return doc.to_dict() if doc.exists else {}

def save_ai_routine(user_id: str, routine_data: dict) -> bool:
    if use_mock:
        mock_db["ai_routines"][user_id] = routine_data
        return True
    
    doc_ref = db.collection("users").document(user_id).collection("ai_routines").document("active")
    doc_ref.set(routine_data)
    return True

def create_user_credentials(email: str, password: str, user_id: str) -> bool:
    email_clean = email.lower().strip()
    pwd_hash = hash_password(password)
    
    if use_mock:
        if email_clean in mock_db["credentials"]:
            return False  # El correo ya está registrado
        mock_db["credentials"][email_clean] = {
            "password_hash": pwd_hash,
            "user_id": user_id
        }
        return True
        
    doc_ref = db.collection("credentials").document(email_clean)
    if doc_ref.get().exists:
        return False
        
    doc_ref.set({
        "password_hash": pwd_hash,
        "user_id": user_id
    })
    return True

def verify_user_credentials(email: str, password: str) -> dict:
    """Devuelve dict con user_id y rol si la autenticación es correcta."""
    email_clean = email.lower().strip()
    pwd_hash = hash_password(password)
    
    if use_mock:
        cred = mock_db["credentials"].get(email_clean)
        if cred and cred["password_hash"] == pwd_hash:
            u_id = cred["user_id"]
            user_data = mock_db["users"].get(u_id, {})
            return {
                "user_id": u_id,
                "role": user_data.get("role", "athlete"),
                "name": user_data.get("personal_info", {}).get("name", "Usuario"),
                "gym_branch_id": user_data.get("gym_branch_id", "branch_central"),
                "assigned_coach_id": user_data.get("assigned_coach_id")
            }
        return {}
        
    doc_ref = db.collection("credentials").document(email_clean)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        if data.get("password_hash") == pwd_hash:
            u_id = data.get("user_id", "")
            user_data = get_user_profile(u_id)
            return {
                "user_id": u_id,
                "role": user_data.get("role", "athlete"),
                "name": user_data.get("personal_info", {}).get("name", "Usuario"),
                "gym_branch_id": user_data.get("gym_branch_id", "branch_central"),
                "assigned_coach_id": user_data.get("assigned_coach_id")
            }
    return {}

# ────────────────────────────────────────────────────────────────
# FUNCIONES SAAS MULTI-ROL (ADMIN, COACH, ATLETA)
# ────────────────────────────────────────────────────────────────

def get_branches() -> list:
    if use_mock:
        return mock_db.get("branches", [])
    docs = db.collection("branches").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def create_branch(branch_data: dict) -> dict:
    branch_id = f"branch_{len(mock_db['branches']) + 1}"
    branch_data["id"] = branch_id
    if use_mock:
        mock_db["branches"].append(branch_data)
        return branch_data
    db.collection("branches").document(branch_id).set(branch_data)
    return branch_data

def get_athletes_for_coach(coach_id: str) -> list:
    athletes = []
    if use_mock:
        for u_id, u_data in mock_db["users"].items():
            if u_data.get("role") == "athlete" and u_data.get("assigned_coach_id") == coach_id:
                athletes.append({"user_id": u_id, **u_data})
        return athletes
    
    docs = db.collection("users").where("role", "==", "athlete").where("assigned_coach_id", "==", coach_id).stream()
    return [{"user_id": d.id, **d.to_dict()} for d in docs]

def get_all_coaches() -> list:
    coaches = []
    if use_mock:
        for u_id, u_data in mock_db["users"].items():
            if u_data.get("role") == "coach":
                coaches.append({"user_id": u_id, **u_data})
        return coaches
    
    docs = db.collection("users").where("role", "==", "coach").stream()
    return [{"user_id": d.id, **d.to_dict()} for d in docs]

def reassign_athlete(athlete_id: str, new_coach_id: str) -> bool:
    if use_mock:
        if athlete_id in mock_db["users"]:
            mock_db["users"][athlete_id]["assigned_coach_id"] = new_coach_id
            return True
        return False
    
    doc_ref = db.collection("users").document(athlete_id)
    if doc_ref.get().exists:
        doc_ref.update({"assigned_coach_id": new_coach_id})
        return True
    return False

def create_routine_request(user_id: str, request_data: dict) -> dict:
    user_data = get_user_profile(user_id)
    req_id = f"req_{len(mock_db.get('routine_requests', [])) + 1}"
    full_req = {
        "id": req_id,
        "user_id": user_id,
        "athlete_name": user_data.get("personal_info", {}).get("name", "Atleta"),
        "coach_id": user_data.get("assigned_coach_id", "coach_carlos"),
        "requested_days": request_data.get("requested_days", ["Lunes", "Miércoles", "Viernes"]),
        "requested_goal": request_data.get("requested_goal", "hipertrofia"),
        "notes": request_data.get("notes", ""),
        "health_conditions": user_data.get("fitness_profile", {}).get("health_conditions", []),
        "status": "pending",
        "created_at": "2026-08-05T12:00:00Z"
    }
    
    if use_mock:
        mock_db["routine_requests"].insert(0, full_req)
        return full_req
        
    db.collection("routine_requests").document(req_id).set(full_req)
    return full_req

def get_pending_requests_for_coach(coach_id: str) -> list:
    if use_mock:
        return [r for r in mock_db.get("routine_requests", []) if r.get("coach_id") == coach_id and r.get("status") == "pending"]
    docs = db.collection("routine_requests").where("coach_id", "==", coach_id).where("status", "==", "pending").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_athlete_routine_requests(user_id: str) -> list:
    if use_mock:
        return [r for r in mock_db.get("routine_requests", []) if r.get("user_id") == user_id]
    docs = db.collection("routine_requests").where("user_id", "==", user_id).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def process_routine_request(request_id: str, action: str, feedback: str) -> dict:
    target_req = None
    if use_mock:
        for r in mock_db.get("routine_requests", []):
            if r["id"] == request_id:
                target_req = r
                break
    else:
        doc_ref = db.collection("routine_requests").document(request_id)
        doc = doc_ref.get()
        if doc.exists:
            target_req = doc.to_dict()
            target_req["id"] = doc.id

    if not target_req:
        return None

    new_status = "approved" if action == "approve" else "rejected"
    target_req["status"] = new_status
    target_req["feedback"] = feedback

    if use_mock:
        if new_status == "approved":
            # Si se aprueba, actualizamos el perfil del usuario con los nuevos días y meta
            u_id = target_req["user_id"]
            if u_id in mock_db["users"]:
                mock_db["users"][u_id]["fitness_profile"]["training_days"] = target_req["requested_days"]
                mock_db["users"][u_id]["fitness_profile"]["goal"] = target_req["requested_goal"]
        return target_req

    doc_ref = db.collection("routine_requests").document(request_id)
    doc_ref.update({"status": new_status, "feedback": feedback})

    if new_status == "approved":
        u_id = target_req["user_id"]
        db.collection("users").document(u_id).update({
            "fitness_profile.training_days": target_req["requested_days"],
            "fitness_profile.goal": target_req["requested_goal"]
        })

    return target_req


# ────────────────────────────────────────────────────────────────
# FUNCIONES DE GESTIÓN GLOBAL PARA ADMIN Y FICHA TÉCNICA
# ────────────────────────────────────────────────────────────────

def get_all_users_admin() -> list:
    """Retorna directorio completo de todos los usuarios del sistema para el Admin."""
    branches_map = {b["id"]: b["name"] for b in mock_db.get("branches", [])}
    coaches_map = {u_id: u_data.get("personal_info", {}).get("name", "Coach") for u_id, u_data in mock_db["users"].items() if u_data.get("role") == "coach"}
    
    users_list = []
    for u_id, u_data in mock_db["users"].items():
        # Buscar correo asociado en credenciales
        email = ""
        for em, cred in mock_db["credentials"].items():
            if cred.get("user_id") == u_id:
                email = em
                break
                
        branch_id = u_data.get("gym_branch_id", "branch_central")
        coach_id = u_data.get("assigned_coach_id")
        
        # Calcular estadísticas breves
        sess_list = mock_db["workout_sessions"].get(u_id, [])
        total_vol = sum(s.get("total_volume", 0) for s in sess_list)
        
        users_list.append({
            "user_id": u_id,
            "email": email,
            "name": u_data.get("personal_info", {}).get("name", "Usuario"),
            "role": u_data.get("role", "athlete"),
            "is_active": u_data.get("is_active", True),
            "created_at": u_data.get("created_at", "2026-01-01T00:00:00Z"),
            "gym_branch_id": branch_id,
            "gym_branch_name": branches_map.get(branch_id, "Sucursal Central"),
            "assigned_coach_id": coach_id,
            "assigned_coach_name": coaches_map.get(coach_id, "Sin Asignar") if coach_id else "N/A",
            "goal": u_data.get("fitness_profile", {}).get("goal", "hipertrofia"),
            "health_conditions": u_data.get("fitness_profile", {}).get("health_conditions", []),
            "total_sessions": len(sess_list),
            "accumulated_volume": total_vol
        })
    return users_list

def toggle_user_status(user_id: str, is_active: bool) -> bool:
    if use_mock:
        if user_id in mock_db["users"]:
            mock_db["users"][user_id]["is_active"] = is_active
            return True
        return False
    doc_ref = db.collection("users").document(user_id)
    if doc_ref.get().exists:
        doc_ref.update({"is_active": is_active})
        return True
    return False

def update_user_branch(user_id: str, new_branch_id: str) -> bool:
    if use_mock:
        if user_id in mock_db["users"]:
            mock_db["users"][user_id]["gym_branch_id"] = new_branch_id
            return True
        return False
    doc_ref = db.collection("users").document(user_id)
    if doc_ref.get().exists:
        doc_ref.update({"gym_branch_id": new_branch_id})
        return True
    return False

def get_athlete_technical_file(user_id: str) -> dict:
    """Devuelve la ficha técnica completa del atleta para el Coach y Admin."""
    user_data = get_user_profile(user_id)
    if not user_data:
        return {}
        
    sessions = get_workout_sessions(user_id)
    ai_routine = get_ai_routine(user_id)
    
    # Calcular Récords Personales (PRs) de Carga Máxima por Ejercicio
    prs = {}
    for sess in sessions:
        for ex in sess.get("exercises", []):
            ex_name = ex.get("exercise_name", "Ejercicio")
            for s in ex.get("sets", []):
                w = float(s.get("weight", 0.0))
                r = int(s.get("reps", 0))
                if ex_name not in prs or w > prs[ex_name]["max_weight"]:
                    prs[ex_name] = {"max_weight": w, "reps": r, "date": sess.get("date")}
                    
    total_volume = sum(s.get("total_volume", 0) for s in sessions)
    
    return {
        "user_id": user_id,
        "personal_info": user_data.get("personal_info", {}),
        "physical_metrics": user_data.get("physical_metrics", {}),
        "fitness_profile": user_data.get("fitness_profile", {}),
        "nutrition_profile": user_data.get("nutrition_profile", {}),
        "is_active": user_data.get("is_active", True),
        "created_at": user_data.get("created_at", "2026-01-01T00:00:00Z"),
        "total_sessions": len(sessions),
        "total_volume_lifted": total_volume,
        "personal_records": prs,
        "workout_history": sessions,
        "active_routine": ai_routine
    }

def admin_update_user_full(user_id: str, update_data: dict) -> bool:
    """Actualización completa de datos de un usuario desde el panel de Admin."""
    if use_mock:
        if user_id in mock_db["users"]:
            u = mock_db["users"][user_id]
            u["personal_info"]["name"] = update_data.get("name", u["personal_info"]["name"])
            u["role"] = update_data.get("role", u.get("role"))
            u["gym_branch_id"] = update_data.get("gym_branch_id", u.get("gym_branch_id"))
            u["assigned_coach_id"] = update_data.get("assigned_coach_id", u.get("assigned_coach_id"))
            u["fitness_profile"]["goal"] = update_data.get("goal", u["fitness_profile"]["goal"])
            u["fitness_profile"]["level"] = update_data.get("level", u["fitness_profile"]["level"])
            u["fitness_profile"]["health_conditions"] = update_data.get("health_conditions", u["fitness_profile"].get("health_conditions", []))
            u["fitness_profile"]["training_days"] = update_data.get("training_days", u["fitness_profile"].get("training_days", []))
            
            # Actualizar correo y/o contraseña en credenciales
            new_email = update_data.get("email", "").lower().strip()
            new_password = update_data.get("new_password", "").strip()
            
            # Buscar credencial actual
            old_email = None
            for em, cred in mock_db["credentials"].items():
                if cred["user_id"] == user_id:
                    old_email = em
                    break
            
            target_email = new_email if new_email else old_email
            if old_email and target_email:
                pwd_hash = mock_db["credentials"][old_email]["password_hash"]
                if new_password:
                    pwd_hash = hash_password(new_password)
                
                if old_email != target_email:
                    del mock_db["credentials"][old_email]
                    
                mock_db["credentials"][target_email] = {"password_hash": pwd_hash, "user_id": user_id}
            return True
        return False
        
    doc_ref = db.collection("users").document(user_id)
    if doc_ref.get().exists:
        doc_ref.update({
            "personal_info.name": update_data.get("name"),
            "role": update_data.get("role"),
            "gym_branch_id": update_data.get("gym_branch_id"),
            "assigned_coach_id": update_data.get("assigned_coach_id"),
            "fitness_profile.goal": update_data.get("goal"),
            "fitness_profile.health_conditions": update_data.get("health_conditions"),
            "fitness_profile.training_days": update_data.get("training_days")
        })
        return True
    return False



