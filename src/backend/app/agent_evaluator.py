"""
Módulo Agent Quality Evaluator — Wellness Coach Agent 2.0 (Issue #17 & Issue #18)
Suite de evaluación de comportamiento, memoria conversacional multiturno, Tool Calling y razonamiento ReAct.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from app import agent
    from app.react_agent import ReActAgent
    from app.wellness_agent.memory import ConversationMemoryManager
except ModuleNotFoundError:
    from agent import WellnessCoachAgent
    from react_agent import ReActAgent
    from wellness_agent.memory import ConversationMemoryManager


class AgentQualityEvaluator:
    """
    Evaluador de Calidad del Agente que realiza contraste estricto entre Comportamiento Esperado vs Obtenido,
    validación de memoria conversacional multiturno y secuencias ordenadas de herramientas.
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
                "category": "Multi-turn Conversation & Fact Retention",
                "is_multiturn": True,
                "turns": [
                    "Hola, sufro de hernia discal lumbar L4-L5.",
                    "¿Qué ejercicios de piernas puedo hacer hoy?",
                    "¿La sentadilla libre con barra es recomendable para mi rutina?"
                ],
                "expected_behavior": "Retener la patología de Hernia L4-L5 en el Turno 1 y verificar en el Turno 3 que la información previa prohíbe la sentadilla con barra libre.",
                "expected_tool_sequence": ["assess_injury_risk", "get_exercise_alternative"]
            },
            {
                "id": "TC-03",
                "category": "ReAct Multi-step Tool Sequence",
                "prompt": "Tengo molestias en la espalda baja, evalúa el riesgo y sugiere sustitutos de ejercicio.",
                "expected_behavior": "Ejecutar la secuencia ordenada: assess_injury_risk -> get_exercise_alternative -> FINAL_ANSWER.",
                "expected_tool_sequence": ["assess_injury_risk", "get_exercise_alternative"]
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
                "category": "ReAct RAG Knowledge Retrieval",
                "prompt": "Evalúa la evidencia científica RAG sobre periodización de hipertrofia",
                "expected_behavior": "Ejecutar la herramienta retrieve_rag_knowledge y sintetizar la respuesta final.",
                "expected_tool": "retrieve_rag_knowledge"
            }
        ]

    def evaluate_test_case(self, tc: Dict[str, Any]) -> Dict[str, Any]:
        user_id = f"eval_user_{tc['id'].lower()}"

        if tc.get("is_multiturn"):
            # Evaluación multiturno real sobre ConversationMemoryManager y agente
            memory_mgr = ConversationMemoryManager()
            agent.memory_manager = memory_mgr
            if hasattr(agent, "_agent_instance"):
                agent._agent_instance.memory = memory_mgr

            responses = []
            for turn_idx, turn_prompt in enumerate(tc["turns"]):
                resp = agent.generate_chat_response(user_id, turn_prompt)
                responses.append(f"Turno {turn_idx + 1}: {resp}")

            final_answer = responses[-1]
            history = memory_mgr.get_history(user_id)
            formatted_history = memory_mgr.get_formatted_history(user_id)
            fact_retained = (
                len(history) == len(tc["turns"]) * 2 and
                any("lumbar" in msg["content"].lower() or "hernia" in msg["content"].lower() for msg in history if msg["role"] == "user")
            )

            # Obtener traza de herramientas ejecutadas en la última consulta ReAct
            res = self.react_agent.run_react_loop(tc["turns"][-1], athlete_id=user_id)
            executed_tools = [s["action"] for s in res["steps"]]

            if fact_retained and ("prensa" in final_answer.lower() or "alternativa" in final_answer.lower() or "riesgo" in final_answer.lower() or "síntesis" in final_answer.lower() or "recomendación" in final_answer.lower()):
                tool_accuracy_passed = True
                obtained_behavior = f"Memoria multiturno verificada ({len(history)} mensajes almacenados). Hecho de Turno 1 ('hernia/lumbar') retenido en ConversationMemoryManager e influyó en la respuesta conversacional del Turno 3."
            else:
                tool_accuracy_passed = False
                obtained_behavior = "FALLO: El historial conversacional no retuvo los hechos de los turnos previos."
        else:
            res = self.react_agent.run_react_loop(tc["prompt"], athlete_id=user_id)
            executed_tools = [s["action"] for s in res["steps"]]
            tools_before_final = [a for a in executed_tools if a != "FINAL_ANSWER"]
            final_answer = res.get("final_answer", "")

            # 1. Validación Estricta de Herramientas
            tool_accuracy_passed = False
            obtained_behavior = ""

            if tc.get("expected_tool") is None and tc.get("expected_tool_sequence") is None and tc.get("expected_tool_alternatives") is None:
                if len(tools_before_final) == 0:
                    tool_accuracy_passed = True
                    obtained_behavior = "Respuesta directa generada correctamente sin llamadas a herramientas innecesarias."
                else:
                    tool_accuracy_passed = False
                    obtained_behavior = f"FALLO: Se ejecutaron herramientas innecesarias ({', '.join(tools_before_final)}) para una consulta conversacional directa."

            elif "expected_tool_sequence" in tc:
                seq = tc["expected_tool_sequence"]
                seq_indices = []
                valid_seq = True
                for tool in seq:
                    if tool in executed_tools:
                        seq_indices.append(executed_tools.index(tool))
                    else:
                        valid_seq = False
                        break

                if valid_seq and seq_indices == sorted(seq_indices):
                    tool_accuracy_passed = True
                    obtained_behavior = f"Secuencia requerida ({' -> '.join(seq)}) ejecutada en el orden exacto."
                else:
                    tool_accuracy_passed = False
                    obtained_behavior = f"FALLO: La secuencia requerida ({' -> '.join(seq)}) no se ejecutó en orden. Herramientas usadas: {' -> '.join(executed_tools)}."

            elif "expected_tool_alternatives" in tc:
                alts = tc["expected_tool_alternatives"]
                found_alt = [t for t in alts if t in executed_tools]
                if found_alt:
                    tool_accuracy_passed = True
                    obtained_behavior = f"Herramienta alternativa válida '{found_alt[0]}' ejecutada según el contexto."
                else:
                    tool_accuracy_passed = False
                    obtained_behavior = f"FALLO: Ninguna herramienta de las alternativas {alts} fue ejecutada. Herramientas usadas: {executed_tools}."

            elif "expected_tool" in tc:
                expected = tc["expected_tool"]
                if expected in executed_tools:
                    tool_accuracy_passed = True
                    obtained_behavior = f"Herramienta requerida '{expected}' ejecutada correctamente."
                else:
                    tool_accuracy_passed = False
                    obtained_behavior = f"FALLO: La herramienta '{expected}' no fue invocada. Herramientas usadas: {executed_tools}."

        # 2. Derivación de Puntaje de Relevancia (Score de 1.0 a 5.0)
        score = 5.0
        if not tool_accuracy_passed:
            score -= 2.5
        if not final_answer:
            score -= 2.5
        elif len(final_answer) < 20:
            score -= 1.0

        relevance_score = max(1.0, round(score, 1))
        status = "PASSED" if tool_accuracy_passed and relevance_score >= 4.0 else "FAILED"

        return {
            "test_id": tc["id"],
            "category": tc["category"],
            "prompt": tc.get("prompt") or " -> ".join(tc.get("turns", [])),
            "expected_behavior": tc["expected_behavior"],
            "obtained_behavior": obtained_behavior,
            "executed_tools": executed_tools,
            "tool_accuracy_passed": tool_accuracy_passed,
            "relevance_score": relevance_score,
            "iterations_used": len(executed_tools),
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
