# 🐍 Backend API — Wellness Platform (FastAPI)

Este directorio contiene el código fuente del backend desarrollado con **Python 3.12** y **FastAPI**.

---

## 🛠️ Tecnologías Utilizadas

- **Framework Web**: FastAPI 0.110.0
- **Servidor ASGI**: Uvicorn
- **Base de Datos NoSQL**: Google Cloud Firestore / Memory Engine (`database.py`)
- **Integración con IA**: OpenRouter Cloud API / Google Gemini API (`agent.py`)
- **Seguridad**: Hash de contraseñas con Passlib (`pbkdf2_sha256`)

---

## ⚙️ Configuración e Instalación Local

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor de desarrollo
uvicorn app.main:app --reload --port 8001
```

---

## 🛰️ Principales Endpoints

- `POST /api/v1/auth/login`: Autenticación multi-rol.
- `POST /api/v1/auth/register`: Registro público de atletas.
- `GET /api/v1/branches`: Consulta de sucursales activas.
- `GET /api/v1/athlete/{id}/technical-file`: Expediente técnico deportivo y médico.
- `POST /api/v1/admin/reassign-athlete`: Reasignación de entrenador por el administrador.
- `POST /api/v1/ai/chat/{id}`: Asistente interactivo de IA.
