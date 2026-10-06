"""Definición centralizada del tema visual y tokens de UI."""

from __future__ import annotations

from .config import BG, INK, LINE, MUTED, NAVY, PRIMARY, PRIMARY_SOFT


def get_theme_palette(dark_mode: bool) -> dict[str, str]:
    """Devuelve el conjunto de colores para el tema activo."""
    return {
        "ink": "#F2F3FF" if dark_mode else INK,
        "muted": "#B7B9D0" if dark_mode else MUTED,
        "bg": "#101226" if dark_mode else BG,
        "line": "#353958" if dark_mode else LINE,
        "panel": "#1A1D35" if dark_mode else "#fff",
        "soft": "#242746" if dark_mode else "#FAF9FF",
        "sidebar_item": "#E6E8FF" if dark_mode else "#F4F5FF",
        "sidebar_heading": "#B9BCE8" if dark_mode else "#B9BCE8",
        "navy": NAVY,
        "primary": PRIMARY,
        "primary_soft": PRIMARY_SOFT,
    }
