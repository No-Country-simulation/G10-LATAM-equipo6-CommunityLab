import streamlit as st

from scripts.state import MENU_GROUPS, get_active_view, set_active_view
from scripts.utils import H


def render():
    with st.sidebar:
        H("""
        <div class="brand">🌐<div>CommunityLab<small>Conversaciones que<br>generan conocimiento</small></div></div>
        """)

        for group_index, group in enumerate(MENU_GROUPS):
            H(f'<div class="nav-title">{group["label"]}</div>')
            with st.container(key=f"nav_group_{group_index}"):
                for item in group["items"]:
                    active = item["key"] == get_active_view()
                    if st.button(
                        f"{item['icon']} {item['label']}",
                        key=f"nav_{item['key']}",
                        type="primary" if active else "secondary",
                        use_container_width=True,
                    ):
                        set_active_view(item["key"])
                        st.rerun()

        # Tarjeta de Identidad de Equipo y Créditos Institucionales
        H("""
        <div style="margin-top:20px; padding:12px; border-radius:12px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); font-size:0.75rem; color:#A5B4FC;">
            <div style="font-weight:800; font-size:0.82rem; color:#FFFFFF; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                🏆 <span>Hackathon ONE G10 · Team 6</span>
            </div>
            <div style="color:#C7D2FE; margin-bottom:8px; font-size:0.7rem;">
                Oracle Next Education & Alura Latam
            </div>
            <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
                <a href="https://www.linkedin.com/company/hackaton-one-g10-team-6/" target="_blank" style="text-decoration:none; background:#434BB2; color:#fff !important; padding:2px 8px; border-radius:6px; font-size:0.68rem; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                    💼 LinkedIn Page
                </a>
                <span style="background:rgba(249,115,22,0.2); color:#FDBA74; padding:2px 6px; border-radius:6px; font-size:0.68rem; font-weight:600;">
                    ☁️ OCI Always Free
                </span>
            </div>
        </div>
        """)
