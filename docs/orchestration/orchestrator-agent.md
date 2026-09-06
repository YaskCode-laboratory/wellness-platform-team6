# Orchestrator Agent — Supervisor Central del Sistema Multiagente

## 1. Misión y Responsabilidades

El **Orchestrator Agent** es el componente supervisor responsable de recibir todas las interacciones entrantes de los usuarios, determinar el dominio de la consulta, delegar la tarea al agente idóneo y garantizar la observabilidad de las operaciones.

---

## 2. Diagrama de Estados y Flujo de Procesamiento

`mermaid
stateDiagram-v2
    [*] --> RecibirConsulta: Mensaje del Usuario
    RecibirConsulta --> ClasificarIntencion: Extracción de Keywords y Contexto
    
    ClasificarIntencion --> DelegarCoach: WORKOUT_BIOMECHANICS
    ClasificarIntencion --> DelegarNutricion: NUTRITION
    ClasificarIntencion --> DelegarMotivacion: MOTIVATION
    ClasificarIntencion --> DelegarAnalitica: ANALYTICS
    ClasificarIntencion --> CoordinarMultidominio: MULTIDOMAIN
    
    DelegarCoach --> VerificarCiclos
    DelegarNutricion --> VerificarCiclos
    DelegarMotivacion --> VerificarCiclos
    DelegarAnalitica --> VerificarCiclos
    
    CoordinarMultidominio --> DelegarCoach: Subtarea 1
    CoordinarMultidominio --> DelegarNutricion: Subtarea 2
    
    VerificarCiclos --> GenerarRespuesta: Delegación Válida
    VerificarCiclos --> FallbackSeguro: Ciclo Detectado / Error
    
    GenerarRespuesta --> RegistrarTraza: Asignar Trace ID y Spans
    FallbackSeguro --> RegistrarTraza
    
    RegistrarTraza --> [*]: Retornar al Cliente
`

---

## 3. Clasificación de Intenciones (AgentIntent)

El orquestador clasifica las intenciones evaluando el vocabulario semántico y la presencia de múltiples dominios simultáneos:

1. **WORKOUT_BIOMECHANICS:** Consultas de técnica, rutinas, series, repeticiones, biomecánica y adaptaciones médicas por lesiones.
2. **NUTRITION:** Consultas de cálculo de TDEE, distribución de macronutrientes, balance energético y dietas.
3. **MOTIVATION:** Consultas de adherencia, pérdida de ánimo, constancia y disciplina deportiva.
4. **ANALYTICS:** Consultas de volumen acumulado (kg), progreso histórico y récords personales.
5. **MULTIDOMAIN:** Consultas compuestas que involucran dos o más dominios (ej. Rutina + Macros).
6. **GENERAL:** Saludos o consultas abiertas (enrutadas al Coach por defecto).

---

## 4. Mitigación de Bucles y Resiliencia

El supervisor implementa dos mecanismos clave de protección:
- **Límite de Profundidad de Delegación (max_delegations=5):** Evita ciclos de reenvío indefinido entre agentes.
- **Manejo de Errores con Fallback Estructurado:** En caso de excepción no controlada en un agente especialista, el supervisor retorna un mensaje de contingencia seguro con estado error_fallback sin interrumpir la experiencia del usuario.
