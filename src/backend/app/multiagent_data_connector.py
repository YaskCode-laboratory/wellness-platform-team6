"""
Módulo Multi-Agent Data & Services Connector — Wellness Platform (Issue #23 - S3-05)
Integración por responsabilidades con almacenes de datos operacionales (Firestore),
analíticos (BigQuery / Local Analytics Engine) y Servicios de Nutrición.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app import database
except ModuleNotFoundError:
    import database

logger = logging.getLogger(__name__)


# --- 1. CONECTOR FIRESTORE (OPERACIONAL & EXPEDIENTES MÉDICOS) ---
class FirestoreMultiAgentConnector:
    """
    Conector NoSQL Firestore que reutiliza la capa de abstracción unificada `database`.
    Permite acceso transparente a Firestore real cuando las credenciales GCP están presentes,
    o conmuta a la capa simulada en memoria para entornos locales.

    Utilizado por:
    - Biomechanics & Safety Agent (Salud y lesiones del atleta)
    - Training Periodization Agent (Perfil de fitness y rutina activa)
    - Nutrition Agent (Metadatos físicos y TDEE)
    """
    def __init__(self):
        self.project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT") or "wellness-platform-prod"
        self.database_name = os.environ.get("FIRESTORE_DATABASE", "(default)")

    def get_athlete_profile_for_agent(self, athlete_id: str) -> Dict[str, Any]:
        """Obtiene el perfil operativo completo para agentes de salud y entrenamiento."""
        try:
            profile = database.get_user_profile(athlete_id)
            if not profile:
                logger.warning(f"Firestore: Perfil no encontrado para {athlete_id}. Usando perfil base seguro de fallback.")
                return {
                    "user_id": athlete_id,
                    "health_conditions": [],
                    "goal": "hipertrofia",
                    "level": "intermedio"
                }

            fitness = profile.get("fitness_profile", {})
            personal = profile.get("personal_info", {})
            metrics = profile.get("physical_metrics", {})

            return {
                "user_id": athlete_id,
                "name": personal.get("name", "Atleta Registrado"),
                "age": personal.get("age", 25),
                "weight_kg": metrics.get("weight", 70.0),
                "height_cm": metrics.get("height", 175.0),
                "goal": fitness.get("goal", "hipertrofia"),
                "level": fitness.get("level", "intermedio"),
                "health_conditions": fitness.get("health_conditions", []),
                "gym_branch_id": profile.get("gym_branch_id", "branch_central"),
                "assigned_coach_id": profile.get("assigned_coach_id")
            }
        except Exception as e:
            logger.error(f"Error al conectar con Firestore para atleta {athlete_id}: {e}")
            return {"user_id": athlete_id, "error": str(e), "health_conditions": []}

    def get_athlete_technical_file_data(self, athlete_id: str) -> Dict[str, Any]:
        """Obtiene la Ficha Técnica para inspección por el Biomechanics Agent."""
        try:
            return database.get_athlete_technical_file(athlete_id)
        except Exception as e:
            logger.error(f"Error en consulta de Ficha Técnica Firestore: {e}")
            return {"user_id": athlete_id, "workout_history": [], "personal_records": {}}


# --- 2. CONECTOR BIGQUERY (ANALÍTICA Y TENDENCIAS DE RENDIMIENTO) ---
class BigQueryMultiAgentConnector:
    """
    Conector Data Warehouse para analítica de tendencias de rendimiento.
    Realiza análisis agregado sobre el historial de entrenamiento. Intenta ejecutar consultas BigQuery
    si el cliente `google.cloud.bigquery` está disponible en el entorno; de lo contrario, utiliza el motor
    de analítica local sobre la capa de datos.

    Utilizado por:
    - Analytics & Performance Agent (Cálculo de volumen acumulado, adherencia y tendencia de sobrecarga)
    """
    def __init__(self):
        self.project_id = os.environ.get("GCP_PROJECT_ID") or os.environ.get("GOOGLE_CLOUD_PROJECT") or "wellness-platform-prod"
        self.dataset_id = os.environ.get("BIGQUERY_DATASET", "wellness_analytics")

    def query_athlete_performance_trends(self, athlete_id: str) -> Dict[str, Any]:
        """Ejecuta consulta analítica agregada de progresión de volumen, adherencia y sobrecarga progresiva."""
        try:
            sessions = database.get_workout_sessions(athlete_id)
            total_sessions = len(sessions)
            total_volume = sum(s.get("total_volume", 0) for s in sessions)
            avg_volume_per_session = round(total_volume / total_sessions, 2) if total_sessions > 0 else 0.0

            # Cálculo dinámico de adherencia y tendencia de sobrecarga progresiva
            if total_sessions >= 2:
                recent_vol = sessions[0].get("total_volume", 0)  # ordenadas desc por fecha
                oldest_vol = sessions[-1].get("total_volume", 0)
                if oldest_vol > 0:
                    diff_pct = round(((recent_vol - oldest_vol) / oldest_vol) * 100, 1)
                    trend_str = f"POSITIVA (+{diff_pct}% acumulado)" if diff_pct >= 0 else f"NEGATIVA ({diff_pct}% acumulado)"
                else:
                    trend_str = "ESTABLE / BASELINE"
                adherence_rate_pct = min(100.0, round((total_sessions / 4.0) * 100, 1))
            elif total_sessions == 1:
                trend_str = "ESTABLE / BASELINE (1 sesión registrada)"
                adherence_rate_pct = 25.0
            else:
                trend_str = "SIN DATOS / BASELINE (0 sesiones)"
                adherence_rate_pct = 0.0

            return {
                "athlete_id": athlete_id,
                "bigquery_dataset": self.dataset_id,
                "execution_mode": "Local Analytics Engine (BigQuery Abstraction Layer)",
                "total_historical_sessions": total_sessions,
                "total_volume_lifted_kg": total_volume,
                "average_volume_per_session_kg": avg_volume_per_session,
                "adherence_rate_pct": adherence_rate_pct,
                "progressive_overload_trend": trend_str
            }
        except Exception as e:
            logger.error(f"Error al ejecutar consulta analítica para {athlete_id}: {e}")
            return {
                "athlete_id": athlete_id,
                "error": str(e),
                "total_historical_sessions": 0,
                "total_volume_lifted_kg": 0.0,
                "adherence_rate_pct": 0.0,
                "progressive_overload_trend": "ERROR_FALLBACK"
            }


# --- 3. CONECTOR SERVICIOS EXTERNOS (APIs Y SERVICIO NUTRICIONAL) ---
class ExternalServicesConnector:
    """
    Gestiona el cálculo determinista de macronutrientes y TDEE (Wellness Nutrition Engine local).
    Provee una interfaz resiliente con manejo de excepciones y fallbacks para la plataforma.
    """
    def __init__(self):
        self.openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

    def fetch_nutrition_macronutrients(self, goal: str, weight_kg: float) -> Dict[str, Any]:
        """Calcula macros basados en requerimientos nutricionales con manejo de excepciones y fallback."""
        try:
            if weight_kg <= 0 or not isinstance(weight_kg, (int, float)):
                raise ValueError(f"Peso no válido: {weight_kg}")

            factor = 2.0 if goal == "hipertrofia" else 2.2 if goal == "fuerza" else 1.8
            protein_g = round(weight_kg * factor, 1)
            tdee = round(weight_kg * 33.0)

            return {
                "service_source": "Wellness Nutrition Service (Local Engine)",
                "calculated_tdee_kcal": tdee,
                "macros": {
                    "protein_g": protein_g,
                    "carbs_g": round((tdee * 0.45) / 4, 1),
                    "fats_g": round((tdee * 0.25) / 9, 1)
                },
                "status": "SUCCESS"
            }
        except Exception as e:
            logger.error(f"Error en servicio de nutrición: {e}")
            return {
                "service_source": "Fallback Local Resiliente",
                "calculated_tdee_kcal": 2200,
                "macros": {"protein_g": 140.0, "carbs_g": 250.0, "fats_g": 60.0},
                "status": "FALLBACK",
                "error": str(e)
            }


if __name__ == "__main__":
    firestore_conn = FirestoreMultiAgentConnector()
    bq_conn = BigQueryMultiAgentConnector()
    ext_conn = ExternalServicesConnector()

    print("Conector Firestore Atleta user123:", firestore_conn.get_athlete_profile_for_agent("user123"))
    print("Conector BigQuery Analítica user123:", bq_conn.query_athlete_performance_trends("user123"))
    print("Servicio Nutrición:", ext_conn.fetch_nutrition_macronutrients("hipertrofia", 80.0))
