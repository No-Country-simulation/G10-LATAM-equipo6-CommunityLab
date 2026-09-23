# 🤖 Guía Técnica: Interacciones Dinámicas Nativas con n8n (Telegram, Discord, Slack)

Esta guía documenta la **Vía n8n Nativa** para interactuar dinámicamente con **Telegram, Discord y Slack**. En este enfoque, el orquestador visual n8n gestiona el ciclo de vida completo mediante Webhooks, procesa la inferencia mediante nodos de Inteligencia Artificial (Groq Cloud) y responde de vuelta a cada plataforma con formatos enriquecidos (Markdown, Embeds y Slack Blocks).

---

## 1. Principio Fundamental: Independencia Total entre n8n y Python Puro

> [!IMPORTANT]
> **REGLA DE ARQUITECTURA DEL PROYECTO:**  
> Los procesos de **n8n** y los procesos de **Python puro** son dos vías **completamente independientes, desacopladas y paralelas**.
>
> - **Vía n8n Nativo:** Se orquesta visualmente dentro del contenedor Docker de n8n, atiende peticiones vía Webhook público (ngrok) y persiste en `data/paquete_procesado_canales_n8n.json`.
> - **Vía Python Puro:** Se ejecuta vía `scripts/run_bots.py`, atiende peticiones salientes por Long Polling / WebSocket y persiste en `data/paquete_procesado_canales_python.json`.

---

## 2. Estado de los Flujos en tu n8n Local

Los 3 flujos nativos ya fueron creados e **importados automáticamente en tu contenedor Docker de n8n** (`http://localhost:5678`):

| Flujo en n8n                         | Archivo en Repositorio                              | Canal    | Formato de Respuesta                        |
| :----------------------------------- | :-------------------------------------------------- | :------- | :------------------------------------------ |
| **`CommunityLab_Telegram_Dinamico`** | `n8n/workflows/communitylab_telegram_dinamico.json` | Telegram | Markdown con emojis + análisis + tip/post   |
| **`CommunityLab_Discord_Dinamico`**  | `n8n/workflows/communitylab_discord_dinamico.json`  | Discord  | Embed enriquecido con color por sentimiento |
| **`CommunityLab_Slack_Dinamico`**    | `n8n/workflows/communitylab_slack_dinamico.json`    | Slack    | Slack Block Kit en hilo (*thread_ts*)       |

---

## 3. Modelo de IA Validado en n8n: `openai/gpt-oss-20b`

> [!TIP]
> **Configuración del Modelo Groq:**  
> Anteriormente el flujo utilizaba `llama-3.3-70b-versatile`, el cual generaba un error `404 model_not_found` en las cuentas de Groq Cloud estándar.  
> Se actualizó el nodo **Groq Chat Model** (tanto en el lienzo como en el historial de publicación `workflow_history`) al modelo validado y altamente eficiente:
> **`openai/gpt-oss-20b`**  
> Este modelo genera respuestas estructuradas en JSON de alta calidad que alimentan directamente al `Structured Output Parser`.

---

## 4. Requisito de Red y Docker: Túnel ngrok y `ENTORNO_DEPLOY`

Telegram, Discord y Slack necesitan enviar peticiones HTTP POST a una URL pública con HTTPS.

1. **Levantar el túnel ngrok hacia el puerto 5678 de n8n:**
   ```powershell
   ngrok http 5678
   ```
   ngrok entregará una URL como:
   `https://<TU_SUBDOMINIO>.ngrok-free.app`

2. **Actualizar `.env` con la URL generada:**
   ```ini
   ENTORNO_DEPLOY=LOCAL
   N8N_LOCAL_WEBHOOK_BASE=https://<TU_SUBDOMINIO>.ngrok-free.app/
   N8N_LOCAL_WEBHOOK_URL=https://<TU_SUBDOMINIO>.ngrok-free.app/webhook/communitylab-ingesta
   ```

3. **Arranque inteligente en Docker:**
   Al ejecutar `docker compose up -d`, el `entrypoint` dinámico detecta `ENTORNO_DEPLOY=LOCAL` e inyecta la URL de ngrok tanto en `WEBHOOK_URL` como en `N8N_WEBHOOK_URL`, permitiendo que n8n registre automáticamente el webhook oficial en Telegram.

---

## 5. Reglas Clave al Usar el Flujo de Telegram en n8n

### Regla 1: NO pulsar "Execute workflow" si el flujo está `Published` (Verde)
- Cuando el flujo está en modo **Published**, n8n ya tiene registrado el webhook de producción ante Telegram.
- Si haces clic en el botón naranja *"Execute workflow"* o *"Test this trigger"*, n8n intenta conectar un webhook temporal de pruebas (`/webhook-test/...`), arrojando el error de advertencia:
  > *"Because of limitations in Telegram Trigger, n8n can't listen for test executions at the same time as listening for production ones."*
- **Uso correcto:** Con el flujo en verde (`Published`), **NO** presiones ningún botón en n8n. Simplemente escribe en el chat de Telegram y n8n responderá automáticamente.

### Regla 2: Coexistencia con `run_bots.py` (Long Polling)
- Si ejecutas el script de Python `python scripts/run_bots.py --channel telegram` con el mismo token, Python forzará a Telegram a borrar el Webhook (`deleteWebhook`).
- Si luego detienes Python y quieres que n8n vuelva a responder, debes restaurar el Webhook de n8n simplemente reiniciando el contenedor:
  ```bash
  docker restart communitylab-n8n
  ```
- **Mejor Práctica recomendada:** Asignar en `@BotFather` un bot dedicado para Python y otro para n8n, garantizando que ambos puedan funcionar en paralelo sin tocarse.

---

## 6. Verificación del Webhook de Telegram

Para comprobar el estado de registro del webhook ante los servidores de Telegram, ejecuta:
```bash
curl -s "https://api.telegram.org/bot<TU_TOKEN>/getWebhookInfo"
```

**Salida correcta esperada:**
```json
{
  "ok": true,
  "result": {
    "url": "https://<TU_SUBDOMINIO>.ngrok-free.app/webhook/bddb1a63-db0d-42b4-b168-50fb6958f0b9/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

---

## 7. Integración de Discord con n8n (Flujo Dinámico con Embeds)

### 7.1 Arquitectura del Flujo (`CommunityLab_Discord_Dinamico`)

El flujo nativo de Discord en n8n (`DC001CommunityLb`) opera con una arquitectura desacoplada de alto rendimiento:

```
[Cliente / Canal / App]
       │
       ▼ (HTTP POST con author, content, channel)
[Discord Webhook Inbound]
       │
       ▼
[Procesador IA Discord] (Groq 'openai/gpt-oss-20b')
       │
       ▼
[Structured Output Parser] (Valida esquema JSON estricto)
       │
       ▼
[Formatear Discord Embed] (Asigna color HEX por sentimiento y campos clave)
       │
       ├────────────────────────────────────────┐
       ▼                                        ▼
[Enviar a Canal Discord]               [Responder a Webhook Discord]
(Publica Embed vía webhook oficial)     (HTTP 200 con JSON procesado)
```

### 7.2 Lógica de Color Dinámico en Discord Embed
El nodo **Formatear Discord Embed** (`Code`) asigna un color hexadecimal codificado a decimal según el sentimiento detectado por la IA:
- **Positivo (`0x2ecc71` / 3066993):** Verde esmeralda.
- **Negativo (`0xe74c3c` / 15158332):** Rojo carmesí.
- **Neutro (`0xf1c40f` / 15844367):** Amarillo oro.

### 7.3 Configuración del Webhook Saliente a Discord
- **URL de Webhook del Canal (`#general`):**
  `https://discord.com/api/webhooks/<WEBHOOK_ID>/<WEBHOOK_TOKEN>`
- **Variable de Entorno asociada en `.env`:**
  ```ini
  DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/<WEBHOOK_ID>/<WEBHOOK_TOKEN>
  ```

---

## 8. Integración de Slack con n8n (Flujo Dinámico con Block Kit)

### 8.1 ¿Por qué se requieren DOS Apps de Slack distintas? (Arquitectura Dual Explicada)

En la plataforma de Slack Developer, **Socket Mode** y los **Webhooks HTTP (Request URL)** son **mutuamente excluyentes por aplicación**:

* **La Limitación Estricta de Slack:** Si en una app activas *Socket Mode* (`xapp-...`), Slack **inhabilita completamente** la casilla de *Request URL* y enruta el 100% de los eventos hacia el WebSocket saliente (el cual escucha el script de Python). Slack no permite enviar simultáneamente el mismo evento por WebSocket y por HTTP POST en una misma aplicación.
* **La Solución Arquitectónica:** Crear **dos aplicaciones independientes** dentro del **mismo Workspace (`G10-LATAM-06`)** y agregarlas al mismo canal (`#all-g10-latam-06`):

| Aplicación en Slack | Rol / Motor | Modo de Conexión | ¿Requiere script en terminal? | Tokens en `.env` | Identidad en Chat |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **App 1: `G10-LATAM-06`** | **Python Puro** | **Socket Mode** (`ON`) | **SÍ:** `python scripts/run_bots.py --channel slack` | `SLACK1_LOCAL_BOT_TOKEN`<br>`SLACK1_LOCAL_APP_TOKEN` | `@G10-LATAM-06` (logo `E06`) |
| **App 2: `G10-LATAM-06-N8N`** | **n8n Nativo** | **Webhook HTTP** (Socket Mode `OFF`, Request URL) | **NO:** Corre 24/7 en Docker automáticamente | `SLACK2_LOCAL_BOT_TOKEN` | `@G10-LATAM-06-N8N` (logo `E06`) |

> [!TIP]
> **Ventaja Clave:** Ambas inteligencias conviven de forma pacífica y simultánea en el mismo canal. Cuando mencionas a `@G10-LATAM-06` responde Python; cuando mencionas a `@G10-LATAM-06-N8N` responde n8n, sin necesidad de alternar configuraciones.

---

### 8.2 Guía Paso a Paso de Configuración de la App 2 (`G10-LATAM-06-N8N`) en `api.slack.com`

1. **Crear la App:**
   - Ingresa a [api.slack.com/apps](https://api.slack.com/apps) -> Haz clic en **Create New App** -> Selecciona **From scratch** (Blank app).
   - **App Name:** `G10-LATAM-06-N8N`.
   - **Workspace:** Selecciona el **mismo**: `G10-LATAM-06`.
2. **Socket Mode (¡Crucial!):**
   - Ve a **Socket Mode** en el menú izquierdo.
   - **Asegúrate de que Socket Mode esté en OFF (Desactivado)**. Si estuviera activo, Slack bloquearía la casilla de Request URL.
3. **OAuth & Permissions:**
   - Ve a **OAuth & Permissions** -> Desplázate a **Bot Token Scopes** y añade:
     - `app_mentions:read` (para recibir eventos de menciones).
     - `chat:write` (para publicar mensajes).
     - `channels:history` (para consultar el canal).
   - Sube y haz clic en el botón verde: **Install to G10-LATAM-06**.
   - Copia el **Bot User OAuth Token** (`xoxb-...`) y colócalo en el `.env`:
     ```ini
     SLACK2_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK2_BOT_TOKEN>
     ```
4. **Event Subscriptions:**
   - Ve a **Event Subscriptions** en el menú izquierdo y activa **Enable Events -> ON**.
   - En **Request URL**, pega tu URL de webhook de ngrok:
     ```text
     https://<TU_SUBDOMINIO_NGROK>.ngrok-free.app/webhook/communitylab-slack
     ```
     *(Slack enviará un challenge HTTP POST instantáneo. El flujo de n8n responderá con el valor del challenge y aparecerá un check verde: `Verified ✔`)*.
   - Despliega **Subscribe to bot events**:
     - Haz clic en **Add Bot User Event**.
     - Selecciona: **`app_mention`**.
   - Haz clic en el botón verde inferior: **Save Changes**. (Si Slack pide reinstalar la app por cambio de scopes, haz clic en el aviso superior para reinstalar).
5. **Invitar a `@G10-LATAM-06-N8N` al Canal:**
   - En la app de Slack, entra en `#all-g10-latam-06`.
   - Escribe `/invite @G10-LATAM-06-N8N` y agrégalo.

---

### 8.3 ¿Hay que correr algún script en consola para n8n?

> [!NOTE]
> **NO, ABSOLUTAMENTE NINGUNO.**  
> A diferencia de Python Puro (que requiere ejecutar `python scripts/run_bots.py --channel slack` en una consola abierta), el bot de n8n (`@G10-LATAM-06-N8N`):
> 1. Se ejecuta dentro del contenedor Docker `communitylab-n8n` que está levantado 24/7 en segundo plano.
> 2. Recibe las llamadas entrantes a través del túnel `ngrok http 5678`.
> 3. Funciona de manera totalmente autónoma: solo con mencionar a `@G10-LATAM-06-N8N` en Slack, n8n se despierta, procesa y publica.

---

### 8.4 Resolución del Problema de la Doble Respuesta (Slack Timeout & Retries)

Durante las primeras pruebas en vivo, al realizar una sola pregunta a `@G10-LATAM-06-N8N`, el bot respondía **dos veces** en el hilo. La investigación en la base de datos de n8n reveló dos ejecuciones (`ID 21` e `ID 22`) separadas por **exactamente 3.003 segundos**.

#### La Causa Técnica (Regla de los 3 Segundos de Slack):
Slack exige que cualquier servidor receptor de Webhooks devuelva un código `HTTP 200` en **menos de 3 segundos**. Como el LLM de Groq (`openai/gpt-oss-20b`) tomaba ~4.5 segundos en generar la respuesta estructurada, Slack daba por fallida la entrega y disparaba un **reintento automático (Retry #1)** con las cabeceras `X-Slack-Retry-Num: 1` y `X-Slack-Retry-Reason: http_timeout`. Al procesar ambos eventos, n8n publicaba dos veces.

#### La Solución Implementada en n8n:
Se rediseñó el flujo `CommunityLab_Slack_Dinamico` (ID `SK001CommunityLb`) con una arquitectura **asíncrona anti-reintentos**:

```
[Slack Webhook Inbound]
       │
       ▼
[¿Es Verificación de Slack?]
       │
       ├─ True  ──► [Responder Challenge Slack] (Devuelve challenge en URL Verification)
       │
       └─ False ──► [Filtrar Reintentos Slack] (Descarta si trae cabecera 'x-slack-retry-num')
                            │
                            ▼
                      [Responder a Slack Event] ⚡ (Devuelve HTTP 200 {"status":"ok"} en 0.12s)
                            │
                            ▼  (El procesamiento con IA continúa en segundo plano)
                      [Procesador IA Slack] (Groq 'openai/gpt-oss-20b')
                            │
                            ▼
                      [Formatear Slack Blocks] (Construye 4 bloques estructurados)
                            │
                            ▼
                      [Enviar Mensaje a Slack] (POST a chat.postMessage con SLACK2_LOCAL_BOT_TOKEN)
```

1. **Acuse de recibo inmediato (0.12 segundos):** El nodo `Responder a Slack Event` envía el `HTTP 200` a Slack en apenas **129 ms**. Slack recibe la confirmación al instante y **nunca activa el temporizador de reintentos**.
2. **Filtro de seguridad:** Si existiera un reintento por latencia de red, `Filtrar Reintentos Slack` lo descarta antes de llegar a la IA.
3. **Publicación única garantizada:** La IA genera el análisis y publica **una única respuesta en el hilo**.

---

### 8.5 Configuración del Nodo de Salida (`chat.postMessage`)

- **Método:** `POST`
- **URL:** `https://slack.com/api/chat.postMessage`
- **Autenticación:** Header `Authorization: Bearer <SLACK2_LOCAL_BOT_TOKEN>`
- **Canal de Destino:** `#all-g10-latam-06` (`C0C3C2BPBSB`)
- **Estructura Block Kit generada:**
  - `Header Block`: 🤖 *CommunityLab Assistant*.
  - `Section Block`: Respuesta técnica/amigable generada por IA.
  - `Context Block`: Badges de sentimiento (`:large_green_circle: Positivo`, `:large_yellow_circle: Neutro`, `:red_circle: Negativo`), categoría técnica y temas clave.
  - `Section Block`: Tip Técnico / FAQ técnica estructurada o post de LinkedIn sugerido.

---

### 8.6 Pruebas en Vivo Verificadas y Comprobadas en Slack

| Prueba | Endpoint / Origen | Consulta Enviada | Sentimiento | Respuesta Visual en Slack `#all-g10-latam-06` |
| :--- | :--- | :--- | :--- | :--- |
| **Prueba A (Local)** | `http://localhost:5678/webhook/communitylab-slack` | *¿Cómo configuro un bucket en Oracle Cloud (OCI) para almacenar copias de seguridad de bases de datos de forma segura?* | `NEUTRO` (`:large_yellow_circle:`) | ✅ Publicada tarjeta Block Kit con guía técnica y FAQ de OCI. |
| **Prueba B (Pública ngrok)** | `https://<NGROK_URL>/webhook/communitylab-slack` | *¡Excelente noticia equipo! Acabamos de desplegar el microservicio en OCI y los tiempos de latencia bajaron un 40%.* | `POSITIVO` (`:large_green_circle:`) | ✅ Publicada felicitación oficial destacando el logro y la eficiencia en OCI. |
| **Prueba C (Chat Directo)** | Mención `@G10-LATAM-06-N8N` en `#all-g10-latam-06` | *Hola, ¿cómo configuro un bucket en OCI?* | `NEUTRO` (`:large_yellow_circle:`) | ✅ Respondida en el hilo con **una única respuesta** tras aplicar la solución anti-reintentos. |
