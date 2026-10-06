"""Manejo de st.session_state y navegación de CommunityLab."""
import streamlit as st

from .data_adapter import get_by_id_map, get_real_posts

MENU_GROUPS = [
    {
        "label": "INICIO",
        "items": [
            {"key": "dashboard", "label": "Dashboard de la comunidad", "icon": "📊"},
        ],
    },
    {
        "label": "🚀 INGESTA & FUENTES",
        "items": [
            {"key": "live_channels", "label": "Fuentes activas", "icon": "📡"},
            {"key": "batch_processing", "label": "Procesamiento por lotes", "icon": "📦"},
        ],
    },
    {
        "label": "💼 CURADURÍA DE CONTENIDO",
        "items": [
            {"key": "pending_review", "label": "Pendientes de revisión", "icon": "📋"},
            {"key": "approved_assets", "label": "Historias y aprobados", "icon": "🟢"},
            {"key": "faqs", "label": "FAQ & dudas técnicas", "icon": "💡"},
        ],
    },
    {
        "label": "☁️ OCI & ACTIVO DIGITAL",
        "items": [
            {"key": "cloud_explorer", "label": "Almacenamiento OCI", "icon": "📁"},
            {"key": "par_links", "label": "Activos generados", "icon": "🔗"},
        ],
    },
    {
        "label": "⚙️ CONEXIONES & CANALES",
        "items": [
            {"key": "bot_status", "label": "Estado de automatizaciones", "icon": "🤖"},
            {"key": "webhooks_tunnel", "label": "Webhooks & distribución", "icon": "🌐"},
        ],
    },
    {
        "label": "📖 OBSERVABILIDAD",
        "items": [
            {"key": "flow_diagram", "label": "Flujo del pipeline", "icon": "🗺️"},
            {"key": "live_logs", "label": "Logs y eventos", "icon": "📜"},
        ],
    },
    {
        "label": "⚙️ CONFIGURACIÓN",
        "items": [
            {"key": "settings", "label": "Settings / Configuración", "icon": "🔐"},
        ],
    },
    {
        "label": "AYUDA",
        "items": [
            {"key": "support", "label": "Soporte", "icon": "❔"},
        ],
    },
]
MENU_ITEMS = [item for group in MENU_GROUPS for item in group["items"]]


def init_state():
    posts = get_real_posts()
    first_id = posts[0]["id"] if posts else "0"

    st.session_state.setdefault("sel", first_id)
    st.session_state.setdefault("dark_mode", False)
    st.session_state.setdefault("active_view", "dashboard")

    if st.session_state.active_view not in {item["key"] for item in MENU_ITEMS}:
        st.session_state.active_view = "dashboard"

    for p in posts:
        st.session_state.setdefault(f"copy_{p['id']}", p["copy"])


def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode


VIEW_ALIASES = {
    "fuentes-activas": "live_channels",
    "pendientes-revision": "pending_review",
    "almacenamiento-oci": "cloud_explorer",
    "estado-automatizaciones": "bot_status",
    "flujo-pipeline": "flow_diagram",
    "configuracion": "settings",
}


def set_active_view(view: str):
    canonical = VIEW_ALIASES.get(view, view)
    valid = {item["key"] for item in MENU_ITEMS}
    if canonical in valid:
        st.session_state.active_view = canonical
    elif view in valid:
        st.session_state.active_view = view


def get_active_view() -> str:
    return st.session_state.get("active_view", "dashboard")


def select_post(pid: str):
    st.session_state.sel = pid


def get_selected() -> dict:
    by_id = get_by_id_map()
    sel_id = st.session_state.get("sel")
    if sel_id in by_id:
        return by_id[sel_id]
    posts = get_real_posts()
    return posts[0] if posts else {}


def get_copy(post: dict) -> str:
    key = f"copy_{post['id']}"
    if key in st.session_state:
        return st.session_state[key]
    return post.get("copy", "")
