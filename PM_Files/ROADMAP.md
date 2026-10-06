# 🗺️ Roadmap y Plan Maestro: CommunityLab (Equipo 6)
**Hackathon ONE G10 — Oracle Next Education & Alura / No Country**

---

## 🎯 Objetivo del Proyecto
Desarrollar un MVP de un **Motor Inteligente de Transformación y Distribución para Comunidades Digitales**:
1. Ingesta de interacciones de comunidad (JSON, CSV, Webhook).
2. Análisis de sentimiento, extracción de temas y categorización mediante LLMs (Google Gemini).
3. Generación de copys optimizados multicanal (LinkedIn, Twitter/X, Newsletters, Tips/FAQs).
4. Persistencia obligatoria de activos en **Oracle Cloud Infrastructure (OCI) Object Storage (Always Free)**.
5. Panel de visualización y curaduría de publicaciones en **Streamlit**.
6. Despliegue en máquina virtual Linux en **OCI Compute Always Free** (diferencial).

---

## 👥 Células de Trabajo y Roles (9 Integrantes)

Para optimizar la colaboración y garantizar aprendizaje transversal, el equipo se divide en 3 células clave:

### 🧠 Célula 1: IA, Prompts & Orquestación (n8n & Gemini)
* **Miembros sugeridos:** Max Ferrer, Edwin Enriquez, Juan Luis Mansilla, José Medina.
* **Responsabilidades:**
  * Diseño de *system prompts* con *few-shot learning* para distintos canales y tonos.
  * Extracción estructurada de métricas de sentimiento y temas clave.
  * Implementación y modelado de flujos en **n8n** (nodos de webhook, Gemini AI, bifurcación switch y exportación JSON a `n8n/workflows/`).
  * Subflujo síncrono de generación e iteración de imágenes para posts (`POST /webhook/generar-imagen-post` con Gemini Prompt Engineer + Pollinations.ai / FLUX + persistencia OCI S3).
  * Investigación e integración de conectores de publicación externa a **LinkedIn & X (Twitter)** (análisis de restricciones de API y alternativas 100% free - Max Ferrer).
  * Integración híbrida con scripts de Python auxiliares si son requeridos.

### ☁️ Célula 2: Cloud OCI, Infraestructura & Backend
* **Miembros sugeridos:** César Cely (PM & Cloud), José Medina (Admin VM), Raúl Gallardo.
* **Responsabilidades:**
  * Administración y mantenimiento de la VM Linux Always Free en **OCI Compute** (`147.15.9.116`), con Docker y n8n activo.
  * Configuración de Bucket en **OCI Object Storage** (Always Free) y credenciales de acceso.
  * Integración de n8n / Python con OCI Object Storage para persistencia de activos de marketing.
  * Manejo seguro de variables de entorno (`.env`, `.env.example`).

### 💻 Célula 3: Frontend (Streamlit), Datos & QA
* **Miembros sugeridos:** Edwin Enriquez (Especialista QA), Carol Arancay, Max Ferrer (Adaptación Frontend), Víctor Araya, Rodrigo Ramírez.
* **Responsabilidades:**
  * Creación y enriquecimiento de datasets de prueba (`data/interacciones_ejemplo.json` y `.csv`).
  * Desarrollo y modernización del panel en **Streamlit** (adaptación del template UI de Carol Arancay por Max Ferrer: Dashboard general, Fuentes activas, Curaduría, Histórico OCI y Settings).
  * Pruebas funcionales, automatización de pruebas (Selenium / Pytest) y control de calidad.
  * Documentación de flujos de usuario y guías de uso.

---

## 📅 Cronograma Detallado Sprint a Sprint (Semanas 0 a 5)

```mermaid
%%{init: {
  'theme': 'base',
  'themeVariables': {
    'doneTaskBkgColor': '#10B981',
    'doneTaskBorderColor': '#059669',
    'activeTaskBkgColor': '#3B82F6',
    'activeTaskBorderColor': '#1D4ED8',
    'taskBkgColor': '#94A3B8',
    'taskBorderColor': '#64748B',
    'critBkgColor': '#F59E0B',
    'critBorderColor': '#D97706',
    'todayLineColor': '#EF4444'
  }
}}%%
gantt
    title Cronograma de Trabajo - CommunityLab (Equipo 6)
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m
    
    section S0: Setup & OCI VM
    First Meet & Roles                :done, s0_1, 2026-09-14, 2026-09-16
    Repo, Dataset & VM OCI Ready      :done, s0_2, 2026-09-16, 2026-09-18
    Sprint Demo Meet S0               :crit, done, s0_3, 2026-09-18, 2026-09-19
    
    section S1: Ingesta & IA Pipeline
    Pipeline n8n + LLM Resiliente     :done, s1_1, 2026-09-21, 2026-09-23
    Extracción Estructurada JSON      :done, s1_2, 2026-09-21, 2026-09-24
    Sprint Demo Meet S1               :crit, done, s1_3, 2026-09-24, 2026-09-25
    
    section S2: Persistencia OCI & Routing
    Bifurcaciones de Contenido        :done, s2_1, 2026-09-28, 2026-09-30
    Conexión OCI Object Storage       :done, s2_2, 2026-09-28, 2026-10-01
    Sprint Demo Meet S2               :crit, done, s2_3, 2026-10-01, 2026-10-02
    
    section S3: UI Streamlit & Cloud
    Desarrollo Panel Streamlit        :done, s3_1, 2026-10-05, 2026-10-07
    Curaduria Cloud OCI Native        :done, s3_2, 2026-10-06, 2026-10-08
    Sprint Demo Meet S3               :crit, done, s3_3, 2026-10-08, 2026-10-09
    
    section S4: Integración E2E & QA
    Pruebas E2E & Blindaje QA (49/49) :active, s4_1, 2026-10-12, 2026-10-14
    Grabación Demo Preliminar         :active, s4_2, 2026-10-13, 2026-10-15
    Sprint Demo Meet S4               :crit, s4_3, 2026-10-15, 2026-10-16
    
    section S5: Pitch & Demo Day
    Video Demo Final YouTube          :s5_1, 2026-10-19, 2026-10-22
    Pre Demo Meet (Jueves)            :crit, s5_2, 2026-10-22, 2026-10-23
    Demo Day (Presentación Oficial)   :crit, s5_3, 2026-10-27, 2026-10-29
```

> 🟢 **Verde (`done`):** Tareas completadas con éxito.  
> 🔵 **Azul (`active`):** Tareas actualmente en desarrollo activo.  
> 🟠 **Ámbar / Naranja (`crit`):** Hitos críticos y Sprint Demo Meets obligatorios.  
> ⚪ **Gris:** Tareas programadas pendientes para los próximos sprints.

---

### Semana 0: Kickoff, Repositorio, Dataset y VM OCI (Completada con éxito)
* **Objetivo:** Definir reglas de juego, estructura del código, dataset inicial y dejar la infraestructura cloud base operando.
* **Entregables logrados:**
  - [x] Repositorio oficial conectado y clonado.
  - [x] Acta de la 1ª reunión (`PM_Files/acta-primera-reunion_14092026.md`).
  - [x] Estructura base de carpetas creada (`src/`, `data/`, `n8n/`, `PM_Files/`).
  - [x] Archivo `data/interacciones_ejemplo.json` con 15 casos variados (testimonios, dudas técnicas, felicitaciones).
  - [x] **Hito adelantado:** Despliegue de VM Ubuntu Always Free en **OCI Compute** (`147.15.9.116`) con Docker Compose y n8n productivo configurado con volumen persistente.
  - [x] Configuración de variables de entorno seguras (`.env.example` con Gemini, Groq, n8n y OCI).
  - [x] **Sprint Demo Meet S0**.

---

### Semana 1: Ingesta de Datos & Pipeline de LLM (Completada con éxito 🎉)
* **Objetivo:** Ingerir las interacciones de la comunidad y procesarlas a través del LLM devolviendo el JSON estructurado obligatorio.
* **Lunes:** *Sprint Planning Meet*. Asignación formal de tareas.
* **Entregables logrados:**
  - [x] Ingesta y parseo del lote de 15 mensajes en el contenedor de n8n montado desde `./data/`.
  - [x] Conexión con LLM (Gemini / Groq) mediante `Basic LLM Chain`.
  - [x] Implementación de patrón tolerante a fallos y *Rate Limits* (nodo `Loop Over Items` + `Wait` de 10s).
  - [x] Estandarización del prompt del sistema para extracción estricta: `sentimiento`, `tipo_contenido`, `temas_clave`, `post_linkedin` y `tip_tecnico_faq` ([prompt_templates.json](file:///home/cesar-cely/Proyectos/G10-LATAM-equipo6-CommunityLab/src/ai_engine/prompt_templates.json)).
  - [x] Salida de activos formateada y validada en JSON estricto.
  - [x] Script Python complementario con Pydantic en `src/ai_engine/` para validación programática (`schemas.py` y `validator.py`).
* **Jueves:** *Sprint Demo Meet S1*. Demostración en vivo del pipeline en n8n procesando los 15 casos con salida JSON formal.
* **Fin de semana:** Subir entregables de avance a No Country.

---

### Semana 2: Enrutamiento Condicional & Persistencia en OCI Object Storage (Completada con éxito 🎉)
* **Objetivo:** Bifurcar los contenidos clasificados y guardar los paquetes de marketing directamente en la nube de Oracle (Always Free).
* **Lunes:** *Sprint Planning Meet*.
* **Entregables logrados:**
  - [x] Configuración del Bucket en **OCI Object Storage** y credenciales API / Customer Secret Key (S3-compatible).
  - [x] Enrutamiento condicional en n8n con nodo `Switch` (`n8n/workflows/ingestion_groq_subflow.json`):
    - Rama A: Logros/Contrataciones $\rightarrow$ Copys optimizados para LinkedIn y Newsletter.
    - Rama B: Dudas técnicas $\rightarrow$ Formato FAQ / Tip de soporte.
    - Rama C: Feedback general $\rightarrow$ Métricas para el Community Manager.
    - Rama D: Proyectos / Showcase de la comunidad.
  - [x] Subida automatizada de activos a OCI Object Storage (`activos/{fecha}/paquete-distribucion.json`) desde n8n o cliente Python (`src/cloud_oci/storage_client.py`).
  - [x] Verificación de lectura de URLs firmadas / objetos almacenados.
* **Jueves:** *Sprint Demo Meet S2*. Demostración de subida automática al bucket de OCI y verificación de URLs de los paquetes generados.
* **Fin de semana:** Subir entregables a No Country.

---

### Semana 3: Panel de Curaduría en Streamlit & Despliegue en VM OCI (Completada con éxito 🎉)
* **Objetivo:** Dotar a la solución de una interfaz gráfica moderna (desplegada en la VM de OCI) para que los Community Managers revisen, editen y aprueben copys, con arquitectura cloud-native contra OCI Object Storage.
* **Lunes:** *Sprint Planning Meet*.
* **Entregables logrados:**
  - [x] Interfaz web con **Streamlit** en `src/ui/app.py`:
    - Vista 1: Bandeja de curaduría cloud-first con estados dinámicos (`🟢 APROBADO`, `🔴 DESCARTADO`, `🔵 LEÍDO` para FAQs y Feedback) persistidos en `curaduria/curaduria_aprobados.json` en OCI.
    - Vista 2: Orquestador interactivo dual (Motor 1 n8n vía Webhook HTTP y Motor 2 Pipeline Python Nativo con Gemini 2.5).
    - Vista 3: Explorador y gestor de activos archivados en OCI Object Storage (`activos/{YYYY-MM-DD}/*.json`) con capacidad de vaciado en nube.
  - [x] Generación homologada de **4 archivos temáticos especializados** en OCI para ambos motores:
    - `marketing_linkedin_logros.json`
    - `marketing_showcase.json`
    - `faqs_soporte_tecnico.json`
    - `metricas_feedback_comunidad.json`
  - [x] Arquitectura *Stateless* en VM: Eliminación de archivos temporales locales redundantes y deduplicación inteligente consultando directamente OCI Object Storage.
  - [x] Suite de 49 pruebas unitarias e integrales automáticas (`pytest tests/ -v`).
* **Jueves:** *Sprint Demo Meet S3*. Recorrido interactivo completo desde la carga de datos hasta la curaduría en tiempo real con persistencia en OCI.
* **Fin de semana:** Subir entregables a No Country.

---

### Semana 4: Canales Omnicanal, Rediseño UI NovaEdu & Blindaje QA (Completada con éxito 🎉)
* **Objetivo:** Estabilizar la aplicación integral, integrar bots omnicanal en tiempo real (Telegram, Discord, Slack), rediseñar la UI corporativa y expandir la suite de pruebas.
* **Lunes:** *Sprint Planning Meet*.
* **Desarrollo y Avances Logrados:**
  - [x] **Integración Omnicanal en Vivo (`src/channels/`):**
    - Telegram Bot (`@G10_Latam_06_bot`) con long polling en hilo secundario y webhook HTTP seguro para n8n.
    - Discord Bot (`G10-LATAM-06`) con Gateway WebSocket asíncrono y soporte para menciones/canales.
    - Slack Bot con Socket Mode WebSocket sin requerir exponer puertos públicos de entrada.
    - Gestor centralizado `OmnichannelBotManager` con soporte de arranque concurrente y arranque automático con `AUTOSTART_BOTS=true`.
  - [x] **Conmutador Dinámico de Motor (Dual-Engine Live):**
    - Permite conmutar en tiempo real desde el sidebar de Streamlit entre procesamiento local **🐍 Python Nativo (Gemini 2.5/3.5)** o despacho a los flujos de **⚡ n8n Workflow**.
  - [x] **Rediseño Completo de UI (NovaEdu Design System):**
    - Implementación de CSS puro profesional (`src/ui/styles.py`) con paleta Deep Navy (#0d131f), Electric Blue (#3b82f6) y Amber Gold (#f59e0b).
    - Tipografía moderna (Outfit & Inter de Google Fonts), botones interactivos, cards de curaduría con métricas y controles visuales optimizados.
  - [x] **Correcciones Críticas de Resiliencia en Nube:**
    - Corrección en la deserialización de fechas y métricas agregadas en la pestaña *Histórico OCI* (`TypeError NoneType`).
    - Adaptación del webhook de n8n para Telegram para operar en HTTP directo evitando el bloqueo de certificados SSL en IP de OCI.
    - Sincronización dinámica de paquetes procesados hacia OCI Object Storage (`sm.upload_asset_package`).
  - [x] **Expansión y Automatización QA:**
    - Suite automatizada ampliada de 49 a **73 tests unitarios e integrales pasando al 100%** (`pytest tests/ -v`).
  - [x] **Despliegue y Validación en Servidor OCI (`147.15.9.116`):**
    - Apertura de reglas de red (puerto 8501 y 5678) y validación en vivo.
  - [x] **Subworkflow de Generación e Iteración de Imágenes (`CommunityLab_Generador_Imagenes_Post` - José Medina):**
    - Implementación de microservicio síncrono dedicado en n8n (`POST /webhook/generar-imagen-post`).
    - Cadena de 5 nodos: Webhook Trigger $\rightarrow$ Google Gemini (*Prompt Engineer* para traducción y estilo 3D isométrico) $\rightarrow$ Code Node (limpieza y URL encode) $\rightarrow$ Inferencia en Pollinations.ai (modelo FLUX con seed aleatoria por iteración) $\rightarrow$ Subida directa de binario a OCI Object Storage vía S3 (`/previews/preview_{id_post}.png`) $\rightarrow$ Respuesta `200 OK` con URL pública.
  - [ ] **Integración del Generador de Imágenes en Frontend (Streamlit):**
    - Conectar el botón de "Generar / Regenerar Imagen" del Editor de Contenido al endpoint `/webhook/generar-imagen-post`.
    - Input para `instruccion_custom` en la tarjeta de curaduría para ajuste de estilo visual por el Community Manager.
    - Renderizado responsivo de la imagen generada (`preview_{id_post}.png`) en el mockup de LinkedIn con `st.image()`.
  - [x] **Pruebas de Publicación Directa en LinkedIn & X / Twitter (Investigación & POC - Max Ferrer):**
    - **LinkedIn:** Superación de la restricción de 60 días para páginas corporativas mediante creación de página suplementaria vinculada al perfil ([Hackathon ONE G10 Team 6](https://www.linkedin.com/company/hackaton-one-g10-team-6/)). Validación exitosa de publicación automatizada vía `cURL` lista para integrarse.
    - **X (Twitter):** Evaluación de costos y restricciones de planes de pago de la API oficial; investigación de vías alternativas para preservar el principio 100% Free de la Hackathon.
  - [x] **Adaptación del Nuevo Template UI Streamlit Modular (Carol Huarancay, Max Ferrer & César Cely):**
    - Despliegue modular completado y unificado en la rama `main` (`src/ui/components` y `src/ui/views`).
    - Navegación lateral estructurada en 7 secciones:
      - 📊 *Dashboard de la Comunidad:* Métricas globales, gráficos por canal y sentimiento LLM.
      - 📝 *Curaduría Humana Tri-Panel:* Bandeja de pendientes, editor central y preview interactivo con selector de fuente OCI vs Local y solución al cálculo de respuestas IA.
      - 📥 *Procesamiento e Ingesta:* Carga por lotes y conmutación de motor Dual (Python / n8n).
      - ☁️ *Almacenamiento OCI:* Explorador de objetos persistidos, volumen en nube y enlaces PAR.
      - 📡 *Conexiones & Bots:* Monitoreo y control directo de bots omnicanal (Telegram, Discord, Slack).
      - ⚙️ *Settings & Seguridad:* Gestión unificada de variables de entorno protegida con Clave de Verificación Administrativa (`SETTINGS_ADMIN_KEY`).
      - 🩺 *Observabilidad & Logs:* Visor de logs del sistema en tiempo real.
* **Jueves:** *Sprint Demo Meet S4*. Demostración omnicanal en vivo con Telegram, Discord, Slack y panel de curaduría NovaEdu en OCI.
* **Fin de semana:** Subir entregables a No Country.

---

### Semana 5: Pre-Demo, Video Demo Final y Demo Day
* **Objetivo:** Presentación del proyecto ante la comunidad evaluadora y cierre formal de la Hackathon.
* **Lunes:** *Sprint Planning Meet* de cierre. Apertura de feedback entre compañeros en la plataforma.
* **Tareas críticas:**
  - [ ] Integración y pruebas E2E de la Versión 2 del generador de imágenes (opciones avanzadas de aspecto y estilos).
  - [ ] Integración del conector de publicación automática en LinkedIn (aprobación en un clic desde la curaduría).
  - [ ] Consolidación de la adaptación del template UI de Carol & Max en la rama principal.
  - [ ] Grabación y edición del **Video Demo de YouTube** (máximo 10 minutos, destacando el problema de negocio, arquitectura en OCI Always Free, orquestación en n8n e IA, generación de copys e imágenes).
  - [ ] Pulido final del `README.md` (diagrama de arquitectura, capturas de pantalla, badges, pasos de instalación).
  - [ ] **Pre Demo Meet (Jueves):** Ensayo general con mentores de No Country / Oracle.
  - [ ] **Subir entregables finales** (Cierre formal domingo 23:59 pm).
  - [ ] **Demo Day (Martes/Jueves):** Presentación en vivo y pitch del equipo.

