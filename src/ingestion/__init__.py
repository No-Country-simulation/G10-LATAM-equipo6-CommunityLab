"""Módulo de ingestión y normalización de datos para CommunityLab."""

from .data_loader import (
    cargar_interacciones_desde_json,
    filtrar_por_canal,
    filtrar_por_tipo,
    generar_lotes,
    obtener_canales_unicos,
    obtener_tipos_unicos,
)

__all__ = [
    "cargar_interacciones_desde_json",
    "filtrar_por_canal",
    "filtrar_por_tipo",
    "generar_lotes",
    "obtener_canales_unicos",
    "obtener_tipos_unicos",
]
