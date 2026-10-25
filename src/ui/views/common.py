"""Elementos y tarjetas compartidas para las vistas."""

import streamlit as st

from scripts.icons import icon_svg
from scripts.utils import H

EMOJI_TO_LUCIDE = {
    "📊": "dashboard",
    "💬": "message-square",
    "🩺": "activity",
    "🧭": "git-branch",
    "☁️": "cloud",
    "📥": "download",
    "📡": "radio",
    "😊": "smile",
    "✅": "check-circle",
    "💡": "lightbulb",
    "🟢": "circle-check",
    "✨": "sparkles",
    "🤖": "bot",
    "🔄": "refresh-cw",
    "📦": "package",
    "📁": "cloud",
    "🔗": "link",
    "🌐": "globe",
    "🗺️": "workflow",
    "📜": "file-text",
    "🔐": "settings",
    "❔": "help-circle",
    "📄": "file-text",
    "🎮": "discord",
    "✈️": "telegram",
    "💼": "briefcase",
    "🏆": "award",
}


def render_page_card(title: str, body: str, icon: str = "sparkles"):
    icon_name = EMOJI_TO_LUCIDE.get(icon, icon)
    svg = icon_svg(icon_name, size=20, color="#4F46E5", extra_style="margin-right:6px;")
    H(f"""
    <div class="pcard" style="display:block;padding:16px 20px;margin-bottom:12px;background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;">
      <div class="panel-title" style="margin-bottom:6px;font-size:1.05rem;display:flex;align-items:center;gap:6px;color:#1E293B;">
        {svg} <span>{title}</span>
      </div>
      <div style="color:#64748B;line-height:1.55;font-size:0.88rem;">{body}</div>
    </div>
    """)


def render_module_placeholder(title: str, description: str, icon: str = "sparkles"):
    render_page_card(title, description, icon)
    st.info("Vista informativa. Puedes configurar o conectar este módulo en la sección de Configuración.")
