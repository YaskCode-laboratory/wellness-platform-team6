#!/usr/bin/env python3
"""
Script CLI para la Evaluación del Desempeño del Sistema RAG (Wellness Lift).
Ejecuta el conjunto de pruebas de data/evaluation/test_queries.json y guarda el informe en data/evaluation/evaluation_results.json.
"""

import json
import sys
from pathlib import Path

# Configurar encoding UTF-8 en stdout si es necesario
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
SYS_BACKEND_DIR = ROOT_DIR / "src" / "backend"
if str(SYS_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(SYS_BACKEND_DIR))

from app.rag_evaluator import RAGEvaluator


def main():
    print("=" * 75)
    print("INICIANDO EVALUACION DE RECUPERACION Y CALIDAD RAG (WELLNESS LIFT)")
    print("=" * 75)

    test_queries_file = ROOT_DIR / "data" / "evaluation" / "test_queries.json"
    output_results_file = ROOT_DIR / "data" / "evaluation" / "evaluation_results.json"

    if not test_queries_file.exists():
        print(f"Error: No se encontro el archivo de consultas en {test_queries_file}")
        sys.exit(1)

    with open(test_queries_file, "r", encoding="utf-8") as f:
        test_queries = json.load(f)

    print(f"Se cargaron {len(test_queries)} consultas de prueba desde test_queries.json\n")

    evaluator = RAGEvaluator()
    evaluation_report = evaluator.evaluate_all(test_queries, top_k=3)

    output_results_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_results_file, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2, ensure_ascii=False)

    summary = evaluation_report["summary"]

    print("=" * 75)
    print("RESUMEN GENERAL DE METRICAS DE EVALUACION (TOP-3)")
    print("=" * 75)
    print(f"Consultas evaluadas:            {summary['total_queries']}")
    print(f"Precision@3 promedio:          {summary['mean_precision_at_k'] * 100:.2f}%")
    print(f"Recall@3 promedio:             {summary['mean_recall_at_k'] * 100:.2f}%")
    print(f"Mean Reciprocal Rank (MRR):     {summary['mean_mrr']:.4f}")
    print(f"Precision en Seguridad Medica: {summary['medical_safety_accuracy'] * 100:.2f}%")
    print("-" * 75)

    print("\nDETALLE POR CASO DE PRUEBA:")
    print("-" * 75)
    for res in evaluation_report["detailed_results"]:
        status = "OK" if res["safety_passed"] else "ALERTA"
        print(f"[{res['query_id']}] Category: {res['category']}")
        print(f"     Query: {res['query'][:65]}...")
        print(f"     Precision@3: {res['precision_at_k']:.2f} | Recall@3: {res['recall_at_k']:.2f} | MRR: {res['mrr']:.2f} | Safety: {status}")
        print("-" * 75)

    print(f"\nResultados guardados exitosamente en: {output_results_file}")
    print("=" * 75)


if __name__ == "__main__":
    main()
