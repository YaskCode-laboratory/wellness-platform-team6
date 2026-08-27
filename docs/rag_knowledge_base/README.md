# 🧠 Base de Conocimiento Especializada para el Sistema RAG — Wellness Lift (Issue #5)

Este directorio contiene la arquitectura documental y el cuerpo de conocimiento científico-técnico que alimenta el sistema **Retrieval-Augmented Generation (RAG)** de la plataforma **Wellness Lift**, correspondiendo a la tarea **[S1-01 - Diseñar la base de conocimiento del dominio] (Issue #5)**.

---

## 📌 Estructura y Taxonomía de Documentos

```
docs/rag_knowledge_base/
├── biomechanics_and_safety.md      # Principios biomecánicos y seguridad articular
├── hypertrophy_periodization.md   # Programación de hipertrofia y sobrecarga progresiva
├── medical_adaptations.md          # Matriz de contraindicaciones y ejercicios sustitutos
├── knowledge_base_manifest.json    # Manifiesto de metadatos e índices del motor RAG
└── README.md                       # Documentación del diseño y criterios RAG
```

---

## 🔬 Fuentes de Conocimiento Identificadas y Justificadas

1. **NSCA (National Strength and Conditioning Association)**: Estándares internacionales de ejecución técnica, selección de ejercicios e intensidad biomecánica en levantamiento de pesas.
2. **ISB (International Society of Biomechanics)**: Criterios cinemáticos y cinéticos de reducción de vectores de cizallamiento y compresión lumbar.
3. **Guías Clínicas de Medicina Deportiva y Rehabilitación**: Protocolos de adaptación de cargas ante patologías musculo-esqueléticas (hernias discales lumbares, lesiones ligamentosas de rodilla, hipertensión arterial y síndrome de pinzamiento de hombro).

---

## ⚙️ Integración con el Motor del Backend (`src/backend/app/agent.py`)

El backend consume estos documentos durante la fase de inyección de contexto para garantizar que el Agente IA filtre los ejercicios según la condición de salud del atleta antes de generar o adaptar la rutina.
