"""Lista de posts con búsqueda y filtros combinables para curaduría."""
import streamlit as st

from scripts.config import BADGE, FILTROS
from scripts.services import get_visible_posts
from scripts.state import select_post
from scripts.utils import H, banner, esc


def render():
    with st.container(border=True):
        q = st.text_input("Buscar post", placeholder="Buscar en interacciones o copies…", label_visibility="collapsed", key="q_post")
        filtro = st.radio("Filtro", FILTROS, horizontal=True, label_visibility="collapsed", key="filtro_estado_radio")

        filter_row_1 = st.columns(2)
        with filter_row_1[0]:
            sentimiento = st.selectbox("Sentimiento", ["Todos", "positivo", "negativo", "neutro"], key="filter_sentiment")
        with filter_row_1[1]:
            motor = st.selectbox("Motor", ["Todos", "Python", "N8N"], key="filter_engine")

        filter_row_2 = st.columns(2)
        with filter_row_2[0]:
            canal = st.selectbox("Canal de origen", ["Todos", "Telegram", "Discord", "Slack", "Lotes"], key="filter_channel")
        with filter_row_2[1]:
            tipo = st.selectbox(
                "Tipo",
                ["Todos", "logro_contratacion", "duda_tecnica", "showcase", "feedback_general"],
                key="filter_type",
            )

        visibles = get_visible_posts(q, filtro, sentimiento, motor, canal, tipo)
        st.caption(f"**{len(visibles)}** activos encontrados")
        if not visibles:
            st.info("No hay activos con ese filtro. Prueba cambiando el filtro o la búsqueda.")

        selected_id = st.session_state.get("sel")
        if visibles and not any(post["id"] == selected_id for post in visibles):
            select_post(visibles[0]["id"])

        for p in visibles:
            sel = p["id"] == st.session_state.get("sel")
            bg, fg = BADGE.get(p["estado"], ("#F3F4F6", "#4B5563"))
            H(f"""
            <div class="pcard {'sel' if sel else ''}">
              <div style="width:72px;flex:none">{banner(p, small=True)}</div>
              <div class="meta">
                <div class="t">{esc(p['title'])}</div>
                <div class="c">{p.get('canal_ingesta', 'Canal')} · {p.get('fecha', '')}</div>
                <span class="badge" style="background:{bg};color:{fg}">{p['estado']}</span>
                <span class="ago">{p.get('hace', '')}</span>
              </div>
            </div>""")
            st.button(
                "👉 Editando" if sel else "Editar activo",
                key=f"pick_{p['id']}",
                on_click=select_post,
                args=(p["id"],),
                type="primary" if sel else "secondary",
                use_container_width=True,
            )

        return next((post for post in visibles if post["id"] == st.session_state.get("sel")), None)
