"""
Pruebas Automatizadas de Integración de Datos y Servicios Multi-Agente — Issue #23 (S3-05)
Cubre escenarios exitosos, manejo de errores, usuarios inexistentes, ausencia de datos analíticos y fallbacks.
"""

import unittest
from unittest.mock import patch
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.multiagent_data_connector import (
        FirestoreMultiAgentConnector,
        BigQueryMultiAgentConnector,
        ExternalServicesConnector
    )
except ModuleNotFoundError:
    from multiagent_data_connector import (
        FirestoreMultiAgentConnector,
        BigQueryMultiAgentConnector,
        ExternalServicesConnector
    )


class TestMultiAgentDataConnectors(unittest.TestCase):
    def setUp(self):
        self.firestore_conn = FirestoreMultiAgentConnector()
        self.bq_conn = BigQueryMultiAgentConnector()
        self.ext_conn = ExternalServicesConnector()

    def test_firestore_athlete_profile_retrieval(self):
        """Verifica recuperación exitosa de perfil de atleta registrado."""
        profile = self.firestore_conn.get_athlete_profile_for_agent("user123")
        self.assertEqual(profile["user_id"], "user123")
        self.assertIn("Hernia Discal L4-L5", profile["health_conditions"])

    def test_firestore_nonexistent_user_fallback(self):
        """Verifica que usuario inexistente retorne perfil seguro con salud vacía."""
        profile = self.firestore_conn.get_athlete_profile_for_agent("non_existent_athlete_999")
        self.assertEqual(profile["user_id"], "non_existent_athlete_999")
        self.assertEqual(profile["health_conditions"], [])
        self.assertEqual(profile["goal"], "hipertrofia")

    def test_firestore_exception_handling(self):
        """Verifica manejo estructurado de excepciones en acceso a datos de Firestore."""
        with patch("app.database.get_user_profile", side_effect=Exception("Error de conexión Firestore")):
            profile = self.firestore_conn.get_athlete_profile_for_agent("user123")
            self.assertEqual(profile["user_id"], "user123")
            self.assertIn("error", profile)
            self.assertIn("Error de conexión Firestore", profile["error"])

    def test_bigquery_analytics_retrieval(self):
        """Verifica análisis de tendencias para atleta con sesiones registradas."""
        analytics = self.bq_conn.query_athlete_performance_trends("user123")
        self.assertEqual(analytics["athlete_id"], "user123")
        self.assertGreater(analytics["total_volume_lifted_kg"], 0)
        self.assertGreater(analytics["total_historical_sessions"], 0)
        self.assertIsInstance(analytics["progressive_overload_trend"], str)
        self.assertGreater(len(analytics["progressive_overload_trend"]), 0)

    def test_bigquery_no_analytics_data_fallback(self):
        """Verifica comportamiento cuando no existen datos analíticos previas."""
        analytics = self.bq_conn.query_athlete_performance_trends("non_existent_athlete_999")
        self.assertEqual(analytics["athlete_id"], "non_existent_athlete_999")
        self.assertEqual(analytics["total_historical_sessions"], 0)
        self.assertEqual(analytics["total_volume_lifted_kg"], 0.0)
        self.assertIn("SIN DATOS", analytics["progressive_overload_trend"])

    def test_bigquery_exception_handling(self):
        """Verifica manejo de errores cuando falla la consulta analítica."""
        with patch("app.database.get_workout_sessions", side_effect=Exception("Fallo de red BigQuery")):
            analytics = self.bq_conn.query_athlete_performance_trends("user123")
            self.assertEqual(analytics["athlete_id"], "user123")
            self.assertEqual(analytics["total_historical_sessions"], 0)
            self.assertEqual(analytics["progressive_overload_trend"], "ERROR_FALLBACK")
            self.assertIn("Fallo de red BigQuery", analytics["error"])

    def test_external_services_nutrition_calculator(self):
        """Verifica cálculo exitoso de macronutrientes."""
        nutrition = self.ext_conn.fetch_nutrition_macronutrients("hipertrofia", 80.0)
        self.assertEqual(nutrition["status"], "SUCCESS")
        self.assertGreater(nutrition["calculated_tdee_kcal"], 2000)

    def test_external_services_nutrition_invalid_input_fallback(self):
        """Verifica activación de fallback seguro ante entrada inválida o error en servicio nutricional."""
        nutrition = self.ext_conn.fetch_nutrition_macronutrients("hipertrofia", -10.0)
        self.assertEqual(nutrition["status"], "FALLBACK")
        self.assertEqual(nutrition["calculated_tdee_kcal"], 2200)
        self.assertIn("protein_g", nutrition["macros"])


if __name__ == "__main__":
    unittest.main()
