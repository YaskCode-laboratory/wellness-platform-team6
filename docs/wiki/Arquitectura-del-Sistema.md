# 🏛️ Arquitectura del Sistema — Wellness Lift

## 1. Visión General
La arquitectura de **Wellness Lift** está diseñada bajo el patrón de microservicios desarticulados, combinando una aplicación web de página única (SPA React) con un backend asíncrono en FastAPI y un motor conversacional dotado de RAG y razonamiento ReAct.

---

## 2. Diagrama de Componentes (Mermaid)

```mermaid
graph TD
    subgraph "Capa de Presentación (Frontend SPA)"
        UI[React SPA - Vite + Tailwind CSS + Emil Kowalski Style]
    end

    subgraph "Capa de Aplicación (Backend FastAPI)"
        API[Endpoints RESTful /api/v1/...]
        Auth[Módulo de Autenticación JWT/UUID]
        DB_Connector[Controlador de Base de Datos]
        AgentCore[Wellness Coach Agent 2.0]
        ReActEngine[Motor ReAct - Thought/Action/Obs]
    end

    subgraph "Capa de Herramientas & IA"
        T1[get_athlete_technical_file]
        T2[search_medical_contraindications]
        T3[query_rag_vector_store]
        T4[calculate_progressive_overload]
    end

    subgraph "Capa de Datos & Persistencia"
        Firestore[(Google Cloud Firestore NoSQL)]
        VectorDB[(In-Memory Cosine Vector DB)]
        LLM[OpenRouter API / Gemini 1.5 Pro]
    end

    UI --> API
    API --> Auth & DB_Connector & AgentCore
    AgentCore --> ReActEngine
    ReActEngine --> T1 & T2 & T3 & T4
    T1 --> DB_Connector
    T3 --> VectorDB
    DB_Connector --> Firestore
    AgentCore --> LLM
```

---

## 3. Capas Principales del Sistema

1. **Frontend SPA (React 19 + Vite 8)**:
   - Diseño moderno basado en componentes modulares.
   - Soporte para cambio de roles (Atleta, Coach, Administrador) y chat conversacional interactivo.
2. **Backend RESTful (FastAPI 0.110)**:
   - Enrutamiento optimizado, validación de schemas con Pydantic y CORS abierto para consumo seguro.
3. **Capa de Persistencia Híbrida**:
   - Soporte dual: Almacenamiento NoSQL en **Google Cloud Firestore** con fallback automático a **Mock Database Memory Store** para ejecuciones locales sin dependencias externas.
