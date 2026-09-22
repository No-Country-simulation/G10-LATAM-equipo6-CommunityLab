"""Bot de Discord para CommunityLab mediante WebSocket Gateway (discord.py)."""

import logging
import os
from typing import Optional

import discord
from discord.ext import commands

from src.channels.dispatcher import ChannelMessageDispatcher

logger = logging.getLogger("CommunityLab.Channels.Discord")


class CommunityLabDiscordBot(commands.Bot):
    """Cliente de Discord para recibir y responder interacciones en tiempo real."""

    def __init__(
        self,
        token: Optional[str] = None,
        dispatcher: Optional[ChannelMessageDispatcher] = None,
        command_prefix: str = "!",
    ) -> None:
        """Inicializa el bot de Discord con sus intents requeridos.

        Args:
            token: Token de la aplicación Discord. Si es None, lee DISCORD_BOT_TOKEN de .env.
            dispatcher: Instancia de ChannelMessageDispatcher.
            command_prefix: Prefijo de comandos (por defecto '!').
        """
        intents = discord.Intents.default()
        intents.message_content = True  # Requiere Message Content Intent habilitado

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.token = os.getenv("DISCORD_BOT_TOKEN") if token is None else token
        self.dispatcher = dispatcher or ChannelMessageDispatcher()

    async def on_ready(self) -> None:
        """Evento ejecutado cuando el bot se conecta al Gateway de Discord."""
        logger.info("Discord Bot conectado como %s (ID: %s)", self.user, getattr(self.user, "id", None))
        print(f"🎮 [Discord Bot] Conectado exitosamente como {self.user}")

    async def on_message(self, message: discord.Message) -> None:
        """Manejador de mensajes entrantes en canales y mensajes directos."""
        # Evitar responderse a sí mismo
        if message.author == self.user:
            return

        # Procesar si mencionan al bot o si es mensaje directo
        es_mencion = self.user and self.user.mentioned_in(message)
        es_dm = isinstance(message.channel, discord.DMChannel)

        if es_mencion or es_dm:
            async with message.channel.typing():
                autor_nombre = message.author.display_name or message.author.name
                canal_nombre = getattr(message.channel, "name", "direct-message")
                texto_crudo = message.content

                # Limpiar la mención si existe
                if self.user:
                    texto_crudo = texto_crudo.replace(f"<@{self.user.id}>", "").strip()

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

                except Exception as e:
                    logger.error("Error en Discord Bot al procesar mensaje: %s", e)
                    await message.reply(f"⚠️ Error al analizar con CommunityLab: {e}")

        await self.process_commands(message)

    def start_bot(self) -> None:
        """Inicia el bot de Discord conectándose al Gateway."""
        if not self.token:
            raise ValueError(
                "No se encontró DISCORD_BOT_TOKEN. Configúralo en .env o pásalo al instanciar el bot."
            )
        self.run(self.token)
