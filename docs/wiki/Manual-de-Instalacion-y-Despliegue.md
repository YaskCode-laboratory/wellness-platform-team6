# 🚀 Manual de Instalación y Despliegue — Wellness Lift

## 1. Requisitos Previos
- **Python**: v3.12 o superior.
- **Node.js**: v18.0 o superior (con `npm` o `pnpm`).
- **Git**: v2.40 o superior.

---

## 2. Ejecución Local (Puesta en Marcha)

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/YaskCode-laboratory/wellness-platform-team6.git
cd wellness-platform-team6
git checkout dev
```

### Paso 2: Configurar e Iniciar el Backend (FastAPI)
```bash
# Crear y activar entorno virtual Python
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias backend
pip install -r src/backend/requirements.txt

# Iniciar servidor Uvicorn
cd src/backend
uvicorn app.main:app --reload --port 8000
```
- **Documentación Swagger API**: `http://localhost:8000/docs`

### Paso 3: Configurar e Iniciar el Frontend (React SPA)
En una nueva terminal:
```bash
cd src/frontend
npm install
npm run dev
```
- **Aplicación Web**: `http://localhost:5173`

---

## 3. Despliegue en la Nube (AWS)

- **Backend (AWS EC2)**: Desplegado en instancia Ubuntu Linux con servidor `systemctl` y proxy inverso Nginx.
- **Frontend (AWS Amplify)**: Integrado con CI/CD automático desde la rama `main` en GitHub.
- **CI/CD Pipeline (GitHub Actions)**: `.github/workflows/deploy.yml` ejecuta pruebas automáticas en cada push a `main`.
