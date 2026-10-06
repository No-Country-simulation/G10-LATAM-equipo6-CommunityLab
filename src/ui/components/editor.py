"""Editor de contenido y aprobación para la curaduría humana."""
from datetime import date, time
import streamlit as st

from scripts.config import CANAL_ICON, MAX_CHARS, TODOS_LOS_CANALES
from scripts.utils import H, banner
from src.ui.services import guardar_curaduria_humana


def render(post: dict) -> list:
    """Dibuja el editor y devuelve los canales seleccionados."""
    with st.container(border=True):
        H('<div class="panel-title">✍️ Editor y Curaduría Humana</div>')

        # Interacción original
        raw = post.get("_raw", {})
        interaccion = raw.get("interaccion", {})
        if interaccion.get("texto"):
            with st.expander("📥 Ver Interacción Original de Comunidad", expanded=False):
                st.info(f'"{interaccion.get("texto")}"')
                st.caption(f"Autor: **{interaccion.get('autor')}** | Canal: **{interaccion.get('canal')}** | ID: `{interaccion.get('id')}`")

        c1, c2 = st.columns([3, 1.2])
        canal_dest = post.get("canal", "LinkedIn")
        icon_canal = CANAL_ICON.get(canal_dest, "💼")
        c1.markdown(f"**Destino sugerido: {icon_canal} {canal_dest}**")
        if c2.button("🔄 Refrescar", key=f"reinit_{post['id']}", use_container_width=True):
            st.rerun()

        st.markdown("**Copy generado para redes / soporte:**")
        copy_actual = st.text_area(
            "Copy",
            value=post.get("copy", ""),
            key=f"copy_input_{post['id']}",
            height=200,
            max_chars=MAX_CHARS,
            label_visibility="collapsed",
        )
        # Sincronizar en session_state
        st.session_state[f"copy_{post['id']}"] = copy_actual

        # Botones de Acción de Curaduría Real
        b_col1, b_col2, b_col3 = st.columns(3)
        with b_col1:
            if st.button("✅ Aprobar", key=f"btn_ap_{post['id']}", type="primary", use_container_width=True):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="aprobado",
                )
                st.toast(f"¡Activo '{post['id']}' aprobado exitosamente en OCI!", icon="✅")
                st.rerun()

        with b_col2:
            if st.button("❌ Descartar", key=f"btn_desc_{post['id']}", use_container_width=True):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="rechazado",
                )
                st.toast(f"Activo '{post['id']}' marcado como descartado.", icon="⚠️")
                st.rerun()

        with b_col3:
            if st.button("👁️ Leído", key=f"btn_read_{post['id']}", use_container_width=True):
                guardar_curaduria_humana(
                    id_interaccion=post["id"],
                    copy_aprobado=copy_actual,
                    estado_aprobacion="leido",
                )
                st.toast(f"Activo '{post['id']}' marcado como leído.", icon="ℹ️")
                st.rerun()

        st.markdown("<hr style='margin:12px 0; border-color:#e3e6f2;' />", unsafe_allow_html=True)
        st.caption("Visual / Banner representativo del activo:")
        H(banner(post))

        k1, k2 = st.columns(2)
        with k1:
            st.markdown("**Canales de publicación**")
            canales = st.multiselect(
                "Canales",
                TODOS_LOS_CANALES,
                default=[canal_dest] if canal_dest in TODOS_LOS_CANALES else ["LinkedIn"],
                label_visibility="collapsed",
                key=f"canales_{post['id']}",
            )
        with k2:
            st.markdown("**Fecha y hora programada**")
            st.date_input("Fecha", value=date.today(), format="DD/MM/YYYY", label_visibility="collapsed", key=f"fecha_{post['id']}")
            st.time_input("Hora", value=time(10, 0), label_visibility="collapsed", key=f"hora_{post['id']}")

        with st.expander("⚙️ Opciones avanzadas de distribución"):
            st.toggle("Añadir hashtags institucionales (#OracleONE #Alura)", value=True, key=f"hash_{post['id']}")
            st.toggle("Habilitar comentarios y feedback", value=True, key=f"com_{post['id']}")
            st.text_input("Parámetros de seguimiento UTM", value="utm_source=communitylab&utm_campaign=hackathon", key=f"utm_{post['id']}")

    return canales
