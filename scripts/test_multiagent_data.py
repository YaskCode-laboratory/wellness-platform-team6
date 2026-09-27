"""
Script de Prueba de Integración Multi-Agente con Datos y Servicios — Issue #23 (S3-05)
Demuestra el acceso por responsabilidades a Firestore, Analítica de Rendimiento y Servicio Nutricional,
diferenciando explícitamente el modo de ejecución (Local/Mock vs Cloud Real).
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app import database
from app.multiagent_data_connector import (
    FirestoreMultiAgentConnector,
    BigQueryMultiAgentConnector,
    ExternalServicesConnector
)

def run_data_integration_demo():
    use_mock = getattr(database, "use_mock", True)
    mode_label = "MODO LOCAL / MOCK EN MEMORIA" if use_mock else "MODO REAL CLOUD GCP (FIRESTORE / BIGQUERY)"

    print(f"[START] === DEMOSTRACIÓN DE INTEGRACIÓN DE DATOS Y SERVICIOS MULTI-AGENTE ===")
    print(f"[ENTORNO ACTIVO]: {mode_label}\n")

    firestore_conn = FirestoreMultiAgentConnector()
    bq_conn = BigQueryMultiAgentConnector()
    ext_conn = ExternalServicesConnector()

    test_athletes = ["user123", "user456", "non_existent_user"]

    for athlete_id in test_athletes:
        print(f"==================================================")
        print(f"[ATHLETE ID: {athlete_id}] Consulta de Integración de Datos ({mode_label})")
        print(f"--------------------------------------------------")

        # 1. Firestore (Biomechanics & Training Agents)
        profile = firestore_conn.get_athlete_profile_for_agent(athlete_id)
        tech_file = firestore_conn.get_athlete_technical_file_data(athlete_id)
        print(f"[FIRESTORE ({'Mock' if use_mock else 'Real'})] Nombre: {profile.get('name', 'N/A')} | Condición Médica: {profile.get('health_conditions', [])}")
        print(f"[FIRESTORE ({'Mock' if use_mock else 'Real'})] Historial Sesiones: {len(tech_file.get('workout_history', []))} registradas")

        # 2. BigQuery Analytics (Analytics Agent)
        bq_trends = bq_conn.query_athlete_performance_trends(athlete_id)
        print(f"[ANALÍTICA (BigQuery Layer)] Volumen Total Acumulado: {bq_trends.get('total_volume_lifted_kg', 0.0)} kg")
        print(f"[ANALÍTICA (BigQuery Layer)] Adherencia: {bq_trends.get('adherence_rate_pct', 0.0)}%")
        print(f"[ANALÍTICA (BigQuery Layer)] Tendencia Sobrecarga: {bq_trends.get('progressive_overload_trend', 'N/A')}")

        # 3. Servicio de Nutrición (Nutrition Agent)
        goal = profile.get("goal", "hipertrofia")
        weight = profile.get("weight_kg", 70.0)
        nutrition = ext_conn.fetch_nutrition_macronutrients(goal, weight)
        print(f"[SERVICIOS ({nutrition.get('service_source')})] Status: {nutrition.get('status')} | TDEE: {nutrition.get('calculated_tdee_kcal')} kcal | Proteínas: {nutrition.get('macros', {}).get('protein_g')}g")
        print(f"==================================================\n")

if __name__ == "__main__":
    run_data_integration_demo()
