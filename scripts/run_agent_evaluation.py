"""
Script de Evaluación de Comportamiento y Calidad del Agente 2.0 — Wellness Lift (Issue #17)
Ejecuta los casos de prueba de calidad, Tool Calling, memoria conversacional y razonamiento ReAct.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.agent_evaluator import AgentQualityEvaluator

def run_evaluation_benchmark():
    print("[START] === INICIANDO EVALUACION DE COMPORTAMIENTO Y CALIDAD DEL AGENTE 2.0 ===\n")
    evaluator = AgentQualityEvaluator()
    report = evaluator.run_suite()

    print(f"[SUMMARY] RESUMEN DE EVALUACION DE CALIDAD:")
    print(f"  - Total Casos de Prueba: {report['total_test_cases']}")
    print(f"  - Casos Aprobados (PASSED): {report['passed_test_cases']}")
    print(f"  - Casos Fallidos (FAILED): {report['failed_test_cases']}")
    print(f"  - Precisión General: {report['overall_accuracy_pct']}%")
    print(f"  - Puntaje Promedio de Relevancia: {report['average_relevance_score']}/5.0\n")

    print("--------------------------------------------------")
    print("[TEST CASES] DETALLE DE CASOS DE PRUEBA EVALUADOS:")
    print("--------------------------------------------------")
    for ev in report["evaluations"]:
        print(f"[{ev['test_id']}] {ev['category']} -> Estado: {ev['status']}")
        print(f"  Prompt: '{ev['prompt']}'")
        print(f"  Herramientas Ejecutadas: {', '.join(ev['executed_tools'])}")
        print(f"  Iteraciones Utilizadas: {ev['iterations_used']}")
        print(f"  Puntaje Relevancia: {ev['relevance_score']}/5.0\n")

    print("--------------------------------------------------")
    print("[LIMITATIONS] LIMITACIONES IDENTIFICADAS:")
    for lim in report["limitations_identified"]:
        print(f"  - {lim}")

    print("\n[IMPROVEMENTS] PROPUESTAS DE MEJORA:")
    for imp in report["proposed_improvements"]:
        print(f"  - {imp}")

    # Guardar resultados en data/agent_evaluation_results.json
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'agent_evaluation_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n[SUCCESS] Resultados de evaluación guardados en: {output_file}")

if __name__ == "__main__":
    run_evaluation_benchmark()
