# Acta de Reunión – Sprint Planning Meet – Equipo 6 (CommunityLab)

**Proyecto:** CommunityLab (Hackathon ONE G10 — Oracle Next Education & Alura / No Country)  
**Fecha:** 21 de septiembre de 2026  
**Horario:** 19:00 hs Hora Colombia (COT) / 21:00 hs Hora Argentina (ART)  
**Plataforma:** Google Meet  
**Repositorio Oficial:** `G10-LATAM-equipo6-CommunityLab`  
**Documento Fuente:** [Notas-Sprint-Planning-Meet_21092026.md](Notas-Sprint-Planning-Meet_21092026.md)  
**Registro y Transcripción Oficial:** [Documento Google Docs](https://docs.google.com/document/d/1No8FWxeM7hYfMi2hF-I1DV1CtnhhHYjnby9wPEKnspM/edit?usp=drive_web&tab=t.afp9131fwiwm)

---

## 1. Asistentes y Ausencias

### Asistentes a la Sesión:
* **César Augusto Cely Pulido** (Project Manager / Cloud Architect & Tech Lead)
* **Max Ferrer Cabanillas Salas** (Backend & Pipeline Developer)
* **Raúl Delfín Gallardo** (QA & Cloud Support)
* **Carol Yesenia Huarancay Osorio** (Frontend / UX & Data)

### Ausentes (Convocados no asistentes):
* **José Medina** (Oracle Ecosystem & n8n / LLMs Specialist)
* **Juan Luis Mansilla** (Backend & Fullstack Developer)
* **Edwin Gustavo Enríquez Arias** (QA Lead & Automation)
* **Rodrigo Ramírez** (Testing & Soporte)
* **Víctor Araya** (Frontend & Documentación)

> *Nota de difusión:* Esta acta se emite de forma detallada y estructurada para garantizar que los miembros ausentes comprendan las decisiones arquitectónicas clave adoptadas, el estado del repositorio principal y los compromisos asignados para la semana.

---

## 2. Resumen Ejecutivo de la Reunión

Durante la sesión se consolidó la unificación de los desarrollos realizados en el orquestador **n8n** y el pipeline en **Python nativo**. Se demostró la arquitectura de persistencia especializada en **Oracle Cloud Infrastructure (OCI) Object Storage**, se estableció la política de control de curaduría y registros de auditoría, y se acordó fusionar el trabajo integrado directamente en la rama principal (`main`). Asimismo, se definieron los alcances de cara a la interfaz de usuario en **Streamlit** y las configuraciones de red pendientes en la máquina virtual (VM) de OCI.

---

## 3. Puntos Tratados y Discusiones Detalladas

### 3.1 Unificación de Repositorios y Resolución de Entornos
* **Diagnóstico de accesos y credenciales:** Raúl Gallardo reportó un incidente con la clave API de Groq durante ejecuciones locales. Por su parte, César Cely expuso que surgieron dificultades de acceso al entorno virtual de OCI, por lo cual se utilizó temporalmente un bucket personal en OCI para contrastar y validar las pruebas de persistencia.
* **Flexibilidad Local vs. Cloud:** Max Ferrer explicó que la arquitectura debía permitir alternar de forma transparente entre contenedores Docker locales y el entorno Always Free en OCI Compute.
* **Consenso:** Se acordó unificar todas las líneas de trabajo y ramas bajo la estructura oficial del repositorio.

### 3.2 Arquitectura Dual Homologada: n8n y Pipeline Python Nativo
* **Convivencia de ambos motores:** Max Ferrer fundamentó que los motores de Python y n8n no son excluyentes sino complementarios:
  * **Motor Python Nativo:** Proporciona inferencia ultrarrápida en memoria (Zero-Hop IPC) con bajo consumo de CPU/RAM, ideal para el procesamiento por lotes en la VM con recursos limitados.
  * **Orquestador n8n:** Aporta flexibilidad visual, manejo de webhooks y capacidad de integración para multiagentes o canales conversacionales (Slack/Discord) en etapas posteriores.
* **Especialización en 4 Archivos Temáticos:** César Cely detalló que ambos motores quedan homologados para clasificar el dataset y generar exactamente los mismos **4 archivos temáticos** en el bucket de OCI:
  1. `marketing_linkedin_logros.json` (Copys para LinkedIn, Twitter y logros destacados).
  2. `marketing_showcase.json` (Proyectos y desarrollos de estudiantes).
  3. `faqs_soporte_tecnico.json` (Tips técnicos y soluciones paso a paso).
  4. `metricas_feedback_comunidad.json` (Salud, sentimiento y retroalimentación de comunidad).

### 3.3 Mitigación de Rate Limits y Trazabilidad (Logging)
* César Cely y Max Ferrer señalaron las constantes restricciones de cuota y saturación de tokens en la capa gratuita de proveedores como Groq y Gemini.
* Para mitigar esto y brindar total observabilidad, se crearon registros de auditoría y trazas rotativas diarias (`logs/communitylab-YYYY-MM-DD.log`), facilitando la depuración durante pruebas con lotes de 3, 5, 7 y 15 interacciones.

### 3.4 Persistencia, Curaduría y Deduplicación en OCI
* **Estructura de particionamiento:** Se validó la convención de guardado en el bucket `communitylab-activos-marketing` bajo la ruta temporal `activos/{YYYY-MM-DD}/`.
* **Control de Curaduría:** César Cely explicó el archivo de persistencia en nube `curaduria/curaduria_aprobados.json` que almacena el estado de cada interacción (`🟢 APROBADO`, `🔴 DESCARTADO`, `🔵 LEÍDO`), garantizando que las revisiones humanas no se pierdan ni se dupliquen entre reinicios.

### 3.5 Alcance del MVP y Requisitos de Ingesta
* Carol Huarancay recordó los lineamientos del reto respecto a la automatización de la recolección (por lotes de 15 registros o canales conversacionales).
* Max Ferrer y César Cely ratificaron que la **prioridad absoluta del MVP** es el procesamiento robusto por lotes (JSON/CSV) hacia OCI Object Storage. Las integraciones automáticas vía bot/webhook en canales de chat en vivo quedan previstas para la fase de refinamiento/post-MVP.

### 3.6 Frontend, UX y Panel de Curaduría en Streamlit
* Max Ferrer enfatizó que la versión funcional actual de Streamlit en `src/ui/app.py` sirvió como banco de pruebas y servicios de backend.
* Se convocó a la **Célula de Frontend** para que lidere el refinamiento visual, usabilidad y diseño del panel para los Community Managers.
* Carol Huarancay asumió el compromiso de proponer y elaborar un prototipo/diseño amigable para optimizar la interfaz de usuario.

### 3.7 Fusión a Rama Principal y Despliegue en VM OCI
* **Merge a `main`:** Con el visto bueno de Max Ferrer y el equipo presente, César Cely ejecutó la fusión formal de la rama integrada (`feat/semana3-integration-e2e`) hacia `main`.
* **Actualización en el Servidor OCI:** Se sincronizaron los servicios en la VM Linux Always Free (`147.15.9.116`, usuario `ubuntu`, directorio `G10-LATAM-equipo6-CommunityLab`).
* **Reglas de Seguridad de Red:** Se identificó que el puerto `8501` (Streamlit) requiere la apertura de reglas de ingreso (Ingress Rules) en la Security List de la VCN en la consola de Oracle Cloud.

---

## 4. Acuerdos y Decisiones Clave

1. **Adopción de Arquitectura Dual:** Se mantienen activos y homologados tanto el **Motor 1 (n8n)** como el **Motor 2 (Python Nativo con Gemini)**, ambos generando los 4 archivos especializados hacia OCI.
2. **Fusión a `main` Completada:** El código probado (49 tests unitarios aprobados al 100%) es la nueva base oficial en la rama `main`.
3. **Persistencia Cloud-First:** OCI Object Storage es la única fuente de verdad; no se almacenarán archivos masivos temporales en el disco de la VM (Arquitectura Stateless).
4. **Próxima Sesión de Trabajo:** Se fijó la siguiente reunión sincrónica para el **miércoles 23 de septiembre de 2026 a las 19:00 hs COT / 21:00 hs ART**.

---

## 5. Matriz de Compromisos y Próximos Pasos

| # | Tarea / Compromiso | Responsable | Célula / Rol | Estado |
| :---: | :--- | :--- | :--- | :---: |
| 1 | **Prototipo Frontend / UI:** Diseñar maqueta o mejoras visuales para el panel de curaduría de Streamlit | Carol Yesenia Huarancay | Célula Frontend | Asignado |
| 2 | **Reglas de Red OCI (Puerto 8501):** Habilitar regla de ingreso (*Ingress Rule*) en la consola de OCI para exponer Streamlit en la IP pública | José Medina / César Cely | Célula Cloud OCI | En curso |
| 3 | **Sincronización Local con `main`:** Ejecutar `git checkout main && git pull origin main` para tener los últimos cambios | Todo el equipo | General | Pendiente |
| 4 | **Configuración de Variables de Entorno Locales:** Ajustar credenciales en `.env` (Gemini, OCI, n8n) usando `.env.example` | Todo el equipo | General | Pendiente |
| 5 | **Comunicación y Notificación:** Difundir esta acta y el estado de la rama `main` por los canales de Discord y WhatsApp del equipo | César Augusto Cely Pulido | PM / Tech Lead | Completado |
| 6 | **Pruebas de Calidad & Casos Extremos (QA):** Diseñar casos de prueba con datos atípicos para validar resiliencia del pipeline | Edwin Enríquez / Raúl Gallardo / Rodrigo Ramírez | Célula QA | En curso |

---

*Acta redactada y homologada por la Coordinación del Equipo 6 a partir de las notas de transcripción oficial y notas de Gemini de la reunión del 21/09/2026.*
