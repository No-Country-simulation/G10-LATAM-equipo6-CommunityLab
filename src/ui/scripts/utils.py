"""Helpers de renderizado HTML y banners."""
import html as _html
import re

import streamlit as st

from .config import NAVY, PRIMARY
from .icons import icon_svg


def H(s: str):
    """Renderiza HTML sin que Markdown lo confunda con bloques de código."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def esc(text: str) -> str:
    return _html.escape(str(text or "")).replace("\n", "<br>")


def hashtags(text_html: str) -> str:
    return re.sub(r"(#\w+)", rf'<span style="color:{PRIMARY}; font-weight:600;">\1</span>', text_html)


def banner(p: dict, small: bool = False) -> str:
    """Pieza gráfica visual generada con estilos modernos y vectoriales."""
    title_size = "0.95rem" if small else "1.4rem"
    sub_size = "0.75rem"
    ratio = "1/1" if small else "1.9/1"
    radius = "8px" if small else "12px"
    icon_size = 28 if small else 64
    pad = "6px" if small else "16px"

    icon_name = p.get("icon_name") or "sparkles"
    svg_icon = icon_svg(icon_name, size=icon_size, color="#4F46E5", stroke_width=2.0)

    extra = ""
    if not small:
        small_spark = icon_svg("sparkles", size=12, color="#A5B4FC")
        extra = (
            f'<div style="font-size:{sub_size};margin-top:6px;opacity:.85">{esc(p.get("sub", ""))}</div>'
            f'<div style="position:absolute;right:14px;bottom:10px;font-weight:700;font-size:0.75rem;display:flex;align-items:center;gap:4px;">'
            f'{small_spark} <span>CommunityLab · Oracle & Alura</span></div>'
        )

    return f"""
    <div style="display:flex;aspect-ratio:{ratio};border-radius:{radius};overflow:hidden;background:linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);border:1px solid #C7D2FE;">
      <div style="flex:1;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.6);">{svg_icon}</div>
      <div style="flex:1.2;background:{NAVY};color:#fff;padding:{pad};display:flex;flex-direction:column;justify-content:center;position:relative">
        <div style="font-weight:800;font-size:{title_size};line-height:1.15;color:#FFFFFF;">{esc(p.get('banner', 'CommunityLab'))}</div>
        {extra}
      </div>
    </div>"""
