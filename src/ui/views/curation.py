"""Vistas de moderación, aprobación y banco de soluciones técnicas."""

from __future__ import annotations

import streamlit as st

from components import editor, post_list, preview
from scripts.config import BADGE, CANAL_ICON
from scripts.data_adapter import obtener_opciones_fuente
from scripts.icons import icon_svg
from scripts.services import get_visible_posts
from scripts.state import select_post
from scripts.utils import H, esc
from .common import render_page_card


def render_pending_review():
    """Vista principal de revisión humana de publicaciones generadas."""
    # Selector de Fuente / Paquete (Nube vs Local)
    opciones_fuente = obtener_opciones_fuente()
    etiquetas = [opt[0] for opt in opciones_fuente]
    idx_defecto = 0
    sel_actual = st.session_state.get("selected_package_label")
    if sel_actual in etiquetas:
        idx_defecto = etiquetas.index(sel_actual)

    col_sel, col_ref = st.columns([4, 1.2])
    with col_sel:
        fuente_elegida = st.selectbox(
            "Origen de los datos:",
            etiquetas,
            index=idx_defecto,
            key="sb_fuente_curaduria",
            help="Selecciona el paquete de mensajes almacenado en Oracle Cloud o en disco local.",
        )
        if fuente_elegida != st.session_state.get("selected_package_label"):
            st.session_state["selected_package_label"] = fuente_elegida
            st.rerun()

    with col_ref:
        st.write("")
        st.write("")
        if st.button("Actualizar", icon=":material/refresh:", use_container_width=True, help="Recarga la lista de mensajes"):
            st.rerun()

    todos = get_visible_posts()
    n_total = len(todos)
    n_aprobados = sum(1 for p in todos if p.get("estado") == "Aprobado")
    n_pendientes = sum(1 for p in todos if p.get("estado") in {"Pendiente", "En revisión"})
    n_descartados = sum(1 for p in todos if p.get("estado") == "Descartado")

    # Barra resumen de moderación
    es_oci = "OCI" in str(st.session_state.get("selected_package_label", ""))
    cloud_icon = icon_svg("cloud", size=14, color="#2563EB" if es_oci else "#64748B")
    clock_icon = icon_svg("clock", size=14, color="#D97706")
    check_icon = icon_svg("check-circle", size=14, color="#059669")
    x_icon = icon_svg("x-circle", size=14, color="#DC2626")
    board_icon = icon_svg("clipboard-check", size=22, color="#1E3A8A")

    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%); border:1px solid #DBEAFE; border-radius:14px; padding:14px 20px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:12px;">
                {board_icon}
                <div>
                    <span style="font-weight:800; font-size:1.05rem; color:#1E3A8A;">Centro de Moderación y Curaduría</span>
                    <div style="font-size:0.8rem; color:#64748B;">Revisa, edita con IA y aprueba publicaciones antes de compartirlas en redes oficiales.</div>
                </div>
            </div>
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                <span class="status-pill {'oci' if es_oci else 'standby'}" style="display:inline-flex; align-items:center; gap:5px;">{cloud_icon} Fuente: {'Nube OCI' if es_oci else 'Archivo Local'}</span>
                <span class="status-pill standby" style="display:inline-flex; align-items:center; gap:5px;">{clock_icon} {n_pendientes} Pendientes</span>
                <span class="status-pill online" style="display:inline-flex; align-items:center; gap:5px;">{check_icon} {n_aprobados} Aprobados</span>
                <span class="status-pill offline" style="display:inline-flex; align-items:center; gap:5px;">{x_icon} {n_descartados} Descartados</span>
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
            st.info("Ajusta los filtros o selecciona un paquete con datos para revisar publicaciones.")
        with col_prev:
            st.empty()
        return

    with col_edit:
        canales = editor.render(post)

    with col_prev:
        preview.render(post, canales)


def render_approved_assets():
    """Muestra el catálogo de publicaciones aprobadas y listas para distribución."""
    render_page_card(
        "Publicaciones Aprobadas y Listas para Distribuir",
        "Colección de piezas de contenido revisadas y validadas por el moderador, listas para copiar o enviar a redes.",
        "circle-check",
    )

    aprobados = [p for p in get_visible_posts() if p.get("estado") == "Aprobado"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Aprobadas", len(aprobados))
    c2.metric("Canal Principal", "LinkedIn" if aprobados else "-")
    c3.metric("Sincronización en Nube", "Sincronizado" if aprobados else "Pendiente")

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)

    if not aprobados:
        st.info("Aún no hay publicaciones con estado **Aprobado**. Dirígete a **Pendientes de Revisión** para moderar y aprobar contenidos.")
        return

    for post in aprobados:
        with st.container(border=True):
            cols = st.columns([3, 1])
            with cols[0]:
                st.markdown(f"### {post.get('title')}")
                st.caption(f"Canal de procedencia: **{post.get('canal_ingesta')}** | Autor: **{post.get('sub')}** | ID: `{post.get('id')}`")
            with cols[1]:
                if st.button("Editar de nuevo", icon=":material/edit:", key=f"edit_ap_{post['id']}", use_container_width=True):
                    select_post(post["id"])
                    st.session_state["active_view"] = "pending_review"
                    st.rerun()

            copy_txt = post.get("copy", "")
            st.text_area("Texto Aprobado", value=copy_txt, height=120, key=f"txt_ap_{post['id']}", disabled=True)

            action_cols = st.columns([1, 1, 2])
            with action_cols[0]:
                if st.button("Copiar Texto", icon=":material/content_copy:", key=f"cp_ap_{post['id']}", use_container_width=True):
                    st.toast("Texto copiado al portapapeles.", icon=":material/check:")
            with action_cols[1]:
                if st.button("Re-enviar", icon=":material/send:", key=f"repub_ap_{post['id']}", use_container_width=True):
                    st.toast(f"Publicación enviada a {post.get('canal', 'LinkedIn')}.", icon=":material/check:")


def render_faqs():
    """Catálogo y repositorio de dudas técnicas y preguntas frecuentes resueltas por IA."""
    render_page_card(
        "Preguntas Frecuentes y Banco de Soluciones Técnicas",
        "Consultas técnicas de estudiantes en Discord, Telegram y Slack, resueltas automáticamente por la Inteligencia Artificial.",
        "lightbulb",
    )

    todos = get_visible_posts()
    faqs = [p for p in todos if p.get("tipo") == "duda_tecnica"]

    # Filtro por temas
    st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#64748B; margin-bottom:8px;'>Filtrar por Tema Técnico:</div>", unsafe_allow_html=True)
    tags = ["Todos", "OCI", "Docker", "Spring", "Java", "Python", "Git"]
    tag_cols = st.columns(len(tags))
    selected_tag = st.session_state.get("active_faq_tag", "Todos")

    for i, tag in enumerate(tags):
        with tag_cols[i]:
            is_active = (selected_tag == tag)
            if st.button(
                tag,
                key=f"tag_btn_{tag}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state["active_faq_tag"] = tag
                st.rerun()

    q = st.text_input("Buscar en soluciones", placeholder="Buscar por palabra clave: spring, docker, react, oci, git...", key="q_faq")

    # Aplicar filtros combinados
    if selected_tag != "Todos":
        faqs = [f for f in faqs if selected_tag.lower() in f.get("title", "").lower() or selected_tag.lower() in f.get("copy", "").lower()]

    if q:
        faqs = [f for f in faqs if q.lower() in f.get("title", "").lower() or q.lower() in f.get("copy", "").lower()]

    st.caption(f"**{len(faqs)}** preguntas técnicas encontradas")

    if not faqs:
        st.info("No se encontraron preguntas técnicas con los filtros actuales. Prueba seleccionando 'Todos' o cambiando el término de búsqueda.")
        return

    for item in faqs:
        raw_inter = item.get("_raw", {}).get("interaccion", {})
        title_clean = item.get('title', '').replace('[DUDA_TECNICA]', '').strip()
        with st.expander(f"Consulta: {title_clean}", expanded=False):
            st.markdown(f"**Pregunta de la Comunidad ({item.get('canal_ingesta')} · {raw_inter.get('autor', 'Estudiante')}):**")
            st.info(raw_inter.get("texto", item.get("sub", "")))

            st.markdown("**Respuesta Técnica Generada por IA:**")
            st.success(item.get("copy", ""))

            c_meta1, c_meta2, c_meta3 = st.columns([2, 1, 1])
            c_meta1.caption(f"Motor: `{item.get('motor')}` | Sentimiento: `{item.get('sentimiento')}` | ID: `{item.get('id')}`")
            with c_meta2:
                if st.button("Copiar Respuesta", icon=":material/content_copy:", key=f"cp_faq_{item['id']}", use_container_width=True):
                    st.toast("Respuesta copiada al portapapeles.", icon=":material/check:")
            with c_meta3:
                if st.button("Editar en Moderación", icon=":material/edit:", key=f"faq_btn_{item['id']}", use_container_width=True):
                    select_post(item["id"])
                    st.session_state["active_view"] = "pending_review"
                    st.rerun()
