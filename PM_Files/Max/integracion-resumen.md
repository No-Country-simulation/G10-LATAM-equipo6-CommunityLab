# ⚡ Guía Resumen: Integración de Canales Interactivos (Telegram, Discord, Slack)

> **Desarrollador:** Max Ferrer Cabanillas Salas (`mcabanillassalas`)  
> **Proyecto:** CommunityLab - Hackathon ONE G10 (Oracle & Alura / No Country)  
> **Rol:** Backend & Pipeline Developer  
> **Propósito:** Guía ejecutiva y hoja de ruta rápida para que el equipo pueda replicar, configurar y probar localmente los 3 canales interactivos en ambas vías (**Python Puro** y **n8n Nativo**).

---

## 1. Matriz Rápida de Ejecución y Requisitos

Esta tabla resume de un vistazo qué necesita cada canal y cada vía para funcionar en tu entorno local:

| Canal | Motor / Vía | ¿Requiere correr script en consola? | ¿Requiere túnel ngrok? | ¿Opera en simultáneo o requiere alternancia? | Identidad en Chat / Endpoint |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Discord** | **Python Puro** | **SÍ:** `python scripts/run_bots.py --channel discord` | **NO** (WebSocket directo) | **100% Simultáneo** (Sin interferencia) | `@G10-LATAM-06` en `#general` |
| **Discord** | **n8n Nativo** | **NO** (corre autónomo en Docker) | Solo si se llama el webhook externamente | **100% Simultáneo** (Sin interferencia) | Embeds vía Webhook saliente en `#general` |
| **Slack** | **Python Puro** | **SÍ:** `python scripts/run_bots.py --channel slack` | **NO** (Socket Mode WebSocket) | **100% Simultáneo** (Gracias a App 1) | `@G10-LATAM-06` en `#all-g10-latam-06` |
| **Slack** | **n8n Nativo** | **NO** (corre autónomo en Docker) | **SÍ:** `ngrok http 5678` | **100% Simultáneo** (Gracias a App 2) | `@G10-LATAM-06-N8N` en `#all-g10-latam-06` |
| **Telegram** | **Python Puro** | **SÍ:** `python scripts/run_bots.py --channel telegram` | **NO** (Long Polling saliente) | ⚠️ **Alternancia** *(con el token compartido)* | `@G10_Latam_06_bot` |
| **Telegram** | **n8n Nativo** | **NO** (corre autónomo en Docker) | **SÍ:** `ngrok http 5678` | ⚠️ **Alternancia** *(con el token compartido)* | `@G10_Latam_06_bot` |

---

## 2. Preguntas Frecuentes y Respuestas Clave

### Q1: ¿Las 3 integraciones pueden ejecutarse simultáneamente o se necesita hacer algún switcheo?
* **Discord:** **100% Simultáneo.** Python usa el Gateway WebSocket del bot y n8n usa un Webhook URL saliente. Ambos pueden estar activos al mismo tiempo sin ningún conflicto.
* **Slack:** **100% Simultáneo.** Se diseñó una **arquitectura de dos apps separadas en el mismo Workspace (`G10-LATAM-06`)**. Ambas conviven juntas en el canal `#all-g10-latam-06`. Mencionas a `@G10-LATAM-06` y responde Python; mencionas a `@G10-LATAM-06-N8N` y responde n8n. No hay ningún switcheo manual.
* **Telegram:** **Requiere alternancia temporal (con el token actual).** Al compartir un único Bot Token entre Python y n8n, cuando lanzas el script de Python (`Long Polling`), Telegram borra el Webhook de n8n. Para que n8n vuelva a funcionar, debes cerrar Python y reiniciar el contenedor Docker (`docker restart communitylab-n8n`).  
  *(Ver la sección 3.2 para entender cómo funciona la experiencia de usuario si se crean dos bots en Telegram vs Slack)*.

### Q2: ¿Qué Apps necesitan correr un script de Python antes de probar?
**ÚNICAMENTE las vías de Python Puro:**
* Para probar Telegram en Python: `python scripts/run_bots.py --channel telegram`
* Para probar Discord en Python: `python scripts/run_bots.py --channel discord`
* Para probar Slack en Python: `python scripts/run_bots.py --channel slack`

> 💡 **En n8n NO se corre ningún script en consola.**  
> Los 3 flujos de n8n corren de forma autónoma dentro del contenedor Docker `communitylab-n8n` las 24 horas del día.

### Q3: ¿Qué Apps necesitan ejecutar ngrok primero en local?
**ÚNICAMENTE las vías de n8n Nativo (`ngrok http 5678`):**
1. **Slack con n8n (`@G10-LATAM-06-N8N`):** Obligatorio. Slack envía los eventos HTTP POST a la URL pública de ngrok (`/webhook/communitylab-slack`).
2. **Telegram con n8n:** Obligatorio. Telegram notifica al Webhook público que ngrok redirige a Docker.
3. **Discord con n8n:** Opcional. Solo si se desea invocar el Webhook receptor desde un servicio externo a tu máquina.

> 🚫 **Python Puro NUNCA necesita ngrok:**  
> Ninguno de los 3 bots de Python necesita ngrok porque todos se conectan por **conexiones salientes directas** hacia los servidores de Slack (Socket Mode WebSocket), Discord (Gateway WebSocket) y Telegram (Long Polling).

---

## 3. Alcances Adicionales y Relevantes para la Integración

### 3.1 Arquitectura Dual de Slack (¿Por qué 2 Apps?)
En la plataforma de Slack, **Socket Mode** y los **Webhooks HTTP (Request URL)** son **mutuamente excluyentes**:
- Si activas Socket Mode para Python, Slack **desactiva** la casilla de Request URL.
- Para evitar tener que entrar a la web de Slack a cambiar configuraciones cada vez que se prueba una u otra vía, se crearon **dos aplicaciones en el mismo Workspace**:
  1. **`G10-LATAM-06` (App 1):** Con Socket Mode ON y token `SLACK1_...` para Python.
  2. **`G10-LATAM-06-N8N` (App 2):** Con Socket Mode OFF y Request URL de ngrok para n8n.
  Ambas están agregadas como agentes en `#all-g10-latam-06`.

### 3.2 Telegram: ¿Dos Contactos o un Mismo Grupo? (Experiencia de Usuario vs Slack)

> [!NOTE]
> **ACLARACIÓN CLAVE SOBRE TELEGRAM:**  
> A diferencia de Slack (donde existe un workspace con canales compartidos y ambos bots son miembros del canal `#all-g10-latam-06`), en Telegram el comportamiento depende de la modalidad de uso:
> 
> 1. **En Chat Privado (1 a 1):**  
>    Si se crean dos bots en `@BotFather` (ej: `@G10_Python_Bot` y `@G10_N8n_Bot`), el usuario los verá como **dos contactos distintos** en su lista de chats de Telegram y tendrá que elegir a quién escribirle de forma privada.
> 
> 2. **En un Grupo de Telegram (El equivalente exacto a Slack):**  
>    Si se desea tener **exactamente la misma experiencia unificada de Slack**, se crea un **Grupo de Telegram** (ej. *Hackathon G10 CommunityLab*) y se invita a ambos bots:
>    * `@G10_Python_Bot` (escuchando vía Python Long Polling).
>    * `@G10_N8n_Bot` (escuchando vía n8n Webhook).  
>    En el grupo, los miembros interactúan con ambos mediante menciones (`@`) en la misma ventana de conversación, logrando **100% de simultaneidad y convivencia en un solo lugar**.
> 
> 3. **Con un Solo Bot Oficial (Esquema Actual):**  
>    Presenta un único contacto oficial al usuario final (`@G10_Latam_06_bot`), pero exige alternar entre Python y n8n según el motor que se esté evaluando en el momento.

### 3.3 Solución al Doble Mensaje en Slack con n8n (Regla de 3 Segundos)
Slack exige recibir un código `HTTP 200` en menos de **3 segundos**. Como el modelo de IA (Groq) toma ~4.5s en generar la respuesta analítica, Slack disparaba un reintento automático (Retry #1), provocando que n8n respondiera dos veces.
- **Solución implementada en n8n:** El flujo envía un `HTTP 200 {"status":"ok"}` en **0.12 segundos** apenas entra el evento, y luego filtra cualquier cabecera `x-slack-retry-num`. El procesamiento de la IA continúa en segundo plano y publica **una única respuesta limpia** en el hilo.

### 3.4 Modelo de Inteligencia Artificial Validado en n8n
- En todos los flujos de n8n se utiliza el modelo: **`openai/gpt-oss-20b`** en Groq Cloud.
- *(Nota técnica: No usar `llama-3.3-70b-versatile` en Groq ya que retorna error 404 `model_not_found` en planes comunitarios)*.

### 3.5 Persistencia Desacoplada e Independiente
Para que el equipo de frontend/curaduría pueda auditar exactamente qué generó cada motor, la persistencia está dividida:
* **Vía Python:** Guarda acumulativamente en `data/paquete_procesado_canales_python.json`.
* **Vía n8n:** Guarda en `data/paquete_procesado_canales_n8n.json`.
* **Trazabilidad:** Logs diarios rotativos generados en `logs/communitylab-YYYY-MM-DD.log`.

---

### 3.6 Curaduría Omnicanal, Detección de Canales y Sincronización en Streamlit (src/ui/app.py)
Para que los Community Managers puedan auditar, curar y filtrar tanto los lotes generados por pipeline batch como los mensajes procesados en vivo desde bots interactivos:
* **Soporte de Fuentes Múltiples:** El selector de la vista *"Curaduría de Activos"* permite elegir entre los lotes en OCI Storage, el archivo de canales en vivo de Python (data/paquete_procesado_canales_python.json) y el de n8n (data/paquete_procesado_canales_n8n.json).
* **Detección Automática de Canal (detectar_canal_digital):** Algoritmo de resolución multi-criterio que identifica con precisión el canal de procedencia:
  - Inspecciona prefijos de ID: tg_ (Telegram), dc_ (Discord), slk_ (Slack).
  - Inspecciona metadatos nativos: canal_origen_bot, interaccion.canal y metadata_externa.
* **Badges Visuales Distintivos:** Cada tarjeta y encabezado en el panel presenta un badge destacado con su ícono y canal:
  - [✈️ Telegram]
  - [🎮 Discord]
  - [💬 Slack]
  - [📊 Dataset Batch]
* **Filtro Interactivo de 4 Columnas:** La barra superior de filtros ahora cuenta con 4 selectores simultáneos:
  1. *Filtrar por canal de origen* (Todos, ✈️ Telegram, 🎮 Discord, 💬 Slack, 📊 Dataset Batch).
  2. *Filtrar por tipo de activo* (Todos, LinkedIn, X / Twitter, FAQ / Tip).
  3. *Filtrar por estado* (Todos, Pendiente, Aprobado, Descartado).
  4. *Filtrar por sentimiento* (Todos, Positivo, Neutro, Negativo).
* **Sincronización Cloud con un Clic:** Se agregó el botón interactivo [ ☁️ Subir a Storage ] para respaldar el archivo de canales locales directamente hacia Oracle Cloud Infrastructure (OCI Object Storage) como un nuevo lote oficial.
* **Saneamiento y Estabilidad:** Corrección de la importación get_n8n_webhook_url en app.py y sanitización total de credenciales y webhooks en .env.example y flujos de n8n.

---

## 4. Paquete de Documentación para el Equipo

Para que cualquier miembro del equipo pueda replicar todo el entorno localmente, se recomienda compartir el siguiente conjunto de documentos:

1. **`integracion-resumen.md`** *(este documento)*: Visión ejecutiva, tabla rápida, aclaración Telegram/Slack y scripts/ngrok.
2. **`integracion-python.md`**: Guía técnica detallada de la vía Python Puro (instalación, scripts y logs).
3. **`integracion-n8n.md`**: Guía técnica detallada de la vía n8n Nativo (Docker, workflows y solución anti-reintentos).
4. **`ngrok-guia.md`**: Instrucciones para instalar, autenticar y levantar el túnel ngrok local.

### 📌 Documentos Adicionales Recomendados para Adjuntar:
* **`generar-token.md` (¡Altamente Recomendado!):**  
  Detalla paso a paso con capturas y rutas exactas cómo obtener cada token en BotFather (Telegram), Discord Developer Portal y Slack API (`xoxb-...` y `xapp-...`). Sin este documento, un compañero que quiera levantar sus propios bots no sabrá qué casillas marcar.
* **`entorno.md`:**  
  Explica cómo funciona la variable maestra `ENTORNO_DEPLOY=LOCAL` vs `PRODUCCION` y cómo el `docker-compose.yml` conmuta automáticamente las URLs de webhook.
