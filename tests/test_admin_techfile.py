import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app import database

def test_admin_and_techfile():
    print("=== TEST 1: DIRECTORIO GLOBAL DE USUARIOS (ADMIN) ===")
    users = database.get_all_users_admin()
    print(f"Total usuarios en directorio: {len(users)}")
    for u in users:
        print(f"  - {u['name']} | Rol: {u['role']} | Sucursal: {u['gym_branch_name']} | Activo: {u['is_active']} | Coach: {u['assigned_coach_name']}")
    assert len(users) >= 4

    print("\n=== TEST 2: ACTIVAR / INACTIVAR USUARIO ===")
    toggled = database.toggle_user_status("user456", False)
    print("Inactivar Ana Gómez:", toggled)
    user_ana = database.get_user_profile("user456")
    assert user_ana.get("is_active") == False

    # Restaurar
    database.toggle_user_status("user456", True)

    print("\n=== TEST 3: TRASLADAR ENTRENADOR O ATLETA DE SUCURSAL ===")
    moved = database.update_user_branch("coach_carlos", "branch_norte")
    print("Trasladar Coach Carlos a Sucursal Norte:", moved)
    updated_carlos = database.get_user_profile("coach_carlos")
    assert updated_carlos.get("gym_branch_id") == "branch_norte"

    print("\n=== TEST 4: FICHA TÉCNICA COMPLETA DEL ATLETA (DÍA POR DÍA) ===")
    tech_file = database.get_athlete_technical_file("user123")
    print("Ficha Técnica Atleta:", tech_file["personal_info"]["name"])
    print("Récords Personales (PRs):", tech_file["personal_records"])
    print("Total Volumen Levantado:", tech_file["total_volume_lifted"], "kg")
    print(f"Sesiones día a día ({len(tech_file['workout_history'])}):")
    for s in tech_file["workout_history"]:
        day = s.get("day_name", "Día")
        date = s.get("date", "")[:10]
        exs = [e["exercise_name"] for e in s.get("exercises", [])]
        print(f"  - [{date}] {day}: {', '.join(exs)}")
    assert len(tech_file["workout_history"]) >= 3

    print("\n[OK] TODAS LAS PRUEBAS BACKEND DE ADMIN Y FICHA TÉCNICA PASARON EXITOSAMENTE.")

if __name__ == "__main__":
    test_admin_and_techfile()
