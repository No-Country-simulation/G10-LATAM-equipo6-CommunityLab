"""Sistema de logging centralizado y configurable para CommunityLab.

Permite habilitar trazas detalladas de depuración (DEBUG) tanto en consola como en
archivo rotativo mediante la variable de entorno ENABLE_DETAILED_LOG.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Optional

from datetime import datetime
from dotenv import load_dotenv

# Asegurar carga de variables de entorno
load_dotenv()


def is_detailed_log_enabled() -> bool:
    """Verifica si el logging detallado está habilitado en el archivo .env."""
    val = os.getenv("ENABLE_DETAILED_LOG", "false").strip().lower()
    return val in ("true", "1", "yes", "si", "on")


def get_log_file_path() -> Path:
    """Obtiene la ruta del archivo de log diario (ej: logs/communitylab-2026-09-20.log)."""
    configured_path = os.getenv("LOG_FILE_PATH", "logs/communitylab.log")
    date_str = datetime.now().strftime("%Y-%m-%d")
    p = Path(configured_path)
    if "{date}" in configured_path:
        return Path(configured_path.format(date=date_str))
    stem = p.stem.replace(f"-{date_str}", "")
    return p.parent / f"{stem}-{date_str}{p.suffix}"


def setup_logger(name: str = "CommunityLab") -> logging.Logger:
    """Configura y retorna una instancia de logger según las variables de entorno.

    Si ENABLE_DETAILED_LOG=true:
        - Nivel de log: DEBUG.
        - Formato con timestamp, archivo y número de línea.
        - Salida dual: Consola (sys.stdout) y archivo rotativo (logs/communitylab.log).
    Si ENABLE_DETAILED_LOG=false:
        - Nivel de log: INFO.
        - Salida en consola y archivo a nivel INFO.

    Args:
        name: Nombre identificador del logger.

    Returns:
        logging.Logger configurado.
    """
    logger = logging.getLogger(name)

    # Si ya tiene handlers configurados, retornar para evitar duplicados
    if logger.handlers:
        return logger

    detailed = is_detailed_log_enabled()
    level = logging.DEBUG if detailed else logging.INFO
    logger.setLevel(level)

    # Evitar propagación al root logger para no duplicar líneas
    logger.propagate = False

    # Formatos de logging
    if detailed:
        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formato = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # 1. Handler para Consola (stdout) con soporte UTF-8 en Windows
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formato)
    logger.addHandler(console_handler)

    # 2. Handler para Archivo Rotativo
    try:
        log_file = get_log_file_path()
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Archivo rotativo de máximo 5 MB, con hasta 3 backups
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("No se pudo inicializar el archivo de log en '%s': %s", log_file, e)

    return logger


def obtener_ultimas_lineas_log(num_lineas: int = 50) -> List[str]:
    """Lee y retorna las últimas N líneas del archivo de log.

    Args:
        num_lineas: Cantidad de líneas recientes a devolver.

    Returns:
        Lista de strings con las líneas leídas.
    """
    log_file = get_log_file_path()
    if not log_file.exists():
        return [f"Archivo de log no encontrado en: {log_file}"]

    try:
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            return lines[-num_lineas:] if len(lines) > num_lineas else lines
    except Exception as e:
        return [f"Error al leer archivo de log: {e}"]


def limpiar_archivo_log() -> bool:
    """Vacía el contenido del archivo de log actual."""
    log_file = get_log_file_path()
    try:
        if log_file.exists():
            log_file.write_text("", encoding="utf-8")
        return True
    except Exception:
        return False
