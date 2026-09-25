# 🐍 Guía de Interacción y Canales Dinámicos: Python Puro

Esta guía describe en detalle la arquitectura, configuración, ejecución y pruebas de los tres canales interactivos (**Telegram**, **Discord** y **Slack**) implementados con **Python Puro** en el proyecto **CommunityLab**.

---

## 1. Filosofía de Canales en Python Puro

A diferencia de la orquestación en n8n (que utiliza Webhooks HTTP y nodos visuales), la vía de **Python Puro**:

1. **Opera directamente en el backend local/cloud** utilizando bibliotecas oficiales (`python-telegram-bot`, `discord.py`, `slack-bolt`).
2. **Utiliza conexiones salientes seguras (Long Polling y WebSockets)**:
   - **Telegram:** Long Polling (`getUpdates`). No requiere abrir puertos ni túneles ngrok.
   - **Discord:** WebSocket Gateway (`gateway.discord.gg`). Conexión bidireccional permanente.
   - **Slack:** Socket Mode (`wss://wss-primary.slack.com`). Conexión WebSocket mediante un App-Level Token (`xapp-...`), sin requerir servidor HTTP público ni ngrok para Python.
3. **Persistencia Unificada e Inmediata:** Toda interacción recibida por cualquier canal se enruta a través de `ChannelMessageDispatcher`, se procesa con Gemini y se persiste acumulativamente en:
   📁 **`data/paquete_procesado_canales_python.json`**
4. **Trazabilidad en Logs Diarios:** Registro cronológico estructurado en:
   📁 **`logs/communitylab-YYYY-MM-DD.log`**

---

## 2. Variables de Entorno en `.env` (Python Puro)

Para ejecutar los bots de Python en entorno local, el archivo `.env` debe contener:

```ini
# ==============================================================================
# CONFIGURACIÓN MAESTRA DE DESPLIEGUE
# ==============================================================================
ENTORNO_DEPLOY=LOCAL

# ==============================================================================
# 1. TELEGRAM (PYTHON PURO - LONG POLLING)
# ==============================================================================
TELEGRAM_LOCAL_BOT_TOKEN=<TU_TELEGRAM_BOT_TOKEN>
TELEGRAM_BOT_TOKEN=<TU_TELEGRAM_BOT_TOKEN>

# ==============================================================================
# 2. DISCORD (PYTHON PURO - WEBSOCKET GATEWAY)
# ==============================================================================
DISCORD_LOCAL_BOT_TOKEN=<TU_DISCORD_BOT_TOKEN>
DISCORD_BOT_TOKEN=<TU_DISCORD_BOT_TOKEN>

# ==============================================================================
# 3. SLACK APP 1: PYTHON PURO (SOCKET MODE WEBSOCKET)
# ==============================================================================
SLACK1_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK1_BOT_TOKEN>
SLACK1_LOCAL_APP_TOKEN=xapp-1-<TU_SLACK1_APP_TOKEN>

# SLACK APP 2: N8N NATIVO (WEBHOOK HTTP - REFERENCIA)
SLACK2_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK2_BOT_TOKEN>
```

---

## 3. Manejo Automático de Entornos (`src/utils/config.py`)

El archivo `src/utils/config.py` abstrae la selección del token en función de `ENTORNO_DEPLOY`:

- `get_slack_bot_token()` -> Devuelve `SLACK1_LOCAL_BOT_TOKEN` en LOCAL.
- `get_slack_app_token()` -> Devuelve `SLACK1_LOCAL_APP_TOKEN` en LOCAL.
- `get_slack2_bot_token()` -> Devuelve `SLACK2_LOCAL_BOT_TOKEN` para n8n.
- `get_telegram_bot_token()` -> Devuelve `TELEGRAM_LOCAL_BOT_TOKEN` en LOCAL.
- `get_discord_bot_token()` -> Devuelve `DISCORD_LOCAL_BOT_TOKEN` en LOCAL.

---

## 4. Advertencia de Coexistencia con Telegram (Long Polling vs Webhooks)

> [!WARNING]
> **COMPORTAMIENTO OFICIAL DE TELEGRAM API:**  
> Un bot de Telegram **NO puede operar simultáneamente con Webhook (n8n) y con Long Polling (Python)** bajo el mismo Token.
>
> - **¿Qué sucede al ejecutar Python?**  
>   Al lanzar `run_bots.py --channel telegram`, la librería `python-telegram-bot` ejecuta automáticamente un comando `deleteWebhook()` en Telegram para recibir mensajes por polling.
> - **Consecuencia al detener Python:**  
>   Si detienes el script con `CTRL+C`, el Webhook de n8n queda eliminado en Telegram. Para volver a recibir mensajes en n8n, se debe reiniciar el contenedor Docker (`docker restart communitylab-n8n`).
>
> **Recomendación para Independencia Total:**  
> Crear dos bots en BotFather (ej. `@CommunityLab_Python_Bot` y `@CommunityLab_N8n_Bot`). Así operan en simultáneo sin interferir.

---

## 5. Arquitectura del Código en `src/channels/`

El código de Python está modularizado y desacoplado:

1. **`src/channels/dispatcher.py` (`ChannelMessageDispatcher`):**
   - Recibe el texto entrante de cualquier canal.
   - Envía la consulta a `GeminiService.process_interaction()`.
   - Genera respuestas formateadas según la plataforma (`telegram_markdown`, `discord_embed`, `slack_blocks`).
   - Persiste de forma acumulativa e inmediata en `data/paquete_procesado_canales_python.json`.
   - Registra trazas en `logs/communitylab-YYYY-MM-DD.log`.

2. **`src/channels/telegram_bot.py` (`CommunityLabTelegramBot`):**
   - Implementa `python-telegram-bot` con comandos `/start`, `/help` y captura de texto.
   - Envía estado de escritura (`typing`) mientras la IA procesa.

3. **`src/channels/discord_bot.py` (`CommunityLabDiscordBot`):**
   - Implementa `discord.py` escuchando menciones o mensajes directos.
   - Responde con un Embed dinámico con código de color según sentimiento.

4. **`src/channels/slack_bot.py` (`CommunityLabSlackBot`):**
   - Implementa `slack_bolt` con Socket Mode.
   - Responde en hilo (_thread_) mediante Slack Block Kit.

---

## 6. Ejecución Paso a Paso desde la Terminal

> [!IMPORTANT]
> **¿HAY QUE CORRER ALGÚN SCRIPT EN CONSOLA PARA LOS BOTS DE PYTHON?**  
> **SÍ, OBLIGATORIAMENTE.**  
> Los bots de Python son procesos cliente locales. **NO son servicios de fondo automáticos**.  
> Para que el bot de Telegram, Discord o Slack responda en vivo desde Python, debes **tener una terminal abierta corriendo su respectivo comando**. Si cierras la terminal o detienes el script (`CTRL+C`), el bot dejará de responder.  
> _(Por el contrario, n8n corre de forma autónoma 24/7 dentro del contenedor Docker sin necesidad de terminal)._

Con el entorno virtual activado (`.\env3.11\Scripts\Activate`):

### 6.1 Iniciar el Bot de Telegram (Python Puro)

```bash
python scripts/run_bots.py --channel telegram
```

- **Salida esperada:**
  ```text
  [CONFIG] Entorno de despliegue activo: LOCAL
  [START] Iniciando bot de Telegram (Long Polling)...
  [Telegram Bot] Conectado y escuchando mensajes vía Long Polling...
  ```

### 6.2 Iniciar el Bot de Discord (Python Puro)

```bash
python scripts/run_bots.py --channel discord
```

- **Salida esperada:**
  ```text
  [CONFIG] Entorno de despliegue activo: LOCAL
  [START] Iniciando bot de Discord (WebSocket Gateway)...
  [Discord Bot] Conectado exitosamente como G10-LATAM-06#8759 (ID: 1552136363787157644)
  [Discord Bot] Servidores conectados: ['G            10-LATAM-06']
  ```

### 6.3 Iniciar el Bot de Slack (Python Puro)

```bash
python scripts/run_bots.py --channel slack
```

- **Salida esperada:**
  ```text
  [CONFIG] Entorno de despliegue activo: LOCAL
  2026-09-23 00:45:00 [INFO] [CommunityLab.Channels.Slack] Iniciando Slack Bot con Socket Mode...
  ⚡ [Slack Bot] Conectado y escuchando menciones vía Socket Mode...
  Bolt app is running!
  ```

---

## 7. Verificación Realizada en Vivo: Discord Bot (Comprobado)

La integración de **Discord en Python Puro** fue probada y certificada en el servidor **`G10-LATAM-06`**:

1. **Arranque en consola:**
   ```bash
   python scripts/run_bots.py --channel discord
   ```
2. **Mensaje entrante del usuario (`maxcabanillass` en `#general`):**
   ```text
   @G10-LATAM-06 Hola, ¿cómo configuro un bucket en Oracle Cloud (OCI)?
   ```
3. **Procesamiento de Inferencia y Respuesta:**
   - Consulta normalizada por `ChannelMessageDispatcher`.
   - `GeminiService` detectó sentimiento neutro y generó solución técnica.
   - El bot respondió en `#general` con un **Discord Embed** enriquecido.
4. **Persistencia y Trazabilidad:**
   - Evento guardado en: `data/paquete_procesado_canales_python.json`.
   - Log registrado en: `logs/communitylab-2026-09-22.log`.

---

## 8. Verificación y Configuración Detallada: Slack Bot con Python Puro

### 8.1 ¿Por qué se necesitan DOS Aplicaciones de Slack? (La Causa Técnica)

En Slack Developer, una aplicación **NO puede tener activos simultáneamente Socket Mode y HTTP Webhook**:

1. **Regla de Exclusión Mutua de Slack:**
   - Cuando habilitas **Socket Mode** en una aplicación de Slack, la plataforma **inhabilita completamente** la casilla de _Request URL_ (Webhooks HTTP).
   - Slack asume que el 100% de los eventos serán recibidos por una conexión WebSocket cliente (`wss://...`).
2. **El Conflicto:**
   - **Python** utiliza `SocketModeHandler` (`slack-bolt`) -> Requiere **Socket Mode = ON**.
   - **n8n** utiliza Webhooks HTTP a través del túnel ngrok -> Requiere **Socket Mode = OFF** y **Request URL activa**.
   - Si intentáramos usar una sola app de Slack, tendríamos que entrar a `api.slack.com` a activar o desactivar Socket Mode cada vez que quisiéramos alternar entre Python y n8n.
3. **La Solución Arquitectónica:**
   - Crear **DOS aplicaciones separadas** en el **mismo Workspace (`G10-LATAM-06`)**:
     - **App 1: `G10-LATAM-06` (Exclusiva para Python):** Socket Mode ON, autenticada con `SLACK1_LOCAL_APP_TOKEN` y `SLACK1_LOCAL_BOT_TOKEN`.
     - **App 2: `G10-LATAM-06-N8N` (Exclusiva para n8n):** Socket Mode OFF, Request URL apuntando a ngrok, autenticada con `SLACK2_LOCAL_BOT_TOKEN`.
   - **Resultado:** Ambas apps están agregadas al canal `#all-g10-latam-06`. Cuando mencionas a `@G10-LATAM-06` responde Python; cuando mencionas a `@G10-LATAM-06-N8N` responde n8n. **Ambas coexisten en el mismo canal al mismo tiempo**.

---

### 8.2 Configuración Exacta de la App 1 (Python) en `api.slack.com`

1. **Nombre de la App:** `G10-LATAM-06`.
2. **Workspace:** `G10-LATAM-06`.
3. **Socket Mode (Menú lateral izquierdo -> Socket Mode):**
   - Activar el switch: **Enable Socket Mode -> ON**.
   - En la ventana modal emergente, nombrar el token: `socket-mode-token`.
   - Scope asignado: `connections:write`.
   - Guardar el token generado (`xapp-1-...`) en el `.env`:
     ```ini
     SLACK1_LOCAL_APP_TOKEN=xapp-1-<TU_SLACK1_APP_TOKEN>
     ```
4. **OAuth & Permissions (Menú lateral izquierdo -> OAuth & Permissions):**
   - En **Bot Token Scopes**, añadir los 4 scopes requeridos:
     - `app_mentions:read` (para escuchar menciones `@G10-LATAM-06`).
     - `chat:write` (para enviar respuestas al canal).
     - `channels:history` (para leer el contexto del canal).
     - `im:history` (para recibir mensajes directos 1 a 1).
   - Subir y presionar el botón verde: **Install to G10-LATAM-06** (o _Reinstall_).
   - Copiar el **Bot User OAuth Token** (`xoxb-...`) y guardarlo en el `.env`:
     ```ini
     SLACK1_LOCAL_BOT_TOKEN=xoxb-<TU_SLACK1_BOT_TOKEN>
     ```
5. **Event Subscriptions (Menú lateral izquierdo -> Event Subscriptions):**
   - Activar **Enable Events -> ON**.
   - _(Nota: Verás un mensaje que dice que los eventos se reciben vía Socket Mode, no requiere Request URL)_.
   - Desplegar **Subscribe to bot events**:
     - Añadir evento: `app_mention`.
     - Añadir evento: `message.im`.
   - Presionar **Save Changes**.
6. **Invitar la App al Canal de Slack:**
   - En la aplicación de Slack, entrar al canal `#all-g10-latam-06`.
   - Escribir `/invite @G10-LATAM-06` o entrar en detalles del canal -> _Integraciones / Agents & apps_ -> Añadir `G10-LATAM-06`.

---

### 8.3 Ejecución y Prueba en Vivo (Terminal y Slack)

1. **Abrir la terminal y lanzar el bot:**
   ```bash
   python scripts/run_bots.py --channel slack
   ```
2. **Entrar a Slack en el canal `#all-g10-latam-06` y escribir:**
   ```text
   @G10-LATAM-06 Hola, ¿cómo configuro un bucket en Oracle Cloud (OCI)?
   ```
3. **Traza Real Verificada en Consola (`logs/communitylab-2026-09-23.log`):**
   ```text
   2026-09-23 00:45:00 [INFO] [CommunityLab.Channels.Slack] Iniciando Slack Bot con Socket Mode...
   ⚡ [Slack Bot] Conectado y escuchando menciones vía Socket Mode...
   Bolt app is running!
   2026-09-23 00:45:53 [INFO] [CommunityLab.Channels.Slack] Slack mención recibida de 'U0C3RER0ZHC' en canal 'C0C3C2BPBSB': <@U0C4MR0GHC0> Hola, ¿cómo configuro un bucket en Oracle Cloud (OCI)?
   [Slack Bot] Mención recibida de 'U0C3RER0ZHC' en #C0C3C2BPBSB: <@U0C4MR0GHC0> Hola, ¿cómo configuro un bucket en Oracle Clo...
   2026-09-23 00:45:53 [INFO] [CommunityLab.Channels.Dispatcher] Dispatcher procesando mensaje [slk_1790142352.624119] de 'User_U0C3RER0ZHC' en '#slack-C0C3C2BPBSB' (69 chars)
   2026-09-23 00:46:01 [INFO] [CommunityLab.Channels.Dispatcher] [Dispatcher] Activo guardado localmente en 'data/paquete_procesado_canales_python.json' (Total acumulado: 10)
   2026-09-23 00:46:02 [INFO] [CommunityLab.Channels.Slack] Respuesta enviada exitosamente a Slack para 'U0C3RER0ZHC'
   ```
4. **Respuesta en Slack:**
   El bot `@G10-LATAM-06` responde en el mismo hilo con una tarjeta Block Kit con badges de sentimiento, guía técnica de OCI y copy sugerido para LinkedIn.
