"""Bot de Telegram para CommunityLab mediante Long Polling (python-telegram-bot)."""

import logging
import os
from typing import Any, Optional

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from src.channels.dispatcher import ChannelMessageDispatcher

logger = logging.getLogger("CommunityLab.Channels.Telegram")


class CommunityLabTelegramBot:
    """Gestiona el ciclo de vida y los eventos del bot de Telegram."""

    def __init__(
        self,
        token: Optional[str] = None,
        dispatcher: Optional[ChannelMessageDispatcher] = None,
    ) -> None:
        """Inicializa el bot con token y dispatcher.

        Args:
            token: Token de la API de Telegram. Si es None, lee TELEGRAM_BOT_TOKEN de .env.
            dispatcher: Instancia de ChannelMessageDispatcher para procesar con IA.
        """
        self.token = os.getenv("TELEGRAM_BOT_TOKEN") if token is None else token
        self.dispatcher = dispatcher or ChannelMessageDispatcher()
        self.application: Optional[Application] = None

    def build_application(self) -> Application:
        """Construye y registra los manejadores de comandos y mensajes."""
        if not self.token:
            raise ValueError(
                "No se encontró TELEGRAM_BOT_TOKEN. Configúralo en .env o pásalo al instanciar el bot."
            )

        app = ApplicationBuilder().token(self.token).build()

        app.add_handler(CommandHandler("start", self.handle_start))
        app.add_handler(CommandHandler("help", self.handle_help))
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_incoming_text)
        )

        self.application = app
        return app

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manejador del comando /start."""
        if not update.effective_user or not update.effective_message:
            return
        nombre = update.effective_user.first_name
        saludo = (
            f"👋 ¡Hola {nombre}! Bienvenido a *CommunityLab Bot* (Modo Python Nativo).\n\n"
            "Envía cualquier consulta, duda técnica, testimonio de empleo o feedback "
            "de los cursos. Nuestro motor de IA (Gemini 2.5 Flash) lo procesará al instante.\n\n"
            "Comandos disponibles:\n"
            "• `/start` - Iniciar bot y ver bienvenida\n"
            "• `/help` - Ver ayuda técnica"
        )
        await update.effective_message.reply_text(saludo, parse_mode="Markdown")

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Manejador del comando /help."""
        if not update.effective_message:
            return
        ayuda = (
            "ℹ️ *Ayuda de CommunityLab Assistant*\n\n"
            "Este bot opera mediante *Long Polling* sin requerir túneles ni ngrok.\n"
            "Cada mensaje que envías es procesado por el pipeline:\n"
            "1. Normalización de la interacción (Pydantic).\n"
            "2. Análisis semántico y extracción de copys (Gemini Flash).\n"
            "3. Acumulación en el paquete de distribución para curaduría."
        )
        await update.effective_message.reply_text(ayuda, parse_mode="Markdown")

    async def handle_incoming_text(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Procesa mensajes de texto regulares del usuario."""
        if not update.effective_user or not update.effective_message:
            return

        usuario = update.effective_user.first_name or "Usuario Telegram"
        texto = update.effective_message.text or ""
        msg_id = f"tg_{update.effective_message.message_id}"
        chat_id = update.effective_chat.id if update.effective_chat else None

        if chat_id:
            await context.bot.send_chat_action(chat_id=chat_id, action="typing")

        try:
            _, respuestas = self.dispatcher.process_incoming_message(
                canal_origen="#telegram-comunidad",
                autor=usuario,
                texto=texto,
                mensaje_id_externo=msg_id,
                metadata={"chat_id": chat_id, "username": update.effective_user.username},
            )
            respuesta_md = respuestas["telegram_markdown"]
            await update.effective_message.reply_text(respuesta_md, parse_mode="Markdown")

        except Exception as e:
            logger.error("Error procesando mensaje de Telegram: %s", e)
            await update.effective_message.reply_text(
                f"⚠️ Ocurrió un error al procesar tu interacción: {e}"
            )

    def run_polling(self) -> None:
        """Inicia el bot en modo Long Polling continuo."""
        app = self.build_application()
        logger.info("Iniciando Telegram Bot en modo Long Polling...")
        print("🤖 [Telegram Bot] Conectado y escuchando mensajes vía Long Polling...")
        app.run_polling()
