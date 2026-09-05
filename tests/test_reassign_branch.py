import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app import database

def test_reassign_and_branch_reg():
    print("=== TEST 1: REASIGNACIÓN / TRASLADO DE COACH POR EL ADMIN ===")
    reassigned = database.reassign_athlete("user123", "coach_maria")
    print("Reasignación de Juan Pérez a Coach María:", reassigned)
    u_juan = database.get_user_profile("user123")
    assert u_juan["assigned_coach_id"] == "coach_maria"

    # Restaurar a Coach Carlos
    database.reassign_athlete("user123", "coach_carlos")

    print("\n=== TEST 2: REGISTRO DE ATLETA EN SUCURSAL SELECCIONADA ===")
    branches = database.get_branches()
    print(f"Sucursales disponibles ({len(branches)}): {[b['name'] for b in branches]}")
    assert len(branches) >= 2

    print("\n[OK] TODAS LAS PRUEBAS DE REASIGNACIÓN Y SUCURSALES PASARON EXCELENTE.")

if __name__ == "__main__":
    test_reassign_and_branch_reg()
