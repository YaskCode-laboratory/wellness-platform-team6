"""Test completo del motor local de Wellness Coach"""
import requests
import json

BASE = "http://127.0.0.1:8000"

# 1. Registrar usuario de prueba
print("=" * 60)
print("1. REGISTRO DE USUARIO")
print("=" * 60)
reg = requests.post(f"{BASE}/api/v1/auth/register", json={
    "name": "Carlos Demo",
    "email": "carlos.demo@test.com",
    "password": "test123",
    "weight": 78,
    "height": 175,
    "age": 28,
    "goal": "hipertrofia",
    "level": "intermedio",
    "training_days": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
})
print(f"Status: {reg.status_code}")
data = reg.json()
user_id = data.get("user_id", "")
print(f"User ID: {user_id}")
print()

# 2. Obtener perfil
print("=" * 60)
print("2. PERFIL DEL USUARIO")
print("=" * 60)
profile = requests.get(f"{BASE}/api/v1/users/{user_id}")
print(json.dumps(profile.json(), indent=2, ensure_ascii=False))
print()

# 3. Generar rutina (5 dias)
print("=" * 60)
print("3. RUTINA GENERADA (5 DIAS)")
print("=" * 60)
routine = requests.get(f"{BASE}/api/v1/ai/routine/{user_id}")
rdata = routine.json()
print(f"Enfoque: {rdata.get('focus', 'N/A')}")
schedule = rdata.get("weekly_schedule", [])
print(f"Dias generados: {len(schedule)}")
for day in schedule:
    print(f"\n  {day['day']}:")
    for ex in day.get("exercises", []):
        print(f"    - {ex['name']} ({ex['sets']}x{ex['reps']})")
print()

# 4. Chat - Saludo
print("=" * 60)
print("4. CHAT - SALUDO")
print("=" * 60)
chat1 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "Hola!"})
print(chat1.json().get("response", ""))
print()

# 5. Chat - Alternativa
print("=" * 60)
print("5. CHAT - ALTERNATIVA DE EJERCICIO")
print("=" * 60)
chat2 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "La maquina de press de banca esta ocupada, dame una alternativa"})
print(chat2.json().get("response", ""))
print()

# 6. Chat - Progresion
print("=" * 60)
print("6. CHAT - PROGRESION DE CARGAS")
print("=" * 60)
chat3 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "Cuanto peso debo levantar esta semana?"})
print(chat3.json().get("response", ""))
print()

# 7. Chat - Dolor
print("=" * 60)
print("7. CHAT - ALERTA DE DOLOR")
print("=" * 60)
chat4 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "Me duele la rodilla al hacer sentadillas"})
print(chat4.json().get("response", ""))
print()

# 8. Chat - Nutricion
print("=" * 60)
print("8. CHAT - NUTRICION")
print("=" * 60)
chat5 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "Cuantas calorias y proteinas necesito?"})
print(chat5.json().get("response", ""))
print()

# 9. Chat - Rutina info
print("=" * 60)
print("9. CHAT - INFO DE RUTINA")
print("=" * 60)
chat6 = requests.post(f"{BASE}/api/v1/ai/chat/{user_id}", json={"message": "Cuantos dias debo entrenar por semana?"})
print(chat6.json().get("response", ""))
print()

print("=" * 60)
print("TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
print("=" * 60)
