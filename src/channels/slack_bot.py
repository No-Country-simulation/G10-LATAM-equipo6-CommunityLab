"""Bot de Slack para CommunityLab mediante Socket Mode (slack-bolt)."""

import logging
import os
from typing import Any, Callable, Dict, Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.channels.dispatcher import ChannelMessageDispatcher

logger = logging.getLogger("CommunityLab.Channels.Slack")


class CommunityLabSlackBot:
    """Cliente de Slack con soporte de Socket Mode sin túneles ngrok."""

    def __init__(
        self,
        bot_token: Optional[str] = None,
        app_token: Optional[str] = None,
        dispatcher: Optional[ChannelMessageDispatcher] = None,
    ) -> None:
        """Inicializa la app de Slack.

        Args:
            bot_token: Token de bot 'xoxb-...'. Si es None, lee SLACK_BOT_TOKEN de .env.
            app_token: Token de app 'xapp-...'. Si es None, lee SLACK_APP_TOKEN de .env.
            dispatcher: Instancia de ChannelMessageDispatcher.
        """
        self.bot_token = os.getenv("SLACK_BOT_TOKEN") if bot_token is None else bot_token
        self.app_token = os.getenv("SLACK_APP_TOKEN") if app_token is None else app_token
        self.dispatcher = dispatcher or ChannelMessageDispatcher()

        self.app: Optional[App] = None
        self.handler: Optional[SocketModeHandler] = None

    def build_app(self, token_verification_enabled: bool = True) -> App:
        """Construye la aplicación Slack Bolt y registra los eventos."""
        if not self.bot_token:
            raise ValueError("No se encontró SLACK_BOT_TOKEN ('xoxb-...'). Configúralo en .env.")

        app = App(token=self.bot_token, token_verification_enabled=token_verification_enabled)

        @app.event("app_mention")
        def handle_mention(body: Dict[str, Any], say: Callable[..., Any]) -> None:
            event = body.get("event", {})
            user_id = event.get("user", "SlackUser")
            text_crudo = event.get("text", "")
            channel_id = event.get("channel", "general")
            thread_ts = event.get("thread_ts", event.get("ts"))

            logger.info("Slack mención recibida de '%s' en canal '%s'", user_id, channel_id)

            try:
                _, respuestas = self.dispatcher.process_incoming_message(
                    canal_origen=f"#slack-{channel_id}",
                    autor=f"User_{user_id}",
                    texto=text_crudo,
                    mensaje_id_externo=f"slk_{event.get('ts')}",
                    metadata={"user_id": user_id, "channel": channel_id},
                )

                bloques = respuestas["slack_blocks"]
                say(blocks=bloques, text="Análisis de CommunityLab completado", thread_ts=thread_ts)

            except Exception as e:
                logger.error("Error en Slack Bot: %s", e)
                say(text=f"⚠️ Error procesando en CommunityLab: {e}", thread_ts=thread_ts)

        self.app = app
        return app

    def start_socket_mode(self) -> None:
        """Inicia la conexión WebSocket saliente con Socket Mode."""
        if not self.app_token:
            raise ValueError("No se encontró SLACK_APP_TOKEN ('xapp-...'). Configúralo en .env.")

        app = self.build_app()
        logger.info("Iniciando Slack Bot con Socket Mode...")
        print("💬 [Slack Bot] Conectado y escuchando menciones vía Socket Mode...")
        handler = SocketModeHandler(app, self.app_token)
        self.handler = handler
        handler.start()
