"""Modulo de configuracion y gestion de entornos para CommunityLab.

Permite conmutar automaticamente entre PRODUCCION y LOCAL segun la variable
ENTORNO_DEPLOY del archivo .env.
"""

from __future__ import annotations

import os
from typing import Any, Dict
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


def get_entorno_deploy() -> str:
    """Devuelve el entorno de despliegue actual: 'PRODUCCION' o 'LOCAL'."""
    val = os.getenv("ENTORNO_DEPLOY", "LOCAL").strip().upper()
    if val in ("PROD", "PRODUCCION", "PRODUCTION"):
        return "PRODUCCION"
    return "LOCAL"


def is_production() -> bool:
    """Retorna True si el entorno activo es PRODUCCION."""
    return get_entorno_deploy() == "PRODUCCION"


def is_local() -> bool:
    """Retorna True si el entorno activo es LOCAL."""
    return get_entorno_deploy() == "LOCAL"


def get_telegram_token() -> str:
    """Retorna el token de Telegram segun el entorno de despliegue."""
    if is_production():
        return os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    return (
        os.getenv("TELEGRAM_LOCAL_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    )


def get_discord_token() -> str:
    """Retorna el token de Discord segun el entorno de despliegue."""
    if is_production():
        return os.getenv("DISCORD_BOT_TOKEN", "").strip()
    return (
        os.getenv("DISCORD_LOCAL_BOT_TOKEN", "").strip()
        or os.getenv("DISCORD_BOT_TOKEN", "").strip()
    )


def get_slack_bot_token() -> str:
    """Retorna el token bot (xoxb-...) de Slack segun el entorno de despliegue."""
    if is_production():
        return os.getenv("SLACK_BOT_TOKEN", "").strip()
    return (
        os.getenv("SLACK_LOCAL_BOT_TOKEN", "").strip()
        or os.getenv("SLACK_BOT_TOKEN", "").strip()
    )


def get_slack_app_token() -> str:
    """Retorna el app token (xapp-...) de Slack segun el entorno de despliegue."""
    if is_production():
        return os.getenv("SLACK_APP_TOKEN", "").strip()
    return (
        os.getenv("SLACK_LOCAL_APP_TOKEN", "").strip()
        or os.getenv("SLACK_APP_TOKEN", "").strip()
    )


def get_n8n_webhook_url() -> str:
    """Retorna la URL del Webhook de ingesta de n8n segun el entorno activo."""
    if is_production():
        return os.getenv("N8N_WEBHOOK_URL", "http://147.15.9.116:5678/").strip()
    return (
        os.getenv("N8N_LOCAL_WEBHOOK_URL", "").strip()
        or os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/communitylab-ingesta").strip()
    )


def get_n8n_webhook_base() -> str:
    """Retorna la URL base de Webhooks de n8n para Docker/tunel segun el entorno."""
    if is_production():
        return os.getenv("N8N_WEBHOOK_URL", "http://147.15.9.116:5678/").strip()
    return (
        os.getenv("N8N_LOCAL_WEBHOOK_BASE", "").strip()
        or os.getenv("N8N_LOCAL_WEBHOOK_URL", "http://localhost:5678/").strip()
    )


def get_n8n_host() -> str:
    """Retorna el Host de n8n segun el entorno."""
    if is_production():
        return os.getenv("N8N_HOST", "0.0.0.0").strip()
    return os.getenv("N8N_LOCAL_HOST", "http://localhost").strip()


def get_n8n_port() -> int:
    """Retorna el Puerto de n8n segun el entorno."""
    if is_production():
        return int(os.getenv("N8N_PORT", "5678"))
    return int(os.getenv("N8N_LOCAL_PORT", "5678"))


def get_active_config_summary() -> Dict[str, Any]:
    """Genera un resumen seguro de la configuracion activa (sin exponer tokens completos)."""
    entorno = get_entorno_deploy()
    tg = get_telegram_token()
    dc = get_discord_token()
    sb = get_slack_bot_token()
    sa = get_slack_app_token()

    def mask(tok: str) -> str:
        if not tok or tok.startswith("tu_") or tok.startswith("produccion_"):
            return tok or "(No configurado)"
        return tok[:8] + "..." + tok[-4:] if len(tok) > 12 else "***"

    return {
        "entorno_deploy": entorno,
        "n8n_webhook_url": get_n8n_webhook_url(),
        "n8n_webhook_base": get_n8n_webhook_base(),
        "n8n_host": get_n8n_host(),
        "n8n_port": get_n8n_port(),
        "telegram_token_active": mask(tg),
        "discord_token_active": mask(dc),
        "slack_bot_token_active": mask(sb),
        "slack_app_token_active": mask(sa),
    }
