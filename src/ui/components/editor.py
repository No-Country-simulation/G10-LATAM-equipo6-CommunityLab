"""Editor de contenido y aprobación para la moderación humana."""
from datetime import date, time
import streamlit as st

from scripts.config import MAX_CHARS, TODOS_LOS_CANALES
from scripts.icons import icon_svg
from scripts.utils import H, banner
from src.ui.services import guardar_curaduria_humana


def render(post: dict) -> list:
    """Dibuja el editor y devuelve los canales seleccionados."""
    with st.container(border=True):
        edit_icon = icon_svg("edit", size=18, color="#4F46E5", extra_style="margin-right:6px;")
        H(f'<div class="panel-title" style="display:flex;align-items:center;gap:6px;">{edit_icon} <span>Editor de Publicación</span></div>')

        # Interacción original recibida
        raw = post.get("_raw", {})
        interaccion = raw.get("interaccion", {})
        if interaccion.get("texto"):
            msg_icon = icon_svg("message-square", size=15, color="#64748B", extra_style="margin-right:5px;")
            with st.expander("Ver mensaje original de la comunidad", expanded=False):
                st.info(f'"{interaccion.get("texto")}"')
                st.caption(f"Autor: **{interaccion.get('autor')}** | Canal: **{interaccion.get('canal')}** | ID: `{interaccion.get('id')}`")

        c1, c2 = st.columns([3, 1.2])
        canal_dest = post.get("canal", "LinkedIn")
        share_icon = icon_svg("share", size=15, color="#6366F1", extra_style="margin-right:4px;")
        c1.markdown(f"<div style='font-size:0.88rem; font-weight:600; color:#334155; margin-top:6px; display:flex; align-items:center;'>{share_icon} Canal sugerido: <b style='margin-left:4px;'>{canal_dest}</b></div>", unsafe_allow_html=True)
        if c2.button("Restablecer", icon=":material/refresh:", key=f"reinit_{post['id']}", use_container_width=True, help="Restaura el texto generado originalmente por la IA"):
            st.rerun()

        st.markdown("<div style='font-weight:600; font-size:0.85rem; color:#475569; margin-top:8px;'>Texto generado para la publicación:</div>", unsafe_allow_html=True)
        copy_actual = st.text_area(
            "Texto de la publicación",
            value=post.get("copy", ""),
            key=f"copy_input_{post['id']}",
            height=200,
            max_chars=MAX_CHARS,
            label_visibility="collapsed",
            help="Edita el texto generado por la IA antes de aprobarlo o enviarlo a distribución.",
        )
        # Sincronizar en session_state
        st.session_state[f"copy_{post['id']}"] = copy_actual

        # Botones de Acción de Curaduría
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            if st.button("Aprobar", icon=":material/check_circle:", key=f"btn_ap_{post['id']}", type="primary", use_container_width=True, help="Aprueba el texto para que quede listo para publicar"):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="aprobado",
                )
                st.toast(f"Publicación '{post['id']}' aprobada y guardada.", icon=":material/check:")
                st.rerun()

        with b_col2:
            if st.button("Descartar", icon=":material/cancel:", key=f"btn_desc_{post['id']}", use_container_width=True, help="Descarta este mensaje si no es relevante"):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="rechazado",
                )
                st.toast(f"Publicación '{post['id']}' marcada como descartada.", icon=":material/info:")
                st.rerun()

        with b_col3:
            if st.button("Marcar Leído", icon=":material/visibility:", key=f"btn_read_{post['id']}", use_container_width=True, help="Guarda el mensaje como revisado sin publicarlo"):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="leido",
                )
                st.toast(f"Publicación '{post['id']}' marcada como leída.", icon=":material/visibility:")
                st.rerun()

        st.markdown("<hr style='margin:14px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
        st.caption("Pieza gráfica generada para acompañar la publicación:")
        H(banner(post))

        k1, k2 = st.columns(2)
        with k1:
            st.markdown("<div style='font-weight:600; font-size:0.82rem; color:#475569;'>Canales de destino</div>", unsafe_allow_html=True)
            canales = st.multiselect(
                "Canales de destino",
                TODOS_LOS_CANALES,
                default=[canal_dest] if canal_dest in TODOS_LOS_CANALES else ["LinkedIn"],
                label_visibility="collapsed",
                key=f"canales_{post['id']}",
            )
        with k2:
            st.markdown("<div style='font-weight:600; font-size:0.82rem; color:#475569;'>Programación</div>", unsafe_allow_html=True)
            date_col, time_col = st.columns(2)
            with date_col:
                st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY", label_visibility="collapsed", key=f"fecha_{post['id']}")
            with time_col:
                st.time_input("Hora", value=time(10, 0), label_visibility="collapsed", key=f"hora_{post['id']}")

        with st.expander("Opciones adicionales de publicación"):
            st.toggle("Incluir etiquetas de comunidad (#OracleONE #AluraLatam)", value=True, key=f"hash_{post['id']}")
            st.toggle("Permitir comentarios públicos", value=True, key=f"com_{post['id']}")
            st.text_input("Código de seguimiento (UTM)", value="utm_source=communitylab&utm_campaign=hackathon", key=f"utm_{post['id']}")

    return canales
