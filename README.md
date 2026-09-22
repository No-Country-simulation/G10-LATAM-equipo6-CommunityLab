# 🚀 CommunityLab — Motor Inteligente de Transformación y Distribución para Comunidades Digitales

> **Hackathon ONE G10 — Oracle Next Education & Alura / No Country**  
> **Equipo 6 — LATAM**

---

## 📌 Descripción del Proyecto
**CommunityLab** es una plataforma automatizada que ingiere la actividad orgánica de comunidades de aprendizaje y tecnología (chats de Discord, foros, dudas de cursos, testimonios espontáneos) y la transforma mediante Modelos de Lenguaje (LLMs) en **activos de marketing y distribución listos para publicar**:
- 💼 **Publicaciones inspiradoras para LinkedIn & X (Twitter)** a partir de contrataciones y logros de estudiantes.
- 📰 **Resúmenes semanales (Community Highlights)** y secciones destacadas para Newsletters.
- 💡 **Preguntas Frecuentes (FAQs) y Tips Técnicos** detectados automáticamente desde las dudas recurrentes.
- ☁️ **Persistencia en la nube:** almacenamiento seguro y estructurado de los activos en **Oracle Cloud Infrastructure (OCI) Object Storage (Always Free)**.
- 📊 **Panel de Curaduría en Streamlit:** interfaz visual para que el equipo de Community Managers y Marketing apruebe, edite y gestione los copys antes de publicarlos.

---

## 🏗️ Arquitectura de la Solución (Dual-Engine Cloud-Native)

CommunityLab cuenta con una **arquitectura dual de orquestación homologada** que permite procesar interacciones tanto desde un workflow automatizado visual (**n8n**) como desde un pipeline directo de alto rendimiento (**Python Nativo con Google Gemini**), convergiendo ambos en **Oracle Cloud Infrastructure (OCI) Object Storage** como única fuente de verdad:

```mermaid
flowchart TD
    A[Canales de Comunidad: Discord / Webhooks / JSON / CSV] -->|Dataset Ingesta| DEDUP{Deduplicador Inteligente OCI}
    
    subgraph DUAL_ENGINE ["Motores de Procesamiento Homologados"]
        DEDUP -->|Motor 1: Orquestador No-Code| N8N[Workflow n8n con Webhook HTTP]
        DEDUP -->|Motor 2: Pipeline Python Nativo| PY[src/pipeline.py con Google Gemini 2.5]
    end
    
    subgraph ESPECIALIZACION ["4 Archivos Temáticos Especializados"]
        N8N & PY --> ARCH1[marketing_linkedin_logros.json]
        N8N & PY --> ARCH2[marketing_showcase.json]
        N8N & PY --> ARCH3[faqs_soporte_tecnico.json]
        N8N & PY --> ARCH4[metricas_feedback_comunidad.json]
    end
    
    subgraph OCI_CLOUD ["Oracle Cloud Infrastructure (Always Free)"]
        ARCH1 & ARCH2 & ARCH3 & ARCH4 -->|Subida Cloud Directa| BUCKET[("OCI Object Storage: communitylab-activos-marketing<br/>activos/YYYY-MM-DD/*.json")]
        CUR_DATA[("curaduria/curaduria_aprobados.json")]
    end
    
    subgraph STREAMLIT_PANEL ["Panel Interactivo de Curaduría (Streamlit)"]
        BUCKET -->|Lectura Cloud-First| UI[src/ui/app.py: Dashboard & Curaduría]
        UI -->|Aprobar 🟢 / Descartar 🔴 / Leer 🔵| CUR_DATA
        UI -->|Disparo de Lotes| DUAL_ENGINE
    end
```

---

## 👥 Equipo 6 (Integrantes y Roles)

| Integrante | Ubicación | Rol Principal |
| :--- | :--- | :--- |
| **César Augusto Cely Pulido** | Bogotá, Colombia | **Project Manager & Cloud Architect** |
| **Max Ferrer Cabanillas Salas** | Lima, Perú | **Backend & Pipeline Developer** |
| **Raúl Gallardo** | Buenos Aires, Argentina | **QA & Cloud Support** |
| **José Medina** | Paraguay | **Oracle Ecosystem & N8N / LLMs Specialist** |
| **Juan Luis Mansilla** | Puerto Montt, Chile | **Backend & Fullstack Developer** |
| **Edwin Gustavo Enriquez Arias** | La Paz, Bolivia | **QA Lead, Testing Automation & Backend** |
| **Carol Yesenia Arancay Osorio** | Lima, Perú | **Frontend / UX & Data** |
| **Víctor Araya** | LATAM | **Frontend & Documentación** |
| **Rodrigo Ramírez** | LATAM | **Testing & Soporte** |

---

## 📁 Estructura del Repositorio

```text
├── docker-compose.yml                # Despliegue de n8n (Local & OCI Compute VM)
├── .env.example                      # Plantilla de variables de entorno (Gemini, OCI, n8n)
├── README.md                         # Documentación general y arquitectura
├── backend-pipeline.md               # Guía técnica profunda del Backend y persistencia OCI
├── PM_Files/                         # Gestión del Proyecto y Metodología Ágil
│   ├── ROADMAP.md                    # Plan maestro de 5 semanas, hitos y demos
│   ├── Actas_Reuniones/              # Minutas y actas de reuniones semanales
│   └── Proyecto 3 – 🚀 CommunityLab.pdf # Especificación oficial del reto
├── data/
│   └── interacciones_ejemplo.json    # Dataset oficial con 15 interacciones simuladas
├── logs/                             # Trazas y auditoría de ejecución rotativas diarias
├── n8n/                              # Orquestación de flujos
│   ├── README.md                     # Guía de conexión a la VM OCI y versionado
│   └── workflows/                    # Workflows exportados en JSON para Git
├── src/
│   ├── ai_engine/                    # Modelos Pydantic v2, prompts y cliente Gemini
│   ├── cloud_oci/                    # Conector con Oracle Cloud Infrastructure Object Storage
│   ├── ingestion/                    # Lectura, validación, batching y deduplicación
│   ├── pipeline.py                   # Pipeline Python E2E y CLI
│   ├── ui/                           # Panel de curaduría y orquestador en Streamlit
│   └── utils/                        # Logging y utilidades transversales
└── tests/                            # Suite automatizada (49/49 pruebas pasando)
```

---

## ⚙️ Requisitos Previos y Configuración Local

### 1. Clonar el Repositorio
```bash
git clone git@github.com:No-Country-simulation/G10-LATAM-equipo6-CommunityLab.git
cd G10-LATAM-equipo6-CommunityLab
```

### 2. Configurar el Entorno Virtual de Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Variables de Entorno
Copia el archivo `.env.example` como `.env` y completa tus credenciales de Gemini y OCI:
```bash
cp .env.example .env
```

### 4. Ejecución del Panel de Curaduría (Streamlit)
```bash
streamlit run src/ui/app.py
```
Accede a través de tu navegador a `http://localhost:8501`.

### 5. Orquestador n8n
- **En la Nube (Instancia oficial del equipo):** La VM de OCI Always Free corre n8n directamente en [http://147.15.9.116:5678](http://147.15.9.116:5678).
- **En Local:** Ejecuta `docker compose up -d` y accede en `http://localhost:5678`.
- Consulta la guía completa de flujos y versionado en [`n8n/README.md`](n8n/README.md).

### 6. Ejecución de Pruebas Automatizadas
```bash
pytest tests/ -v
```
*Total:* 49 tests unitarios e integrales (100% aprobados).

---

## 📅 Roadmap de Sprints (5 Semanas)
Consulta el cronograma completo y los entregables por sprint en [ROADMAP.md](PM_Files/ROADMAP.md).