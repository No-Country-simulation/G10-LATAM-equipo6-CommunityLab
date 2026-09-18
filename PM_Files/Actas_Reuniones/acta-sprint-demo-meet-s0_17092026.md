# Acta de Reunión – Sprint Demo Meet S0 – Equipo 6 (CommunityLab)

**Proyecto:** CommunityLab (Hackathon ONE G10 — Oracle Next Education & Alura / No Country)  
**Fecha:** 17 de septiembre de 2026  
**Horario:** 18:55 GMT-05:00 (19:00 hs Hora Colombia / COT)  
**Plataforma:** Google Meet  
**Repositorio Oficial:** `G10-LATAM-equipo6-CommunityLab`  
**Documento Fuente:** [Sprint Demo Meet (obligatorio) - 2026_09_17 18_55 GMT-05_00 - Notas de Gemini.md](file:///home/cesar-cely/Proyectos/G10-LATAM-equipo6-CommunityLab/PM_Files/Actas_Reuniones/Sprint%20Demo%20Meet%20%28obligatorio%29%20-%202026_09_17%2018_55%20GMT-05_00%20-%20Notas%20de%20Gemini.md)  
**Grabación / Transcripción:** [Registro oficial en Google Docs](https://docs.google.com/document/d/1l-16hZqBr15HDEG3xFsCaAGHImTt7vEBuRdBRKrvzRg/edit?usp=drive_web&tab=t.ig9bhj31sr3o)

---

## 1. Asistentes

* **César Augusto Cely Pulido** (Product Manager / Cloud & Tech Lead)
* **José Medina** (Admin VM / Cloud OCI & N8N)
* **Juan Luis Mansilla** (Backend & Automatización)
* **Edwin Gustavo Enríquez Arias** (Especialista QA & Automatización)
* **Raúl Delfín Gallardo** (Infraestructura / Soporte TI / RRHH)
* **Max Ferrer Cabanillas Salas** (Backend & Móvil)
* **Carol Yesenia Huarancay Osorio** (Frontend & QA)

---

## 2. Orden del Día y Puntos Tratados

### 2.1 Presentación del Equipo y Perfiles en Comunidad
* Se solicitó a los miembros compartir los enlaces de sus perfiles de LinkedIn en el canal de Discord del equipo.
* César Cely consolidará esta información para realizar la presentación oficial del equipo en el canal general de No Country / Discord.

### 2.2 Sincronización de GitHub y Docker en Entorno Local vs. VM
* Juan Luis Mansilla expuso una incidencia local al levantar Docker relacionada con un volumen externo no encontrado, solucionada creando el volumen manualmente.
* César Cely aclaró que este comportamiento provino de la configuración específica del despliegue Docker realizado por José Medina en la VM de Oracle Cloud Infrastructure (OCI), confirmando el estándar para levantar el stack en local.

### 2.3 Avance del Roadmap y Entrega del MVP (Semana 0 / Sprint Demo S0)
* Se validó el cumplimiento total de los objetivos de la Semana 0:
  1. Estructuración y versionado del repositorio en GitHub.
  2. Despliegue en máquina virtual Linux en **OCI Compute (Always Free)** gestionado por José Medina y César Cely.
  3. Configuración de **Docker y n8n** en la VM remota.
  4. Dataset de pruebas con 15 interacciones representativas de comunidad (`data/interacciones_ejemplo.json`).
  5. Conexión de n8n con motor de IA y normalización de *system prompts*.

### 2.4 Demostración en Vivo de n8n y Resiliencia del Pipeline de IA
* César Cely ejecutó una demo en vivo procesando el lote de 15 casos de prueba en n8n:
  * **Modelo de IA y balanceo:** Se integró y probó Grok en paralelo con Google Gemini para evaluar velocidad y límites de tasa/cuotas.
  * **Estructura de salida JSON estricta:** Sentimiento (positivo, neutro, negativo), tipo de contenido, tecnologías clave extraídas, copys generados para LinkedIn y tips/soluciones técnicas integradas.
  * **Patrón tolerante a fallos (Rate Limit & Token Handling):** Se implementó una espera fija de 12 segundos entre mensajes y una política de reintentos automática (3 intentos con intervalo de 5 segundos) para evitar bloqueos por consumo de tokens.
  * **Manejo de credenciales y versiones:** Los flujos en n8n son importables vía JSON desde GitHub; cada desarrollador puede configurar sus credenciales y guardar versiones de trabajo agregando sus iniciales al nombre del workflow.

### 2.5 Arquitectura de Datos, Curaduría (Streamlit) y Bucket OCI
* **Panel de Curaduría:** Se aclaró que la interfaz en Streamlit permitirá curar, editar y validar copys antes de publicarse, así como reprocesar manualmente registros atípicos (feedback loop).
* **Alcance MVP:** La publicación automática directa en redes sociales (APIs de LinkedIn/X) queda excluida del MVP inicial y se abordará en fases posteriores.
* **Persistencia en la Nube:** Persistencia obligatoria de los JSONs procesados en un Bucket de **OCI Object Storage (Always Free)**. José Medina liderará la configuración del bucket y provisión de variables de conexión.

### 2.6 Acuerdos de Gestión y Frecuencia de Sincronización
* A propuesta de Carol Huarancay y consensuado por el equipo (Raúl Gallardo, José Medina, Edwin Enríquez), se fijó el calendario semanal de reuniones cortas de seguimiento:
  * **Días:** Lunes, Miércoles y Jueves.
  * **Horario:** 19:00 hs (Hora Colombia / COT).
  * **Duración:** Sesiones breves de 15 a 30 minutos para destrabar bloqueos y revisar avances.

---

## 3. Acuerdos y Decisiones Clave

1. **Cadencia de Reuniones:** Quedan establecidas sesiones de seguimiento obligatorias y cortas los días **lunes, miércoles y jueves a las 19:00 hs COT**.
2. **Control de Versiones en n8n:** Para no sobreescribir flujos compartidos en la VM, cada miembro nombrará sus flujos de trabajo agregando su sufijo/iniciales (ej. `wf_procesamiento_ingesta_CC`).
3. **Persistencia OCI:** El almacenamiento oficial para copys y métricas procesadas será un Bucket de **Oracle Cloud Infrastructure (OCI) Object Storage**.
4. **Resiliencia en LLMs:** El flujo de n8n mantendrá pausas y políticas de reintento configuradas para operar dentro de las cuotas gratuitas de las APIs de IA (Gemini / Grok).

---

## 4. Compromisos y Plan de Acción (Sprint 1)

| # | Tarea / Compromiso | Responsable | Célula / Área | Estado |
| :---: | :--- | :--- | :--- | :---: |
| 1 | Compartir enlace del perfil de LinkedIn en el Discord del equipo | Todo el equipo | General | Pendiente |
| 2 | Armar y publicar la presentación oficial del equipo en el Discord general | César Augusto Cely Pulido | PM / Coordinación | Pendiente |
| 3 | Levantar y realizar revisión técnica del ambiente en la máquina virtual (OCI) | Edwin Gustavo Enríquez Arias | Célula 1 & 3 (QA / Infra) | Pendiente |
| 4 | Configurar el Bucket en OCI Object Storage y proveer variables de entorno | José Medina | Célula 2 (Cloud OCI) | Pendiente |
| 5 | Definir el subflujo/nodo de n8n para exportación y carga al Bucket de OCI | César Cely / José Medina | Célula 1 & 2 (n8n / OCI) | Pendiente |
| 6 | Programar y enviar invitaciones para las reuniones de lunes, miércoles y jueves | César Augusto Cely Pulido | PM / Coordinación | En curso |
| 7 | Diseñar la lógica de bifurcación (*switch*) por tipo de contenido en n8n | Célula de IA (Edwin, Juan Luis, Max) | Célula 1 (IA & n8n) | Pendiente |
| 8 | Inicio de maqueta y prototipo de la UI de curaduría en Streamlit | Célula Frontend (Carol, Edwin, Rodrigo) | Célula 3 (Streamlit) | Pendiente |

---

*Acta consolidada y homologada a partir de la transcripción oficial y notas de Gemini de la sesión del 17/09/2026.*
