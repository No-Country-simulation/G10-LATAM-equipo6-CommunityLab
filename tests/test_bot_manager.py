# -*- coding: utf-8 -*-
"""Pruebas unitarias para el gestor omnicanal de bots (OmnichannelBotManager)."""

from unittest.mock import MagicMock, patch
import pytest

from src.channels.bot_manager import OmnichannelBotManager, get_bot_manager


@pytest.fixture
def mock_dispatcher():
    """Mock del dispatcher universal de mensajes."""
    dispatcher = MagicMock()
    dispatcher.process_incoming_message.return_value = (
        MagicMock(),
        {"telegram_text": "OK", "discord_embed": {}, "slack_blocks": []},
    )
    return dispatcher


@pytest.fixture
def clean_manager(mock_dispatcher):
    """Crea una instancia fresca de OmnichannelBotManager para pruebas."""
    manager = OmnichannelBotManager(dispatcher=mock_dispatcher)
    # Limpiar estado previo
    for ch in ["telegram", "discord", "slack"]:
        manager._status[ch]["running"] = False
        manager._status[ch]["error"] = None
    return manager


def test_singleton_get_instance():
    """Verifica que get_bot_manager retorne una instancia única singleton."""
    inst1 = get_bot_manager()
    inst2 = OmnichannelBotManager.get_instance()
    assert inst1 is inst2
    assert isinstance(inst1, OmnichannelBotManager)


def test_initial_status(clean_manager):
    """Verifica que el estado inicial de los bots sea inactivo y estructurado."""
    status = clean_manager.get_status()
    assert "telegram" in status
    assert "discord" in status
    assert "slack" in status

    for ch in ["telegram", "discord", "slack"]:
        assert status[ch]["running"] is False
        assert status[ch]["error"] is None
        assert "label" in status[ch]
        assert "info" in status[ch]
        assert "mode" in status[ch]

    assert clean_manager.is_running() is False
    assert clean_manager.is_running("telegram") is False


def test_missing_tokens_handling(clean_manager):
    """Verifica que el gestor maneje elegantemente la ausencia de tokens sin excepciones."""
    with patch("src.channels.bot_manager.get_telegram_token", return_value=None):
        ok, msg = clean_manager.start_telegram()
        assert ok is False
        assert "no configurado" in msg
        assert clean_manager._status["telegram"]["running"] is False
        assert clean_manager._status["telegram"]["error"] is not None

    with patch("src.channels.bot_manager.get_discord_token", return_value=None):
        ok, msg = clean_manager.start_discord()
        assert ok is False
        assert "no configurado" in msg
        assert clean_manager._status["discord"]["running"] is False

    with patch("src.channels.bot_manager.get_slack_bot_token", return_value=None):
        ok, msg = clean_manager.start_slack()
        assert ok is False
        assert "incompletos" in msg
        assert clean_manager._status["slack"]["running"] is False


def test_start_and_stop_telegram_mocked(clean_manager):
    """Verifica el ciclo de vida de inicio y parada de Telegram con mocks."""
    mock_app = MagicMock()
    mock_app.updater = MagicMock()
    mock_app.updater.running = True
    clean_manager._telegram_app = mock_app
    clean_manager._status["telegram"]["running"] = True

    # Detener
    ok, msg = clean_manager.stop_telegram()
    assert ok is True
    assert clean_manager._status["telegram"]["running"] is False

    # Iniciar con token mockeado
    with patch("src.channels.bot_manager.get_telegram_token", return_value="mock_tg_token"), \
         patch("threading.Thread") as mock_thread:
        ok, msg = clean_manager.start_telegram()
        assert ok is True
        mock_thread.assert_called_once()


def test_start_and_stop_discord_mocked(clean_manager):
    """Verifica el ciclo de vida de inicio y parada de Discord con mocks."""
    mock_bot = MagicMock()
    mock_bot.is_closed.return_value = False
    clean_manager._discord_bot = mock_bot
    clean_manager._status["discord"]["running"] = True

    ok, msg = clean_manager.stop_discord()
    assert ok is True
    assert clean_manager._status["discord"]["running"] is False

    with patch("src.channels.bot_manager.get_discord_token", return_value="mock_dc_token"), \
         patch("threading.Thread") as mock_thread:
        ok, msg = clean_manager.start_discord()
        assert ok is True
        mock_thread.assert_called_once()


def test_start_and_stop_slack_mocked(clean_manager):
    """Verifica el inicio y parada de Slack con mocks."""
    mock_handler = MagicMock()
    clean_manager._slack_handler = mock_handler
    clean_manager._status["slack"]["running"] = True

    ok, msg = clean_manager.stop_slack()
    assert ok is True
    mock_handler.close.assert_called_once()
    assert clean_manager._status["slack"]["running"] is False

    with patch("src.channels.bot_manager.get_slack_bot_token", return_value="xoxb-mock"), \
         patch("src.channels.bot_manager.get_slack_app_token", return_value="xapp-mock"), \
         patch("src.channels.slack_bot.CommunityLabSlackBot.build_app"), \
         patch("slack_bolt.adapter.socket_mode.SocketModeHandler") as mock_sm_class:
        mock_sm_instance = MagicMock()
        mock_sm_class.return_value = mock_sm_instance

        ok, msg = clean_manager.start_slack()
        assert ok is True
        mock_sm_instance.connect.assert_called_once()
        assert clean_manager._status["slack"]["running"] is True


def test_start_channel_invalid(clean_manager):
    """Verifica manejo de canal desconocido."""
    ok, msg = clean_manager.start_channel("whatsapp")
    assert ok is False
    assert "desconocido" in msg

    ok_stop, msg_stop = clean_manager.stop_channel("whatsapp")
    assert ok_stop is False
    assert "desconocido" in msg_stop


def test_start_all_and_stop_all(clean_manager):
    """Verifica llamadas masivas a start_all y stop_all."""
    with patch.object(clean_manager, "start_telegram", return_value=(True, "OK")), \
         patch.object(clean_manager, "start_discord", return_value=(True, "OK")), \
         patch.object(clean_manager, "start_slack", return_value=(True, "OK")):
        results = clean_manager.start_all()
        assert len(results) == 3
        assert results["telegram"] == (True, "OK")
        assert results["discord"] == (True, "OK")
        assert results["slack"] == (True, "OK")

    with patch.object(clean_manager, "stop_telegram", return_value=(True, "OK")), \
         patch.object(clean_manager, "stop_discord", return_value=(True, "OK")), \
         patch.object(clean_manager, "stop_slack", return_value=(True, "OK")):
        results_stop = clean_manager.stop_all()
        assert len(results_stop) == 3
        assert results_stop["telegram"] == (True, "OK")
        assert results_stop["discord"] == (True, "OK")
        assert results_stop["slack"] == (True, "OK")
