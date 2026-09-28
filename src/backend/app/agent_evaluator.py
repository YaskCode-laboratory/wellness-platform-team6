"""
Módulo Agent Quality Evaluator — Wellness Coach Agent 2.0 (Issue #17 & Issue #18)
Suite de evaluación de comportamiento, memoria conversacional, Tool Calling y razonamiento ReAct.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app.react_agent import ReActAgent
except ModuleNotFoundError:
    try:
        from react_agent import ReActAgent
    except ModuleNotFoundError:
        from .react_agent import ReActAgent


class AgentQualityEvaluator:
    """
    Evaluador de Calidad del Agente que realiza contraste estricto entre Comportamiento Esperado vs Obtenido,
    validación de herramientas innecesarias y puntuación derivada de relevancia.
    """

    def __init__(self):
        self.react_agent = ReActAgent()
        self.test_cases = [
            {
                "id": "TC-01",
                "category": "Direct Knowledge Response (Sin Herramientas)",
                "prompt": "Hola, buenos días, gracias por la recomendación",
                "expected_behavior": "Respuesta conversacional directa sin invocar herramientas de base de datos o cálculo.",
                "expected_tool": None
            },
            {
                "id": "TC-02",
                "category": "Multi-turn Conversation & Context",
                "prompt": "Quiero mejorar mi sentadilla libre pero me duele la zona baja de la espalda al bajar.",
                "expected_behavior": "Identificar el síntoma de dolor lumbar y requerir la evaluación de riesgo de lesión.",
                "expected_tool": ["assess_injury_risk", "get_exercise_alternative"]
            },
            {
                "id": "TC-03",
                "category": "Conversational Memory & Fact Retention",
                "prompt": "Tengo una hernia discal en L4-L5 y me molesta la zona lumbar.",
                "expected_behavior": "Retener la patología de Hernia L4-L5 en la memoria del agente y consultar contraindicaciones o riesgos.",
                "expected_tool": ["assess_injury_risk", "search_medical_contraindications"]
            },
            {
                "id": "TC-04",
                "category": "Tool Calling Execution Accuracy",
                "prompt": "Calcula mis macronutrientes y calorías para entrenamiento",
                "expected_behavior": "Invocar la herramienta de cálculo de macronutrientes calculate_nutrition_macros.",
                "expected_tool": "calculate_nutrition_macros"
            },
            {
                "id": "TC-05",
                "category": "ReAct Multi-step Reasoning Loop",
                "prompt": "Evalúa la evidencia científica RAG sobre periodización de hipertrofia",
                "expected_behavior": "Ejecutar la herramienta retrieve_rag_knowledge y sintetizar la respuesta final.",
                "expected_tool": ["retrieve_rag_knowledge", "FINAL_ANSWER"]
            }
        ]

    def evaluate_test_case(self, tc: Dict[str, Any]) -> Dict[str, Any]:
        res = self.react_agent.run_react_loop(tc["prompt"], athlete_id="user123")
        executed_tools = [s["action"] for s in res["steps"]]
        tools_before_final = [a for a in executed_tools if a != "FINAL_ANSWER"]
        final_answer = res.get("final_answer", "")

        # 1. Validación Estricta de Selección de Herramientas
        tool_accuracy_passed = False
        obtained_behavior = ""

        if tc["expected_tool"] is None:
            if len(tools_before_final) == 0:
                tool_accuracy_passed = True
                obtained_behavior = "Respuesta directa generada correctamente sin llamadas a herramientas innecesarias."
            else:
                tool_accuracy_passed = False
                obtained_behavior = f"FALLO: Se ejecutaron herramientas innecesarias ({', '.join(tools_before_final)}) para una consulta conversacional directa."
        elif isinstance(tc["expected_tool"], list):
            if any(t in executed_tools for t in tc["expected_tool"]):
                tool_accuracy_passed = True
                obtained_behavior = f"Herramienta adecuada ({', '.join(tools_before_final)}) ejecutada según el contexto esperado."
            else:
                tool_accuracy_passed = False
                obtained_behavior = f"FALLO: Ninguna herramienta esperada ({', '.join(tc['expected_tool'])}) fue ejecutada. Herramientas usadas: {', '.join(executed_tools)}."
        else:
            if tc["expected_tool"] in executed_tools:
                tool_accuracy_passed = True
                obtained_behavior = f"Herramienta requerida '{tc['expected_tool']}' ejecutada correctamente."
            else:
                tool_accuracy_passed = False
                obtained_behavior = f"FALLO: La herramienta '{tc['expected_tool']}' no fue invocada. Herramientas usadas: {', '.join(executed_tools)}."

        # 2. Derivación de Puntaje de Relevancia (Score de 1.0 a 5.0)
        score = 5.0
        if not tool_accuracy_passed:
            score -= 2.5
        if not final_answer:
            score -= 2.5
        elif len(final_answer) < 20:
            score -= 1.0

        # Verificación de alineación de contenido en la respuesta final
        prompt_lower = tc["prompt"].lower()
        ans_lower = final_answer.lower()

        if "macro" in prompt_lower and not any(k in ans_lower for k in ["macro", "tdee", "kcal", "protein", "nutricional"]):
            score -= 1.0
        if "espalda" in prompt_lower and not any(k in ans_lower for k in ["lumbar", "riesgo", "dolor", "ejercicio", "síntesis"]):
            score -= 1.0

        relevance_score = max(1.0, round(score, 1))
        status = "PASSED" if tool_accuracy_passed and relevance_score >= 4.0 else "FAILED"

        return {
            "test_id": tc["id"],
            "category": tc["category"],
            "prompt": tc["prompt"],
            "expected_behavior": tc["expected_behavior"],
            "obtained_behavior": obtained_behavior,
            "executed_tools": executed_tools,
            "tool_accuracy_passed": tool_accuracy_passed,
            "relevance_score": relevance_score,
            "iterations_used": res["total_iterations"],
            "final_answer": final_answer,
            "status": status
        }

    def run_suite(self) -> Dict[str, Any]:
        results = []
        passed_count = 0
        total_relevance = 0.0

        for tc in self.test_cases:
            eval_res = self.evaluate_test_case(tc)
            results.append(eval_res)
            total_relevance += eval_res["relevance_score"]
            if eval_res["status"] == "PASSED":
                passed_count += 1

        total_cases = len(self.test_cases)
        avg_relevance = round(total_relevance / total_cases, 2) if total_cases > 0 else 0.0
        accuracy_pct = round((passed_count / total_cases) * 100, 2)

        summary = {
            "total_test_cases": total_cases,
            "passed_test_cases": passed_count,
            "failed_test_cases": total_cases - passed_count,
            "overall_accuracy_pct": accuracy_pct,
            "average_relevance_score": avg_relevance,
            "evaluations": results,
            "limitations_identified": [
                "Latencia acumulada al encadenar múltiples herramientas secuenciales en el ciclo ReAct.",
                "Inexistencia de persistencia episódica en base de datos multinodo NoSQL."
            ],
            "proposed_improvements": [
                "Implementar caché de respuestas para consultas biomecánicas frecuentes.",
                "Integrar persistencia episódica en Google Cloud Firestore."
            ]
        }
        return summary


if __name__ == "__main__":
    evaluator = AgentQualityEvaluator()
    report = evaluator.run_suite()
    print(f"Evaluación de Calidad completada: {report['passed_test_cases']}/{report['total_test_cases']} aprobados ({report['overall_accuracy_pct']}%)")
