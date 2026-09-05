import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app import database

def test_logger_and_coach_edit():
    print("=== TEST 1: REGISTRO DE ENTRENAMIENTO EN VIVO DESDE MODO GIMNASIO ===")
    session_data = {
        "date": "2026-08-05T19:00:00Z",
        "exercises": [
            {
                "exercise_id": "bench_press",
                "exercise_name": "Press de Banca Plano con Barra",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight": 70.0, "completed": True},
                    {"set_number": 2, "reps": 10, "weight": 75.0, "completed": True}
                ]
            }
        ]
    }
    saved = database.save_workout_session("user123", session_data)
    print("Sesión guardada exitosamente:", saved)
    sessions = database.get_workout_sessions("user123")
    latest = sessions[0]
    assert latest["total_volume"] == (70.0 * 10) + (75.0 * 10)

    print("\n=== TEST 2: EDICIÓN DE RUTINA POR EL COACH ===")
    custom_routine = {
        "focus": "Hipertrofia Personalizada por Coach Carlos",
        "weekly_schedule": [
            {
                "day": "Lunes (Empuje Específico del Coach)",
                "exercises": [
                    {"name": "Press de Banca Plano", "sets": 4, "reps": "6-8"},
                    {"name": "Press Inclinado con Mancuernas", "sets": 4, "reps": "8-10"}
                ]
            }
        ]
    }
    saved_r = database.save_ai_routine("user123", custom_routine)
    print("Rutina guardada por coach:", saved_r)
    check_r = database.get_ai_routine("user123")
    assert check_r["focus"] == "Hipertrofia Personalizada por Coach Carlos"

    print("\n=== TEST 3: EDICIÓN DE USUARIO POR EL ADMIN ===")
    updated_user = database.admin_update_user_full("user456", {
        "name": "Ana Gómez Modificada",
        "email": "ana.gomez@wellness.com",
        "role": "athlete",
        "gym_branch_id": "branch_norte",
        "assigned_coach_id": "coach_maria",
        "goal": "fuerza",
        "health_conditions": ["Lesión de Rodilla (Menisco)"],
        "training_days": ["Lunes", "Miércoles", "Viernes"]
      })
    print("Edición por Admin exitosa:", updated_user)
    u_data = database.get_user_profile("user456")
    assert u_data["personal_info"]["name"] == "Ana Gómez Modificada"

    print("\n[OK] TODAS LAS PRUEBAS BACKEND PASARON CON ÉXITO.")

if __name__ == "__main__":
    test_logger_and_coach_edit()
