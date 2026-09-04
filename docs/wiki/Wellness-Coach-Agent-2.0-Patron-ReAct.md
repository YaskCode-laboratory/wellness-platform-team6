# 🧠 Wellness Coach Agent 2.0 — Patrón ReAct

## 1. Ciclo de Razonamiento ReAct (`Thought -> Action -> Observation -> Final Answer`)
El **Wellness Coach Agent 2.0** (`src/backend/app/react_agent.py`) combina razonamiento reflexivo, llamadas a herramientas y observaciones empíricas antes de generar una prescripción deportiva:

```mermaid
flowchart TD
    A[Solicitud del Usuario] --> B[Thought 1: Analizar requerimiento]
    B --> C[Action: get_athlete_technical_file]
    C --> D[Observation 1: Detecta Hernia L4-L5]
    D --> E[Thought 2: Buscar contraindicaciones]
    E --> F[Action: search_medical_contraindications]
    F --> G[Observation 2: Prohibir Sentadilla Libre, Recomendar Prensa 45°]
    G --> H[Thought 3: Calcular volumen]
    H --> I[Action: calculate_progressive_overload]
    I --> J[Observation 3: Volumen 3200 kg, Carga +5%]
    J --> K[Thought Final: Sintetizar respuesta]
    K --> L[Final Answer: Plan Adaptado Validado]
```

---

## 2. Registro de Herramientas (*Tool Registry*)
1. `get_athlete_technical_file`: Consulta expediente de salud y rutina actual.
2. `search_medical_contraindications`: Retorna ejercicios prohibidos y sustitutos biomecánicos.
3. `query_rag_vector_store`: Recupera evidencia científica de la base vectorial.
4. `calculate_progressive_overload`: Calcula volumen total ($V = S \times R \times C$) y sugiere sobrecarga progresiva (+5%).

---

## 3. Protección Anti-Bucles Infinitos
- Restricción a un máximo de **5 iteraciones** (`max_iterations = 5`).
- Firma Hash de Llamada (`action_name:action_input`). Si se detecta invocación idéntica, fuerza la síntesis inmediata en `FINAL_ANSWER`.

---

## 4. Benchmark de Evaluación de Calidad
- **Total Casos Evaluados**: 5
- **Tasa de Éxito (*Accuracy*)**: `100.0%`
- **Puntaje de Relevancia**: `5.0 / 5.0`
- **Bucles Infinitos Detectados**: 0
