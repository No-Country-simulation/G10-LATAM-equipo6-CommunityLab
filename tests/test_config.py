import os
import pytest
from src.utils.config import (
    get_entorno_deploy,
    is_production,
    is_local,
    get_telegram_token,
    get_discord_token,
    get_slack_bot_token,
    get_slack_app_token,
    get_n8n_webhook_url,
    get_n8n_webhook_base,
    get_n8n_host,
    get_n8n_port,
    get_active_config_summary,
)


def test_config_local_environment(monkeypatch):
    monkeypatch.setenv("ENTORNO_DEPLOY", "LOCAL")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "prod_tg_token")
    monkeypatch.setenv("TELEGRAM_LOCAL_BOT_TOKEN", "local_tg_token_123456789")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "prod_dc_token")
    monkeypatch.setenv("DISCORD_LOCAL_BOT_TOKEN", "local_dc_token")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-prod")
    monkeypatch.setenv("SLACK_LOCAL_BOT_TOKEN", "xoxb-local")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-prod")
    monkeypatch.setenv("SLACK_LOCAL_APP_TOKEN", "xapp-local")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "http://147.15.9.116:5678/")
    monkeypatch.setenv("N8N_LOCAL_WEBHOOK_URL", "https://ngrok.app/webhook/local")
    monkeypatch.setenv("N8N_LOCAL_WEBHOOK_BASE", "https://ngrok.app/")
    monkeypatch.setenv("N8N_LOCAL_HOST", "http://localhost")
    monkeypatch.setenv("N8N_LOCAL_PORT", "5678")

    assert get_entorno_deploy() == "LOCAL"
    assert is_local() is True
    assert is_production() is False
    assert get_telegram_token() == "local_tg_token_123456789"
    assert get_discord_token() == "local_dc_token"
    assert get_slack_bot_token() == "xoxb-local"
    assert get_slack_app_token() == "xapp-local"
    assert get_n8n_webhook_url() == "https://ngrok.app/webhook/local"
    assert get_n8n_webhook_base() == "https://ngrok.app/"
    assert get_n8n_host() == "http://localhost"
    assert get_n8n_port() == 5678

    summary = get_active_config_summary()
    assert summary["entorno_deploy"] == "LOCAL"
    assert "..." in summary["telegram_token_active"]


def test_config_produccion_environment(monkeypatch):
    monkeypatch.setenv("ENTORNO_DEPLOY", "PRODUCCION")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "prod_tg_token_987654321")
    monkeypatch.setenv("TELEGRAM_LOCAL_BOT_TOKEN", "local_tg_token")
    monkeypatch.setenv("DISCORD_BOT_TOKEN", "prod_dc_token")
    monkeypatch.setenv("DISCORD_LOCAL_BOT_TOKEN", "local_dc_token")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-prod")
    monkeypatch.setenv("SLACK_LOCAL_BOT_TOKEN", "xoxb-local")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-prod")
    monkeypatch.setenv("SLACK_LOCAL_APP_TOKEN", "xapp-local")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "http://147.15.9.116:5678/")
    monkeypatch.setenv("N8N_HOST", "0.0.0.0")
    monkeypatch.setenv("N8N_PORT", "5678")
    monkeypatch.setenv("N8N_LOCAL_WEBHOOK_URL", "https://ngrok.app/webhook/local")

    assert get_entorno_deploy() == "PRODUCCION"
    assert is_local() is False
    assert is_production() is True
    assert get_telegram_token() == "prod_tg_token_987654321"
    assert get_discord_token() == "prod_dc_token"
    assert get_slack_bot_token() == "xoxb-prod"
    assert get_slack_app_token() == "xapp-prod"
    assert get_n8n_webhook_url() == "http://147.15.9.116:5678/"
    assert get_n8n_webhook_base() == "http://147.15.9.116:5678/"
    assert get_n8n_host() == "0.0.0.0"
    assert get_n8n_port() == 5678


def test_config_local_fallback_when_local_token_not_set(monkeypatch):
    monkeypatch.setenv("ENTORNO_DEPLOY", "LOCAL")
    monkeypatch.setenv("TELEGRAM_LOCAL_BOT_TOKEN", "")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "legacy_token")

    assert get_telegram_token() == "legacy_token"
