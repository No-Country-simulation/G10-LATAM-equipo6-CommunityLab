"""Editor de contenido y aprobación para la moderación humana."""
from datetime import date, time
import html
import streamlit as st

from scripts.config import MAX_CHARS, TODOS_LOS_CANALES
from scripts.icons import icon_svg
from scripts.utils import H, banner
from src.ui.services import generar_imagen_post, guardar_curaduria_humana, validar_url_imagen


def _temas_del_post(post: dict) -> list[str]:
    """Hashtags del activo, tolerando el formato anidado y el plano de OCI."""
    raw = post.get("_raw") or {}
    activo = raw.get("activo") or {}
    temas = activo.get("temas_clave") or raw.get("temas_clave") or []
    if isinstance(temas, str):
        temas = [t.strip() for t in temas.split(",") if t.strip()]
    return [str(t).strip() for t in temas if str(t).strip()]


def html_imagen(src: str) -> str:
    """HTML de la imagen, con el mismo marco que el banner de colores."""
    seguro = html.escape(src, quote=True)
    return (
        f'<img src="{seguro}" alt="Imagen del post" '
        f'style="width:100%;aspect-ratio:1.9/1;object-fit:cover;border-radius:12px;display:block;" />'
    )


def _mostrar_imagen(url: str) -> None:
    """Pinta la imagen por HTML. st.image abre como archivo local cualquier URL que no reconozca."""
    H(html_imagen(url))


def _render_generador_imagen(post: dict, copy_actual: str) -> None:
    """Muestra la imagen debajo del copy, con generación y adjunto local."""
    post_id = post["id"]
    clave = f"imagen_url_{post_id}"
    clave_local = f"imagen_local_{post_id}"
    clave_nombre = f"imagen_local_nombre_{post_id}"
    clave_firma = f"imagen_local_firma_{post_id}"

    c_motor, c_prompt, c_btn, c_adj = st.columns([1.1, 1.8, 1.05, 1.05], vertical_alignment="bottom")
    with c_motor:
        motor_opcion = st.selectbox(
            "Motor",
            ["🐍 Python (Gemini)", "⚡ n8n (Groq)"],
            key=f"motor_gen_img_{post_id}",
            help="Selecciona el motor para generar la imagen: Python Nativo con Gemini o Webhook síncrono n8n.",
            label_visibility="collapsed",
        )
    with c_prompt:
        instruccion = st.text_input(
            "Instrucción visual (opcional)",
            placeholder="Instrucción visual opcional. Ej: estilo 3D isométrico",
            key=f"img_prompt_{post_id}",
            label_visibility="collapsed",
            help="Ajuste de estilo visual. Si lo dejas vacío, se arma con el copy y los temas clave.",
        )
    with c_btn:
        generar = st.button(
            "Generar",
            key=f"btn_img_{post_id}",
            type="secondary",
            use_container_width=True,
            help="Generar imagen con el motor seleccionado",
        )
    with c_adj:
        adjuntar = st.button(
            "📎 Adjuntar",
            key=f"btn_adj_{post_id}",
            type="secondary",
            use_container_width=True,
            help="Adjuntar una imagen desde tu computadora",
        )

    mostrar_adjunto = f"mostrar_adjunto_{post_id}"
    if adjuntar:
        st.session_state[mostrar_adjunto] = True
    archivo = None
    if st.session_state.get(mostrar_adjunto):
        archivo = st.file_uploader(
            "Imagen desde tu computadora",
            type=["png", "jpg", "jpeg", "webp", "gif"],
            key=f"adjunto_{post_id}",
        )

    if generar:
        st.session_state.pop(clave, None)
        st.session_state.pop(clave_local, None)
        st.session_state.pop(clave_nombre, None)
        motor_sel = "python" if "Python" in motor_opcion else "n8n"
        with st.spinner(f"Generando imagen vía {motor_opcion} y guardando en OCI..."):
            try:
                resultado = generar_imagen_post(
                    id_post=post_id,
                    solucion_tecnica=copy_actual,
                    temas_clave=_temas_del_post(post),
                    instruccion_custom=instruccion,
                    motor=motor_sel,
                )
            except Exception as exc:
                st.error(str(exc))
            else:
                st.session_state[clave] = resultado["image_url"]
                st.toast(f"Imagen generada con éxito ({motor_opcion}) y guardada en OCI.", icon="🖼️")
    elif archivo is not None:
        firma = f"{archivo.name}:{archivo.size}"
        if firma != st.session_state.get(clave_firma):
            st.session_state[clave_firma] = firma
            st.session_state[clave_local] = archivo.getvalue()
            st.session_state[clave_nombre] = archivo.name
            st.session_state.pop(clave, None)
            st.toast(f"Imagen adjunta: {archivo.name}", icon="📎")

    image_url = st.session_state.get(clave)
    if not image_url:
        return
    try:
        st.session_state[clave] = validar_url_imagen(image_url)
    except Exception as exc:
        st.session_state.pop(clave, None)
        st.error(str(exc))


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

        _render_generador_imagen(post, copy_actual)

        # Botones de Acción de Curaduría Real
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

        st.markdown("<hr style='margin:12px 0; border-color:#e3e6f2;' />", unsafe_allow_html=True)
        st.caption("Visual / Banner representativo del activo:")
        imagen_local = st.session_state.get(f"imagen_local_{post['id']}")
        imagen_url = st.session_state.get(f"imagen_url_{post['id']}")
        if imagen_local:
            st.image(imagen_local, use_container_width=True)
        elif imagen_url:
            _mostrar_imagen(imagen_url)
        else:
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
