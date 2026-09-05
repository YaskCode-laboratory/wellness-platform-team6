import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app import database

def test_suite():
    print("=== TEST 1: OBTENCIÓN DE FICHA TÉCNICA DEL ATLETA ===")
    tf = database.get_athlete_technical_file("user123")
    print("Ficha Técnica recuperada correctamente para:", tf["personal_info"]["name"])
    print("  - Total Sesiones:", tf["total_sessions"])
    print("  - Volumen Total:", tf["total_volume_lifted"], "kg")
    print("  - Récords Personales (PRs):", len(tf["personal_records"]))
    assert tf["personal_info"]["name"] == "Juan Pérez"
    assert tf["total_volume_lifted"] > 0

    print("\n=== TEST 2: CAMBIO DE CONTRASEÑA POR EL ADMIN ===")
    updated = database.admin_update_user_full("user123", {
        "name": "Juan Pérez",
        "email": "juan@wellness.com",
        "new_password": "newpassword123",
        "role": "athlete",
        "gym_branch_id": "branch_central",
        "assigned_coach_id": "coach_carlos",
        "goal": "hipertrofia",
        "health_conditions": ["Hernia Discal L4-L5"],
        "training_days": ["Lunes", "Miércoles", "Viernes"]
    })
    print("Contraseña actualizada por Admin:", updated)
    auth_res = database.verify_user_credentials("juan@wellness.com", "newpassword123")
    print("Verificar nueva contraseña de Juan:", auth_res)
    assert auth_res is not None and auth_res.get("user_id") == "user123"

    # Restaurar contraseña original para no afectar pruebas
    database.admin_update_user_full("user123", {
        "name": "Juan Pérez",
        "email": "juan@wellness.com",
        "new_password": "password123",
        "role": "athlete",
        "gym_branch_id": "branch_central",
        "assigned_coach_id": "coach_carlos",
        "goal": "hipertrofia",
        "health_conditions": ["Hernia Discal L4-L5"],
        "training_days": ["Lunes", "Miércoles", "Viernes"]
    })

    print("\n=== TEST 3: CREACIÓN DE NUEVO ADMIN Y COACH DESDE EL PANEL ADMIN ===")
    new_admin_id = database.create_user_credentials("admin.secundario@wellness.com", "admin123", "admin_2")
    database.save_user_profile("admin_2", {
        "role": "admin",
        "gym_branch_id": "branch_central",
        "personal_info": {"name": "Admin Secundario", "age": 32, "gender": "Masculino"}
    })
    print("Nuevo Admin creado:", new_admin_id)
    auth_admin = database.verify_user_credentials("admin.secundario@wellness.com", "admin123")
    assert auth_admin is not None and auth_admin["role"] == "admin"

    print("\n[OK] TODAS LAS PRUEBAS FINALIZARON CON ÉXITO.")

if __name__ == "__main__":
    test_suite()
