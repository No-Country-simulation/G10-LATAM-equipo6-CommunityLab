"""Helpers de renderizado HTML y banners."""
import html as _html
import re

import streamlit as st

from .config import NAVY, PRIMARY


def H(s: str):
    """Renderiza HTML sin que Markdown lo confunda con bloques de código."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def esc(text: str) -> str:
    return _html.escape(str(text or "")).replace("\n", "<br>")


def hashtags(text_html: str) -> str:
    return re.sub(r"(#\w+)", rf'<span style="color:{PRIMARY}">\1</span>', text_html)


def banner(p: dict, small: bool = False) -> str:
    """Pieza gráfica generada con CSS."""
    title_size = "0.95rem" if small else "1.5rem"
    sub_size = "0.75rem"
    ratio = "1/1" if small else "1.9/1"
    radius = "8px" if small else "12px"
    emoji_size = "1.5rem" if small else "3.8rem"
    pad = "6px" if small else "16px"

    extra = ""
    if not small:
        extra = (
            f'<div style="font-size:{sub_size};margin-top:6px;opacity:.85">{esc(p.get("sub", ""))}</div>'
            '<div style="position:absolute;right:14px;bottom:10px;font-weight:700;font-size:0.75rem">🚀 CommunityLab · Oracle & Alura</div>'
        )

    return f"""
    <div style="display:flex;aspect-ratio:{ratio};border-radius:{radius};overflow:hidden;background:#DCE6F5">
      <div style="flex:1;display:flex;align-items:center;justify-content:center;font-size:{emoji_size}">{p.get('emoji', '🚀')}</div>
      <div style="flex:1.2;background:{NAVY};color:#fff;padding:{pad};display:flex;flex-direction:column;justify-content:center;position:relative">
        <div style="font-weight:800;font-size:{title_size};line-height:1.15">{esc(p.get('banner', 'CommunityLab'))}</div>
        {extra}
      </div>
    </div>"""
