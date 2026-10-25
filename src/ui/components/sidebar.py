import streamlit as st

from scripts.icons import icon_svg
from scripts.state import MENU_GROUPS, get_active_view, set_active_view
from scripts.utils import H


def render():
    with st.sidebar:
        brand_icon = icon_svg("activity", size=22, color="#818CF8")
        H(f"""
        <div class="brand">
            <span style="display:inline-flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:10px; background:rgba(99,102,241,0.18); border:1px solid rgba(129,140,248,0.3);">{brand_icon}</span>
            <div>CommunityLab<small>Plataforma de Inteligencia Comunitaria</small></div>
        </div>
        """)

        for group_index, group in enumerate(MENU_GROUPS):
            H(f'<div class="nav-title">{group["label"]}</div>')
            with st.container(key=f"nav_group_{group_index}"):
                for item in group["items"]:
                    active = item["key"] == get_active_view()
                    if st.button(
                        item["label"],
                        key=f"nav_{item['key']}",
                        icon=item.get("material_icon"),
                        type="primary" if active else "secondary",
                        use_container_width=True,
                    ):
                        set_active_view(item["key"])
                        st.rerun()

        # Tarjeta de Identidad de Equipo y Créditos Institucionales
        award_icon = icon_svg("award", size=15, color="#FBBF24")
        li_icon = icon_svg("linkedin", size=13, color="#FFFFFF")
        cloud_icon = icon_svg("cloud", size=13, color="#FDBA74")
        H(f"""
        <div style="margin-top:20px; padding:12px; border-radius:12px; background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); font-size:0.75rem; color:#A5B4FC;">
            <div style="font-weight:800; font-size:0.82rem; color:#FFFFFF; margin-bottom:4px; display:flex; align-items:center; gap:6px;">
                {award_icon} <span>Hackathon ONE G10 · Equipo 6</span>
            </div>
            <div style="color:#C7D2FE; margin-bottom:8px; font-size:0.7rem;">
                Oracle Next Education & Alura Latam
            </div>
            <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
                <a href="https://www.linkedin.com/company/hackaton-one-g10-team-6/" target="_blank" style="text-decoration:none; background:#434BB2; color:#fff !important; padding:4px 8px; border-radius:6px; font-size:0.68rem; font-weight:600; display:inline-flex; align-items:center; gap:5px;">
                    {li_icon} <span>LinkedIn</span>
                </a>
                <span style="background:rgba(249,115,22,0.18); border:1px solid rgba(249,115,22,0.3); color:#FDBA74; padding:3px 7px; border-radius:6px; font-size:0.68rem; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                    {cloud_icon} <span>OCI Always Free</span>
                </span>
            </div>
        </div>
        """)
