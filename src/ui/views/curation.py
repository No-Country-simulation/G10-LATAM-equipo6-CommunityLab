"""Vistas de revisión, aprobación y publicación de activos de CommunityLab."""

from __future__ import annotations

import streamlit as st

from components import editor, post_list, preview
from scripts.config import BADGE, CANAL_ICON
from scripts.services import get_visible_posts
from scripts.state import select_post
from scripts.utils import H, esc
from .common import render_page_card


def render_pending_review():
    """Vista tri-panel de revisión humana de activos generados."""
    todos = get_visible_posts()
    n_total = len(todos)
    n_aprobados = sum(1 for p in todos if p.get("estado") == "Aprobado")
    n_pendientes = sum(1 for p in todos if p.get("estado") in {"Pendiente", "En revisión"})
    n_descartados = sum(1 for p in todos if p.get("estado") == "Descartado")

    # Barra resumen de curaduría
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#F8FAFC,#EFF6FF); border:1px solid #DBEAFE; border-radius:14px; padding:12px 18px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="font-size:1.4rem;">📋</span>
                <div>
                    <span style="font-weight:800; font-size:1.05rem; color:#1E3A8A;">Centro de Curaduría Humana Tri-Panel</span>
                    <div style="font-size:0.8rem; color:#64748B;">Revisa, ajusta con IA y aprueba copys para persistencia y distribución oficial.</div>
                </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <span class="status-pill standby">⏳ {n_pendientes} Pendientes</span>
                <span class="status-pill online">✅ {n_aprobados} Aprobados</span>
                <span class="status-pill offline">❌ {n_descartados} Descartados</span>
                <span class="status-pill oci">☁️ OCI Sync</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_list, col_edit, col_prev = st.columns([1.05, 1.25, 1.05], gap="medium")

    with col_list:
        post = post_list.render()

    if post is None:
        with col_edit:
            st.info("Ajusta los filtros o selecciona un paquete con datos para revisar activos.")
        with col_prev:
            st.empty()
        return

    with col_edit:
        canales = editor.render(post)

    with col_prev:
        preview.render(post, canales)


def render_approved_assets():
    """Muestra el catálogo de activos aprobados por curaduría humana y listos para distribución."""
    render_page_card(
        "Activos Aprobados y Listos para Distribución",
        "Colección de copys y piezas curadas y validadas por el equipo de moderación. Listas para copiar o publicar.",
        "🟢",
    )

    aprobados = [p for p in get_visible_posts() if p.get("estado") == "Aprobado"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Aprobados", len(aprobados))
    c2.metric("Canal Principal", "LinkedIn" if aprobados else "-")
    c3.metric("OCI Status", "Sincronizado" if aprobados else "Pendiente")

    st.markdown("---")

    if not aprobados:
        st.info("Aún no hay activos con estado **Aprobado**. Dirígete a **Revisión Pendiente** para curar y aprobar contenidos.")
        return

    for post in aprobados:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                icon = CANAL_ICON.get(post.get("canal", "LinkedIn"), "📢")
                st.markdown(f"### {icon} {post.get('title')}")
                st.caption(f"Canal Ingesta: **{post.get('canal_ingesta')}** | Autor: **{post.get('sub')}** | ID: `{post.get('id')}`")
            with cols[1]:
                if st.button("✏️ Editar", key=f"edit_ap_{post['id']}", use_container_width=True):
                    select_post(post["id"])
                    st.session_state["nav_section"] = "curation"
                    st.session_state["nav_view"] = "pending_review"
                    st.rerun()

            copy_txt = post.get("copy", "")
            st.text_area("Copy Final Validado", value=copy_txt, height=120, key=f"txt_ap_{post['id']}", disabled=True)

            action_cols = st.columns([1, 1, 2])
            with action_cols[0]:
                if st.button("📋 Copiar Copy", key=f"cp_ap_{post['id']}", use_container_width=True):
                    st.toast("Copy copiado al portapapeles (simulado)", icon="📋")
            with action_cols[1]:
                if st.button("🚀 Re-publicar", key=f"repub_ap_{post['id']}", use_container_width=True):
                    st.toast(f"Publicación re-despachada a {post.get('canal', 'LinkedIn')}", icon="🚀")


def render_faqs():
    """Catálogo y repositorio de dudas técnicas y FAQs resueltas por IA y comunidad."""
    render_page_card(
        "FAQs & Base de Conocimiento Técnico (Knowledge Base)",
        "Dudas y consultas técnicas detectadas en Discord, Telegram y Slack, enriquecidas con soluciones de Gemini 2.5 Flash y Groq.",
        "💡",
    )

    todos = get_visible_posts()
    faqs = [p for p in todos if p.get("tipo") == "duda_tecnica"]

    # Tag Cloud de Tecnologías
    st.markdown("<div style='font-size:0.8rem; font-weight:700; color:#64748B; margin-bottom:6px;'>Filtro Rápido por Temáticas (#TagCloud):</div>", unsafe_allow_html=True)
    tags = ["Todos", "OCI", "Docker", "Spring", "Java", "Python", "Git"]
    tag_cols = st.columns(len(tags))
    selected_tag = st.session_state.get("active_faq_tag", "Todos")

    for i, tag in enumerate(tags):
        with tag_cols[i]:
            is_active = (selected_tag == tag)
            if st.button(
                f"#{tag}",
                key=f"tag_btn_{tag}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["active_faq_tag"] = tag
                st.rerun()

    q = st.text_input("🔍 Buscar en preguntas y respuestas técnicas", placeholder="ej. spring, docker, react, oci, git...", key="q_faq")

    # Aplicar filtros combinados
    if selected_tag != "Todos":
        faqs = [f for f in faqs if selected_tag.lower() in f.get("title", "").lower() or selected_tag.lower() in f.get("copy", "").lower()]

    if q:
        faqs = [f for f in faqs if q.lower() in f.get("title", "").lower() or q.lower() in f.get("copy", "").lower()]

    st.caption(f"**{len(faqs)}** preguntas técnicas indexadas bajo el filtro actual")

    if not faqs:
        st.info("No se encontraron preguntas técnicas con los filtros actuales. Prueba seleccionando '#Todos' o cambiando el término de búsqueda.")
        return

    for item in faqs:
        raw_inter = item.get("_raw", {}).get("interaccion", {})
        with st.expander(f"💡 {item.get('title')}", expanded=False):
            st.markdown(f"**Pregunta de la Comunidad ({item.get('canal_ingesta')} · {raw_inter.get('autor', 'Estudiante')}):**")
            st.info(raw_inter.get("texto", item.get("sub", "")))

            st.markdown("**Respuesta Técnica Generada / Solución Curada:**")
            st.success(item.get("copy", ""))

            c_meta1, c_meta2, c_meta3 = st.columns([2, 1, 1])
            c_meta1.caption(f"Motor: `{item.get('motor')}` | Sentimiento: `{item.get('sentimiento')}` | ID: `{item.get('id')}`")
            with c_meta2:
                if st.button("📋 Copiar Solución", key=f"cp_faq_{item['id']}", use_container_width=True):
                    st.toast("Solución copiada al portapapeles.", icon="📋")
            with c_meta3:
                if st.button("Editar en Curaduría", key=f"faq_btn_{item['id']}", use_container_width=True):
                    select_post(item["id"])
                    st.session_state["active_view"] = "pending_review"
                    st.rerun()
