"""Elementos y tarjetas compartidas para las vistas."""

import streamlit as st

from scripts.utils import H


def render_page_card(title: str, body: str, icon: str = "✨"):
    H(f"""
    <div class="pcard" style="display:block;padding:16px 20px;margin-bottom:12px;">
      <div class="panel-title" style="margin-bottom:6px;font-size:1.15rem;">{icon} {title}</div>
      <div style="color:#6B7090;line-height:1.55;font-size:0.9rem;">{body}</div>
    </div>
    """)


def render_module_placeholder(title: str, description: str, icon: str):
    render_page_card(title, description, icon)
    st.info("Vista de demostración. Puedes configurar o conectar este módulo en la sección de Settings.")
