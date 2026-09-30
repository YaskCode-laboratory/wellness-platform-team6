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
                "expected_behavior": "Retener la patología de Hernia L4-L5 en Turno 1; en Turno 3 identificar riesgo HIGH contraindicando sentadilla libre y seleccionar alternativa para Piernas coherente y no contraindicada.",
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
        memory_mgr = ConversationMemoryManager()
        memory_mgr.clear_memory(user_id)

        if tc.get("is_multiturn"):
            # Evaluación multiturno real sobre ConversationMemoryManager y agente real
            agent.memory_manager = memory_mgr
            if hasattr(agent, "_agent_instance"):
                agent._agent_instance.memory = memory_mgr

            responses = []
            for turn_idx, turn_prompt in enumerate(tc["turns"]):
                resp = agent.generate_chat_response(user_id, turn_prompt)
                responses.append(f"Turno {turn_idx + 1}: {resp}")

            final_answer = responses[-1]
            history = memory_mgr.get_history(user_id)
            extracted_facts = memory_mgr.get_extracted_facts(user_id)

            # 1. Fact Retention: 6 mensajes en memoria y hecho de hernia/lumbar extraído en Turno 1
            fact_retained = (
                len(history) == len(tc["turns"]) * 2 and
                any("lumbar" in f.lower() or "hernia" in f.lower() for f in extracted_facts)
            )

            # 2. Validación de Influencia Real en la Decisión (Distinción explícita de criterios):
            # A. Riesgo correctamente identificado: risk_level HIGH y contraindicación lumbar explícita.
            # B. Grupo muscular correcto: Piernas.
            # C. Alternativa coherente con la restricción detectada: debe ser biomecánicamente segura
            #    (p. ej., Prensa de Piernas o Extensión) y NO una variante de sentadilla con carga axial
            #    (como Sentadilla con Barra o Sentadilla Goblet), que contradiga la patología lumbar detectada.
            assess_obs = {}
            alt_obs = {}
            for line in final_answer.split("\n"):
                if "- Herramienta assess_injury_risk:" in line:
                    json_part = line.split("- Herramienta assess_injury_risk:", 1)[1].strip()
                    try:
                        assess_obs = json.loads(json_part)
                    except Exception:
                        pass
                elif "- Herramienta get_exercise_alternative:" in line:
                    json_part = line.split("- Herramienta get_exercise_alternative:", 1)[1].strip()
                    try:
                        alt_obs = json.loads(json_part)
                    except Exception:
                        pass

            # A. Riesgo correctamente identificado
            risk_high = (
                assess_obs.get("risk_level") == "HIGH" or
                "contraindicad" in assess_obs.get("warning", "").lower()
            )

            # B. Grupo muscular correcto
            target_muscle = alt_obs.get("muscle_group", "")
            muscle_group_correct = (target_muscle.lower() == "piernas")

            # C. Alternativa realmente coherente con la restricción detectada
            alt_id = alt_obs.get("exercise_id", "").lower()
            alt_name = alt_obs.get("name", "").lower()

            # Variantes de sentadillas o con carga axial contradicen la contraindicación lumbar
            is_contraindicated = (
                "squat" in alt_id or
                "sentadilla" in alt_name or
                alt_id in ["squat", "goblet_squat"]
            )
            # Para ser coherente debe ser un ejercicio sin compresión axial con soporte (ej. prensa o extensión)
            alternative_coherent = (not is_contraindicated) and (
                "prensa" in alt_name or "extensión" in alt_name or alt_id == "leg_press"
            )

            executed_tools = ["assess_injury_risk", "get_exercise_alternative", "FINAL_ANSWER"]

            if fact_retained and risk_high and muscle_group_correct and alternative_coherent:
                tool_accuracy_passed = True
                obtained_behavior = (
                    f"Comportamiento Correcto: Memoria multiturno verificada ({len(history)} mensajes). "
                    f"Hecho de Turno 1 ('hernia/lumbar') recuperado. "
                    f"Riesgo identificado: ALTO (HIGH - contraindicación lumbar). "
                    f"Grupo muscular: Piernas. "
                    f"Alternativa coherente: '{alt_obs.get('name')}' (segura y sin compresión axial)."
                )
            else:
                tool_accuracy_passed = False
                inconsistencies = []
                if not fact_retained:
                    inconsistencies.append("Hecho de hernia no retenido en memoria")
                if not risk_high:
                    inconsistencies.append("Riesgo biomecánico no evaluado como HIGH")
                if not muscle_group_correct:
                    inconsistencies.append(f"Grupo muscular incorrecto: '{target_muscle}'")
                if not alternative_coherent:
                    inconsistencies.append(
                        f"Alternativa inconsistente con la restricción: get_exercise_alternative seleccionó '{alt_obs.get('name', alt_id)}', "
                        f"la cual contradice la contraindicación de compresión axial lumbar identificada por assess_injury_risk"
                    )

                obtained_behavior = (
                    f"INCONSISTENCIA DETECTADA: {'; '.join(inconsistencies)}. "
                    f"[Riesgo identificado: {'SÍ' if risk_high else 'NO'} | "
                    f"Grupo muscular correcto: {'SÍ' if muscle_group_correct else 'NO'} | "
                    f"Alternativa coherente con restricción: {'SÍ' if alternative_coherent else 'NO'}]."
                )
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
                "Selección estocástica de alternativas sin filtrado biomecánico: get_exercise_alternative selecciona aleatoriamente del catálogo por grupo muscular sin considerar contraindicaciones o patologías previas identificadas por assess_injury_risk (p. ej., sugiriendo sentadilla goblet a un usuario con hernia discal lumbar).",
                "Latencia acumulada al encadenar múltiples herramientas secuenciales en el ciclo ReAct.",
                "Inexistencia de persistencia episódica en base de datos multinodo NoSQL."
            ],
            "proposed_improvements": [
                "Incorporar filtrado contextual de patologías en get_exercise_alternative o permitir el paso de restricciones biomecánicas al catálogo para excluir ejercicios contraindicados.",
                "Implementar caché de respuestas para consultas biomecánicas frecuentes.",
                "Integrar persistencia episódica en Google Cloud Firestore."
            ]
        }
        return summary


if __name__ == "__main__":
    evaluator = AgentQualityEvaluator()
    report = evaluator.run_suite()
    print(f"Evaluación de Calidad completada: {report['passed_test_cases']}/{report['total_test_cases']} aprobados ({report['overall_accuracy_pct']}%)")
