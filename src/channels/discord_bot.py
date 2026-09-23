"""Bot de Discord para CommunityLab mediante WebSocket Gateway (discord.py)."""

from __future__ import annotations

import os
import re
from typing import Optional
import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.utils.logger import setup_logger
from src.utils.config import get_discord_token
from src.channels.dispatcher import ChannelMessageDispatcher

load_dotenv()
logger = setup_logger("CommunityLab.Channels.Discord")


class CommunityLabDiscordBot(commands.Bot):
    """Bot de Discord conectado al Gateway oficial en tiempo real."""

    def __init__(
        self,
        token: Optional[str] = None,
        dispatcher: Optional[ChannelMessageDispatcher] = None,
        command_prefix: str = "!",
    ) -> None:
        """Inicializa el cliente de Discord con intents de contenido de mensajes.

        Args:
            token: Token de la aplicación Discord. Si es None, lee DISCORD_LOCAL_BOT_TOKEN o DISCORD_BOT_TOKEN.
            dispatcher: Instancia de ChannelMessageDispatcher.
            command_prefix: Prefijo de comandos (por defecto '!').
        """
        intents = discord.Intents.default()
        intents.messages = True
        intents.guild_messages = True
        intents.dm_messages = True
        intents.message_content = True  # Requiere Message Content Intent habilitado

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = get_discord_token() if token is None else token
        self.dispatcher = dispatcher or ChannelMessageDispatcher()

    async def on_ready(self) -> None:
        """Evento ejecutado cuando el bot se conecta al Gateway de Discord."""
        logger.info("Discord Bot conectado como %s (ID: %s)", self.user, getattr(self.user, "id", None))
        print(f"[Discord Bot] Conectado exitosamente como {self.user} (ID: {getattr(self.user, 'id', None)})")
        print(f"[Discord Bot] Servidores conectados: {[g.name for g in self.guilds]}")

    async def on_message(self, message: discord.Message) -> None:
        """Manejador de mensajes entrantes en canales y mensajes directos."""
        # Evitar responderse a sí mismo
        if message.author == self.user:
            return

        autor_nombre = message.author.display_name or message.author.name
        canal_nombre = getattr(message.channel, "name", "direct-message")
        texto_crudo = message.content or ""

        bot_name = self.user.name.lower() if self.user else ""
        bot_display = getattr(self.user, "display_name", "").lower() if self.user else ""

        es_mencion = bool(
            (self.user in message.mentions)
            or (self.user and self.user.mentioned_in(message))
            or (self.user and f"<@{self.user.id}>" in texto_crudo)
            or (self.user and f"<@!{self.user.id}>" in texto_crudo)
            or (bot_name and bot_name in texto_crudo.lower())
            or (bot_display and bot_display in texto_crudo.lower())
        )
        es_dm = isinstance(message.channel, discord.DMChannel)
        es_canal_general = canal_nombre.lower() in ("general", "dudas", "consultas", "bot", "communitylab")

        print(f"[Discord] [MSG ENTRANTE] Canal: #{canal_nombre} | De: {autor_nombre} | Texto: '{texto_crudo}' | Mencion: {es_mencion}")
        logger.info("[Discord] Mensaje detectado de %s en #%s: '%s' (mencion=%s, dm=%s)", autor_nombre, canal_nombre, texto_crudo, es_mencion, es_dm)

        # Responder si mencionan al bot, si es mensaje directo, o si escriben en canal general de pruebas
        if es_mencion or es_dm or es_canal_general:
            if not texto_crudo.strip():
                print("[Discord] [AVISO] El texto recibido está vacío. Verifica que 'Message Content Intent' esté activado en Discord Developer Portal.")
                return

            async with message.channel.typing():
                # Limpiar menciones de usuario o rol (<@123...>, <@&123...>) para la IA
                texto_crudo = re.sub(r'<@&?[0-9]+>', '', texto_crudo)
                if bot_name:
                    texto_crudo = texto_crudo.replace(f"@{self.user.name}", "")
                texto_crudo = texto_crudo.strip()

                if not texto_crudo:
                    texto_crudo = "Hola"

                msg_id = f"dc_{message.id}"

                try:
                    _, respuestas = self.dispatcher.process_incoming_message(
                        canal_origen=f"#{canal_nombre}",
                        autor=autor_nombre,
                        texto=texto_crudo,
                        mensaje_id_externo=msg_id,
                        metadata={"guild_id": getattr(message.guild, "id", None)},
                    )

                    dict_embed = respuestas["discord_embed"]
                    embed = discord.Embed(
                        title=dict_embed["title"],
                        description=dict_embed["description"],
                        color=dict_embed["color"],
                    )
                    for f in dict_embed["fields"]:
                        embed.add_field(name=f["name"], value=f["value"], inline=f.get("inline", False))
                    embed.set_footer(text=dict_embed["footer"]["text"])

                    await message.reply(embed=embed)
                    print(f"[Discord] [OK] Respuesta enviada exitosamente a {autor_nombre}.")
                    logger.info("[Discord] Respuesta enviada exitosamente a %s (Msg ID: %s)", autor_nombre, msg_id)

                except Exception as e:
                    logger.error("Error en Discord Bot al procesar mensaje: %s", e)
                    print(f"[Discord] [ERROR] Error procesando mensaje: {e}")
                    await message.reply(f"⚠️ Ocurrió un error al procesar tu consulta con CommunityLab IA: {e}")

        await self.process_commands(message)

    def start_bot(self) -> None:
        """Inicia el bot de Discord conectándose al Gateway."""
        if not self.token:
            raise ValueError(
                "No se encontró DISCORD_BOT_TOKEN (o DISCORD_LOCAL_BOT_TOKEN en LOCAL). Configúralo en .env o pásalo al instanciar el bot."
            )
        self.run(self.token)
