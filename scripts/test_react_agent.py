"""
Script de Prueba del Patrón ReAct — Wellness Coach Agent 2.0 (Issue #16)
Demuestra el ciclo Thought -> Action -> Observation -> Final Answer en tareas complejas de varias decisiones.
"""

import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))
from app.react_agent import ReActAgent

def run_react_agent_demo():
    print("[START] === DEMOSTRACION DEL PATRON REACT Y FLUJO DE RAZONAMIENTO ===\n")
    agent = ReActAgent()

    test_scenarios = [
        {
            "prompt": "Evalúa mi rutina actual de tren inferior y adapta los ejercicios según mi expediente médico",
            "athlete_id": "user123"  # Juan Pérez (Hernia L4-L5)
        },
        {
            "prompt": "Revisa las condiciones médicas de María Fernández y sugiere reemplazos para sentadilla hack",
            "athlete_id": "user456"  # María Fernández (Lesión Rodilla)
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"==================================================")
        print(f"[ESCENARIO #{i}] Prompt: '{scenario['prompt']}' (ID: {scenario['athlete_id']})")
        print(f"--------------------------------------------------")

        result = agent.run_react_loop(scenario["prompt"], athlete_id=scenario["athlete_id"])

        for step in result["steps"]:
            print(f"\n[THOUGHT] {step['thought']}")
            if step["action"] != "FINAL_ANSWER":
                print(f"[ACTION] {step['action']}({step.get('action_input')})")
                print(f"[OBSERVATION] {step['observation']}")

        print(f"\n[FINAL ANSWER] Respuesta Sintetizada:\n{result['final_answer']}")
        print(f"==================================================\n")

if __name__ == "__main__":
    run_react_agent_demo()
