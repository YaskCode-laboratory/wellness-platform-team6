# 👥 Gestión Multi-Rol y Ficha Técnica — Wellness Lift

## 1. Arquitectura de Roles
Wellness Lift proporciona paneles especializados para tres perfiles de usuario:

### 🏋️ Atleta (Athlete)
- Registro de entrenamientos en vivo (Modo Gimnasio con cálculo de RPE y volumen por serie).
- Visualización de rutinas semanales adaptadas.
- Solicitud de cambio de programa con notas biomecánicas.
- Asistente AI Chat interactivo.

### 📋 Entrenador (Coach)
- Gestión de atletas asignados.
- Visualización de Ficha Técnica Deportiva y Médica de sus atletas.
- Aprobación o rechazo de solicitudes de rutina con feedback personalizado.
- Edición y personalización directa de rutinas generadas por la IA.

### 🛡️ Administrador (Admin)
- Directorio global de usuarios (Atletas, Coaches, Admins).
- Inactivación/Activación de cuentas.
- Registro de nuevo personal (*Staff*) y Entrenadores.
- Reasignación de atletas entre entrenadores.
- Traslado de usuarios entre sucursales del gimnasio.

---

## 2. Ficha Técnica Deportiva y Médica del Atleta
Módulo unificado accesible vía `/api/v1/athlete/{user_id}/technical-file`:
- **Datos Personales y Métricas**: Nombre, edad, peso, altura e IMC.
- **Historial Clínico**: Lesiones y condiciones médicas activas.
- **Récords Personales (PRs)**: Cargas máximas históricas por ejercicio.
- **Volumen Total Acumulado**: Kilos totales levantados en la plataforma.
- **Bitácora Día a Día**: Registro detallado de sesiones pasadas.
