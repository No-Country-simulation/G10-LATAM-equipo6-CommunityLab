# 🚀 Presentación Ejecutiva de CommunityLab (4 Slides)

> **Proyecto:** CommunityLab — Motor Inteligente de Transformación y Curaduría de Comunidades Digitales  
> **Evento:** Hackathon ONE G10 — Oracle Next Education, Alura & No Country  
> **Equipo:** Equipo 6 — LATAM  
> **Formato:** Presentación Ejecutiva de 4 Diapositivas (~5 minutos)  
> **Documento PDF Oficial:** [`PM_Files/Presentacion_CommunityLab_4_Slides.pdf`](Presentacion_CommunityLab_4_Slides.pdf)

---

## 🖥️ SLIDE 1: Portada, Problema y Propuesta de Valor

### 📌 Contenido Visual de la Diapositiva
* **Título Principal:** CommunityLab
* **Subtítulo:** Motor Inteligente de Transformación y Curaduría para Comunidades Digitales
* **Badge / Contexto:** Hackathon ONE G10 | Oracle Next Education & Alura | Equipo 6 LATAM

#### 🔴 El Problema de las Comunidades Masivas
* **Sobrecarga de Información:** Comunidades técnicas educativas con miles de mensajes diarios en Discord, Telegram y Slack.
* **Pérdida de Valor Orgánico:** Más del 90% de contrataciones estudiantiles, resoluciones técnicas de código y testimonios inspiradores quedan sepultados en el chat.
* **Cuello de Botella Manual:** La curaduría artesanal toma horas a los Community Managers y retrasa la amplificación del impacto institucional.

#### 🟢 La Solución CommunityLab
* **Escucha Activa Omnicanal:** Ingesta en tiempo real mediante bots de Telegram, Discord y Slack + procesamiento de lotes históricos.
* **Enriquecimiento con IA Multimodal:** Generación automática de posts para LinkedIn, hilos de X, FAQs técnicas y métricas comunitarias.
* **Impacto Inmediato:** Transformación en segundos a **Costo $0 de Infraestructura** (100% Oracle Cloud Infrastructure Always Free).

### 🎙️ Guion / Notas del Presentador (Slide 1)
> *"Muy buenos días a todos. Somos el Equipo 6 de la Hackathon Oracle ONE y les presentamos **CommunityLab**. En comunidades educativas masivas como ONE y Alura, miles de estudiantes interactúan a diario compartiendo logros increíbles, contrataciones y dudas técnicas. Sin embargo, más del 90% de ese valor se pierde en el historial de Discord, Telegram y Slack porque curarlo manualmente es inviable. **CommunityLab** resuelve este dolor: escucha activamente la comunidad, extrae ese valor con IA generativa, lo enriquece con piezas visuales y lo deja listo para aprobación y distribución oficial en un solo clic, operando 100% sobre la capa Always Free de Oracle Cloud."*

---

## 🖥️ SLIDE 2: Arquitectura Técnica & Ecosistema Oracle Cloud

### 📌 Contenido Visual de la Diapositiva
* **Título Principal:** Arquitectura Cloud-Native & Orquestación Dual
* **Subtítulo:** Robustez Empresarial 100% en Oracle Cloud Infrastructure (Always Free)

```text
[ Telegram / Discord / Slack ] ──► [ Despachador Omnicanal ]
          ▲                                    │
          │                        ┌───────────┴───────────┐
          │                        ▼                       ▼
          │               [ Motor Python ]         [ Motor n8n ]
          │               Gemini 2.5 Flash       Groq Llama 3 / S3
          │                        │                       │
          │                        └───────────┬───────────┘
          │                                    ▼
[ OCI Compute + Caddy SSL ] ◄─── [ OCI Object Storage ] (4 Archivos JSON + PAR)
```

#### ☁️ Pilares de Infraestructura OCI Always Free
* **OCI Compute VM (Ubuntu):** Alojamiento de la app modular Streamlit, bots omnicanal y contenedor Docker de n8n.
* **OCI Object Storage:** Persistencia cronológica (`activos/YYYY-MM-DD/*.json`) con descubrimiento automático y ordenación inversa.
* **Tokens PAR (Pre-Authenticated Requests):** Visualización privada y segura de imágenes sin exponer públicamente el bucket.
* **Dominio & SSL Caddy:** Conexión segura HTTPS con certificados automáticos Let's Encrypt ([hackathon-g10-latam-06.duckdns.org](https://hackathon-g10-latam-06.duckdns.org)).

#### ⚙️ Dual-Engine Homologado
* **🐍 Python Nativo:** Inferencia directa con Google Gemini 2.5 Flash y validación estricta con Pydantic v2 (~2 a 4 seg).
* **⚡ Orquestador n8n:** Webhooks HTTP síncronos en contenedor Docker con Groq LLM y conector directo S3.
* **Especialización en 4 Archivos Temáticos:** `marketing_linkedin_logros`, `marketing_showcase`, `faqs_soporte_tecnico` y `metricas_feedback_comunidad`.

### 🎙️ Guion / Notas del Presentador (Slide 2)
> *"Nuestra arquitectura fue diseñada con estándares empresariales de alta disponibilidad y tolerancia a fallos. Implementamos un pipeline **Dual-Engine homologado**: podemos procesar datos tanto con un motor nativo en Python usando Gemini 2.5 Flash, como a través de flujos visuales en n8n con Groq. Toda la información se valida con esquemas Pydantic estrictos y se persiste en Oracle Cloud Object Storage organizada en cuatro archivos temáticos especializados. Además, implementamos tokens PAR para que las imágenes privadas se rendericen de forma segura en el navegador sin comprometer los datos de la nube."*

---

## 🖥️ SLIDE 3: Demostración Funcional: Curaduría Humana Tri-Panel & IA Generativa

### 📌 Contenido Visual de la Diapositiva
* **Título Principal:** Centro de Curaduría Humana Tri-Panel & Generación Multimedia
* **Subtítulo:** Control Total, Accesibilidad de Alto Contraste y Decisión en 1 Clic

#### 1️⃣ Panel Izquierdo: Gestión y Filtros
* **Pastillas Segmentadas (*Segmented Pills*):** Filtrado ágil por `Todos`, `Pendientes`, `Aprobados`, `Publicados`.
* **Filtros Combinados:** Sentimiento (Positivo/Neutro/Negativo), Canal de Ingesta y Motor de Orquestación.
* **Selector de Fuente OCI / Local:** Descubrimiento dinámico de los paquetes generados en el día.

#### 2️⃣ Panel Central: Edición & Generador de Imágenes
* **Editor de Copys Multicanal:** Ajuste rápido de texto generado para LinkedIn y X con conteo de caracteres.
* **Generador Visual Dual-Engine:** Inferencia de imágenes con Gemini 2.5 o n8n + Pollinations FLUX + subida de adjuntos locales.
* **Botonera Dinámica Semántica:** Botones interactivos que reflejan el estado del activo (`✅ Aprobado (Activo)`, `❌ Descartado (Activo)`, `👁️ Leído (Activo)`).

#### 3️⃣ Panel Derecho: Mockup en Tiempo Real & Publicación
* **Previsualización Fidedigna:** Simulación de interfaz nativa para LinkedIn, X, Discord y Slack.
* **Conmutador de Dispositivo:** Verificación de legibilidad en pantallas de escritorio y dispositivos móviles.
* **Persistencia Inmediata:** Registro formal en `curaduria_aprobados.json` listo para integración API.

### 🎙️ Guion / Notas del Presentador (Slide 3)
> *"El corazón operativo de CommunityLab es su **Centro de Curaduría Humana Tri-Panel**. En el panel izquierdo, el moderador cuenta con filtros instantáneos por pastillas segmentadas y un selector de fuente en OCI que detecta automáticamente los archivos generados en el día. En el panel central, revisa el copy generado por la IA, puede generar imágenes temáticas con FLUX o Gemini, y toma decisiones mediante botones dinámicos con alto contraste y estados activos visibles. Finalmente, en el panel derecho, visualiza en tiempo real cómo lucirá el post en LinkedIn o X antes de publicarlo. Esto garantiza un control editorial humano del 100% antes de cualquier distribución oficial."*

---

## 🖥️ SLIDE 4: Equipo Multidisciplinario, Rigor QA & Impacto

### 📌 Contenido Visual de la Diapositiva
* **Título Principal:** Equipo Multidisciplinario, Rigor QA & Resultados
* **Subtítulo:** Compromiso Ágil, Automatización y Despliegue en Producción

#### 👥 Equipo 6 LATAM (7 Integrantes)
| Integrante | Ubicación | Especialidad / Rol |
| :--- | :--- | :--- |
| **César Augusto Cely Pulido** | Bogotá, Colombia | **Project Manager & Cloud Architect** |
| **Max Ferrer Cabanillas Salas** | Lima, Perú | **Backend & Pipeline Developer** |
| **José Medina** | Paraguay | **Oracle Ecosystem & N8N / LLMs Specialist** |
| **Edwin Gustavo Enriquez Arias** | La Paz, Bolivia | **QA Lead, Testing Automation & Backend** |
| **Carol Yesenia Arancay Osorio** | Lima, Perú | **Frontend / UX & Data** |
| **Raúl Gallardo** | Buenos Aires, Argentina | **QA & Cloud Support** |
| **Luygy Ruben Vivas Moreno** | Colombia | **QA & Pruebas Funcionales** |

#### 🏆 Indicadores de Éxito & Calidad
* **Rigor QA:** **82 de 82 pruebas automatizadas pasando al 100% (`pytest tests/ -v`)** cubriendo ingesta, validación Pydantic, cliente OCI, bots y frontend.
* **Semana Ganada de Ventaja:** Gracias a la velocidad de entrega en el sprint, la Semana 5 se dedicó íntegramente a *hardening*, pruebas de carga y blindaje de accesibilidad.
* **Despliegue Productivo en Vivo:** Aplicación operativa 24/7 con certificado SSL en [`https://hackathon-g10-latam-06.duckdns.org`](https://hackathon-g10-latam-06.duckdns.org).

### 🎙️ Guion / Notas del Presentador (Slide 4)
> *"Detrás de CommunityLab hay un equipo multidisciplinario de siete profesionales de cinco países de Latinoamérica trabajando bajo metodología ágil. Gracias a nuestra disciplina y rigor técnico, logramos una suite de **82 pruebas automatizadas pasando al 100%** y terminamos el desarrollo una semana antes de lo previsto, permitiéndonos blindar la seguridad, la resiliencia de los bots y la accesibilidad de la interfaz. CommunityLab no es solo un prototipo: es una solución real, desplegada en producción sobre Oracle Cloud y lista para transformar la manera en que las comunidades técnicas comunican su éxito al mundo. ¡Muchas gracias!"*

---

## 📊 Matriz Comparativa de las 4 Diapositivas

| Diapositiva | Objetivo Principal | Concepto Clave | Tiempo Sugerido |
| :---: | :--- | :--- | :---: |
| **Slide 1** | **El Problema & La Solución** | Pérdida de valor orgánico $\rightarrow$ Escucha activa omnicanal | 1:15 min |
| **Slide 2** | **Arquitectura Técnica** | OCI Always Free + Dual-Engine (Python Gemini / n8n Groq) | 1:15 min |
| **Slide 3** | **Demostración de Funcionalidades** | Tri-Panel de Curaduría + Generador de Imágenes IA | 1:30 min |
| **Slide 4** | **Equipo, QA & Conclusión** | 7 Miembros LATAM + 82/82 Tests + Producción en Vivo | 1:00 min |
