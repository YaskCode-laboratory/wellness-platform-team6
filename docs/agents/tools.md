# Especificación de Herramientas del Agente (AgentToolRegistry) — Wellness Lift

Documentación técnica del catálogo de herramientas asociadas (*Tool Calling*) para el **Wellness Coach Agent 2.0**.

---

## 1. Visión General del Registro de Herramientas

El módulo `AgentToolRegistry` ubicado en [`src/backend/app/wellness_agent/tools.py`](../../src/backend/app/wellness_agent/tools.py) proporciona capacidades de ejecución de funciones para consultar bases de datos locales, realizar cálculos biomecánicos/nutricionales y consultar la base vectorial RAG.

---

## 2. Catálogo de Herramientas y Esquemas de Funciones

### A. `get_exercise_alternative`
- **Propósito**: Obtener una alternativa de ejercicio perteneciente al mismo grupo muscular.
- **Entradas**: `muscle_group` (cadena de texto: Pecho, Espalda, Piernas, Hombros, Bíceps, Tríceps).
- **Salida**: Objeto JSON con `status`, `exercise_id` y `name`.

### B. `calculate_nutrition_macros`
- **Propósito**: Calcular el TDEE y el desglose de macronutrientes (Proteínas, Carbohidratos, Grasas) para un usuario.
- **Entradas**: `user_id` (identificador único del usuario).
- **Salida**: Objeto JSON con `tdee`, `protein`, `carbs` y `fats`.

### C. `assess_injury_risk`
- **Propósito**: Evaluar si un ejercicio genera riesgo biomecánico según las lesiones registradas en el perfil del usuario.
- **Entradas**: `user_id` (identificador del usuario), `exercise_name` (nombre del ejercicio a evaluar).
- **Salida**: Objeto JSON con `risk_level` (HIGH / LOW), `warning` y `safe_recommendation`.

### D. `retrieve_rag_knowledge`
- **Propósito**: Realizar búsqueda semántica vectorial en la base de conocimiento RAG.
- **Entradas**: `query_text` (consulta de texto), `top_k` (cantidad de fragmentos a recuperar, por defecto 2).
- **Salida**: Lista de objetos JSON conteniendo `chunk_id`, `heading_context`, `text` y `similarity_score`.

---

## 3. Integración con el Motor de Razonamiento

El motor de razonamiento (`ReasoningEngine`) utiliza el registro de herramientas para enriquecer los prompts del sistema y validar las respuestas antes de retornarlas al usuario.
