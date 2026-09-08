# 🧠 Base de Conocimiento Especializada para el Sistema RAG — Wellness Lift (Issue #5)

Este directorio contiene la arquitectura documental y el cuerpo de conocimiento científico-técnico que alimenta el sistema **Retrieval-Augmented Generation (RAG)** de la plataforma **Wellness Lift**, correspondiendo a la tarea **[S1-01 - Diseñar la base de conocimiento del dominio] (Issue #5)**.

---

## 📌 Estructura y Taxonomía de Documentos

`
docs/rag_knowledge_base/
├── biomechanics_and_safety.md      # Principios biomecánicos y seguridad articular
├── hypertrophy_periodization.md   # Programación de hipertrofia y sobrecarga progresiva
├── medical_adaptations.md          # Matriz de contraindicaciones y ejercicios sustitutos
├── knowledge_base_manifest.json    # Manifiesto de metadatos e índices del motor RAG
└── README.md                       # Documentación del diseño y criterios RAG
`

---

## 🔬 Fuentes de Conocimiento y Trazabilidad Bibliográfica Concreta

Para garantizar la máxima validez científica y trazabilidad de las reglas clínicas y biomecánicas incorporadas en la base de conocimiento, se han referenciado fuentes reconocidas internacionalmente con sus respectivos autores, organismos, títulos y años de publicación:

### 1. Adaptaciones Médicas y Contraindicaciones Clínicas (medical_adaptations.md)
- **Columna Lumbar / Hernia Discal:**
  - **McGill, Stuart M. (2015).** *Low Back Disorders: Evidence-Based Prevention and Rehabilitation* (3.ª edición). Human Kinetics. ISBN: 978-1-4504-7291-3.
  - **Adams, M. A., Bogduk, N., Burton, K., & Dolan, P. (2012).** *The Biomechanics of Back Pain* (3.ª edición). Churchill Livingstone / Elsevier. ISBN: 978-0-7020-4314-7.
- **Rodilla / Patología Femororrotuliana y Ligamentos:**
  - **Escamilla, R. F., Zheng, N., Macleod, T. D., Edwards, W. B., Imamura, R., Hreljac, A., ... & Andrews, J. R. (2012).** *Patellofemoral joint force and stress between a short-arc quad and a leg press*. Physical Therapy in Sport, 13(4), 221-229.
  - **American College of Sports Medicine (ACSM) (2021).** *ACSM's Guidelines for Exercise Testing and Prescription* (11.ª edición). Wolters Kluwer / Lippincott Williams & Wilkins. ISBN: 978-1-9751-5018-1.
- **Hombro / Manguito Rotador y Espacio Subacromial:**
  - **Reinold, M. M., Escamilla, R. F., & Wilk, K. E. (2009).** *Current concepts in the scientific and clinical rationale for exercise selection in rotator cuff and scapular rehabilitation*. Journal of Orthopaedic & Sports Physical Therapy, 39(2), 105-117.
- **Hipertensión Arterial y Control Cardiovascular:**
  - **Pescatello, L. S., MacDonald, H. V., Ash, G. I., et al. (2019).** *Exercise and Hypertension: Position Stand*. Medicine & Science in Sports & Exercise, 51(6), 1314-1323. American College of Sports Medicine.

### 2. Biomecánica y Seguridad Articular (iomechanics_and_safety.md)
- **National Strength and Conditioning Association (NSCA) — Haff, G. G., & Triplett, N. T. (Eds.) (2016).** *Essentials of Strength Training and Conditioning* (4.ª edición). Human Kinetics. ISBN: 978-1-4925-0162-6.
- **International Society of Biomechanics (ISB) — Nigg, B. M., & Herzog, W. (Eds.) (2007).** *Biomechanics of the Musculo-skeletal System* (3.ª edición). John Wiley & Sons. ISBN: 978-0-470-01767-8.

### 3. Hipertrofia y Periodización de Cargas (hypertrophy_periodization.md)
- **Schoenfeld, Brad J. (2020).** *Science and Development of Muscle Hypertrophy* (2.ª edición). Human Kinetics. ISBN: 978-1-4925-9767-4.
- **Helms, E. R., Valdez, A., & Morgan, A. (2015).** *The Muscle and Strength Pyramid: Training* (1.ª edición). Eric Helms & 3D Muscle Journey.

---

## ⚙️ Integración con el Motor del Backend (src/backend/app/agent.py)

El backend consume estos documentos durante la fase de inyección de contexto para garantizar que el Agente IA filtre los ejercicios según la condición de salud del atleta antes de generar o adaptar la rutina.
