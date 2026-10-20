"""Vista previa de publicación con simulación para redes y canales."""
import base64

import streamlit as st

from components.editor import html_imagen
from scripts.config import CANAL_ICON, MUTED
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
        h1, h2 = st.columns([3, 1.3])
        h1.markdown('<div class="panel-title">📱 Vista Previa del Post</div>', unsafe_allow_html=True)
        h2.radio("Dispositivo", ["🖥️", "📱"], horizontal=True, label_visibility="collapsed", key=f"dev_{post['id']}")

        red = st.radio(
            "Red",
            ["LinkedIn", "X", "Discord", "Slack"],
            horizontal=True,
            label_visibility="collapsed",
            format_func=lambda x: f"{CANAL_ICON.get(x, '📢')} {x}",
            key=f"red_{post['id']}",
        )

        copy_txt = get_copy(post)
        caption = hashtags(esc(copy_txt))
        canal_icon = CANAL_ICON.get(red, "💼")

        H(f"""
        <div class="ig">
          <div class="h">
            <div class="a">🚀</div>
            <div>
              <b style="font-size:.85rem">CommunityLab · Oracle ONE</b><br>
              <span style="color:{MUTED};font-size:.72rem">Distribución · {canal_icon} {red}</span>
            </div>
            <span style="margin-left:auto;font-size:0.75rem;color:{MUTED};">Canal: {post.get('canal_ingesta', 'Lotes')}</span>
          </div>
          {_pieza_visual(post)}
          <div style="font-size:1.1rem;margin:8px 0 2px;color:#4B5563;">👍 &nbsp;💬 &nbsp;🔄 &nbsp;🚀</div>
          <div class="cap">{caption}</div>
        </div>""")

        is_approved = post.get("estado") == "Aprobado"
        if is_approved:
            H("""<div class="ready"><b>✅ Listo para publicar</b><br>
            Este activo fue aprobado por curaduría humana y está listo para ser enviado a los canales oficiales.</div>""")
        else:
            st.info(f"ℹ️ Estado actual: **{post.get('estado', 'En revisión')}**. Revisa el copy y aprueba en el editor.")

        st.write("")
        if st.button("🚀 Publicar a Redes / Canales", type="primary", use_container_width=True, key=f"btn_pub_{post['id']}"):
            destinos = ", ".join(canales) if canales else red
            st.toast(f"¡Publicación despachada a {destinos}!", icon="🚀")

        if st.button("💾 Guardar como Borrador", use_container_width=True, key=f"btn_draft_{post['id']}"):
            st.toast("Borrador actualizado localmente.", icon="💾")
