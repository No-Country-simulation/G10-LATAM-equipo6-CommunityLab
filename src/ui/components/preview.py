"""Vista previa de publicación con simulación para redes y canales."""
import base64

import streamlit as st

from components.editor import html_imagen
from scripts.config import MUTED
from scripts.icons import icon_svg
from scripts.state import get_copy
from scripts.utils import H, banner, esc, hashtags


def _pieza_visual(post: dict) -> str:
    """Usa la imagen generada o adjunta en el lugar del banner de colores."""
    post_id = post["id"]
    url = st.session_state.get(f"imagen_url_{post_id}")
    local = st.session_state.get(f"imagen_local_{post_id}")
    if url:
        return html_imagen(url)
    if local:
        nombre = str(st.session_state.get(f"imagen_local_nombre_{post_id}") or "")
        ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else "png"
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "gif": "image/gif"}.get(ext, "image/png")
        encoded = base64.b64encode(local).decode("ascii")
        return html_imagen(f"data:{mime};base64,{encoded}")
    return banner(post)


def render(post: dict, canales: list):
    with st.container(border=True):
        preview_icon = icon_svg("eye", size=18, color="#4F46E5", extra_style="margin-right:6px;")
        h1, h2 = st.columns([3, 1.4])
        h1.markdown(f'<div class="panel-title" style="display:flex;align-items:center;gap:6px;">{preview_icon} <span>Vista Previa</span></div>', unsafe_allow_html=True)
        h2.radio("Dispositivo", ["Escritorio", "Móvil"], horizontal=True, label_visibility="collapsed", key=f"dev_{post['id']}")

        red = st.radio(
            "Plataforma",
            ["LinkedIn", "X", "Discord", "Slack"],
            horizontal=True,
            label_visibility="collapsed",
            key=f"red_{post['id']}",
        )

        copy_txt = get_copy(post)
        caption = hashtags(esc(copy_txt))

        social_icon_name = {
            "LinkedIn": "linkedin",
            "X": "twitter",
            "Discord": "discord",
            "Slack": "slack",
        }.get(red, "share")

        svg_social = icon_svg(social_icon_name, size=15, color="#6366F1")
        spark_logo = icon_svg("activity", size=16, color="#FFFFFF")

        H(f"""
        <div class="ig" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:16px; margin:10px 0;">
          <div class="h" style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
            <div class="a" style="width:36px; height:36px; border-radius:50%; background:#4F46E5; display:flex; align-items:center; justify-content:center;">{spark_logo}</div>
            <div>
              <b style="font-size:.88rem; color:#1E293B;">CommunityLab · Oracle ONE</b><br>
              <span style="color:{MUTED};font-size:.74rem;display:flex;align-items:center;gap:4px;">Canal de salida: {svg_social} <span>{red}</span></span>
            </div>
            <span style="margin-left:auto;font-size:0.75rem;color:{MUTED};background:#F1F5F9;padding:2px 8px;border-radius:6px;">Origen: {post.get('canal_ingesta', 'Lotes')}</span>
          </div>
          {_pieza_visual(post)}
          <div class="cap" style="margin-top:12px; font-size:0.85rem; line-height:1.5; color:#334155;">{caption}</div>
        </div>""")

        is_approved = post.get("estado") == "Aprobado"
        if is_approved:
            check_svg = icon_svg("circle-check", size=18, color="#059669")
            H(f"""<div class="ready" style="display:flex;align-items:flex-start;gap:8px;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:10px;padding:12px;color:#065F46;font-size:0.84rem;">
                <div style="flex-shrink:0;margin-top:2px;">{check_svg}</div>
                <div><b>Listo para publicación</b><br>
                Esta publicación ha sido revisada y aprobada por el moderador. Puede enviarse directamente a los canales seleccionados.</div>
            </div>""")
        else:
            info_svg = icon_svg("info", size=16, color="#2563EB")
            st.info(f"Estado de moderación: **{post.get('estado', 'En revisión')}**. Puedes editar el texto y aprobarlo para habilitar el envío.")

        st.write("")
        if st.button("Publicar en Canales Oficiales", icon=":material/send:", type="primary", use_container_width=True, key=f"btn_pub_{post['id']}"):
            destinos = ", ".join(canales) if canales else red
            st.toast(f"Publicación enviada exitosamente a: {destinos}", icon=":material/check:")

        if st.button("Guardar como Borrador", icon=":material/save:", use_container_width=True, key=f"btn_draft_{post['id']}"):
            st.toast("Borrador guardado localmente.", icon=":material/save:")
