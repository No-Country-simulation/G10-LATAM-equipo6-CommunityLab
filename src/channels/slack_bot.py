"""Bot de Slack para CommunityLab mediante Socket Mode (slack-bolt)."""

import logging
import os
import re
from typing import Any, Callable, Dict, Optional

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.channels.dispatcher import ChannelMessageDispatcher

from src.utils.logger import setup_logger
from src.utils.config import get_slack_bot_token, get_slack_app_token
logger = setup_logger("CommunityLab.Channels.Slack")


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
        self.bot_token = get_slack_bot_token() if bot_token is None else bot_token
        self.app_token = get_slack_app_token() if app_token is None else app_token
        self.dispatcher = dispatcher or ChannelMessageDispatcher()

        self.app: Optional[App] = None
        self.handler: Optional[SocketModeHandler] = None
        self._user_cache: Dict[str, str] = {}

    def get_user_display_name(self, client: Any, user_id: str) -> str:
        """Obtiene el nombre real o display name del usuario de Slack usando la WebClient API con caché."""
        if not user_id or user_id == "SlackUser":
            return "Usuario Slack"
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        try:
            res = client.users_info(user=user_id)
            if res.get("ok"):
                user_info = res.get("user", {})
                profile = user_info.get("profile", {})
                name = (
                    profile.get("display_name")
                    or profile.get("real_name")
                    or user_info.get("real_name")
                    or user_info.get("name")
                    or user_id
                )
                self._user_cache[user_id] = name
                return name
        except Exception as e:
            logger.debug("No se pudo obtener información del usuario Slack '%s': %s", user_id, e)
        default_name = f"User_{user_id}"
        self._user_cache[user_id] = default_name
        return default_name

    def build_app(self, token_verification_enabled: bool = True) -> App:
        """Construye la aplicación Slack Bolt y registra los eventos."""
        if not self.bot_token:
            raise ValueError("No se encontró SLACK_BOT_TOKEN ('xoxb-...'). Configúralo en .env.")

        app = App(token=self.bot_token, token_verification_enabled=token_verification_enabled)

        @app.event("app_mention")
        def handle_mention(body: Dict[str, Any], say: Callable[..., Any], client: Optional[Any] = None) -> None:
            event = body.get("event", {})
            user_id = event.get("user", "SlackUser")
            text_crudo = event.get("text", "")
            channel_id = event.get("channel", "general")
            thread_ts = event.get("thread_ts", event.get("ts"))

            slack_client = client or app.client
            nombre_autor = self.get_user_display_name(slack_client, user_id)
            logger.info("Slack mención recibida de '%s' (%s) en canal '%s': %s", nombre_autor, user_id, channel_id, text_crudo[:80])
            print(f"[Slack Bot] Mención recibida de '{nombre_autor}' ({user_id}) en #{channel_id}: {text_crudo[:60]}...", flush=True)

            # Limpiar mención al bot del texto (<@U12345...>)
            texto_limpio = re.sub(r'<@[A-Z0-9]+>', '', text_crudo).strip()
            if not texto_limpio:
                texto_limpio = "Hola"

            try:
                _, respuestas = self.dispatcher.process_incoming_message(
                    canal_origen=f"#slack-{channel_id}",
                    autor=nombre_autor,
                    texto=texto_limpio,
                    mensaje_id_externo=f"slk_{event.get('ts')}",
                    metadata={"user_id": user_id, "channel": channel_id},
                )

                bloques = respuestas["slack_blocks"]
                say(blocks=bloques, text="Análisis de CommunityLab completado", thread_ts=thread_ts)
                logger.info("Respuesta enviada exitosamente a Slack para '%s'", nombre_autor)

            except Exception as e:
                logger.error("Error en Slack Bot: %s", e)
                say(text=f"⚠️ Error procesando en CommunityLab: {e}", thread_ts=thread_ts)

        @app.event("message")
        def handle_message(body: Dict[str, Any], say: Callable[..., Any], client: Optional[Any] = None) -> None:
            event = body.get("event", {})
            # Ignorar mensajes de bots o ediciones de mensajes
            if event.get("bot_id") or event.get("subtype"):
                return
            channel_type = event.get("channel_type")
            # Manejar mensajes directos (DM) al bot
            if channel_type == "im":
                user_id = event.get("user", "SlackUser")
                text_crudo = event.get("text", "")
                thread_ts = event.get("thread_ts", event.get("ts"))
                slack_client = client or app.client
                nombre_autor = self.get_user_display_name(slack_client, user_id)
                logger.info("Slack DM recibido de '%s' (%s): %s", nombre_autor, user_id, text_crudo[:80])
                print(f"[Slack Bot] Mensaje Directo de '{nombre_autor}' ({user_id}): {text_crudo[:60]}...", flush=True)
                try:
                    _, respuestas = self.dispatcher.process_incoming_message(
                        canal_origen="#slack-dm",
                        autor=nombre_autor,
                        texto=text_crudo,
                        mensaje_id_externo=f"slk_{event.get('ts')}",
                        metadata={"user_id": user_id, "channel_type": "im"},
                    )
                    bloques = respuestas["slack_blocks"]
                    say(blocks=bloques, text="Análisis de CommunityLab completado", thread_ts=thread_ts)
                except Exception as e:
                    logger.error("Error en Slack Bot DM: %s", e)
                    say(text=f"⚠️ Error procesando en CommunityLab: {e}", thread_ts=thread_ts)

        self.app = app
        return app

    def start_socket_mode(self) -> None:
        """Inicia la conexión WebSocket saliente con Socket Mode."""
        if not self.app_token:
            raise ValueError("No se encontró SLACK_APP_TOKEN ('xapp-...'). Configúralo en .env.")

        app = self.build_app()
        logger.info("Iniciando Slack Bot con Socket Mode...")
        print("💬 [Slack Bot] Conectado y escuchando menciones vía Socket Mode...", flush=True)
        handler = SocketModeHandler(app, self.app_token)
        self.handler = handler
        handler.start()
