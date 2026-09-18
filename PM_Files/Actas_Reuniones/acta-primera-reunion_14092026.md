# Acta de la Primera Reunión (First Meet) – Equipo 6 (CommunityLab)

**Proyecto:** CommunityLab (Proyecto 3 - No Country)  
**Fecha:** 14 de septiembre de 2026  
**Horario:** 19:00 hs (Hora Colombia / COT)  
**Plataforma:** Google Meet  
**Repositorio Oficial:** `G10 Latam, equipo 6, Community Lab`  

---

## 1. Asistentes y Perfiles del Equipo

* **César Augusto Cely Pulido** (Bogotá, Colombia) [1, 4]  
  * *Perfil:* Jefe de Telecomunicaciones en Retail. Titulado en Ingeniería de Sistemas con especialización en Gerencia de Proyectos y experiencia como Especialista Cloud [1, 4].  
* **Max Ferrer Cabanillas Salas** (Lima, Perú) [1, 4]  
  * *Perfil:* Bachiller en Ingeniería Industrial con más de 10 años de experiencia en TI como desarrollador backend y móvil [1, 4].  
* **Raúl Gallardo** (Buenos Aires, Argentina) [1, 4]  
  * *Perfil:* Trayectoria en Recursos Humanos, Relaciones Laborales, Control de Calidad en Ingeniería y Soporte TI [1, 4].  
* **José Medina** (Paraguay) [1, 4]  
  * *Perfil:* Desarrollador especializado en el ecosistema Oracle (Forms, Reports, Apex), Analista de Sistemas e investigador en N8N y LLMs [1, 4].  
* **Juan Luis Mansilla** (Puerto Montt, Chile) [1, 4]  
  * *Perfil:* Informático en educación municipal con experiencia en administración de redes, desarrollo backend (Ruby on Rails), frontend (Vue, JS) y automatización [1, 4].  
* **Edwin Gustavo Enriquez Arias** (La Paz, Bolivia) [1, 4]  
  * *Perfil:* Desarrollador backend/frontend, especialista en Control de Calidad (QA), automatización de pruebas (Selenium, Playwright) y RPA [1, 4].  

* **Integrantes del equipo no conectados / por contactar:**  
  Carol Yesenia Arancay Osorio, Víctor Araya y Rodrigo Ramírez [4].  

---

## 2. Orden del Día y Puntos Tratados

### 2.1 Organización Horaria y Logística
* Se analizó la dispersión geográfica del equipo (diferencias de 1 a 2 horas entre países) [4].
* Se acordó que el horario nocturno cercano a las **19:00 horas de Colombia (COT)** es la franja de mayor coincidencia para realizar los sincronizaciones de seguimiento [1, 4].

### 2.2 Alcance del Proyecto CommunityLab (MVP)
* César Cely presentó el resumen del desafío: conectar una solución a canales digitales (Discord, Slack, foros) para extraer interacciones, analizar el sentimiento (positivo, neutro, negativo), detectar testimonios clave y generar publicaciones o preguntas frecuentes (FAQ) [4].
* Se validó que el MVP incluirá ingestión de datos, procesamiento con LLMs (Google Gemini), persistencia en **OCI Object Storage (Always Free)** y un panel de curaduría previa en **Streamlit/Gradio** [4].

### 2.3 Repositorio e Infraestructura
* César Cely confirmó la creación previa de la organización y repositorio en GitHub con el nombre `G10 Latam, equipo 6, Community Lab` [4].
* Se solicitó a todos los miembros enviar sus claves SSH/públicas para configurar permisos de lectura y escritura [3, 4].

### 2.4 Debate de Arquitectura: N8N vs. LangChain / LangGraph
* **Propuesta N8N:** Flujo de 6 nodos (Disparador Webhook, Preprocesamiento, IA/Gemini, Router Condicional, Persistencia OCI y Conexión Externa) [4].
* **Discusión de limitaciones:** Max Ferrer señaló la preocupación sobre los requerimientos de memoria de N8N/Docker frente a la restricción de 1 GB de RAM en las instancias gratuitas de OCI [2, 5].
* **Alternativa Swap SSD:** José Medina explicó que en despliegues con Docker/Terraform es posible asignar un espacio virtual *Swap* desde el SSD para solventar la limitación de RAM sin incurrir en costos [5].
* **Evaluación de alternativas:** Edwin Enriquez y José Medina propusieron investigar la viabilidad de usar frameworks basados en código como **LangChain / LangGraph** como sustituto o complemento a N8N [3, 6].

### 2.5 Estrategia para la Simulación de Datos del MVP
* Para evitar la sobrecarga de conexiones a canales masivos, se acordó simular las interacciones en un canal controlado de **Discord** con mensajes del propio equipo o mediante un archivo CSV con un lote de **15 interacciones reales** [5].

---

## 3. Compromisos y Próximos Pasos

| Tarea / Acción | Responsable | Estado |
| :--- | :--- | :--- |
| **Enviar llaves SSH / públicas de GitHub** a César Cely | Todo el equipo [3] | Pendiente |
| **Completar perfil profesional** en la plataforma No Country | Todo el equipo [3] | Pendiente |
| **Configurar servidor de Discord controlado** para pruebas de MVP | Todo el equipo [3] | Pendiente |
| **Investigación individual** del PDF del proyecto usando Gemini | Todo el equipo [3, 5] | En curso |
| **Análisis de limitaciones de memoria en OCI Tier Free** | José Medina [3, 7] | En curso |
| **Evaluación técnica de LangChain / LangGraph vs. N8N** | José Medina, Edwin Enriquez [3, 6] | En curso |
| **Diseño de propuesta de arquitectura técnica** | Edwin Enriquez [3, 6] | En curso |
| **Crear carpeta externa** para documentación de seguimiento | César Augusto Cely Pulido [3] | Pendiente |

---

*Acta redactada a partir de las notas y transcripción oficial de la sesión del 14/09/2026.* [1, 7]
