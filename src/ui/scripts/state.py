"""Manejo de st.session_state y navegación de CommunityLab."""
import streamlit as st

from .data_adapter import get_by_id_map, get_real_posts

MENU_GROUPS = [
    {
        "label": "PANEL PRINCIPAL",
        "items": [
            {"key": "dashboard", "label": "Resumen General", "icon_name": "dashboard", "material_icon": ":material/dashboard:"},
        ],
    },
    {
        "label": "CAPTURA DE MENSAJES",
        "items": [
            {"key": "live_channels", "label": "Mensajes en Vivo", "icon_name": "activity", "material_icon": ":material/sensors:"},
            {"key": "batch_processing", "label": "Procesar Archivos", "icon_name": "package", "material_icon": ":material/inventory_2:"},
        ],
    },
    {
        "label": "REVISIÓN DE CONTENIDO",
        "items": [
            {"key": "pending_review", "label": "Pendientes de Revisión", "icon_name": "clipboard-check", "material_icon": ":material/fact_check:"},
            {"key": "approved_assets", "label": "Publicaciones Aprobadas", "icon_name": "circle-check", "material_icon": ":material/task_alt:"},
            {"key": "faqs", "label": "Preguntas Frecuentes", "icon_name": "lightbulb", "material_icon": ":material/lightbulb:"},
        ],
    },
    {
        "label": "NUBE Y ALMACENAMIENTO",
        "items": [
            {"key": "cloud_explorer", "label": "Archivos en la Nube", "icon_name": "cloud", "material_icon": ":material/cloud:"},
            {"key": "par_links", "label": "Enlaces Compartidos", "icon_name": "link", "material_icon": ":material/link:"},
        ],
    },
    {
        "label": "CONEXIONES Y BOTS",
        "items": [
            {"key": "bot_status", "label": "Estado de Bots", "icon_name": "bot", "material_icon": ":material/smart_toy:"},
            {"key": "webhooks_tunnel", "label": "Rutas y Webhooks", "icon_name": "webhook", "material_icon": ":material/webhook:"},
        ],
    },
    {
        "label": "MONITOREO DEL SISTEMA",
        "items": [
            {"key": "flow_diagram", "label": "Flujo de Procesamiento", "icon_name": "git-branch", "material_icon": ":material/account_tree:"},
            {"key": "live_logs", "label": "Registro de Actividad", "icon_name": "file-text", "material_icon": ":material/description:"},
        ],
    },
    {
        "label": "ADMINISTRACIÓN",
        "items": [
            {"key": "settings", "label": "Configuración", "icon_name": "settings", "material_icon": ":material/settings:"},
        ],
    },
    {
        "label": "AYUDA",
        "items": [
            {"key": "support", "label": "Centro de Ayuda", "icon_name": "help-circle", "material_icon": ":material/help:"},
        ],
    },
]
MENU_ITEMS = [item for group in MENU_GROUPS for item in group["items"]]


def init_state():
    if "state_initialized" not in st.session_state:
        st.session_state.state_initialized = True
        st.session_state.setdefault("dark_mode", False)
        st.session_state.setdefault("active_view", "dashboard")
        posts = get_real_posts()
        first_id = posts[0]["id"] if posts else "0"
        st.session_state.setdefault("sel", first_id)
        for p in posts:
            st.session_state.setdefault(f"copy_{p['id']}", p["copy"])
    else:
        st.session_state.setdefault("dark_mode", False)
        st.session_state.setdefault("active_view", "dashboard")

    if st.session_state.active_view not in {item["key"] for item in MENU_ITEMS}:
        st.session_state.active_view = "dashboard"


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
