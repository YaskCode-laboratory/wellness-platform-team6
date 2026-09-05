"""
Script de Prueba de Integración Multi-Agente con Datos y Servicios — Issue #23
Demuestra el acceso por responsabilidades a Firestore (Operacional), BigQuery (Analítica) y APIs Externas.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.multiagent_data_connector import (
    FirestoreMultiAgentConnector,
    BigQueryMultiAgentConnector,
    ExternalServicesConnector
)

def run_data_integration_demo():
    print("[START] === DEMOSTRACION DE INTEGRACION DE DATOS Y SERVICIOS MULTI-AGENTE ===\n")
    
    firestore_conn = FirestoreMultiAgentConnector()
    bq_conn = BigQueryMultiAgentConnector()
    ext_conn = ExternalServicesConnector()

    test_athletes = ["user123", "user456"]

    for athlete_id in test_athletes:
        print(f"==================================================")
        print(f"[ATHLETE ID: {athlete_id}] Consulta de Integracion de Datos")
        print(f"--------------------------------------------------")

        # 1. Firestore (Biomechanics & Training Agents)
        profile = firestore_conn.get_athlete_profile_for_agent(athlete_id)
        tech_file = firestore_conn.get_athlete_technical_file_data(athlete_id)
        print(f"[FIRESTORE] Nombre: {profile['name']} | Condición Médica: {profile['health_conditions']}")
        print(f"[FIRESTORE] Historial Sesiones: {len(tech_file.get('workout_history', []))} registradas")

        # 2. BigQuery (Analytics Agent)
        bq_trends = bq_conn.query_athlete_performance_trends(athlete_id)
        print(f"[BIGQUERY] Volumen Total Acumulado: {bq_trends['total_volume_lifted_kg']} kg")
        print(f"[BIGQUERY] Tendencia Sobrecarga: {bq_trends['progressive_overload_trend']}")

        # 3. Servicios Externos (Nutrition Agent)
        nutrition = ext_conn.fetch_nutrition_macronutrients(profile["goal"], profile["weight_kg"])
        print(f"[EXTERNOS] TDEE Calculado: {nutrition['calculated_tdee_kcal']} kcal (Proteínas: {nutrition['macros']['protein_g']}g)")
        print(f"==================================================\n")

if __name__ == "__main__":
    run_data_integration_demo()
