# Documentacion Tecnica — Wellness Platform

Este directorio contiene las especificaciones de arquitectura, diseño de API, modulos de inteligencia artificial y manuales de despliegue en la nube.

## Documentos de Arquitectura y Agentes
- `architecture/multiagent-architecture.md`: Especificacion de la arquitectura multiagente (patron Supervisor) del Sprint 3.
- `orchestration/orchestrator-agent.md`: Especificacion del Orchestrator Agent, clasificacion de intenciones y coordinacion multidominio.
- `agents/interagent-communication.md`: Protocolo de comunicacion y trazabilidad inter-agente (`InterAgentMessage`, `InterAgentResponse`).
- `agent_architecture_sprint2.md`: Documentacion tecnica maestra del Wellness Coach Agent 2.0, memoria conversacional y Tool Calling.
- `react_agent_architecture.md`: Especificacion del flujo de razonamiento ReAct y control de bucles.
- `agent_evaluation_report.md`: Informe de evaluacion de calidad del agente y benchmark S2-06.
- `evaluation/multiagent-evaluation.md`: Benchmark del flujo multiagente y observabilidad de spans.
- `multiagent_data_integration.md`: Integracion de datos y servicios con Google Cloud Firestore y BigQuery.
- `vector_database_integration.md`: Especificacion de la Base de Datos Vectorial RAG e indexacion de embeddings.
- `chunking_strategy.md`: Estrategia de segmentacion semantica Markdown con ventana deslizante.
- `reports/sprint-3-report.md`: Informe final consolidado del Sprint 3.

## Especificaciones de API y Despliegue
- `architecture.md`: Diagrama general de componentes, flujo de datos y modelo de seguridad.
- `api_spec.md`: Especificacion de endpoints RESTful FastAPI.
- `aws_deployment_guide.md`: Guia de despliegue en AWS EC2 y Amplify.
