from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
from app import database, schemas, agent

app = FastAPI(
    title="Wellness Lift API",
    description="Backend en la nube para la plataforma inteligente de gestión Wellness",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde el frontend (Vite/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, se especificaría el dominio de Firebase Hosting
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "Wellness Lift API",
        "database": "Mock Memory" if database.use_mock else "Google Cloud Firestore",
        "ai_agent": "Wellness Engine Local (Estable)"
    }

# --- RUTAS DE AUTENTICACIÓN ---

# --- RUTAS DE AUTENTICACIÓN ---

@app.post("/api/v1/auth/register")
def register_user(reg: schemas.UserRegister):
    user_id = str(uuid.uuid4())
    success = database.create_user_credentials(reg.email, reg.password, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )
    
    initial_profile = {
        "role": reg.role,
        "gym_branch_id": reg.gym_branch_id,
        "assigned_coach_id": reg.assigned_coach_id if reg.role == "athlete" else None,
        "personal_info": {"name": reg.name, "age": reg.age, "gender": "Masculino"},
        "physical_metrics": {"weight": reg.weight, "height": reg.height},
        "fitness_profile": {
            "goal": reg.goal,
            "level": reg.level,
            "limitations": "Ninguna",
            "health_conditions": reg.health_conditions,
            "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
            "training_days": reg.training_days
        }
    }
    database.save_user_profile(user_id, initial_profile)
    return {
        "status": "success", 
        "user_id": user_id, 
        "role": reg.role, 
        "name": reg.name,
        "gym_branch_id": reg.gym_branch_id,
        "message": "Usuario registrado correctamente"
    }

@app.post("/api/v1/auth/login")
def login_user(log: schemas.UserLogin):
    login_info = database.verify_user_credentials(log.email, log.password)
    if not login_info or not login_info.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo electrónico o contraseña incorrectos."
        )
    
    return {
        "status": "success", 
        "user_id": login_info["user_id"], 
        "role": login_info.get("role", "athlete"),
        "name": login_info.get("name", "Usuario"),
        "gym_branch_id": login_info.get("gym_branch_id", "branch_central"),
        "assigned_coach_id": login_info.get("assigned_coach_id"),
        "message": "Inicio de sesión exitoso"
    }

# --- RUTAS DE USUARIOS Y SUCURSALES ---

@app.get("/api/v1/users/{user_id}", response_model=dict)
def get_user(user_id: str):
    profile = database.get_user_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return profile

@app.post("/api/v1/users/{user_id}")
def update_user(user_id: str, profile: schemas.UserProfileUpdate):
    success = database.save_user_profile(user_id, profile.model_dump())
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo guardar el perfil del usuario."
        )
    return {"status": "success", "message": "Perfil guardado correctamente"}

@app.get("/api/v1/branches", response_model=List[dict])
def get_branches():
    return database.get_branches()

@app.post("/api/v1/branches")
def create_branch(branch: schemas.BranchCreate):
    new_b = database.create_branch(branch.model_dump())
    return {"status": "success", "branch": new_b}

# --- RUTAS DE COACH (ENTRENADOR) ---

@app.get("/api/v1/coaches", response_model=List[dict])
def get_all_coaches():
    return database.get_all_coaches()

@app.get("/api/v1/coach/{coach_id}/athletes", response_model=List[dict])
def get_coach_athletes(coach_id: str):
    return database.get_athletes_for_coach(coach_id)

@app.get("/api/v1/coach/{coach_id}/requests", response_model=List[dict])
def get_coach_requests(coach_id: str):
    return database.get_pending_requests_for_coach(coach_id)

@app.post("/api/v1/coach/requests/{request_id}/action")
def action_routine_request(request_id: str, payload: schemas.RoutineRequestAction):
    req = database.process_routine_request(request_id, payload.action, payload.feedback)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")
    
    # Si fue aprobada, regeneramos la rutina con IA considerando las condiciones de salud
    if payload.action == "approve":
        user_id = req["user_id"]
        new_routine = agent.generate_weekly_routine(user_id)
        database.save_ai_routine(user_id, new_routine)
        
    return {"status": "success", "request": req}

# --- RUTAS DE ADMIN DE GIMNASIO ---

@app.get("/api/v1/admin/users", response_model=List[dict])
def get_all_users_admin():
    return database.get_all_users_admin()

@app.post("/api/v1/admin/users/{user_id}/status")
def toggle_user_status_endpoint(user_id: str, payload: schemas.UserStatusUpdate):
    success = database.toggle_user_status(user_id, payload.is_active)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return {"status": "success", "user_id": user_id, "is_active": payload.is_active}

@app.post("/api/v1/admin/users/{user_id}/branch")
def update_user_branch_endpoint(user_id: str, payload: schemas.UserBranchUpdate):
    success = database.update_user_branch(user_id, payload.gym_branch_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return {"status": "success", "user_id": user_id, "gym_branch_id": payload.gym_branch_id}

@app.post("/api/v1/coach/routine/{user_id}")
def update_coach_custom_routine(user_id: str, routine: dict):
    success = database.save_ai_routine(user_id, routine)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo guardar la rutina.")
    return {"status": "success", "message": "Rutina personalizada por el coach guardada correctamente."}

@app.post("/api/v1/admin/users/{user_id}/update")
def admin_update_user_endpoint(user_id: str, payload: schemas.AdminUserFullUpdate):
    success = database.admin_update_user_full(user_id, payload.model_dump())
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado.")
    return {"status": "success", "user_id": user_id, "message": "Datos de usuario actualizados correctamente."}

@app.get("/api/v1/athlete/{user_id}/technical-file", response_model=dict)
def get_athlete_technical_file_endpoint(user_id: str):
    file_data = database.get_athlete_technical_file(user_id)
    if not file_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atleta no encontrado.")
    return file_data

@app.post("/api/v1/admin/staff")
def register_staff(staff: schemas.AdminStaffCreate):
    user_id = str(uuid.uuid4())
    success = database.create_user_credentials(staff.email, staff.password, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en el gimnasio."
        )
    
    staff_profile = {
        "role": staff.role, # 'coach' o 'admin'
        "is_active": True,
        "created_at": "2026-08-05T12:00:00Z",
        "gym_branch_id": staff.gym_branch_id,
        "specialty": staff.specialty or "Gestión y Fuerza",
        "personal_info": {"name": staff.name, "age": 30, "gender": "Masculino"},
        "physical_metrics": {"weight": 80.0, "height": 178.0},
        "fitness_profile": {
            "goal": "fuerza",
            "level": "avanzado",
            "limitations": "Ninguna",
            "health_conditions": [],
            "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
            "training_days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        }
    }
    database.save_user_profile(user_id, staff_profile)
    return {"status": "success", "user_id": user_id, "role": staff.role, "message": f"Usuario {staff.role.upper()} creado con éxito"}

@app.post("/api/v1/admin/coaches")
def register_coach(coach: schemas.CoachCreate):
    user_id = str(uuid.uuid4())
    success = database.create_user_credentials(coach.email, coach.password, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico del entrenador ya está en uso."
        )
    
    coach_profile = {
        "role": "coach",
        "is_active": True,
        "created_at": "2026-08-05T12:00:00Z",
        "gym_branch_id": coach.gym_branch_id,
        "specialty": coach.specialty,
        "personal_info": {"name": coach.name, "age": 30, "gender": "Masculino"},
        "physical_metrics": {"weight": 80.0, "height": 178.0},
        "fitness_profile": {
            "goal": "fuerza",
            "level": "avanzado",
            "limitations": "Ninguna",
            "health_conditions": [],
            "equipment": ["barra", "mancuernas", "poleas", "maquinas"],
            "training_days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        }
    }
    database.save_user_profile(user_id, coach_profile)
    return {"status": "success", "user_id": user_id, "message": "Coach creado con éxito"}

@app.post("/api/v1/admin/reassign-athlete")
def transfer_athlete(payload: schemas.AthleteTransfer):
    success = database.reassign_athlete(payload.athlete_id, payload.new_coach_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo transferir el atleta.")
    return {"status": "success", "message": "Atleta transferido exitosamente al nuevo entrenador"}

# --- RUTAS DE ATLETA (SOLICITUDES DE RUTINA) ---

@app.post("/api/v1/athlete/routine-request/{user_id}")
def request_routine_change(user_id: str, req: schemas.RoutineRequestCreate):
    created_req = database.create_routine_request(user_id, req.model_dump())
    return {"status": "success", "request": created_req}

@app.get("/api/v1/athlete/routine-requests/{user_id}", response_model=List[dict])
def get_athlete_requests(user_id: str):
    return database.get_athlete_routine_requests(user_id)

# --- RUTAS DE EJERCICIOS ---

@app.get("/api/v1/exercises", response_model=List[dict])
def get_exercises():
    exercises = database.get_master_exercises()
    return exercises

# --- RUTAS DE ENTRENAMIENTO (SESIONES) ---

@app.get("/api/v1/sessions/{user_id}", response_model=List[dict])
def get_sessions(user_id: str):
    sessions = database.get_workout_sessions(user_id)
    return sessions

@app.post("/api/v1/sessions/{user_id}")
def create_session(user_id: str, session: schemas.WorkoutSessionLog):
    success = database.save_workout_session(user_id, session.model_dump())
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo registrar la sesión de entrenamiento."
        )
    return {"status": "success", "message": "Entrenamiento registrado con éxito"}

# --- RUTAS DE IA (WELLNESS COACH AGENT) ---

@app.get("/api/v1/ai/routine/{user_id}")
def get_routine(user_id: str):
    routine = database.get_ai_routine(user_id)
    if not routine:
        routine = agent.generate_weekly_routine(user_id)
        database.save_ai_routine(user_id, routine)
    return routine

@app.post("/api/v1/ai/generate-plan/{user_id}")
def generate_plan(user_id: str):
    profile = database.get_user_profile(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe configurar su perfil de usuario antes de generar una rutina personalizada."
        )
    
    routine = agent.generate_weekly_routine(user_id)
    database.save_ai_routine(user_id, routine)
    return routine

@app.post("/api/v1/ai/chat/{user_id}")
def chat_with_coach(user_id: str, query: schemas.ChatQuery):
    try:
        response_text = agent.generate_chat_response(user_id, query.message)
        return {"response": response_text}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en chat AI: {str(e)}"
        )
