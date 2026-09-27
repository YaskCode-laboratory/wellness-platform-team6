"""
MultiAgent Flow Evaluator & Observability Engine — Wellness Platform Team 6 (Issue #24 - S3-06).
Evalúa el comportamiento, la calidad de respuesta, la latencia, la correcta delegación por el Supervisor
y la colaboración inter-agente con trazabilidad estructurada de extremo a extremo.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.orchestrator import OrchestratorAgent, AgentIntent, _orchestrator_instance
    from app.wellness_agent.communication import DelegationTracer, global_tracer
except ModuleNotFoundError:
    try:
        from orchestrator import OrchestratorAgent, AgentIntent, _orchestrator_instance
        from wellness_agent.communication import DelegationTracer, global_tracer
    except ModuleNotFoundError:
        from .orchestrator import OrchestratorAgent, AgentIntent, _orchestrator_instance
        from .wellness_agent.communication import DelegationTracer, global_tracer

logger = logging.getLogger(__name__)


@dataclass
class MultiAgentTestCase:
    id: str
    name: str
    user_id: str
    prompt: str
    expected_intent: str
    expected_primary_agent: str
    requires_collaboration: bool
    expected_collaborators: List[str] = field(default_factory=list)
    quality_criteria: List[str] = field(default_factory=list)


@dataclass
class MultiAgentEvaluationResult:
    case_id: str
    name: str
    prompt: str
    user_id: str
    expected_intent: str
    detected_intent: str
    intent_matched: bool
    expected_agent: str
    actual_agent: str
    delegation_success: bool
    requires_collaboration: bool
    collaboration_success: bool
    collaborators_involved: List[str]
    latency_ms: float
    trace_id: str
    response_content: str
    quality_score_pct: float
    quality_breakdown: Dict[str, bool]
    status: str


class MultiAgentFlowEvaluator:
    """
    Motor de Evaluación y Observabilidad del Sistema Multiagente.
    Ejecuta casos de prueba reproducibles, audita delegaciones y mide la colaboración y rendimiento.
    """

    def __init__(self, orchestrator: Optional[OrchestratorAgent] = None, tracer: Optional[DelegationTracer] = None):
        self.orchestrator = orchestrator or _orchestrator_instance
        self.tracer = tracer or global_tracer
        self.test_cases: List[MultiAgentTestCase] = self._build_benchmark_test_cases()

    def _build_benchmark_test_cases(self) -> List[MultiAgentTestCase]:
        """Define la batería representativa y reproducible de casos de prueba multiagente."""
        return [
            MultiAgentTestCase(
                id="TC-MA-01",
                name="Delegación Directa a Wellness Coach (Biomecánica y Rutina)",
                user_id="athlete_01",
                prompt="¿Qué rutina me recomiendas para hipertrofia de pecho y espalda?",
                expected_intent=AgentIntent.WORKOUT_BIOMECHANICS.value,
                expected_primary_agent="WellnessCoachAgent2.0",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["rutina", "pecho", "espalda", "repeticiones"]
            ),
            MultiAgentTestCase(
                id="TC-MA-02",
                name="Delegación Directa a Nutrition Agent (Cálculo de Macros y TDEE)",
                user_id="athlete_02",
                prompt="Calcula mis calorías y macronutrientes para mi dieta de volumen",
                expected_intent=AgentIntent.NUTRITION.value,
                expected_primary_agent="NutritionAgent",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["tdee", "calorías", "proteínas", "carbohidratos", "grasas"]
            ),
            MultiAgentTestCase(
                id="TC-MA-03",
                name="Delegación Directa a Motivation Agent (Refuerzo Psicológico y Hábitos)",
                user_id="athlete_03",
                prompt="Hoy me siento muy desanimado y con flojera para entrenar",
                expected_intent=AgentIntent.MOTIVATION.value,
                expected_primary_agent="MotivationAgent",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["disciplina", "constancia", "ánimo", "sesiones"]
            ),
            MultiAgentTestCase(
                id="TC-MA-04",
                name="Delegación Directa a Analytics Agent (Métricas y Progreso)",
                user_id="athlete_04",
                prompt="Muestra mi progreso, volumen total acumulado y récord de sesiones",
                expected_intent=AgentIntent.ANALYTICS.value,
                expected_primary_agent="AnalyticsAgent",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["volumen", "sesiones", "progreso", "kg"]
            ),
            MultiAgentTestCase(
                id="TC-MA-05",
                name="Colaboración Inter-Agente Multidominio (Entrenamiento + Nutrición)",
                user_id="athlete_05",
                prompt="Diseña mi rutina de ejercicios de pierna y calcula mis calorías y macronutrientes",
                expected_intent=AgentIntent.MULTIDOMAIN.value,
                expected_primary_agent="OrchestratorAgent (Multidomain)",
                requires_collaboration=True,
                expected_collaborators=["WellnessCoachAgent2.0", "NutritionAgent"],
                quality_criteria=["rutina", "pierna", "tdee", "caloría", "proteína"]
            ),
            MultiAgentTestCase(
                id="TC-MA-06",
                name="Guardrails de Seguridad y Sustitución Biomecánica (Lesión Lumbar)",
                user_id="athlete_06",
                prompt="Tengo una hernia discal lumbar y me duele la espalda baja al hacer sentadilla libre",
                expected_intent=AgentIntent.WORKOUT_BIOMECHANICS.value,
                expected_primary_agent="WellnessCoachAgent2.0",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["contraindic", "alternativa", "prensa", "seguridad"]
            ),
            MultiAgentTestCase(
                id="TC-MA-07",
                name="Manejo de Fallback y Datos Faltantes (Atleta sin Perfil Antropométrico)",
                user_id="unknown_athlete_07",
                prompt="Calcula mis macronutrientes y calorías diarias",
                expected_intent=AgentIntent.NUTRITION.value,
                expected_primary_agent="NutritionAgent",
                requires_collaboration=False,
                expected_collaborators=[],
                quality_criteria=["perfil", "peso", "altura"]
            )
        ]

    def evaluate_test_case(self, test_case: MultiAgentTestCase) -> MultiAgentEvaluationResult:
        """Ejecuta un caso de prueba individual y evalúa intención, delegación, latencia y calidad."""
        start_time = time.perf_counter()
        
        # Ejecución del flujo por el Supervisor Orchestrator
        orch_result = self.orchestrator.process_user_request(test_case.user_id, test_case.prompt)
        total_latency_ms = (time.perf_counter() - start_time) * 1000

        detected_intent = orch_result.get("intent", "")
        intent_matched = (detected_intent == test_case.expected_intent)

        actual_agent = orch_result.get("delegated_agent", "")
        delegation_success = (actual_agent == test_case.expected_primary_agent)

        response_text = orch_result.get("response", "")
        trace_id = orch_result.get("trace_id", "")
        metadata = orch_result.get("metadata", {})

        # Validación de colaboración inter-agente
        collaborators_involved = []
        if test_case.requires_collaboration:
            collaborators_involved = metadata.get("delegated_agents", [])
            collaboration_success = all(collab in collaborators_involved for collab in test_case.expected_collaborators)
        else:
            collaboration_success = True
            collaborators_involved = [actual_agent]

        # Evaluación de calidad por criterios
        quality_breakdown = {}
        criteria_hits = 0
        resp_lower = response_text.lower()
        for criterion in test_case.quality_criteria:
            matched = criterion.lower() in resp_lower
            quality_breakdown[criterion] = matched
            if matched:
                criteria_hits += 1

        quality_score_pct = (criteria_hits / len(test_case.quality_criteria) * 100.0) if test_case.quality_criteria else 100.0

        return MultiAgentEvaluationResult(
            case_id=test_case.id,
            name=test_case.name,
            prompt=test_case.prompt,
            user_id=test_case.user_id,
            expected_intent=test_case.expected_intent,
            detected_intent=detected_intent,
            intent_matched=intent_matched,
            expected_agent=test_case.expected_primary_agent,
            actual_agent=actual_agent,
            delegation_success=delegation_success,
            requires_collaboration=test_case.requires_collaboration,
            collaboration_success=collaboration_success,
            collaborators_involved=collaborators_involved,
            latency_ms=round(total_latency_ms, 2),
            trace_id=trace_id,
            response_content=response_text,
            quality_score_pct=round(quality_score_pct, 1),
            quality_breakdown=quality_breakdown,
            status=orch_result.get("status", "success")
        )

    def run_suite(self) -> Dict[str, Any]:
        """Ejecuta la suite completa de evaluación de flujo multiagente."""
        results: List[MultiAgentEvaluationResult] = []
        
        for case in self.test_cases:
            res = self.evaluate_test_case(case)
            results.append(res)

        total_cases = len(results)
        intent_matches = sum(1 for r in results if r.intent_matched)
        delegation_successes = sum(1 for r in results if r.delegation_success)
        
        # El porcentaje de éxito en colaboración debe calcularse ÚNICAMENTE sobre los casos donde requires_collaboration == True
        collab_cases = [r for r in results if r.requires_collaboration]
        if collab_cases:
            collab_successes = sum(1 for r in collab_cases if r.collaboration_success)
            collaboration_pct = round((collab_successes / len(collab_cases)) * 100.0, 1)
        else:
            collaboration_pct = 100.0

        avg_latency = sum(r.latency_ms for r in results) / total_cases if total_cases > 0 else 0.0
        avg_quality = sum(r.quality_score_pct for r in results) / total_cases if total_cases > 0 else 0.0

        suite_summary = {
            "total_test_cases": total_cases,
            "intent_accuracy_pct": round((intent_matches / total_cases) * 100.0, 1),
            "delegation_accuracy_pct": round((delegation_successes / total_cases) * 100.0, 1),
            "collaboration_success_pct": collaboration_pct,
            "average_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(min(r.latency_ms for r in results), 2) if results else 0,
            "max_latency_ms": round(max(r.latency_ms for r in results), 2) if results else 0,
            "overall_quality_score_pct": round(avg_quality, 1),
            "results": [asdict(r) for r in results],
            "limitations_identified": [
                "La delegación multidominio actual ejecuta agentes concurrentes de forma secuencial en memoria.",
                "El paso de contexto profundo entre agentes está acoplado al formato del Supervisor en lugar de un canal de eventos distribuido (Pub/Sub).",
                "Las consultas nutricionales dependen de la existencia previa del perfil del usuario en Firestore/MockDB."
            ],
            "proposed_improvements": [
                "Implementar ejecución asíncrona paralela (asyncio.gather) para solicitudes multidominio.",
                "Evolución hacia protocolo Model Context Protocol (MCP) para estandarizar contratos de herramientas e interoperabilidad A2A.",
                "Incorporar fallback conversacional interactivo cuando falten datos antropométricos del atleta."
            ]
        }

        return suite_summary


if __name__ == "__main__":
    evaluator = MultiAgentFlowEvaluator()
    summary = evaluator.run_suite()
    print(f"Evaluación Multiagente completada:")
    print(f"- Precisión de Intención: {summary['intent_accuracy_pct']}%")
    print(f"- Precisión de Delegación: {summary['delegation_accuracy_pct']}%")
    print(f"- Éxito de Colaboración: {summary['collaboration_success_pct']}%")
    print(f"- Latencia Promedio: {summary['average_latency_ms']} ms")
    print(f"- Calidad General: {summary['overall_quality_score_pct']}%")
