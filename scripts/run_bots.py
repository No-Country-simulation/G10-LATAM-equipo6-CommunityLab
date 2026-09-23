import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
import sys
import pathlib

# Asegurar que el root del proyecto este en sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -*- coding: utf-8 -*-
"""Lanzador de Bots de Mensajería Dinámica (Telegram, Discord, Slack) para CommunityLab."""

import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

from src.utils.logger import setup_logger
from src.utils.config import get_entorno_deploy, get_active_config_summary
from src.channels.dispatcher import ChannelMessageDispatcher
from src.channels.telegram_bot import CommunityLabTelegramBot
from src.channels.discord_bot import CommunityLabDiscordBot
from src.channels.slack_bot import CommunityLabSlackBot

def main():
    parser = argparse.ArgumentParser(
        description="Lanzador de Bots de Canales Dinámicos - CommunityLab"
    )
    parser.add_argument(
        "--channel",
        choices=["telegram", "discord", "slack"],
        required=True,
        help="Canal interactivo a iniciar (telegram, discord, slack)."
    )
    args = parser.parse_args()

    # Inicializar logging centralizado en consola y archivo rotativo (logs/communitylab-*.log)
    setup_logger("CommunityLab")
    entorno = get_entorno_deploy()
    print(f"[CONFIG] Entorno de despliegue activo: {entorno}")

    dispatcher = ChannelMessageDispatcher()

    if args.channel == "telegram":
        print("[START] Iniciando bot de Telegram (Long Polling)...")
        bot = CommunityLabTelegramBot(dispatcher=dispatcher)
        bot.run_polling()
    elif args.channel == "discord":
        print("[START] Iniciando bot de Discord (WebSocket Gateway)...")
        bot = CommunityLabDiscordBot(dispatcher=dispatcher)
        bot.start_bot()
    elif args.channel == "slack":
        print("[START] Iniciando bot de Slack (Socket Mode)...")
        bot = CommunityLabSlackBot(dispatcher=dispatcher)
        bot.start_socket_mode()

if __name__ == "__main__":
    main()
