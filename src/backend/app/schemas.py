from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Modelos para Perfil de Usuario
class PersonalInfo(BaseModel):
    name: str = Field(..., description="Nombre del usuario")
    age: int = Field(..., ge=12, le=100, description="Edad")
    gender: str = Field(..., description="Género (Masculino, Femenino, Otro)")

class PhysicalMetrics(BaseModel):
    weight: float = Field(..., ge=30, le=250, description="Peso corporal en kg")
    height: float = Field(..., ge=100, le=250, description="Altura en cm")

class FitnessProfile(BaseModel):
    goal: str = Field(..., description="Objetivo principal (hipertrofia, fuerza, definicion)")
    level: str = Field(..., description="Nivel (basico, intermedio, avanzado)")
    limitations: Optional[str] = Field("Ninguna", description="Limitaciones o lesiones físicas generales")
    health_conditions: List[str] = Field(default=[], description="Condiciones médicas o de salud física (ej. Hernia Discal, Lesión Rodilla, Hipertensión, Asma)")
    equipment: List[str] = Field(..., description="Equipamiento disponible (barra, mancuernas, poleas, maquinas)")
    training_days: List[str] = Field(default=["Lunes", "Miércoles", "Viernes"], description="Días de la semana que entrena")

class UserProfileUpdate(BaseModel):
    personal_info: PersonalInfo
    physical_metrics: PhysicalMetrics
    fitness_profile: FitnessProfile

# Modelos para Autenticación y SaaS Multi-Rol
class UserRegister(BaseModel):
    email: str = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=6, description="Contraseña")
    name: str = Field(..., description="Nombre completo")
    role: str = Field("athlete", description="Rol del usuario (admin, coach, athlete)")
    gym_branch_id: str = Field("branch_central", description="ID de la sucursal del gimnasio")
    assigned_coach_id: Optional[str] = Field("coach_carlos", description="ID del entrenador asignado (si es atleta)")
    age: int = Field(25, ge=12, le=100, description="Edad")
    weight: float = Field(70.0, ge=30, le=250, description="Peso corporal en kg")
    height: float = Field(170.0, ge=100, le=250, description="Altura en cm")
    goal: str = Field("hipertrofia", description="Objetivo: hipertrofia, fuerza, definicion")
    level: str = Field("basico", description="Nivel: basico, intermedio, avanzado")
    health_conditions: List[str] = Field(default=[], description="Condiciones médicas o lesiones específicas")
    training_days: List[str] = Field(default=["Lunes", "Miércoles", "Viernes"], description="Días de entrenamiento")

class UserLogin(BaseModel):
    email: str = Field(..., description="Correo electrónico")
    password: str = Field(..., description="Contraseña")

class BranchCreate(BaseModel):
    name: str = Field(..., description="Nombre de la sucursal")
    city: str = Field(..., description="Ciudad / Ubicación")
    address: str = Field(..., description="Dirección física")

class CoachCreate(BaseModel):
    email: str = Field(..., description="Correo del entrenador")
    password: str = Field(..., min_length=6, description="Contraseña inicial")
    name: str = Field(..., description="Nombre del entrenador")
    gym_branch_id: str = Field("branch_central", description="ID de la sucursal")
    specialty: str = Field("Levantamiento de Pesas e Hipertrofia", description="Especialidad")

class AthleteTransfer(BaseModel):
    athlete_id: str = Field(..., description="ID del atleta a transferir")
    new_coach_id: str = Field(..., description="ID del nuevo entrenador asignado")

class UserStatusUpdate(BaseModel):
    is_active: bool = Field(..., description="Estado activo (True) o inactivo (False)")

class UserBranchUpdate(BaseModel):
    gym_branch_id: str = Field(..., description="ID de la nueva sucursal asignada")

class UserCoachUpdate(BaseModel):
    coach_id: str = Field(..., description="ID del nuevo entrenador asignado")

class AdminUserFullUpdate(BaseModel):
    name: str = Field(..., description="Nombre del usuario")
    email: str = Field(..., description="Correo electrónico")
    new_password: Optional[str] = Field(None, description="Nueva contraseña para restablecer (opcional)")
    role: str = Field("athlete", description="Rol del usuario (admin, coach, athlete)")
    gym_branch_id: str = Field("branch_central", description="ID de la sucursal")
    assigned_coach_id: Optional[str] = Field(None, description="ID del coach asignado")
    goal: str = Field("hipertrofia", description="Objetivo")
    level: str = Field("basico", description="Nivel")
    health_conditions: List[str] = Field(default=[], description="Condiciones médicas")
    training_days: List[str] = Field(default=["Lunes", "Miércoles", "Viernes"], description="Días de entrenamiento")

class AdminStaffCreate(BaseModel):
    email: str = Field(..., description="Correo del usuario")
    password: str = Field(..., min_length=6, description="Contraseña inicial")
    name: str = Field(..., description="Nombre del usuario")
    role: str = Field("coach", description="Rol a crear: 'coach' o 'admin'")
    gym_branch_id: str = Field("branch_central", description="ID de la sucursal")
    specialty: Optional[str] = Field("Gestión & Fuerza", description="Especialidad o cargo")

class RoutineRequestCreate(BaseModel):
    requested_days: List[str] = Field(..., description="Nuevos días deseados de entrenamiento")
    requested_goal: str = Field(..., description="Nuevo objetivo deseado")
    notes: Optional[str] = Field("", description="Motivos o comentarios del atleta")

class RoutineRequestAction(BaseModel):
    action: str = Field(..., description="Acción del coach: 'approve' o 'reject'")
    feedback: Optional[str] = Field("", description="Comentarios u observaciones del entrenador")

# Modelos para Registro de Entrenamiento
class SetLog(BaseModel):
    set_number: int
    reps: int
    weight: float
    completed: bool = True

class ExerciseLog(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: List[SetLog]

class WorkoutSessionLog(BaseModel):
    date: str
    exercises: List[ExerciseLog]

# Modelos para Consultas IA
class ChatQuery(BaseModel):
    message: str

