"""
Pruebas Automatizadas de Integración de Datos y Servicios Multi-Agente — Issue #23
"""

import unittest
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
        profile = self.firestore_conn.get_athlete_profile_for_agent("user123")
        self.assertEqual(profile["user_id"], "user123")
        self.assertIn("Hernia Discal L4-L5", profile["health_conditions"])

    def test_bigquery_analytics_retrieval(self):
        analytics = self.bq_conn.query_athlete_performance_trends("user123")
        self.assertEqual(analytics["athlete_id"], "user123")
        self.assertGreater(analytics["total_volume_lifted_kg"], 0)

    def test_external_services_nutrition_calculator(self):
        nutrition = self.ext_conn.fetch_nutrition_macronutrients("hipertrofia", 80.0)
        self.assertEqual(nutrition["status"], "SUCCESS")
        self.assertGreater(nutrition["calculated_tdee_kcal"], 2000)

if __name__ == "__main__":
    unittest.main()
