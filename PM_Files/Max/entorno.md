# Gestión y Conmutación de Entornos: PRODUCCION vs LOCAL

Este documento detalla la arquitectura, configuración y funcionamiento de la variable **`ENTORNO_DEPLOY`** implementada para el proyecto **CommunityLab**, permitiendo alternar de forma transparente e inmediata entre el entorno de **PRODUCCIÓN** (desplegado en la máquina virtual de Oracle Cloud Infrastructure - OCI) y el entorno **LOCAL** (desarrollo con Docker local y túneles ngrok).

---

## 1. Objetivo y Motivación

Anteriormente, las variables de conexión a n8n y los tokens de bots interactivos (Telegram, Discord, Slack) compartían nombres genéricos o requerían comentar/descomentar líneas en el archivo `.env`.

Para garantizar orden, desacoplamiento y evitar sobreescrituras accidentales entre el despliegue cloud en OCI y el entorno local de desarrollo, se implementó un switch maestro:

- **`ENTORNO_DEPLOY=PRODUCCION`**: Activa los endpoints de la máquina virtual OCI y los tokens oficiales del bot en producción.
- **`ENTORNO_DEPLOY=LOCAL`**: Activa los endpoints del contenedor Docker local, la URL pública del túnel ngrok y los tokens de pruebas locales.

---

## 2. Configuración en `.env` y `.env.example`

Ambos archivos fueron reestructurados separando explícitamente los dos entornos:

```ini
# ==============================================================================
# ENTORNO DE DESPLIEGUE (PRODUCCION | LOCAL)
# ==============================================================================
ENTORNO_DEPLOY=LOCAL

# ==============================================================================
# PRODUCCION: n8n Orchestrator (OCI VM)
# ==============================================================================
N8N_WEBHOOK_URL=http://147.15.9.116:5678/
N8N_HOST=0.0.0.0
N8N_PORT=5678

# PRODUCCION: Dynamic Channels / Interactive Bots (Optional)
TELEGRAM_BOT_TOKEN=produccion_telegram_bot_token_aqui
DISCORD_BOT_TOKEN=produccion_discord_bot_token_aqui
SLACK_BOT_TOKEN=xoxb-produccion_slack_bot_token_aqui
SLACK_APP_TOKEN=xapp-produccion_slack_app_token_aqui

# ==============================================================================
# LOCAL: n8n Orchestrator
# ==============================================================================
N8N_LOCAL_WEBHOOK_URL=https://<TU_SUBDOMINIO>.ngrok-free.app/webhook/communitylab-ingesta
N8N_LOCAL_HOST=http://localhost
N8N_LOCAL_PORT=5678
N8N_LOCAL_WEBHOOK_BASE=https://<TU_SUBDOMINIO>.ngrok-free.app/

# LOCAL: Dynamic Channels / Interactive Bots (Optional)
TELEGRAM_LOCAL_BOT_TOKEN=<TU_TELEGRAM_BOT_TOKEN>
DISCORD_LOCAL_BOT_TOKEN=tu_discord_bot_token_aqui
SLACK_LOCAL_BOT_TOKEN=xoxb-tu_slack_bot_token_aqui
SLACK_LOCAL_APP_TOKEN=xapp-tu_slack_app_token_aqui
```

---

## 3. Módulo Centralizado de Configuración (`src/utils/config.py`)

Para que el código Python no tenga condicionales dispersos, se creó el módulo **`src/utils/config.py`** (exportado en `src/utils/__init__.py`), el cual centraliza la resolución de variables:

### Métodos Principales

| Función                       | Descripción                                                                                                            |
| :---------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `get_entorno_deploy()`        | Devuelve `"PRODUCCION"` o `"LOCAL"`. Normaliza variantes como `"PROD"`.                                                |
| `is_production()`             | Retorna `True` si el entorno activo es PRODUCCION.                                                                     |
| `is_local()`                  | Retorna `True` si el entorno activo es LOCAL.                                                                          |
| `get_telegram_token()`        | Si es PRODUCCION devuelve `TELEGRAM_BOT_TOKEN`. Si es LOCAL devuelve `TELEGRAM_LOCAL_BOT_TOKEN` (con fallback seguro). |
| `get_discord_token()`         | Si es PRODUCCION devuelve `DISCORD_BOT_TOKEN`. Si es LOCAL devuelve `DISCORD_LOCAL_BOT_TOKEN`.                         |
| `get_slack_bot_token()`       | Devuelve el token `xoxb-...` correspondiente.                                                                          |
| `get_slack_app_token()`       | Devuelve el app token `xapp-...` correspondiente.                                                                      |
| `get_n8n_webhook_url()`       | Retorna `N8N_WEBHOOK_URL` (OCI) o `N8N_LOCAL_WEBHOOK_URL` (ngrok/local).                                               |
| `get_n8n_webhook_base()`      | Retorna la URL base de webhook para n8n.                                                                               |
| `get_active_config_summary()` | Genera un resumen del entorno enmascarando tokens sensibles para logs o vistas.                                        |

---

## 4. Adaptación en Componentes del Proyecto

### 4.1 Bots Interactivos (`src/channels/`)

- **Telegram (`telegram_bot.py`)**:
  Instancia el bot resolviendo el token mediante `get_telegram_token()`. Si falta el token en local, el mensaje de error guía al desarrollador indicando que revise `TELEGRAM_LOCAL_BOT_TOKEN`.
- **Discord (`discord_bot.py`)**:
  Utiliza `get_discord_token()`.
- **Slack (`slack_bot.py`)**:
  Utiliza `get_slack_bot_token()` y `get_slack_app_token()`.

### 4.2 Interfaz de Usuario Streamlit (`src/ui/`)

- **`services.py`**:
  Al invocar el orquestador n8n mediante HTTP, selecciona `get_n8n_webhook_url()` y etiqueta el motor de orquestación resultante como `"n8n_produccion"` o `"n8n_local"` según `is_production()`.
- **`app.py`**:
  Muestra el endpoint activo por defecto tomado de `get_n8n_webhook_url()`.

### 4.3 Lanzador CLI (`scripts/run_bots.py`)

Al ejecutar el lanzador de bots por terminal, imprime automáticamente un mensaje informativo con el entorno activo:

```bash
python scripts/run_bots.py --channel telegram
# [CONFIG] Entorno de despliegue activo: LOCAL
```

---

## 5. Conmutación Dinámica en Docker (`docker-compose.yml`)

El contenedor de n8n requiere definir la variable `WEBHOOK_URL` (y `N8N_WEBHOOK_URL`) para registrar correctamente los webhooks en Telegram y otros servicios.

Para que Docker respete automáticamente `ENTORNO_DEPLOY` sin necesidad de editar el archivo YAML manualmente, se implementó un `entrypoint` inteligente en `docker-compose.yml`:

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    container_name: communitylab-n8n
    restart: always
    ports:
      - "5678:5678"
    entrypoint:
      - /bin/sh
      - -c
      - |
        if [ "$$ENTORNO_DEPLOY" = "PRODUCCION" ]; then
          TARGET_URL="$$N8N_PROD_WEBHOOK_URL"
        else
          TARGET_URL="$${N8N_LOCAL_WEBHOOK_BASE:-$$N8N_LOCAL_WEBHOOK_URL}"
        fi
        export WEBHOOK_URL="$$TARGET_URL"
        export N8N_WEBHOOK_URL="$$TARGET_URL"
        echo "=================================================="
        echo "[CommunityLab Docker] ENTORNO_DEPLOY=$$ENTORNO_DEPLOY"
        echo "[CommunityLab Docker] N8N_WEBHOOK_URL=$$TARGET_URL"
        echo "=================================================="
        exec /docker-entrypoint.sh
    environment:
      - ENTORNO_DEPLOY=${ENTORNO_DEPLOY:-LOCAL}
      - N8N_PROD_WEBHOOK_URL=${N8N_WEBHOOK_URL:-http://147.15.9.116:5678/}
      - N8N_LOCAL_WEBHOOK_BASE=${N8N_LOCAL_WEBHOOK_BASE:-http://localhost:5678/}
      - N8N_LOCAL_WEBHOOK_URL=${N8N_LOCAL_WEBHOOK_URL:-http://localhost:5678/webhook/communitylab-ingesta}
      # ... demás configuraciones de n8n ...
```

---

## 6. Pruebas y Validación Realizadas

### 6.1 Prueba de Arranque de Docker

Al ejecutar `docker compose up -d --force-recreate`:

```text
Activated workflow "CommunityLab_Ingesta_Local_Webhook" (ID: QCTE96hDXIeffo30)
Activated workflow "CommunityLab_Telegram_Dinamico" (ID: RyuE7yqepKvch0eM)

Editor is now accessible via:
https://<TU_SUBDOMINIO>.ngrok-free.app
```

### 6.2 Verificación del Webhook de Telegram

Se consultó la API de Telegram con el token local para certificar que el webhook apunta al túnel de ngrok:

```json
{
  "url": "https://<TU_SUBDOMINIO>.ngrok-free.app/webhook/bddb1a63-db0d-42b4-b168-50fb6958f0b9/webhook",
  "has_custom_certificate": false,
  "pending_update_count": 0,
  "max_connections": 40
}
```

### 6.3 Suite de Pruebas Automatizadas (`pytest`)

Se creó `tests/test_config.py` con pruebas unitarias que simulan ambos entornos y el comportamiento de fallback:

- `test_config_local_environment` $
ightarrow$ **PASSED**
- `test_config_produccion_environment` $
ightarrow$ **PASSED**
- `test_config_local_fallback_when_local_token_not_set` $
ightarrow$ **PASSED**
- Total de suite de pruebas: **60 passed, 2 skipped, 0 failed**.

---

## 7. Guía Rápida: Cómo Conmutar de Entorno

### Para trabajar en LOCAL:

1. Asegurar en `.env`:
   ```ini
   ENTORNO_DEPLOY=LOCAL
   ```
2. Si el túnel de ngrok cambia de URL, actualizar `N8N_LOCAL_WEBHOOK_BASE` y `N8N_LOCAL_WEBHOOK_URL` en `.env`.
3. Reiniciar el contenedor de Docker para aplicar la nueva URL base:
   ```bash
   docker compose up -d --force-recreate
   ```

### Para trabajar en PRODUCCIÓN (OCI):

1. Cambiar en `.env`:
   ```ini
   ENTORNO_DEPLOY=PRODUCCION
   ```
2. Asegurar que las variables bajo `# PRODUCCION` tengan los valores correspondientes de la máquina virtual OCI y los tokens oficiales.
3. Si ejecutas Docker en la VM de OCI, reiniciar con:
   ```bash
   docker compose up -d --force-recreate
   ```
