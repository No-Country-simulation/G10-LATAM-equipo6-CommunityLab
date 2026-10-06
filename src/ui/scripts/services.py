"""Lógica de filtrado y consulta de posts para la UI modular."""

from __future__ import annotations

from .config import GRUPOS_FILTRO
from .data_adapter import get_real_posts


def get_visible_posts(
    query: str = "",
    filtro: str = "Todos",
    sentimiento: str = "Todos",
    motor: str = "Todos",
    canal: str = "Todos",
    tipo: str = "Todos",
) -> list[dict]:
    """Devuelve los posts que coinciden con búsqueda, estado y metadatos."""
    text = query.strip().lower()
    posts = get_real_posts()

    return [
        post
        for post in posts
        if (filtro == "Todos" or post["estado"] in GRUPOS_FILTRO.get(filtro, set()))
        and (not text or text in post["title"].lower() or text in post.get("copy", "").lower())
        and (sentimiento == "Todos" or post["sentimiento"] == sentimiento)
        and (motor == "Todos" or post["motor"].lower() == motor.lower())
        and (canal == "Todos" or post["canal_ingesta"].lower() == canal.lower())
        and (tipo == "Todos" or post["tipo"] == tipo)
    ]
