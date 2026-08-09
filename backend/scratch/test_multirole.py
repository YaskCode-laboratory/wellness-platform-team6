from app import database, agent

def test_multirole_system():
    print("=== TEST 1: AUTENTICACIÓN Y ROLES ===")
    admin_login = database.verify_user_credentials("admin@wellnessgym.com", "admin123")
    coach_login = database.verify_user_credentials("coach.carlos@wellnessgym.com", "coach123")
    athlete_login = database.verify_user_credentials("juan@wellness.com", "password123")

    print("Admin login:", admin_login)
    print("Coach login:", coach_login)
    print("Athlete login:", athlete_login)
    assert admin_login["role"] == "admin"
    assert coach_login["role"] == "coach"
    assert athlete_login["role"] == "athlete"

    print("\n=== TEST 2: ATLETAS Y CONDICIONES DE SALUD DE COACH ===")
    athletes = database.get_athletes_for_coach("coach_carlos")
    print(f"Atletas a cargo de Coach Carlos ({len(athletes)}):")
    for a in athletes:
        name = a["personal_info"]["name"]
        health = a["fitness_profile"].get("health_conditions", [])
        print(f"  - {name} | Salud: {health}")

    print("\n=== TEST 3: SOLICITUD DE RUTINA Y APROBACIÓN POR COACH ===")
    req_data = {
        "requested_days": ["Lunes", "Martes", "Jueves", "Viernes"],
        "requested_goal": "fuerza",
        "notes": "Necesito 4 días adaptados a mi hernia discal."
    }
    new_req = database.create_routine_request("user123", req_data)
    print("Solicitud creada por Juan:", new_req["id"], "Estado:", new_req["status"])

    pending = database.get_pending_requests_for_coach("coach_carlos")
    print(f"Solicitudes pendientes para Coach Carlos: {len(pending)}")
    assert len(pending) > 0

    # Coach aprueba la solicitud
    processed = database.process_routine_request(new_req["id"], "approve", "Aprobado por Coach Carlos. Rutina adaptada con protección lumbar.")
    print("Solicitud procesada:", processed["id"], "Nuevo Estado:", processed["status"])

    print("\n=== TEST 4: GENERACIÓN DE RUTINA CON IA CON FILTRO MÉDICO ===")
    routine = agent.generate_weekly_routine("user123")
    print("Enfoque de la rutina:", routine.get("focus"))
    print("Días de entrenamiento:", len(routine.get("weekly_schedule", [])))
    assert len(routine.get("weekly_schedule", [])) == 4

    print("\n=== TEST 5: REASIGNACIÓN DE ATLETA (ADMIN) ===")
    reassigned = database.reassign_athlete("user123", "coach_maria")
    print("Reasignación de Juan a Coach María:", reassigned)
    carlos_athletes = database.get_athletes_for_coach("coach_carlos")
    maria_athletes = database.get_athletes_for_coach("coach_maria")
    print(f"Atletas de Coach Carlos: {len(carlos_athletes)} | Atletas de Coach María: {len(maria_athletes)}")
    assert any(a["user_id"] == "user123" for a in maria_athletes)

    print("\n✅ TODAS LAS PRUEBAS BACKEND MULTI-ROL PASARON CON ÉXITO.")

if __name__ == "__main__":
    test_multirole_system()
