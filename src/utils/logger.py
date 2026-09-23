"""Sistema de logging centralizado y configurable para CommunityLab.

Permite habilitar trazas detalladas de depuracion (DEBUG) tanto en consola como en
archivo rotativo diario mediante la variable de entorno ENABLE_DETAILED_LOG.
Cada dia genera estrictamente su propio archivo: logs/communitylab-YYYY-MM-DD.log.
"""

import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Asegurar carga de variables de entorno
load_dotenv()


def is_detailed_log_enabled() -> bool:
    """Verifica si el logging detallado esta habilitado en el archivo .env."""
    val = os.getenv("ENABLE_DETAILED_LOG", "false").strip().lower()
    return val in ("true", "1", "yes", "si", "on")


def get_log_file_path() -> Path:
    """Obtiene la ruta del archivo de log diario actual (ej: logs/communitylab-2026-09-22.log)."""
    configured_path = os.getenv("LOG_FILE_PATH", "logs/communitylab.log")
    date_str = datetime.now().strftime("%Y-%m-%d")
    p = Path(configured_path)
    if "{date}" in configured_path:
        return Path(configured_path.format(date=date_str))
    stem = p.stem
    stem_clean = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", stem)
    return p.parent / f"{stem_clean}-{date_str}{p.suffix}"


class DailyRotatingFileHandler(logging.FileHandler):
    """FileHandler que escribe en logs/communitylab-YYYY-MM-DD.log y rota automaticamente al cambiar de dia."""

    def __init__(self, base_path: Optional[str] = None, encoding: str = "utf-8"):
        configured = base_path or os.getenv("LOG_FILE_PATH", "logs/communitylab.log")
        self.base_path = Path(configured)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self._compute_log_file(self.current_date)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(str(log_file), encoding=encoding)

    def _compute_log_file(self, date_str: str) -> Path:
        stem = self.base_path.stem
        stem_clean = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", stem)
        return self.base_path.parent / f"{stem_clean}-{date_str}{self.base_path.suffix}"

    def emit(self, record: logging.LogRecord) -> None:
        record_date = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d")
        if record_date != self.current_date:
            self.current_date = record_date
            new_log_file = self._compute_log_file(self.current_date)
            new_log_file.parent.mkdir(parents=True, exist_ok=True)
            self.acquire()
            try:
                if self.stream:
                    self.stream.flush()
                    self.stream.close()
                self.baseFilename = str(new_log_file.resolve())
                self.stream = self._open()
            finally:
                self.release()
        super().emit(record)
        # Flush inmediato para asegurar que cada linea quede escrita en disco
        if self.stream:
            self.stream.flush()


def setup_logger(name: str = "CommunityLab") -> logging.Logger:
    """Configura y retorna una instancia de logger segun las variables de entorno.

    Si ENABLE_DETAILED_LOG=true:
        - Nivel de log: DEBUG.
        - Formato con timestamp, archivo y numero de linea.
        - Salida dual: Consola (sys.stdout) y archivo diario rotativo (logs/communitylab-YYYY-MM-DD.log).
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

    # Evitar propagacion hacia ancestros para no duplicar salidas
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

    # 2. Handler para Archivo Diario Rotativo (logs/communitylab-YYYY-MM-DD.log)
    try:
        configured_path = os.getenv("LOG_FILE_PATH", "logs/communitylab.log")
        file_handler = DailyRotatingFileHandler(base_path=configured_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning("No se pudo inicializar el archivo de log rotativo: %s", e)

    return logger


def obtener_ultimas_lineas_log(num_lineas: int = 50) -> List[str]:
    """Lee y retorna las ultimas N lineas del archivo de log diario actual.

    Args:
        num_lineas: Cantidad de lineas recientes a devolver.

    Returns:
        Lista de strings con las lineas leidas.
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
    """Vacia el contenido del archivo de log actual."""
    log_file = get_log_file_path()
    try:
        if log_file.exists():
            log_file.write_text("", encoding="utf-8")
        return True
    except Exception:
        return False
