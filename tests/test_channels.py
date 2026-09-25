# -*- coding: utf-8 -*-
"""Pruebas unitarias para el módulo de canales dinámicos (Telegram, Discord, Slack)."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Chat, Message, Update, User

from src.ai_engine.gemini_service import GeminiService
from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.channels.dispatcher import ChannelMessageDispatcher
from src.channels.discord_bot import CommunityLabDiscordBot
from src.channels.slack_bot import CommunityLabSlackBot
from src.channels.telegram_bot import CommunityLabTelegramBot


@pytest.fixture
def mock_processed_asset():
    """Fixture con un activo procesado representativo conforme a los esquemas Pydantic."""
    interaccion = CommunityInteraction(
        id="msg_test_001",
        autor="Carlos Tester",
        canal="#dudas-cloud-oci",
        tipo="pregunta_tecnica",
        texto="¿Cómo conecto mi bucket de OCI?",
    )
    activo = CommunityLabAssetOutput(
        sentimiento=SentimientoEnum.POSITIVO,
        tipo_contenido=TipoContenidoEnum.DUDA_TECNICA,
        temas_clave=["OCI", "Python", "Cloud"],
        post_linkedin=None,
        tip_tecnico_faq="💡 Para error 401 en OCI, verifica el fingerprint y clave privada.",
    )
    return ProcessedCommunityAsset(interaccion=interaccion, activo=activo)


@pytest.fixture
def mock_ai_service(mock_processed_asset):
    """Fixture que mockea el servicio de IA para evitar llamadas reales a Gemini."""
    service = MagicMock(spec=GeminiService)
    service.process_interaction.return_value = mock_processed_asset
    return service


# =============================================================================
# PRUEBAS DEL DISPATCHER UNIVERSAL
# =============================================================================

def test_dispatcher_process_incoming_message_success(mock_ai_service, tmp_path: Path):
    """Verifica que el dispatcher normalice el mensaje y genere respuestas multi-canal."""
    storage_file = tmp_path / "test_storage.json"
    dispatcher = ChannelMessageDispatcher(
        ai_service=mock_ai_service,
        persist_locally=True,
        storage_path=storage_file,
    )

    item, respuestas = dispatcher.process_incoming_message(
        canal_origen="telegram-general",
        autor="Carlos Tester",
        texto="¿Cómo conecto mi bucket de OCI?",
        mensaje_id_externo="tg_12345",
    )

    # Verificaciones del activo devuelto
    assert item.interaccion.id == "msg_test_001"
    assert item.interaccion.autor == "Carlos Tester"
    assert item.activo.sentimiento == SentimientoEnum.POSITIVO

    # Verificaciones de formatos generados
    assert "telegram_markdown" in respuestas
    assert "CommunityLab IA Assistant" in respuestas["telegram_markdown"]
    assert any(term in respuestas["telegram_markdown"] for term in ["💡 *Solución", "💡 *Tip"])

    assert "discord_embed" in respuestas
    embed = respuestas["discord_embed"]
    assert embed["title"] == "🤖 CommunityLab Assistant"
    assert any("Solución" in f["name"] or "Tip" in f["name"] for f in embed["fields"])

    assert "slack_blocks" in respuestas
    assert len(respuestas["slack_blocks"]) >= 3

    # Verificación de persistencia acumulativa
    assert storage_file.exists()
    datos_guardados = json.loads(storage_file.read_text(encoding="utf-8"))
    assert len(datos_guardados["activos"]) == 1
    assert datos_guardados["activos"][0]["interaccion"]["id"] == "msg_test_001"


def test_dispatcher_persists_accumulatively(mock_ai_service, tmp_path: Path):
    """Verifica que múltiples mensajes se acumulen en el JSON de almacenamiento."""
    storage_file = tmp_path / "test_storage_multi.json"
    dispatcher = ChannelMessageDispatcher(
        ai_service=mock_ai_service,
        persist_locally=True,
        storage_path=storage_file,
    )

    dispatcher.process_incoming_message("canal_1", "User 1", "Mensaje 1")
    dispatcher.process_incoming_message("canal_2", "User 2", "Mensaje 2")

    datos = json.loads(storage_file.read_text(encoding="utf-8"))
    assert datos["metadata_paquete"]["total_activos"] == 2
    assert len(datos["activos"]) == 2


# =============================================================================
# PRUEBAS DEL BOT DE TELEGRAM
# =============================================================================

def test_telegram_bot_missing_token_raises_error(monkeypatch):
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '')
    """Verifica que el bot de Telegram valide la presencia del token."""
    bot = CommunityLabTelegramBot(token="")
    with pytest.raises(ValueError, match="No se encontró TELEGRAM_BOT_TOKEN"):
        bot.build_application()


@pytest.mark.anyio
async def test_telegram_bot_handle_incoming_text_success(mock_ai_service):
    """Verifica el flujo completo de recepción y respuesta de texto en Telegram."""
    dispatcher = ChannelMessageDispatcher(ai_service=mock_ai_service, persist_locally=False)
    bot = CommunityLabTelegramBot(token="dummy_token_123", dispatcher=dispatcher)

    # Mock de objetos de Telegram
    mock_user = MagicMock(spec=User)
    mock_user.first_name = "Ana"
    mock_user.username = "ana_dev"

    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 998877

    mock_message = MagicMock(spec=Message)
    mock_message.message_id = 456
    mock_message.text = "Tengo dudas con n8n"
    mock_message.reply_text = AsyncMock()

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_chat = mock_chat
    mock_update.effective_message = mock_message

    mock_context = MagicMock()
    mock_context.bot.send_chat_action = AsyncMock()

    await bot.handle_incoming_text(mock_update, mock_context)

    # Debe enviar indicador de typing y responder con el Markdown formateado
    mock_context.bot.send_chat_action.assert_called_once_with(chat_id=998877, action="typing")
    mock_message.reply_text.assert_called_once()
    args, kwargs = mock_message.reply_text.call_args
    assert "CommunityLab IA Assistant" in args[0]
    assert kwargs.get("parse_mode") == "Markdown"


@pytest.mark.anyio
async def test_telegram_bot_commands(mock_ai_service):
    """Verifica los comandos /start y /help."""
    bot = CommunityLabTelegramBot(token="dummy", dispatcher=ChannelMessageDispatcher(mock_ai_service))

    mock_message = MagicMock(spec=Message)
    mock_message.reply_text = AsyncMock()

    mock_user = MagicMock(spec=User)
    mock_user.first_name = "Lucas"

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.effective_message = mock_message

    await bot.handle_start(mock_update, MagicMock())
    assert "¡Hola Lucas!" in mock_message.reply_text.call_args[0][0]

    await bot.handle_help(mock_update, MagicMock())
    assert "Ayuda de CommunityLab" in mock_message.reply_text.call_args[0][0]


# =============================================================================
# PRUEBAS DEL BOT DE DISCORD
# =============================================================================

def test_discord_bot_missing_token_raises_error(monkeypatch):
    monkeypatch.setenv('DISCORD_BOT_TOKEN', '')
    """Verifica que el bot de Discord valide la presencia de DISCORD_BOT_TOKEN."""
    bot = CommunityLabDiscordBot(token="")
    with pytest.raises(ValueError, match="No se encontró DISCORD_BOT_TOKEN"):
        bot.start_bot()


@pytest.mark.anyio
async def test_discord_bot_ignores_self_messages(mock_ai_service):
    """Verifica que el bot no procese sus propios mensajes para evitar loops infinitos."""
    dispatcher = ChannelMessageDispatcher(ai_service=mock_ai_service, persist_locally=False)
    bot = CommunityLabDiscordBot(token="dummy", dispatcher=dispatcher)

    # Simular usuario del bot
    bot_user = MagicMock()
    bot._connection.user = bot_user

    mock_msg = MagicMock()
    mock_msg.author = bot_user  # El autor es el mismo bot

    await bot.on_message(mock_msg)
    mock_ai_service.process_interaction.assert_not_called()


@pytest.mark.anyio
async def test_discord_bot_processes_mention_with_embed(mock_ai_service):
    """Verifica que el bot responda con un Embed cuando es mencionado en un canal."""
    dispatcher = ChannelMessageDispatcher(ai_service=mock_ai_service, persist_locally=False)
    bot = CommunityLabDiscordBot(token="dummy", dispatcher=dispatcher)

    bot_user = MagicMock()
    bot_user.id = 12345
    bot._connection.user = bot_user

    mock_author = MagicMock()
    mock_author.display_name = "Mariana"

    mock_channel = MagicMock()
    mock_channel.name = "proyectos-ia"
    mock_channel.typing = MagicMock()
    mock_channel.typing.return_value.__aenter__ = AsyncMock()
    mock_channel.typing.return_value.__aexit__ = AsyncMock()

    mock_msg = MagicMock()
    mock_msg.author = mock_author
    mock_msg.channel = mock_channel
    mock_msg.content = "<@12345> ¿Cómo publico mi proyecto en OCI?"
    mock_msg.id = 888999
    mock_msg.reply = AsyncMock()

    # Configurar que el bot está mencionado
    bot_user.mentioned_in.return_value = True

    await bot.on_message(mock_msg)

    mock_msg.reply.assert_called_once()
    _, kwargs = mock_msg.reply.call_args
    assert "embed" in kwargs
    embed = kwargs["embed"]
    assert embed.title == "🤖 CommunityLab Assistant"


# =============================================================================
# PRUEBAS DEL BOT DE SLACK
# =============================================================================

def test_slack_bot_missing_tokens_raises_error(monkeypatch):
    monkeypatch.setenv('SLACK_BOT_TOKEN', '')
    monkeypatch.setenv('SLACK_APP_TOKEN', '')
    """Verifica validación de tokens bot y app en Slack."""
    bot_no_token = CommunityLabSlackBot(bot_token="", app_token="xapp-123")
    with pytest.raises(ValueError, match="No se encontró SLACK_BOT_TOKEN"):
        bot_no_token.build_app(token_verification_enabled=False)

    bot_no_app = CommunityLabSlackBot(bot_token="xoxb-123", app_token="")
    with pytest.raises(ValueError, match="No se encontró SLACK_APP_TOKEN"):
        bot_no_app.start_socket_mode()


def test_slack_bot_event_handler_dispatches_correctly(mock_ai_service):
    """Verifica que el evento app_mention llame a say con los bloques formateados."""
    dispatcher = ChannelMessageDispatcher(ai_service=mock_ai_service, persist_locally=False)
    bot = CommunityLabSlackBot(bot_token="xoxb-dummy", app_token="xapp-dummy", dispatcher=dispatcher)

    app = bot.build_app(token_verification_enabled=False)
    assert app is not None

    # Extraer el listener registrado para 'app_mention'
    listeners = app._listeners
    assert len(listeners) > 0

    # Invocar el handler simulando el evento de Slack
    handler_func = listeners[0].ack_function

    mock_say = MagicMock()
    body = {
        "event": {
            "user": "U12345",
            "text": "<@BOTID> Gran avance en el módulo de Gemini!",
            "channel": "C999",
            "ts": "1620000000.000100",
        }
    }

    handler_func(body=body, say=mock_say)

    mock_say.assert_called_once()
    _, kwargs = mock_say.call_args
    assert "blocks" in kwargs
    assert kwargs.get("thread_ts") == "1620000000.000100"
    assert len(kwargs["blocks"]) >= 3


def test_slack_bot_resolves_user_display_name():
    """Verifica que el bot de Slack resuelva el nombre real a través del WebClient."""
    bot = CommunityLabSlackBot(bot_token="xoxb-dummy", app_token="xapp-dummy")
    mock_client = MagicMock()
    mock_client.users_info.return_value = {
        "ok": True,
        "user": {
            "name": "cesarcely",
            "real_name": "César Augusto Cely Pulido",
            "profile": {
                "display_name": "César Cely",
                "real_name": "César Augusto Cely Pulido",
            },
        },
    }

    nombre = bot.get_user_display_name(mock_client, "U0C4B8B3K43")
    assert nombre == "César Cely"

    # Verificar caché (segunda llamada no invoca users_info)
    mock_client.users_info.reset_mock()
    nombre_cache = bot.get_user_display_name(mock_client, "U0C4B8B3K43")
    assert nombre_cache == "César Cely"
    mock_client.users_info.assert_not_called()
