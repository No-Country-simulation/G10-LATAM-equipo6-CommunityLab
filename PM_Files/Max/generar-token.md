# 🔑 Guía Paso a Paso: Generación de Tokens y Credenciales de Aplicación

Esta guía detalla el procedimiento oficial y exacto para obtener las credenciales y tokens de acceso necesarios para integrar **Telegram**, **Discord** y **Slack** en **CommunityLab**, tanto para la vía **Python Puro** (`scripts/run_bots.py`) como para la vía **n8n Nativo** (`Docker`).

---

## 1. Telegram Bot Token (`TELEGRAM_LOCAL_BOT_TOKEN` / `TELEGRAM_BOT_TOKEN`)

> Telegram utiliza un único token por bot entregado por `@BotFather`. Con este token se autentican tanto las llamadas por Long Polling en Python como los Webhooks en n8n.

### Paso a Paso:

1. **Abrir Telegram y buscar a `@BotFather`:**
   - En el buscador de Telegram escribe `@BotFather` (asegúrate de que tenga el check azul de verificación oficial).
2. **Crear el Bot:**
   - Envía el comando:
     ```text
     /newbot
     ```
3. **Asignar Nombre Visible:**
   - Escribe el nombre descriptivo del bot (ej. `CommunityLab IA Assistant`).
4. **Asignar Nombre de Usuario (`username`):**
   - Debe terminar obligatoriamente en `bot` (ej. `CommunityLab_Local_Bot` o `CommunityLabMax_Bot`).
5. **Copiar el Token de Acceso HTTP API:**
   - BotFather responderá con un mensaje de confirmación que incluye una clave como:
     ```text
     <TU_TELEGRAM_BOT_TOKEN>
     ```
6. **Guardar en tu archivo `.env`:**
   ```ini
   # Si es para tu entorno local:
   TELEGRAM_LOCAL_BOT_TOKEN=<TU_TELEGRAM_BOT_TOKEN>
   ```

> [!TIP]
> **Recomendación para Independencia Python vs n8n:**  
> Puedes repetir el comando `/newbot` en BotFather para crear un segundo bot (ej: `CommunityLab_N8n_Bot`). Así tendrás un token exclusivo para Python y otro para n8n, permitiendo que ambos operen en simultáneo sin que se cancelen los Webhooks.

---

## 2. Discord Bot Token (`DISCORD_LOCAL_BOT_TOKEN` / `DISCORD_BOT_TOKEN`)

> Discord requiere crear una aplicación en su portal de desarrolladores, activar los permisos de lectura de mensajes (**Message Content Intent**) e invitar el bot a tu servidor mediante un enlace OAuth2.

### Paso 1: Crear la Aplicación y el Bot

1. Ingresa al [Discord Developer Portal](https://discord.com/developers/applications).
2. Inicia sesión con tu cuenta de Discord y haz clic en el botón superior **"New Application"**.
3. Asigna un nombre a la aplicación (ej. `CommunityLab-Assistant`) y acepta los términos.
4. En el menú lateral izquierdo, haz clic en **"Bot"**:
   - En la sección **Build-A-Bot**, puedes personalizar el avatar y nombre.
   - Haz clic en **"Reset Token"** (o **"Copy"**) para generar y copiar el token secreto del bot.
   - Guarda este valor en tu `.env`:
     ```ini
     DISCORD_LOCAL_BOT_TOKEN=<TU_DISCORD_BOT_TOKEN>
     ```

### Paso 2: ¡MUY IMPORTANTE! Habilitar Message Content Intent

Para que el bot pueda leer el texto de las preguntas de los usuarios (y no solo eventos vacíos):

1. En la misma pestaña **"Bot"**, desplázate hacia abajo hasta la sección **"Privileged Gateway Intents"**.
2. **Activa obligatoriamente el interruptor:**
   - 🔘 **Message Content Intent**
3. Haz clic en el botón verde inferior **"Save Changes"**.

### Paso 3: Generar Enlace de Invitación (OAuth2) al Servidor de Discord

1. En el menú lateral izquierdo, ve a **"OAuth2"** -> **"URL Generator"**.
2. En la cuadrícula de **SCOPES**, marca:
   - ☑️ **`bot`**
3. En la cuadrícula de **BOT PERMISSIONS** que aparecerá abajo, marca:
   - ☑️ **Send Messages** (Enviar mensajes)
   - ☑️ **Send Messages in Threads** (Enviar mensajes en hilos)
   - ☑️ **Embed Links** (Incrustar enlaces / Discord Embeds)
   - ☑️ **Read Message History** (Leer historial de mensajes)
   - ☑️ **View Channels** (Ver canales)
4. En la parte inferior se generará una URL como:
   `https://discord.com/oauth2/authorize?client_id=123456789&permissions=277025507392&scope=bot`
5. Copia esa URL, ábrela en una pestaña de tu navegador, selecciona tu servidor de Discord y autoriza el ingreso del bot.

---

## 3. Slack Tokens: Configuración de Dos Apps (Python y n8n)

> [!IMPORTANT]
> **¿POR QUÉ SON OBLIGATORIAS DOS APPS EN SLACK?**  
> En Slack Developer, **Socket Mode (WebSocket)** y **Request URL (Webhooks HTTP)** son **mutuamente excluyentes por aplicación**:  
> - Si activas Socket Mode para que Python escuche eventos vía WebSocket, Slack **inhabilita completamente** la casilla de *Request URL*, impidiendo que n8n pueda registrar su Webhook HTTP.  
> - Si desactivas Socket Mode para que n8n reciba HTTP POSTs, el script de Python con `slack-bolt` no se puede conectar.  
> 
> **La Solución Arquitectónica:** Se crearon **DOS aplicaciones separadas en el mismo Workspace (`G10-LATAM-06`)** y ambas conviven en el mismo canal (`#all-g10-latam-06`):
> 1. **`G10-LATAM-06` (App 1):** Para Python Puro (Socket Mode ON).  
> 2. **`G10-LATAM-06-N8N` (App 2):** Para n8n Nativo (Socket Mode OFF, Request URL ngrok).

---

### 3.1 APP 1: Para Python Puro (`G10-LATAM-06`)

Esta app utiliza una conexión saliente WebSocket segura. No requiere ngrok ni puertos abiertos.

1. **Crear la App:**
   - Ingresa a [api.slack.com/apps](https://api.slack.com/apps) -> **Create New App** -> **From scratch**.
   - **App Name:** `G10-LATAM-06`.
   - **Workspace:** `G10-LATAM-06`.
2. **Generar el App-Level Token (`SLACK1_LOCAL_APP_TOKEN`):**
   - En el menú lateral izquierdo, ve a **Basic Information** -> baja a la sección **App-Level Tokens**.
   - Haz clic en **Generate Token and Scopes**.
   - **Token Name:** `socket-mode-token`.
   - Haz clic en **Add Scope** y añade: `connections:write`.
   - Haz clic en **Generate** y copia el token `xapp-1-...`:
     ```ini
     SLACK1_LOCAL_APP_TOKEN=xapp-1-<TU_SLACK1_APP_TOKEN>
     ```
3. **Activar Socket Mode:**
   - En el menú izquierdo, ve a **Socket Mode** -> activa **Enable Socket Mode -> ON**.
4. **Asignar Permisos y Generar el Bot Token (`SLACK1_LOCAL_BOT_TOKEN`):**
   - Ve a **OAuth & Permissions** -> baja a **Bot Token Scopes** y añade:
     - `app_mentions:read`
     - `chat:write`
     - `channels:history`
     - `im:history`
   - Sube y haz clic en **Install to G10-LATAM-06**.
   - Copia el **Bot User OAuth Token** (`xoxb-...`):
     ```ini
     SLACK1_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK1_BOT_TOKEN>
     ```
5. **Configurar Event Subscriptions:**
   - Ve a **Event Subscriptions** -> activa **Enable Events -> ON**.
   - En **Subscribe to bot events**, añade `app_mention` y `message.im`.
   - Haz clic en **Save Changes**.

---

### 3.2 APP 2: Para n8n Nativo (`G10-LATAM-06-N8N`)

Esta app utiliza Webhooks HTTP estándar para comunicarse con el flujo de n8n a través del túnel ngrok.

1. **Crear la App:**
   - En [api.slack.com/apps](https://api.slack.com/apps) -> **Create New App** -> **From scratch**.
   - **App Name:** `G10-LATAM-06-N8N`.
   - **Workspace:** Selecciona el **mismo**: `G10-LATAM-06`.
2. **Socket Mode (¡Debe quedar en OFF!):**
   - Ve a **Socket Mode** y comprueba que esté **Desactivado (OFF)**.
   - *(Nota: n8n NO utiliza App-Level Token `xapp-...`; solo utiliza Bot Token `xoxb-...`)*.
3. **Asignar Permisos y Generar el Bot Token (`SLACK2_LOCAL_BOT_TOKEN`):**
   - Ve a **OAuth & Permissions** -> **Bot Token Scopes** y añade:
     - `app_mentions:read`
     - `chat:write`
     - `channels:history`
   - Haz clic en **Install to G10-LATAM-06**.
   - Copia el **Bot User OAuth Token** (`xoxb-...`):
     ```ini
     SLACK2_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK2_BOT_TOKEN>
     ```
4. **Configurar Event Subscriptions y URL de ngrok:**
   - Ve a **Event Subscriptions** -> activa **Enable Events -> ON**.
   - En **Request URL**, escribe tu endpoint público de ngrok:
     ```text
     https://<TU_SUBDOMINIO_NGROK>.ngrok-free.app/webhook/communitylab-slack
     ```
     *(Verás aparecer en verde: `Verified ✔`)*.
   - En **Subscribe to bot events**, añade: `app_mention`.
   - Haz clic en **Save Changes**.

---

### 3.3 Integración de Ambos Bots en el Canal de Slack

Para que ambos bots puedan responder a menciones en `#all-g10-latam-06`:
1. Abre tu aplicación de Slack y entra al canal `#all-g10-latam-06`.
2. Escribe en el mensaje del canal:
   ```text
   /invite @G10-LATAM-06
   /invite @G10-LATAM-06-N8N
   ```
3. Ambos aparecerán en la lista de miembros/apps del canal.
4. **Comportamiento en vivo:**
   - Si mencionas a `@G10-LATAM-06`: responde el script de Python (`python scripts/run_bots.py --channel slack`).
   - Si mencionas a `@G10-LATAM-06-N8N`: responde el flujo autónomo de n8n en Docker.
