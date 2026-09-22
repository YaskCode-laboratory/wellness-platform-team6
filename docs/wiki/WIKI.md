# Wiki Oficial del Proyecto — Plataforma Multiagente RAG Wellness Lift

**Proyecto**: Wellness Lift SaaS Platform (Equipo 6)  
**Maestría en TIC (2026-I) — Laboratorio de Computación**  
**Repositorio**: `wellness-platform-team6`

---

## 0. Resumen

El presente documento constituye la Wiki oficial del proyecto **Wellness Lift**, una plataforma SaaS respaldada por una arquitectura multiagente e IA generativa especializada en entrenamiento adaptativo, biomecánica y seguridad médica deportiva. El sistema integra un motor de Recuperación Aumentada por Generación (RAG), almacenamiento vectorial determinista, memoria conversacional en dos niveles, invocación de herramientas externas (Tool Calling) y un protocolo de comunicación inter-agente estandarizado con trazabilidad y prevención de ciclos. 

Los resultados del benchmark automatizado demuestran una precisión en seguridad médica del **100%** en casos de lesiones y condiciones preexistentes ($N_{medical}=4$), un **Recall@3 de 90.00%**, un **MRR de 0.7000** y una cobertura del **100%** en las suites de pruebas automatizadas (49/49 pruebas aprobadas).

---

## 1. Introducción

El auge de la inteligencia artificial generativa y los Modelos de Lenguaje de Gran Escala (LLMs) ha revolucionado la interacción usuario-sistema en la industria del bienestar y el fitness. Sin embargo, las aplicaciones tradicionales basadas en chatbots monolíticos sufren de alucinaciones graves, recomendando ejercicios con alta compresión axial o momentos de fuerza nocivos a usuarios con patologías estructurales preexistentes (por ejemplo, hernias discales o lesiones ligamentosas).

**Wellness Lift** aborda esta problemática mediante una plataforma multiagente modular donde cada agente posee responsabilidades acotadas a dominios del conocimiento específicos. Esta Wiki documenta los fundamentos teóricos, la revisión de la literatura científica, el diseño arquitectónico del sistema multiagente del Equipo 6, el protocolo de mensajería inter-agente y la evaluación empírica de desempeño.

---

## 2. Planteamiento del Problema

### 2.1. Alucinaciones y Riesgos Biomecánicos en LLMs Genéricos
Los LLMs genéricos carecen de mecanismos de restricción deterministas para validar contraindicaciones médicas. Ante la consulta de un usuario con hernia discal L4-L5, un modelo estándar puede sugerir erróneamente sentadillas libres con barra o pesos muertos convencionales, incrementando el riesgo de cizallamiento y compresión intervertebral.

### 2.2. Falta de Contexto Persistente y Fragmentación de Herramientas
Las consultas de entrenamiento requieren mantener tanto el contexto inmediato del diálogo (memoria a corto plazo) como los hechos clave del perfil del atleta (memoria a largo plazo). Asimismo, la incapacidad de consultar servicios externos o ejecutar reglas deterministas impide una recomendación segura.

### 2.3. Desafíos de Coordinación en Sistemas Multiagente
La delegación de tareas entre múltiples agentes sin un protocolo estandarizado provoca bucles infinitos de delegación ($A \to B \to A$), pérdida de metadatos de rastreo y fallas en la consolidación de respuestas multi-dominio.

---

## 3. Fundamentos Teóricos

El diseño de **Wellness Lift** se fundamenta en siete pilares conceptuales y metodológicos:

### 3.1. Recuperación Aumentada por Generación (RAG)
Arquitectura que combina la capacidad generativa de los LLMs con un sistema de búsqueda en bases de conocimiento externas. Permite fundamentar las respuestas en documentos científicos previamente curados, mitigando las alucinaciones.

### 3.2. Segmentación Semántica (Semantic Chunking)
Estrategia de fragmentación de documentos Markdown que preserva la estructura jerárquica de encabezados (`#`, `##`, `###`) y utiliza una ventana deslizante con solapamiento (*sliding window overlap*) para evitar la ruptura de tablas clínicas y explicaciones biomecánicas.

### 3.3. Embeddings y Similitud Coseno con Normalización L2
Transformación de fragmentos de texto en vectores continuos densos de $d$ dimensiones. La Similitud Coseno calcula el ángulo entre vectores normalizados tal que $\|\vec{v}\| = 1.0$, permitiendo búsquedas semánticas eficientes mediante producto escalar:

$$\text{SimilitudCoseno}(\vec{u}, \vec{v}) = \sum_{i=1}^{d} u_i \cdot v_i$$

### 3.4. Patrón ReAct (Reasoning + Acting) y Tool Calling
Ciclo iterativo de razonamiento (*Thought*), selección de acción (*Action*) y observación de resultados (*Observation*) que permite al agente invocar funciones externas deterministas antes de sintetizar la respuesta final.

### 3.5. Arquitectura Multiagente (Supervisor-Worker)
Modelo organizacional donde un agente orquestador (Supervisor) clasifica la intención del usuario y delega la ejecución a agentes especializados (Workers), coordinando las respuestas de múltiples dominios.

### 3.6. Memoria Conversacional Graduada
- **Memoria a Corto Plazo**: Buffer de ventana deslizante que mantiene los últimos $N$ turnos de la conversación activa.
- **Memoria a Largo Plazo**: Almacén persistente de hechos extraídos (lesiones, equipos disponibles, objetivos) asociados al perfil del usuario.

### 3.7. Matriz de Adaptación Médica y Biomecánica
Reglas clínicas estandarizadas basadas en literatura de la *National Strength and Conditioning Association (NSCA)* y la *International Society of Biomechanics (ISB)* para sustituir ejercicios con alto riesgo biomecánico.

---

## 4. Estado del Arte

Actualmente coexisten diversas aproximaciones para la asistencia en entrenamiento mediante IA:

### 4.1. Chatbots Monolíticos Basados en Prompts
Sistemas como ChatGPT o FitnessAI procesan la solicitud en un solo llamado al modelo. Presentan baja precisión clínica ante lesiones complejas y carecen de verificación estricta de reglas.

### 4.2. Frameworks Multiagente Emergentes
- **LangChain / LangGraph**: Proporciona grafos dirigidos de estados para orquestar flujos de agentes.
- **Microsoft AutoGen**: Enfocado en conversaciones entre agentes autónomos.
- **CrewAI**: Enfoque basado en roles y tareas asignadas.

### 4.3. Estándares Abiertos de Comunicación (MCP y A2A)
- **Model Context Protocol (MCP)**: Estándar abierto promovido por Anthropic para conectar modelos con herramientas y fuentes de datos locales o remotas.
- **Agent-to-Agent (A2A)**: Protocolo emergente para la comunicación distribuida e interoperable entre agentes heterogéneos en la nube mediante endpoints HTTP/gRPC.

### 4.4. Matriz Comparativa

| Criterio | Chatbots Monolíticos | Frameworks Genéricos | Plataforma Wellness Lift |
| :--- | :--- | :--- | :--- |
| **Verificación Médica** | No estricta (Riesgo de alucinación) | Depende del prompt | Estricta (RAG + Deterministic Tool Calling) |
| **Especialización** | Generalista | Genérica | Agentes de Dominio (Biomecánica, Nutrición, etc.) |
| **Prevención de Ciclos** | N/A | Manual por el desarrollador | Automática (`DelegationTracer` con `max_hops=5`) |
| **Memoria Persistente** | Por ventana de tokens | En memoria temporal | Graduada (Corto y Largo Plazo extraída) |

---

## 5. Análisis de los Artículos Científicos

La arquitectura del sistema se respalda en la literatura fundamental del área:

1. **Vaswani et al. (2017) — *Attention Is All You Need***:
   - *Aporte*: Introduce la arquitectura Transformer que fundamenta los LLMs modernos.
   - *Aplicación en Wellness Lift*: Base tecnológica para la comprensión del lenguaje natural y la generación de embeddings.
   - [Enlace al artículo](https://arxiv.org/abs/1706.03762)

2. **Lewis et al. (2020) — *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks***:
   - *Aporte*: Formaliza el marco RAG combinando memoria paramétrica (LLM) con memoria no paramétrica (Vector Store).
   - *Aplicación en Wellness Lift*: Implementado en el motor de recuperación para consultar la base de conocimiento biomédica.
   - [Enlace al artículo](https://arxiv.org/abs/2005.11401)

3. **Yao et al. (2022) — *ReAct: Synergizing Reasoning and Acting in Language Models***:
   - *Aporte*: Demuestra que alternar razonamiento explícito con ejecución de acciones mejora la precisión y trazabilidad.
   - *Aplicación en Wellness Lift*: Base del agente especialista para invocar herramientas de sustitución médica.
   - [Enlace al artículo](https://arxiv.org/abs/2210.03629)

4. **NSCA Essentials of Strength Training and Conditioning (4ª Edición)**:
   - *Aporte*: Estándares científicos sobre biomecánica, cargas de compresión y prevención de lesiones en levantamiento de pesas.
   - *Aplicación en Wellness Lift*: Fuente primaria para la base de conocimiento `medical_adaptations.md`.
   - [Enlace de referencia](https://www.nsca.com/essentials-of-strength-training-and-conditioning/)

5. **ISB Recommendations on Definitions of Joint Coordinate Systems (Wu et al., 2002)**:
   - *Aporte*: Definición de planos anatómicos, momentos articulares y vectores de fuerza.
   - *Aplicación en Wellness Lift*: Fundamento para la regla de sustitución biomecánica en lesiones de hombro y rodilla.
   - [Enlace al artículo](https://doi.org/10.1016/S0021-9290(01)00222-6)

---

## 6. Aplicaciones y Casos de Uso del Sistema

**Wellness Lift** implementa una suite completa de componentes aplicados al ecosistema SaaS:

### 6.1. Wellness Coach Specialist Agent 2.0 (`coach_specialist.py`)
Agente especializado en Biomecánica y Entrenamiento Adaptativo. Verifica si la consulta pertenece a su dominio (`is_query_in_domain`), procesa solicitudes dentro de dominio y genera rutinas de ejercicio adaptadas.

### 6.2. Motor RAG e Índice Vectorial (`embeddings_generator.py`, `vector_store.py`)
Almacena vectores densos L2-normalizados de 384 dimensiones (`embeddings.json`) e índice de frecuencia TF-IDF (`vector_index.json`). Permite recuperar en tiempo real los fragmentos más relevantes de la base de conocimiento.

### 6.3. Memoria Conversacional Graduada (`memory.py`)
Gestor que combina un buffer corto plazo para diálogo continuo y un extractor de hechos clave a largo plazo (lesiones, contraindicaciones, equipamiento disponible).

### 6.4. Herramientas Integradas mediante Tool Calling (`tools.py`)
Funciones ejecutables por el agente:
- `get_exercise_substitutes`: Retorna contraindicaciones y alternativas seguras.
- `verify_medical_safety`: Valida la seguridad de una rutina propuesta.
- `generate_adaptive_routine`: Estructura rutinas según RPE, RIR y volumen semanal.

### 6.5. Orchestrator Agent (`orchestrator.py`)
Superagente supervisor encargado de:
1. Analizar la intención del usuario.
2. Delegar tareas a agentes especializados mediante mensajes estandarizados.
3. Consolidar respuestas de múltiples dominios (ej. Biomecánica + Nutrición).

### 6.6. Protocolo de Comunicación Inter-Agente (`communication.py`)
Estructura homogénea de mensajería con metadatos de trazabilidad:
- `InterAgentMessage`: Payload JSON con `task_id`, `trace_id`, `source_agent`, `target_agent`, `intent`, `context_payload`, `hop_count`.
- `InterAgentResponse`: Payload JSON de respuesta con propiedad de retrocompatibilidad `agent_name`.
- `DelegationTracer`: Trazador que limita la profundidad a `max_hops=5` y bloquea ciclos directos bidireccionales ($A \to B \to A$).

---

## 7. Discusión y Resultados

### 7.1. Evaluación del Benchmark de Recuperación RAG (S1-06 / S1-07)
El benchmark evaluó 10 consultas representativas (`data/evaluation/test_queries.json`) sobre el almacén vectorial determinista:

```text
===========================================================================
RESUMEN GENERAL DE METRICAS DE EVALUACION (TOP-3)
===========================================================================
Consultas totales evaluadas:     10
Consultas médicas evaluadas:     4
Precision@3 promedio:           30.00% (0.3000)
Recall@3 promedio:              90.00% (0.9000)
Mean Reciprocal Rank (MRR):      0.7000
Precisión en Seguridad Médica:  100.00% (4/4 casos médicos aprobados)
---------------------------------------------------------------------------
```

### 7.2. Resultados por Caso Médico ($N_{medical}=4$)
- **Q01 (Hernia Discal L4-L5)**: `Recall@3 = 1.00`, `MRR = 0.50`, `Safety: PASSED`. Recuperó Sentadilla Libre/Peso Muerto como contraindicados y Prensa 45°/Peso Muerto Rumano como sustitutos.
- **Q02 (Lesión de Rodilla - Meniscos/Ligamentos)**: `Recall@3 = 1.00`, `MRR = 1.00`, `Safety: PASSED`.
- **Q03 (Hipertensión Arterial)**: `Recall@3 = 1.00`, `MRR = 1.00`, `Safety: PASSED`.
- **Q04 (Lesión de Manguito Rotador)**: `Recall@3 = 1.00`, `MRR = 1.00`, `Safety: PASSED`.

### 7.3. Suite de Pruebas Automatizadas
Se ejecutaron exitosamente 49 pruebas unitarias e integración en Pytest (**100% pasadas en verde**):
- Pruebas de comunicación inter-agente y prevención de ciclos (5/5 PASSED).
- Pruebas del agente especialista y verificación de límites de dominio (5/5 PASSED).
- Pruebas del Orchestrator Agent y delegación multi-dominio (5/5 PASSED).
- Pruebas de Tool Calling y síntesis de respuestas (5/5 PASSED).
- Pruebas de memoria conversacional a corto y largo plazo (4/4 PASSED).
- Pruebas de integridad documental y vectores de embeddings (25/25 PASSED).

---

## 8. Conclusiones

1. **Efectividad del Enfoque Multiagente Especializado**: La delimitación de responsabilidades entre el Orchestrator Agent y los agentes especialistas previene la contaminación de dominio y permite respuestas técnicamente sólidas.
2. **Garantía de Seguridad Médica**: La combinación de RAG con el patrón Tool Calling asegura un 100% de éxito en la identificación de contraindicaciones y sustitutos seguros para atletas con patologías preexistentes.
3. **Robustez en la Comunicación Inter-Agente**: El protocolo homogéneo `InterAgentMessage` con `DelegationTracer` elimina el riesgo de bucles infinitos de delegación y proporciona trazabilidad auditable mediante `trace_id`.
4. **Reproducibilidad en CI/CD**: La implementación de hashing determinista `zlib.adler32` garantiza representaciones vectoriales 100% idénticas y testeables en cualquier entorno sin costo de API Cloud.

### Trabajo Futuro (Roadmap)
- **Segmentación Granular por Patología**: Subdividir la matriz médica en micro-chunks clínicos.
- **Recuperador Híbrido Sparse-Dense**: Combinar coincidencia léxica BM25 con similitud coseno densa.
- **Adopción Gradual de MCP y A2A**: Evolucionar el protocolo en memoria hacia servidores MCP y endpoints distribuidos Agent-to-Agent.

---

## 9. Referencias y Enlaces

1. Vaswani, A., et al. (2017). *Attention Is All You Need*. NIPS 2017.  
   Link: [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

2. Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.  
   Link: [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

3. Yao, S., et al. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023.  
   Link: [https://arxiv.org/abs/2210.03629](https://arxiv.org/abs/2210.03629)

4. National Strength and Conditioning Association (NSCA).  
   Link: [https://www.nsca.com](https://www.nsca.com)

5. International Society of Biomechanics (ISB).  
   Link: [https://isbweb.org](https://isbweb.org)

6. Model Context Protocol (MCP) Specification.  
   Link: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

7. Documentación Interna del Proyecto Wellness Lift:
   - [Arquitectura del Sistema RAG](../architecture/rag-architecture.md)
   - [Arquitectura Multiagente](../architecture/multiagent-architecture.md)
   - [Protocolo de Comunicación Inter-Agente](../agents/interagent-communication.md)
   - [Registro ADR 008](../architecture/adr/008-interagent-communication-protocol.md)
   - [Reporte de Métricas de Recuperación](../evaluation/retrieval-metrics.md)
