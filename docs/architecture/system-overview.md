# 🏛️ Visión General del Sistema — Wellness Lift SaaS

**Wellness Lift** es una plataforma SaaS inteligente multi-sucursal y multi-rol diseñada para la gestión de gimnasios de levantamiento de pesas, entrenadores personales y atletas. Incorpora un motor de **Inteligencia Artificial con Recuperación Aumentada por Generación (RAG)** que adapta rutinas de entrenamiento basándose en ciencia deportiva, periodización y matrices de seguridad médica.

---

## 🏗️ Arquitectura General

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

## 🧩 Componentes del Sistema

1. **Frontend SPA (`src/frontend/`)**: Aplicación web construida con **React 18**, **Vite** y el sistema de diseño Emil Kowalski. Proporciona interfaces adaptadas para Administradores, Entrenadores y Atletas.
2. **Backend API (`src/backend/`)**: Servicio RESTful con **FastAPI** y **Uvicorn** que expone endpoints para la gestión de atletas, sucursales, generación de rutinas y chat IA.
3. **Motor RAG (`src/backend/app/rag_chunker.py`, `embeddings_generator.py`, `rag_evaluator.py`)**: Submodulo encargado de segmentar la base de conocimiento en Markdown, generar vectores de 384 dimensiones ($L2$ normalizados) e indexar el almacén vectorial `data/vector_store/embeddings.json`.
4. **Base de Datos NoSQL**: Conexión a **Google Cloud Firestore** para la persistencia de perfiles de usuario, bitácoras de entrenamiento y asignación de entrenadores.

---

## 📚 Documentación de Arquitectura Relacionada

- [**Arquitectura del Sistema RAG**](./rag-architecture.md): Diagramas de flujo en Mermaid, especificación de componentes y métricas de evaluación.
- [**Registro de Decisiones de Arquitectura (ADR)**](./adr/001-rag-architecture-decisions.md): Decisiones técnicas formalizadas para el motor de embeddings, chunking semántico y métricas de similitud.
- [**Métricas de Recuperación y Calidad**](../evaluation/retrieval-metrics.md): Informe técnico de precisión, recall y seguridad médica.
