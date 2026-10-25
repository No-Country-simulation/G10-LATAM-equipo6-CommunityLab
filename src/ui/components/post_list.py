"""Lista de publicaciones con búsqueda y filtros combinables para curaduría."""
import streamlit as st

from scripts.config import BADGE, FILTROS
from scripts.services import get_visible_posts
from scripts.state import select_post
from scripts.utils import H, banner, esc


def render():
    with st.container(border=True):
        st.markdown("<div style='font-weight:700; font-size:0.95rem; margin-bottom:8px; color:#1E293B;'>Buscar y Filtrar Publicaciones</div>", unsafe_allow_html=True)
        q = st.text_input("Buscar publicación", placeholder="Buscar por autor, contenido o canal…", label_visibility="collapsed", key="q_post")
        filtro = st.radio("Filtro de estado", FILTROS, horizontal=True, label_visibility="collapsed", key="filtro_estado_radio")

        filter_row_1 = st.columns(2)
        with filter_row_1[0]:
            sentimiento = st.selectbox(
                "Sentimiento",
                ["Todos", "positivo", "neutro", "negativo"],
                format_func=lambda x: {"Todos": "Todos", "positivo": "Positivo", "neutro": "Neutro", "negativo": "Negativo"}.get(x, x),
                key="filter_sentiment",
            )
        with filter_row_1[1]:
            motor = st.selectbox(
                "Motor",
                ["Todos", "Python", "N8N"],
                format_func=lambda x: {"Todos": "Todos los motores", "Python": "Python (Gemini)", "N8N": "n8n (Flujos)"}.get(x, x),
                key="filter_engine",
            )

        filter_row_2 = st.columns(2)
        with filter_row_2[0]:
            canal = st.selectbox("Canal de origen", ["Todos", "Telegram", "Discord", "Slack", "Lotes"], key="filter_channel")
        with filter_row_2[1]:
            tipo = st.selectbox(
                "Tipo de contenido",
                ["Todos", "logro_contratacion", "duda_tecnica", "showcase", "feedback_general"],
                format_func=lambda x: {
                    "Todos": "Todos los tipos",
                    "logro_contratacion": "Logro / Empleo",
                    "duda_tecnica": "Duda Técnica",
                    "showcase": "Proyecto Destacado",
                    "feedback_general": "Opinión General",
                }.get(x, x),
                key="filter_type",
            )

        visibles = get_visible_posts(q, filtro, sentimiento, motor, canal, tipo)
        st.caption(f"**{len(visibles)}** publicaciones encontradas")
        if not visibles:
            st.info("No se encontraron publicaciones con estos criterios. Intenta modificar los filtros o el texto de búsqueda.")

        selected_id = st.session_state.get("sel")
        if visibles and not any(post["id"] == selected_id for post in visibles):
            select_post(visibles[0]["id"])

        for p in visibles:
            sel = p["id"] == st.session_state.get("sel")
            bg, fg = BADGE.get(p["estado"], ("#F3F4F6", "#4B5563"))
            H(f"""
            <div class="pcard {'sel' if sel else ''}" key="{p['id']}" style="margin-bottom:8px;">
              <div style="width:72px;flex:none">{banner(p, small=True)}</div>
              <div class="meta" style="flex:1;min-width:0;">
                <div class="t" style="font-weight:700;font-size:0.86rem;line-height:1.2;margin-bottom:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{esc(p['title'])}</div>
                <div class="c" style="font-size:0.75rem;color:#64748B;margin-bottom:4px;">{p.get('canal_ingesta', 'Canal')} · {p.get('fecha', '')}</div>
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                    <span class="badge" style="background:{bg};color:{fg};padding:2px 8px;border-radius:10px;font-size:0.7rem;font-weight:600;">{p['estado']}</span>
                    <span class="ago" style="font-size:0.7rem;color:#94A3B8;">{p.get('hace', '')}</span>
                </div>
              </div>
            </div>""")
            st.button(
                "Editando ahora" if sel else "Editar publicación",
                icon=":material/edit_note:" if sel else ":material/arrow_forward:",
                key=f"pick_{p['id']}",
                on_click=select_post,
                args=(p["id"],),
                type="primary" if sel else "secondary",
                use_container_width=True,
            )

        return next((post for post in visibles if post["id"] == st.session_state.get("sel")), None)
