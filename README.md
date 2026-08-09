# 🏋️‍♂️ Intelligent Wellness & Weightlifting SaaS Platform (Team 6)

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI: 1.0](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React: 18.0](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)
[![Vite: 8.0](https://img.shields.io/badge/Vite-8.0-646cff.svg)](https://vitejs.dev/)
[![Cloud: AWS EC2 & Amplify](https://img.shields.io/badge/AWS-EC2%20%26%20Amplify-ff9900.svg)](https://aws.amazon.com/)

> **Master's Program in ICT (2026-I) — Computing Laboratory Project**  
> **Team 6 Repository**: [wellness-platform-team6](https://github.com/computing-laboratory/wellness-platform-team6)

---

## 📌 Visión General del Proyecto

**Wellness Lift** es una plataforma SaaS inteligente multi-sucursal y multi-rol diseñada para optimizar la gestión de gimnasios de levantamiento de pesas, entrenadores personales y atletas. Integra un motor de **Inteligencia Artificial (OpenRouter Cloud / Gemini)** para la generación adaptativa de rutinas personalizadas basadas en lesiones médicas, periodización deportiva y sobrecarga progresiva.

---

## 🏛️ Arquitectura del Sistema

El proyecto sigue una arquitectura desacoplada de microservicios y Single Page Application (SPA):

```
                               ┌─────────────────────────┐
                               │   AWS Amplify (HTTPS)   │
                               │  Frontend React Vite    │
                               └────────────┬────────────┘
                                            │ HTTP / JSON API
                                            ▼
                               ┌─────────────────────────┐
                               │     AWS EC2 (Ubuntu)    │
                               │  Nginx Reverse Proxy    │
                               │    FastAPI Backend      │
                               └────────────┬────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │   Google Cloud Firestore  │                 │ OpenRouter / Gemini API   │
       │    Base de Datos NoSQL    │                 │   Motor de Agentes de IA  │
       └───────────────────────────┘                 └───────────────────────────┘
```

---

## 👥 Jerarquía de Roles y Credenciales de Demostración

| Rol | Correo Electrónico | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@wellnessgym.com` | `admin123` | Control total, sucursales, alta de staff y reasignación de atletas. |
| **Entrenador (Coach)** | `coach.carlos@wellnessgym.com` | `coach123` | Edición de rutinas, revisión de solicitudes y ficha técnica de alumnos. |
| **Atleta / Cliente** | `juan@wellness.com` | `password123` | Modo Gimnasio en vivo, registro día a día y asistente IA. |

---

## 📁 Estructura del Repositorio

```
wellness-platform-team6/
├── .github/          # Workflows de CI/CD para despliegue automático
├── assets/           # Capturas de pantalla, diagramas y recursos multimedia
├── data/             # Datos semilla en JSON y esquemas de base de datos
├── docker/           # Archivos de contenedorización (Docker & Docker-Compose)
├── docs/             # Especificaciones técnicas, manual de API y guías AWS
├── prompts/          # Prompts del sistema utilizados por el Agente IA
├── scripts/          # Scripts de automatización y despliegue en AWS EC2
├── src/
│   ├── backend/      # API RESTful con FastAPI, Uvicorn y base de datos NoSQL
│   └── frontend/     # Aplicación web SPA con React, Vite y CSS Emil Kowalski Style
├── tests/            # Suite de pruebas unitarias e integración
├── .env.example      # Plantilla de variables de entorno
├── CHANGELOG.md      # Registro de cambios del proyecto
├── LICENSE           # Licencia del proyecto (MIT)
└── README.md         # Documentación principal
```

---

## 🚀 Despliegue en AWS Cloud

- **Backend (FastAPI)**: Servidor Ubuntu `t3.micro` en AWS EC2 administrado por `systemd` y proxy `Nginx`.
- **Frontend (React)**: AWS Amplify Hosting con canal CI/CD continuo conectado a este repositorio de GitHub.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.
