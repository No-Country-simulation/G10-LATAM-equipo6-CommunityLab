"""Gestor Omnicanal de Bots en Segundo Plano para CommunityLab (Telegram, Discord, Slack)."""

import asyncio
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from src.channels.dispatcher import ChannelMessageDispatcher
from src.channels.discord_bot import CommunityLabDiscordBot
from src.channels.slack_bot import CommunityLabSlackBot
from src.channels.telegram_bot import CommunityLabTelegramBot
from src.utils.config import (
    get_discord_token,
    get_slack_app_token,
    get_slack_bot_token,
    get_telegram_token,
)
from src.utils.logger import setup_logger

logger = setup_logger("CommunityLab.Channels.BotManager")


class OmnichannelBotManager:
    """Gestiona el ciclo de vida concurrente de los bots de Telegram, Discord y Slack.

    Permite iniciar y detener los 3 canales en segundo plano de forma no bloqueante,
    ideal para ser controlado directamente desde la interfaz web de Streamlit o servicios daemon.
    """

    _instance: Optional["OmnichannelBotManager"] = None
    _lock = threading.Lock()

    def __init__(self, dispatcher: Optional[ChannelMessageDispatcher] = None) -> None:
        """Inicializa el gestor de bots."""
        self.dispatcher = dispatcher or ChannelMessageDispatcher()

        # Referencias de instancias
        self._telegram_bot: Optional[CommunityLabTelegramBot] = None
        self._telegram_app: Any = None
        self._telegram_loop: Optional[asyncio.AbstractEventLoop] = None
        self._telegram_thread: Optional[threading.Thread] = None

        self._discord_bot: Optional[CommunityLabDiscordBot] = None
        self._discord_loop: Optional[asyncio.AbstractEventLoop] = None
        self._discord_thread: Optional[threading.Thread] = None

        self._slack_bot: Optional[CommunityLabSlackBot] = None
        self._slack_handler: Any = None

        # Estados de los canales
        self._status: Dict[str, Dict[str, Any]] = {
            "telegram": {
                "running": False,
                "label": "✈️ Telegram",
                "info": "@G10_Latam_06_bot",
                "mode": "Long Polling",
                "error": None,
                "last_started": None,
            },
            "discord": {
                "running": False,
                "label": "🎮 Discord",
                "info": "G10-LATAM-06",
                "mode": "Gateway WebSocket",
                "error": None,
                "last_started": None,
            },
            "slack": {
                "running": False,
                "label": "💬 Slack",
                "info": "G10-LATAM-06 (App 1)",
                "mode": "Socket Mode WebSocket",
                "error": None,
                "last_started": None,
            },
        }


    @classmethod
    def get_instance(cls) -> "OmnichannelBotManager":
        """Obtiene la instancia única del gestor (Patrón Singleton)."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    # --------------------------------------------------------------------------
    # GESTIÓN DE TELEGRAM
    # --------------------------------------------------------------------------
    def _run_telegram_worker(self) -> None:
        """Worker en segundo plano para el bot de Telegram."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._telegram_loop = loop

        try:
            token = get_telegram_token()
            if not token:
                raise ValueError("Token de Telegram no configurado en .env (TELEGRAM_BOT_TOKEN).")

            self._telegram_bot = CommunityLabTelegramBot(token=token, dispatcher=self.dispatcher)
            app = self._telegram_bot.build_application()
            self._telegram_app = app

            self._status["telegram"]["running"] = True
            self._status["telegram"]["error"] = None
            self._status["telegram"]["last_started"] = datetime.now(timezone.utc).isoformat()
            logger.info("[BotManager] Telegram Bot iniciado en hilo secundario.")

            # Ejecutar polling sin registrar señales de SO para evitar excepciones en hilos
            app.run_polling(stop_signals=None, close_loop=False)

        except Exception as e:
            logger.error("[BotManager] Error en worker de Telegram: %s", e)
            self._status["telegram"]["error"] = str(e)
        finally:
            self._status["telegram"]["running"] = False
            logger.info("[BotManager] Telegram Bot finalizado.")

    def start_telegram(self) -> Tuple[bool, str]:
        """Inicia el bot de Telegram en segundo plano."""
        if self._status["telegram"]["running"]:
            return True, "Telegram Bot ya se encuentra en ejecución."

        token = get_telegram_token()
        if not token:
            msg = "Token de Telegram no configurado."
            self._status["telegram"]["error"] = msg
            return False, msg

        self._telegram_thread = threading.Thread(
            target=self._run_telegram_worker,
            name="CommunityLab-Telegram-Thread",
            daemon=True,
        )
        self._telegram_thread.start()
        return True, "Telegram Bot iniciado en segundo plano."

    def stop_telegram(self) -> Tuple[bool, str]:
        """Detiene el bot de Telegram."""
        if not self._status["telegram"]["running"]:
            return True, "Telegram Bot no está en ejecución."

        try:
            if self._telegram_app and self._telegram_loop:
                if self._telegram_app.updater and self._telegram_app.updater.running:
                    fut = asyncio.run_coroutine_threadsafe(
                        self._telegram_app.updater.stop(), self._telegram_loop
                    )
                    fut.result(timeout=5)
                fut2 = asyncio.run_coroutine_threadsafe(
                    self._telegram_app.stop(), self._telegram_loop
                )
                fut2.result(timeout=5)
            self._status["telegram"]["running"] = False
            return True, "Telegram Bot detenido correctamente."
        except Exception as e:
            logger.error("[BotManager] Error deteniendo Telegram: %s", e)
            self._status["telegram"]["running"] = False
            return False, f"Error deteniendo Telegram: {e}"

    # --------------------------------------------------------------------------
    # GESTIÓN DE DISCORD
    # --------------------------------------------------------------------------
    def _run_discord_worker(self) -> None:
        """Worker en segundo plano para el bot de Discord."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._discord_loop = loop

        try:
            token = get_discord_token()
            if not token:
                raise ValueError("Token de Discord no configurado en .env (DISCORD_BOT_TOKEN).")

            self._discord_bot = CommunityLabDiscordBot(token=token, dispatcher=self.dispatcher)
            self._status["discord"]["running"] = True
            self._status["discord"]["error"] = None
            self._status["discord"]["last_started"] = datetime.now(timezone.utc).isoformat()
            logger.info("[BotManager] Discord Bot iniciado en hilo secundario.")

            async def _main():
                try:
                    await self._discord_bot.start(token)
                except asyncio.CancelledError:
                    pass
                finally:
                    if self._discord_bot and not self._discord_bot.is_closed():
                        await self._discord_bot.close()

            loop.run_until_complete(_main())

        except Exception as e:
            logger.error("[BotManager] Error en worker de Discord: %s", e)
            self._status["discord"]["error"] = str(e)
        finally:
            self._status["discord"]["running"] = False
            logger.info("[BotManager] Discord Bot finalizado.")

    def start_discord(self) -> Tuple[bool, str]:
        """Inicia el bot de Discord en segundo plano."""
        if self._status["discord"]["running"]:
            return True, "Discord Bot ya se encuentra en ejecución."

        token = get_discord_token()
        if not token:
            msg = "Token de Discord no configurado."
            self._status["discord"]["error"] = msg
            return False, msg

        self._discord_thread = threading.Thread(
            target=self._run_discord_worker,
            name="CommunityLab-Discord-Thread",
            daemon=True,
        )
        self._discord_thread.start()
        return True, "Discord Bot iniciado en segundo plano."

    def stop_discord(self) -> Tuple[bool, str]:
        """Detiene el bot de Discord."""
        if not self._status["discord"]["running"]:
            return True, "Discord Bot no está en ejecución."

        try:
            if self._discord_bot and self._discord_loop and not self._discord_bot.is_closed():
                fut = asyncio.run_coroutine_threadsafe(
                    self._discord_bot.close(), self._discord_loop
                )
                fut.result(timeout=5)
            self._status["discord"]["running"] = False
            return True, "Discord Bot detenido correctamente."
        except Exception as e:
            logger.error("[BotManager] Error deteniendo Discord: %s", e)
            self._status["discord"]["running"] = False
            return False, f"Error deteniendo Discord: {e}"

    # --------------------------------------------------------------------------
    # GESTIÓN DE SLACK
    # --------------------------------------------------------------------------
    def start_slack(self) -> Tuple[bool, str]:
        """Inicia el bot de Slack vía Socket Mode."""
        if self._status["slack"]["running"]:
            return True, "Slack Bot ya se encuentra en ejecución."

        bot_token = get_slack_bot_token()
        app_token = get_slack_app_token()

        if not bot_token or not app_token:
            msg = "Tokens de Slack incompletos (requiere SLACK_BOT_TOKEN y SLACK_APP_TOKEN)."
            self._status["slack"]["error"] = msg
            return False, msg

        try:
            from slack_bolt.adapter.socket_mode import SocketModeHandler

            self._slack_bot = CommunityLabSlackBot(
                bot_token=bot_token,
                app_token=app_token,
                dispatcher=self.dispatcher,
            )
            app = self._slack_bot.build_app()
            handler = SocketModeHandler(app, app_token)
            self._slack_handler = handler

            # connect() establece la conexión WebSocket en segundo plano sin bloquear el hilo
            handler.connect()

            self._status["slack"]["running"] = True
            self._status["slack"]["error"] = None
            self._status["slack"]["last_started"] = datetime.now(timezone.utc).isoformat()
            logger.info("[BotManager] Slack Bot conectado vía Socket Mode.")
            return True, "Slack Bot conectado exitosamente."

        except Exception as e:
            logger.error("[BotManager] Error iniciando Slack: %s", e)
            self._status["slack"]["running"] = False
            self._status["slack"]["error"] = str(e)
            return False, f"Error iniciando Slack: {e}"

    def stop_slack(self) -> Tuple[bool, str]:
        """Detiene el bot de Slack."""
        if not self._status["slack"]["running"]:
            return True, "Slack Bot no está en ejecución."

        try:
            if self._slack_handler:
                self._slack_handler.close()
                self._slack_handler = None
            self._status["slack"]["running"] = False
            return True, "Slack Bot detenido correctamente."
        except Exception as e:
            logger.error("[BotManager] Error deteniendo Slack: %s", e)
            self._status["slack"]["running"] = False
            return False, f"Error deteniendo Slack: {e}"

    # --------------------------------------------------------------------------
    # OPERACIONES GLOBALES (MULTICANAL)
    # --------------------------------------------------------------------------
    def start_channel(self, channel: str) -> Tuple[bool, str]:
        """Inicia un canal específico por nombre ('telegram', 'discord', 'slack')."""
        ch = channel.lower().strip()
        if ch == "telegram":
            return self.start_telegram()
        elif ch == "discord":
            return self.start_discord()
        elif ch == "slack":
            return self.start_slack()
        else:
            return False, f"Canal desconocido: {channel}"

    def stop_channel(self, channel: str) -> Tuple[bool, str]:
        """Detiene un canal específico por nombre."""
        ch = channel.lower().strip()
        if ch == "telegram":
            return self.stop_telegram()
        elif ch == "discord":
            return self.stop_discord()
        elif ch == "slack":
            return self.stop_slack()
        else:
            return False, f"Canal desconocido: {channel}"

    def start_all(self) -> Dict[str, Tuple[bool, str]]:
        """Inicia los 3 canales de forma concurrente."""
        results = {
            "telegram": self.start_telegram(),
            "discord": self.start_discord(),
            "slack": self.start_slack(),
        }
        logger.info("[BotManager] start_all ejecutado. Resultados: %s", results)
        return results

    def stop_all(self) -> Dict[str, Tuple[bool, str]]:
        """Detiene los 3 canales concurrentes."""
        results = {
            "telegram": self.stop_telegram(),
            "discord": self.stop_discord(),
            "slack": self.stop_slack(),
        }
        try:
            logger.info("[BotManager] stop_all ejecutado. Resultados: %s", results)
        except Exception:
            pass
        return results

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        """Retorna el estado detallado de cada canal."""
        return {k: dict(v) for k, v in self._status.items()}

    def is_running(self, channel: Optional[str] = None) -> bool:
        """Verifica si un canal específico o al menos uno está activo."""
        if channel:
            return bool(self._status.get(channel.lower(), {}).get("running", False))
        return any(v.get("running", False) for v in self._status.values())


def get_bot_manager() -> OmnichannelBotManager:
    """Función de conveniencia para obtener el gestor global de bots."""
    return OmnichannelBotManager.get_instance()
