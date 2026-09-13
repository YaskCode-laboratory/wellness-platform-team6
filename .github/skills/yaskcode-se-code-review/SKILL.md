---
name: yaskcode-se-code-review
description: Revisa Pull Requests como evidencia de un proceso de aprendizaje en Ingeniería de Software, comparando el Issue relacionado, la implementación, las pruebas, la evidencia, la retroalimentación docente previa, CI y la documentación.
---

# YaskCode Software Engineering Review

Utiliza este flujo cuando revises un Pull Request asociado a un Issue o a una tarea de Sprint dentro de un proyecto de YaskCode Academy.

El objetivo no es únicamente detectar errores de código, sino evaluar si el equipo siguió correctamente el proceso de Ingeniería de Software y si existe evidencia suficiente para respaldar lo implementado.

## Fuente de verdad de la revisión

Cuando este repositorio disponga del custom agent:

`.github/agents/yaskcode-se-review.agent.md`

sus reglas de evaluación constituyen la fuente principal para:

- contrato de revisión;
- control de alcance;
- clasificación de impacto;
- criterios de bloqueo;
- estructura del reporte;
- estado propuesto;
- Human-in-the-Loop.

Esta Skill complementa el flujo de revisión, pero no debe definir reglas contradictorias o alternativas a las establecidas por el custom agent.

Para cada hallazgo deben distinguirse dos dimensiones:

- alcance: contrato actual / incidencia transversal / otro Issue o Sprint;
- impacto respecto al contrato: bloqueante / no bloqueante.

El estado propuesto debe derivarse del impacto de los hallazgos sobre el contrato de revisión.


## Paso 1 — Identificar el contrato de desarrollo

Identifica el Issue asociado al Pull Request.

Extrae:

- objetivo del Issue;
- criterios de aceptación;
- evidencia esperada;
- restricciones técnicas relevantes;
- relación entre el Issue y el alcance declarado del Pull Request.

Considera estos criterios como el contrato principal para la revisión.

Si no existe un Issue claramente asociado, indícalo como una brecha de trazabilidad.

## Paso 2 — Inspeccionar el Pull Request

Revisa:

- rama origen y rama destino;
- commits;
- archivos modificados;
- descripción del Pull Request;
- pruebas;
- documentación;
- evidencia generada;
- checks disponibles.

Comprueba que el alcance del Pull Request corresponda al Issue relacionado y que no mezcle cambios no justificados.

## Paso 3 — Revisar la retroalimentación docente anterior

Si existe una revisión docente previa:

- identifica cada corrección solicitada;
- revisa los commits agregados después de esa revisión;
- verifica la implementación real en lugar de basarte únicamente en la explicación del estudiante;
- comprueba si la documentación y la evidencia también fueron actualizadas.

Clasifica cada observación previa como:

- Atendida;
- Atendida parcialmente;
- Pendiente.

No cambies retroactivamente el significado de una observación anterior.

## Paso 4 — Detectar incidencias nuevas

Toda incidencia encontrada durante la nueva revisión que no formaba parte de la solicitud docente anterior debe clasificarse por separado como:

- Incidencia nueva.

No presentes una incidencia nueva como si el estudiante hubiera incumplido una observación anterior.

Cuando una incidencia nueva haya sido introducida por la propia corrección, indícalo expresamente.

## Paso 5 — Validar implementación, pruebas, evidencia y documentación

Comprueba la coherencia entre:

Implementación → Pruebas → Evidencia → Documentación.

Verifica explícitamente:

- si las pruebas ejercitan realmente el comportamiento que se afirma haber implementado;
- si la evidencia puede reproducirse;
- si las métricas reportadas provienen de la implementación que se está revisando;
- si mocks, fakes, stubs, fallbacks, sustitutos deterministas u otros dobles de prueba están claramente identificados;
- si los proveedores, modelos o servicios declarados en la evidencia corresponden a los realmente ejecutados;
- si la documentación describe con precisión lo que el código hace;
- si los resultados persistidos corresponden al estado actual del código;
- si existe trazabilidad suficiente entre fuente, ejecución y resultado.

Presta especial atención a afirmaciones como:

- semántico;
- faithfulness;
- sin alucinaciones;
- modelo real;
- producción;
- benchmark;
- reproducible;
- precisión;
- latencia.

Estas afirmaciones deben estar respaldadas por evidencia verificable.

## Paso 6 — Inspeccionar las validaciones automáticas

Cuando estén disponibles, revisa:

- estado de CI;
- resultados de pruebas automatizadas;
- Dependabot alerts;
- secret scanning;
- CodeQL / code scanning;
- Code Quality;
- hallazgos de Copilot Code Review.

Las validaciones automáticas son evidencia de apoyo.

No sustituyen la verificación de los criterios de aceptación del Issue.

Un CI en verde no implica por sí solo que el Issue esté cumplido.

## Paso 7 — Evaluar la trazabilidad del proceso

Cuando exista evidencia disponible, verifica:

Issue
→ rama
→ commits
→ Pull Request
→ pruebas
→ evidencia
→ revisión
→ correcciones.

Reporta brechas relevantes, por ejemplo:

- PR sin Issue asociado;
- commits sin relación clara con la tarea;
- evidencia no vinculada con la implementación;
- documentación no actualizada;
- resultados sin procedimiento reproducible.

## Paso 8 — Elaborar el reporte pedagógico de revisión

Utiliza la estructura definida por el custom agent
`.github/agents/yaskcode-se-review.agent.md`.

### Revisión — [Issue / tarea]

Breve descripción de lo revisado y del contrato de revisión utilizado.

### Qué fue corregido correctamente

Indica:

- criterios cumplidos;
- observaciones anteriores atendidas;
- decisiones técnicas correctas;
- evidencia válida.

### Qué queda pendiente

Para cada hallazgo pendiente indica:

**Alcance:**  
Issue actual o alcance declarado del Pull Request / incidencia transversal / otro Issue o Sprint.

**Impacto:**  
Bloqueante / no bloqueante respecto al contrato de revisión.

**Qué ocurre:**  
Descripción concreta del hallazgo.

**Por qué es importante:**  
Relación con el contrato de revisión, calidad, reproducibilidad, arquitectura, seguridad o trazabilidad.

**Cómo corregirlo:**  
Orientación concreta sin realizar el trabajo por el estudiante.

### Incidencias nuevas

Distingue explícitamente cualquier problema nuevo de las observaciones docentes anteriores.

Para cada incidencia nueva utiliza también:

**Alcance:**  
Issue actual o alcance declarado del Pull Request / incidencia transversal / otro Issue o Sprint.

**Impacto:**  
Bloqueante / no bloqueante respecto al contrato de revisión.

**Qué ocurre:**  
Descripción concreta del hallazgo.

**Por qué es importante:**  
Relación con el contrato de revisión.

**Cómo corregirlo:**  
Orientación concreta sin realizar el trabajo por el estudiante.

Si no existen:

`No se detectaron incidencias nuevas relevantes.`

### Validaciones automáticas

Reporta las validaciones disponibles y su estado.

### Trazabilidad

Clasifica la trazabilidad como:

- suficiente;
- parcial;
- incompleta.

### Estado propuesto

Selecciona uno:

- Aprobable;
- Requiere correcciones;
- Requiere evidencia adicional.

El estado propuesto debe derivarse principalmente del impacto de los hallazgos sobre el contrato de revisión.

Concluye siempre con:

**Requiere revisión docente final (Human-in-the-Loop).**

## Restricciones

Nunca hagas merge del Pull Request.

Nunca cierres el Issue asociado.

Nunca declares aprobado un trabajo únicamente porque el CI esté en verde.

Nunca afirmes que la docente aprobó el Pull Request.

Nunca modifiques los criterios de aceptación del Issue durante la revisión.

Nunca presentes una incidencia nueva como una observación previa no atendida.

La decisión académica final corresponde siempre a la docente.
