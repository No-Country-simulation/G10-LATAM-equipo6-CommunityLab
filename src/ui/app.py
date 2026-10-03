"""CommunityLab · Centro de Operaciones y Curaduría Inteligente.

Arquitectura modular adaptada a la plantilla de producción Streamlit para la Hackathon.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Asegurar resolución limpia de imports tanto para la raíz como para el subdirectorio ui
_UI_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _UI_DIR.parent.parent

for _p in [str(_UI_DIR), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st

from components import header, sidebar
from scripts.state import get_active_view, init_state
from scripts.styles import inject_css
from views import render_view


def configure_app() -> None:
    """Configura la aplicación y los tokens de diseño visual."""
    st.set_page_config(
        page_title="CommunityLab · Panel de Operaciones",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    inject_css()


def main() -> None:
    """Renderiza la aplicación modular: sidebar, header y vista activa."""
    configure_app()
    sidebar.render()
    header.render()
    render_view(get_active_view())


if __name__ == "__main__":
    main()
