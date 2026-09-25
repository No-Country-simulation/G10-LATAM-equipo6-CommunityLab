"""CommunityLab — Panel de Curaduría y Orquestación en Streamlit.

Permite al equipo de Marketing y Community Managers de Oracle ONE / Alura
inspeccionar los activos generados, editar copys, aprobar publicaciones
y disparar ejecuciones del pipeline en tiempo real.
"""

from pathlib import Path
import sys

# Asegurar que la raíz del proyecto esté en sys.path al ejecutar desde cualquier lugar con Streamlit
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import os
from pathlib import Path
import sys
import time
import streamlit as st

from src.ui.services import (
    obtener_ultimos_paquetes,
    cargar_paquete,
    procesar_archivo_ui,
    procesar_archivo_n8n_ui,
    guardar_curaduria_humana,
    obtener_mapa_curaduria,
    fusionar_paquetes,
    vaciar_historico_oci,
    vaciar_historico_oci_local,
    obtener_ids_procesados_sesion,
)
from src.utils.logger import obtener_ultimas_lineas_log, limpiar_archivo_log
from src.utils.config import get_n8n_webhook_url
from src.channels.bot_manager import get_bot_manager
from src.ui.styles import get_novaedu_css

# Configuración de la página
st.set_page_config(
    page_title="CommunityLab — Posts con IA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectar estilos CSS oficiales de NovaEdu
st.markdown(get_novaedu_css(), unsafe_allow_html=True)

# Definición de Vistas Oficiales con nombres NovaEdu
VISTA_CURADURIA = "✨ Posts con IA"
VISTA_PIPELINE = "⚡ Orquestador Dual"
VISTA_HISTORICO = "☁️ Histórico OCI"

# Sidebar con identidad visual de NovaEdu
st.sidebar.markdown(
    """
    <div class="sidebar-brand-header">
        <div class="sidebar-brand-icon">🎓</div>
        <div>
            <div class="sidebar-brand-title">CommunityLab</div>
            <div class="sidebar-brand-subtitle">Oracle ONE & Alura LATAM</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

modo = st.sidebar.radio(
    "Menú Principal",
    [VISTA_CURADURIA, VISTA_PIPELINE, VISTA_HISTORICO],
    label_visibility="collapsed",
)

# TopBar estilo NovaEdu (Header global de la app)
st.markdown(
    """
    <div class="topbar-container">
        <div class="topbar-left">
            <span style="font-size: 20px; font-weight: 800; color: #1A1F36;">CommunityLab</span>
            <span style="color: #94A3B8;">|</span>
            <span style="font-size: 13px; color: #4F566B; font-weight: 600;">Hackathon Oracle Next Education</span>
        </div>
        <div style="display: flex; align-items: center; gap: 14px;">
            <div class="topbar-badge-oci">
                <span class="topbar-pulse"></span>
                <span>OCI Storage Online</span>
            </div>
            <div style="font-size: 13px; font-weight: 700; color: #1A1F36;">
                César Cely &nbsp;<span style="color: #635BFF; font-size: 11px;">(PM & Cloud Lead)</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Canales en Vivo")

bot_manager = get_bot_manager()
status_bots = bot_manager.get_status()
any_running = bot_manager.is_running()

col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("▶️ Iniciar", use_container_width=True, disabled=any_running, help="Inicia la escucha en segundo plano de Telegram, Discord y Slack"):
        bot_manager.start_all()
        st.toast("Bots iniciados en segundo plano.", icon="🚀")
        time.sleep(1)
        st.rerun()

with col_b2:
    if st.button("⏹️ Detener", use_container_width=True, disabled=not any_running, help="Detiene los 3 bots"):
        bot_manager.stop_all()
        st.toast("Bots detenidos.", icon="🛑")
        time.sleep(1)
        st.rerun()

# Estado detallado de cada bot
for k, data in status_bots.items():
    is_on = data["running"]
    color_icon = "🟢" if is_on else "🔴"
    estado_txt = "**En línea**" if is_on else "*Inactivo*"
    st.sidebar.markdown(f"{color_icon} **{data['label']}**: {estado_txt}")
    if data.get("error"):
        st.sidebar.caption(f"⚠️ {data['error']}")
    else:
        st.sidebar.caption(f"ℹ️ {data['info']}")

if any_running:
    st.sidebar.success("📡 Escuchando mensajes en vivo...")

st.sidebar.markdown("---")
st.sidebar.info(
    "**Rol Activo:** Backend & Pipeline \n\n"
    "**Célula 1 & 3:** IA, Pipeline y Curaduría Streamlit."
)

# -----------------------------------------------------------------------------
# VISTA 1: CURADURÍA DE ACTIVOS
# -----------------------------------------------------------------------------
def detectar_canal_digital(item: dict) -> tuple[str, str]:
    """Detecta el canal digital de procedencia del activo (Telegram, Discord, Slack o Dataset Batch).

    Retorna una tupla: (nombre_clave, badge_formateado_con_emoji)
    """
    bot_chan = (item.get("canal_origen_bot") or "").lower()
    inter_chan = (item.get("interaccion", {}).get("canal") or "").lower()
    inter_id = str(item.get("interaccion", {}).get("id") or "").lower()
    tipo_inter = (item.get("interaccion", {}).get("tipo") or "").lower()
    meta_ext = item.get("metadata_externa") or {}
    meta_str = str(meta_ext).lower()

    canal_comb = f"{bot_chan} {inter_chan} {inter_id} {tipo_inter} {meta_str}"

    if "telegram" in canal_comb or inter_id.startswith("tg_") or "chat_id" in meta_str:
        return "Telegram", "✈️ Telegram"
    elif "discord" in canal_comb or inter_id.startswith("dc_") or inter_id.startswith("disc_"):
        return "Discord", "🎮 Discord"
    elif "slack" in canal_comb or inter_id.startswith("slk_") or inter_id.startswith("slack_") or "c0c" in canal_comb:
        return "Slack", "💬 Slack"
    else:
        return "Dataset Batch", "📊 Dataset Batch"


if "Curaduría" in modo or modo == VISTA_CURADURIA:
    st.subheader("📋 Revisión y Aprobación de Copys para Publicación")

    opciones_fuente = []

    # 1. Canales Dinamicos Interactivos (Telegram, Discord, Slack)
    f_canales_py = Path("data/paquete_procesado_canales_python.json")
    if f_canales_py.exists():
        try:
            with open(f_canales_py, "r", encoding="utf-8") as f:
                c_py = json.load(f)
                n_act = len(c_py.get("activos", []))
                opciones_fuente.append(f"Canales (Python): {f_canales_py.as_posix()} ({n_act} activos)")
        except Exception:
            opciones_fuente.append(f"Canales (Python): {f_canales_py.as_posix()}")

    f_canales_n8n = Path("data/paquete_procesado_canales_n8n.json")
    if f_canales_n8n.exists():
        try:
            with open(f_canales_n8n, "r", encoding="utf-8") as f:
                c_n8n = json.load(f)
                n_act = len(c_n8n.get("activos", []))
                opciones_fuente.append(f"Canales (n8n): {f_canales_n8n.as_posix()} ({n_act} activos)")
        except Exception:
            opciones_fuente.append(f"Canales (n8n): {f_canales_n8n.as_posix()}")

    # 2. Lotes en OCI Object Storage (Pipeline Batch E2E)
    paquetes_disponibles = obtener_ultimos_paquetes(limite=30)
    for p in paquetes_disponibles:
        opciones_fuente.append(f"Storage: {p['name']}")

    # 3. Lotes Locales Batch
    for local_f in [Path("data/paquete_procesado_python.json"), Path("data/paquete_procesado_n8n.json"), Path("data/paquete_procesado.json")]:
        if local_f.exists():
            entry = f"Local: {local_f.as_posix()}"
            if entry not in opciones_fuente:
                opciones_fuente.append(entry)

    if not opciones_fuente:
        st.warning(
            "⚠️ Aun no se han generado paquetes de activos. "
            "Ejecuta interacciones en Telegram/Discord/Slack o ve a la pestaña **'🚀 Ejecutar Pipeline'** para procesar interacciones."
        )
    else:
        c_sel1, c_sel2, c_sel3 = st.columns([2.5, 0.8, 1.2])
        with c_sel1:
            fuente_seleccionada = st.selectbox("Selecciona la fuente o lote de activos a inspeccionar:", opciones_fuente)
        with c_sel2:
            st.write("")
            st.write("")
            if st.button("🔄 Refrescar", use_container_width=True, help="Recarga las interacciones más recientes"):
                st.rerun()

        # Cargar datos del paquete
        datos_paquete = None
        if fuente_seleccionada.startswith("Local:") or fuente_seleccionada.startswith("Canales ("):
            partes = fuente_seleccionada.split(":")
            ruta_str = partes[1].strip().split(" ")[0]
            local_p = Path(ruta_str)
            if local_p.exists():
                with open(local_p, "r", encoding="utf-8") as f:
                    datos_paquete = json.load(f)
        else:
            nombre_obj = fuente_seleccionada.replace("Storage: ", "")
            raw_datos = cargar_paquete(nombre_obj)
            if raw_datos:
                # Normalizar si viene del formato especializado de OCI
                if "activos" in raw_datos and raw_datos["activos"] and "activo" not in raw_datos["activos"][0]:
                    norm_activos = []
                    for act in raw_datos["activos"]:
                        tipo_c = act.get("tipo_contenido") or raw_datos.get("metadata", {}).get("categoria", "feedback_general")
                        sent_c = act.get("sentimiento", "positivo" if "logro" in tipo_c or "showcase" in tipo_c else "neutro")
                        norm_activos.append({
                            "interaccion": {
                                "id": act.get("id", "N/A"),
                                "autor": act.get("autor", "Anónimo"),
                                "canal": act.get("canal", "#general"),
                                "texto": act.get("comentario") or act.get("pregunta_original") or act.get("post_linkedin") or "",
                            },
                            "activo": {
                                "tipo_contenido": tipo_c,
                                "sentimiento": sent_c,
                                "temas_clave": act.get("temas_clave", []),
                                "post_linkedin": act.get("post_linkedin"),
                                "tip_tecnico_faq": act.get("tip_tecnico_faq"),
                            },
                            "motor_orquestacion": "n8n_oci_storage",
                        })
                    datos_paquete = {
                        "metadata_paquete": {
                            "total_procesados_exitosamente": len(norm_activos),
                            "motor_orquestacion": "OCI Object Storage (n8n)",
                        },
                        "metricas": {
                            "distribucion_sentimiento": {
                                "positivo": sum(1 for a in norm_activos if a["activo"]["sentimiento"] == "positivo"),
                                "neutro": sum(1 for a in norm_activos if a["activo"]["sentimiento"] == "neutro"),
                                "negativo": sum(1 for a in norm_activos if a["activo"]["sentimiento"] == "negativo"),
                            },
                            "total_posts_linkedin_generados": sum(1 for a in norm_activos if a["activo"].get("post_linkedin")),
                            "total_tips_faq_generados": sum(1 for a in norm_activos if a["activo"].get("tip_tecnico_faq")),
                        },
                        "activos": norm_activos,
                    }
                else:
                    datos_paquete = raw_datos

        if datos_paquete and "activos" in datos_paquete:
            if fuente_seleccionada.startswith("Canales ("):
                with c_sel3:
                    st.write("")
                    st.write("")
                    if st.button("☁️ Subir a Storage", use_container_width=True, help="Sube una copia histórica de estas interacciones a OCI Object Storage"):
                        from src.cloud_oci.storage_client import OCIStorageManager
                        sm = OCIStorageManager(allow_local_fallback=True)
                        motor_name = "python_canales" if "Python" in fuente_seleccionada else "n8n_canales"
                        obj_subido = sm.upload_asset(datos_paquete, motor=motor_name)
                        st.toast(f"¡Interacciones sincronizadas a Storage como '{obj_subido}'!", icon="🚀")
                        time.sleep(1)
                        st.rerun()

            meta = datos_paquete.get("metadata_paquete", {})
            if "metricas" not in datos_paquete or not datos_paquete.get("metricas"):
                activos_list = datos_paquete.get("activos", [])
                datos_paquete["metricas"] = {
                    "distribucion_sentimiento": {
                        "positivo": sum(1 for a in activos_list if (a.get("activo") or {}).get("sentimiento") == "positivo"),
                        "neutro": sum(1 for a in activos_list if (a.get("activo") or {}).get("sentimiento") == "neutro"),
                        "negativo": sum(1 for a in activos_list if (a.get("activo") or {}).get("sentimiento") == "negativo"),
                    },
                    "total_posts_linkedin_generados": sum(1 for a in activos_list if (a.get("activo") or {}).get("post_linkedin")),
                    "total_tips_faq_generados": sum(1 for a in activos_list if (a.get("activo") or {}).get("tip_tecnico_faq")),
                }
            metricas = datos_paquete.get("metricas", {})

            # Métricas resumen en columnas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Procesados", meta.get("total_procesados_exitosamente", len(datos_paquete.get("activos", []))))
            with col2:
                st.metric("Posts LinkedIn", metricas.get("total_posts_linkedin_generados", 0))
            with col3:
                st.metric("Tips Técnicos / FAQ", metricas.get("total_tips_faq_generados", 0))
            with col4:
                sentimientos = metricas.get("distribucion_sentimiento", {})
                st.metric("Positivos", sentimientos.get("positivo", 0))

            st.markdown("---")

            # Stepper superior estilo NovaEdu
            st.markdown(
                """
                <div class="stepper-container">
                    <div class="stepper-step">
                        <div class="step-number completed">✓</div>
                        <div class="step-label">1. Ingesta Multicanal</div>
                    </div>
                    <div style="flex: 1; height: 2px; background: #E2E8F0; margin: 0 12px;"></div>
                    <div class="stepper-step">
                        <div class="step-number completed">✓</div>
                        <div class="step-label">2. Clasificación LLM</div>
                    </div>
                    <div style="flex: 1; height: 2px; background: #635BFF; margin: 0 12px;"></div>
                    <div class="stepper-step">
                        <div class="step-number active">3</div>
                        <div class="step-label active">3. Curaduría y Aprobación</div>
                    </div>
                    <div style="flex: 1; height: 2px; background: #E2E8F0; margin: 0 12px;"></div>
                    <div class="stepper-step">
                        <div class="step-number inactive">4</div>
                        <div class="step-label">4. Persistencia en OCI</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Filtros interactivos (Tipo, Sentimiento, Motor y Canal Digital)
            filtro_col1, filtro_col2, filtro_col3, filtro_col4 = st.columns(4)
            with filtro_col1:
                tipo_filtro = st.selectbox(
                    "Filtrar por tipo:",
                    ["Todos", "logro_contratacion", "duda_tecnica", "showcase", "feedback_general"],
                )
            with filtro_col2:
                sentimiento_filtro = st.selectbox(
                    "Filtrar por sentimiento:",
                    ["Todos", "positivo", "neutro", "negativo"],
                )
            with filtro_col3:
                motor_filtro = st.selectbox(
                    "Filtrar por motor:",
                    ["Todos", "🐍 Python Nativo", "⚡ n8n Local"],
                )
            with filtro_col4:
                canal_digital_filtro = st.selectbox(
                    "Filtrar por canal de origen:",
                    ["Todos", "✈️ Telegram", "🎮 Discord", "💬 Slack", "📊 Dataset Batch"],
                )

            activos = datos_paquete.get("activos", [])

            # Aplicar filtros
            if tipo_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["tipo_contenido"] == tipo_filtro]
            if sentimiento_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["sentimiento"] == sentimiento_filtro]
            if motor_filtro == "🐍 Python Nativo":
                activos = [a for a in activos if "python" in (a.get("motor_orquestacion") or meta.get("motor_orquestacion", "")).lower()]
            elif motor_filtro == "⚡ n8n Local":
                activos = [a for a in activos if "n8n" in (a.get("motor_orquestacion") or meta.get("motor_orquestacion", "")).lower()]
            if canal_digital_filtro != "Todos":
                nombre_clave = canal_digital_filtro.split(" ", 1)[1]
                activos = [a for a in activos if detectar_canal_digital(a)[0] == nombre_clave]

            if not activos:
                st.info("No hay activos que coincidan con los filtros seleccionados.")
            else:
                mapa_curaduria = obtener_mapa_curaduria()

                # LAYOUT EN 3 COLUMNAS ESTILO NOVAEDU
                col_lista, col_editor, col_preview = st.columns([1.1, 1.3, 1.2], gap="medium")

                # Inicializar elemento seleccionado en sesión si no existe
                if "item_curado_seleccionado" not in st.session_state:
                    st.session_state.item_curado_seleccionado = 0

                # Asegurar que el índice seleccionado esté en rango
                if st.session_state.item_curado_seleccionado >= len(activos):
                    st.session_state.item_curado_seleccionado = 0

                # -------------------------------------------------------------
                # COLUMNA 1: LISTA DE POSTS E INTERACCIONES
                # -------------------------------------------------------------
                with col_lista:
                    st.markdown(
                        f"""
                        <div class="panel-card-title">
                            <span>📋 Mensajes ({len(activos)})</span>
                            <span style="font-size: 11px; color: #8792A2;">Lote Activo</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    for idx_item, item in enumerate(activos):
                        inter = item["interaccion"]
                        act = item["activo"]
                        canal_nom, canal_badge = detectar_canal_digital(item)
                        cur_info_item = mapa_curaduria.get(inter["id"])
                        estado_item = cur_info_item.get("estado") if cur_info_item else "pendiente"

                        badge_cls = "pendiente"
                        if estado_item == "aprobado":
                            badge_cls = "aprobado"
                        elif estado_item == "rechazado":
                            badge_cls = "descartado"
                        elif estado_item == "leido":
                            badge_cls = "leido"

                        # Botón selector para activar el item en el editor central
                        is_current = (idx_item == st.session_state.item_curado_seleccionado)
                        btn_label = f"{'👉 ' if is_current else ''}#{idx_item + 1} | {inter['autor']} ({canal_badge})"
                        if st.button(
                            btn_label,
                            key=f"sel_item_{inter['id']}_{idx_item}",
                            use_container_width=True,
                            type="primary" if is_current else "secondary",
                        ):
                            st.session_state.item_curado_seleccionado = idx_item
                            st.rerun()

                        # Resumen visual del mensaje en la lista
                        st.caption(f"**{act['tipo_contenido'].upper()}** — {inter['texto'][:75]}...")
                        st.markdown(
                            f"""
                            <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                                <span class="badge-status-pill {badge_cls}">{estado_item.upper()}</span>
                                <span style="font-size: 10px; color: #8792A2;">ID: {inter['id']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        st.markdown("<hr style='margin: 4px 0 12px 0; border-color: #F1F5F9;'>", unsafe_allow_html=True)

                # Objeto activo actual para el editor y la vista previa
                activo_actual = activos[st.session_state.item_curado_seleccionado]
                inter_act = activo_actual["interaccion"]
                act_act = activo_actual["activo"]
                canal_nombre_act, canal_badge_act = detectar_canal_digital(activo_actual)
                cur_info_act = mapa_curaduria.get(inter_act["id"])
                estado_cur_act = cur_info_act.get("estado") if cur_info_act else "pendiente"

                # -------------------------------------------------------------
                # COLUMNA 2: EDITOR DE CONTENIDO CON IA
                # -------------------------------------------------------------
                with col_editor:
                    st.markdown(
                        f"""
                        <div class="panel-card-title">
                            <span>✍️ Editor de Contenido</span>
                            <span style="font-size: 11px; background: #EEF2FF; color: #4F46E5; padding: 2px 8px; border-radius: 6px;">{act_act['tipo_contenido']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown("**📥 Mensaje Original de la Comunidad:**")
                    st.info(f'"{inter_act["texto"]}"')
                    st.caption(f"Autor: **{inter_act['autor']}** &nbsp;|&nbsp; Canal: `{inter_act['canal']}` ({canal_badge_act})")

                    # Copy o Solución Técnica
                    if act_act.get("post_linkedin"):
                        copy_inicial = cur_info_act.get("copy_aprobado") if cur_info_act else act_act["post_linkedin"]
                        copy_editado = st.text_area(
                            "Copy generado para Redes:",
                            value=copy_inicial,
                            height=180,
                            key=f"editor_copy_{inter_act['id']}",
                        )
                    elif act_act.get("tip_tecnico_faq"):
                        copy_inicial = cur_info_act.get("copy_aprobado") if cur_info_act else act_act["tip_tecnico_faq"]
                        copy_editado = st.text_area(
                            "Solución Técnica / FAQ:",
                            value=copy_inicial,
                            height=180,
                            key=f"editor_faq_{inter_act['id']}",
                        )
                    else:
                        copy_editado = inter_act["texto"]
                        st.info("Feedback clasificado para informe de Community Management.")

                    # Tags y Temas Clave
                    st.markdown("**🏷️ Temas Clave:**")
                    tags_html = "".join([f'<span class="tag-chip-nova">#{t}</span>' for t in act_act.get("temas_clave", [])])
                    st.markdown(tags_html, unsafe_allow_html=True)

                    # Botones de Acción
                    st.write("")
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("✅ Aprobar Contenido", type="primary", use_container_width=True, key=f"btn_ap_nov_{inter_act['id']}"):
                            guardar_curaduria_humana(
                                id_interaccion=inter_act["id"],
                                copy_aprobado=copy_editado,
                                estado_aprobacion="aprobado",
                            )
                            st.toast("¡Activo aprobado y sincronizado en OCI!", icon="🚀")
                            time.sleep(0.5)
                            st.rerun()

                    with col_act2:
                        if st.button("🚫 Descartar", use_container_width=True, key=f"btn_desc_nov_{inter_act['id']}"):
                            guardar_curaduria_humana(
                                id_interaccion=inter_act["id"],
                                copy_aprobado=copy_editado,
                                estado_aprobacion="rechazado",
                            )
                            st.toast("Activo descartado en OCI.", icon="⚠️")
                            time.sleep(0.5)
                            st.rerun()

                # -------------------------------------------------------------
                # COLUMNA 3: MOCKUP REALISTA DE VISTA PREVIA (LINKEDIN)
                # -------------------------------------------------------------
                with col_preview:
                    st.markdown(
                        """
                        <div class="panel-card-title">
                            <span>📱 Vista Previa en Vivo</span>
                            <span style="font-size: 11px; color: #0A66C2; font-weight: 700;">LinkedIn Preview</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    avatar_letter = inter_act["autor"][:1].upper() if inter_act.get("autor") else "U"
                    display_text = copy_editado if copy_editado else inter_act["texto"]
                    tags_preview = " ".join([f"#{t}" for t in act_act.get("temas_clave", [])])

                    st.markdown(
                        f"""
                        <div class="linkedin-mockup-card">
                            <div class="linkedin-author-box">
                                <div class="linkedin-avatar">{avatar_letter}</div>
                                <div class="linkedin-meta">
                                    <h5>{inter_act['autor']}</h5>
                                    <p>Estudiante Oracle Next Education (ONE G10) • Activo ahora</p>
                                </div>
                            </div>
                            <div class="linkedin-content-text">{display_text}</div>
                            <div class="linkedin-tags">{tags_preview} #OracleONE #AluraLATAM #TechTalent</div>
                            <div class="linkedin-reactions-bar">
                                <span>👍 ❤️ 👏 48 reacciones</span>
                                <span>12 comentarios</span>
                            </div>
                            <div class="linkedin-actions-row">
                                <span class="linkedin-action-btn">👍 Reaccionar</span>
                                <span class="linkedin-action-btn">💬 Comentar</span>
                                <span class="linkedin-action-btn">🔄 Compartir</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write("")
                    st.markdown(
                        f"""
                        <div style="background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 10px; padding: 12px; margin-top: 10px;">
                            <div style="font-size: 11px; color: #64748B;">Estado en Oracle Cloud:</div>
                            <div style="font-size: 13px; font-weight: 700; color: #1E293B;">
                                {'🟢 Sincronizado en OCI' if estado_cur_act != 'pendiente' else '⏳ Pendiente de revisión'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# -----------------------------------------------------------------------------
# VISTA 2: EJECUTAR PIPELINE
# -----------------------------------------------------------------------------
elif "Ejecutar Pipeline" in modo or modo == VISTA_PIPELINE:
    st.subheader("⚡ Disparador de Ejecución del Pipeline E2E")
    st.write("Ejecuta el procesamiento sobre el lote oficial de interacciones o sube un archivo personalizado.")

    dataset_defecto = "data/interacciones_ejemplo.json"
    archivo_subido = st.file_uploader("Opcional: Sube un archivo JSON con nuevas interacciones", type=["json"])

    ruta_a_procesar = dataset_defecto
    temp_path = None
    if archivo_subido is not None:
        temp_path = Path(f"data/temp_{archivo_subido.name}")
        temp_path.write_bytes(archivo_subido.read())
        ruta_a_procesar = str(temp_path)
        st.success(f"Archivo subido: `{archivo_subido.name}`")

    st.markdown("---")
    # Fila 1: Límite, Canal, Vaciar Lotes Locales, Vaciar Histórico OCI
    col_f1_1, col_f1_2, col_f1_3, col_f1_4 = st.columns([1.6, 2.2, 1.5, 1.6])
    with col_f1_1:
        limite = st.number_input("Registros a procesar (0=todos):", min_value=0, max_value=100, value=3)
    with col_f1_2:
        canal_filtro = st.selectbox(
            "Filtrar por canal:",
            ["Todos", "#logros-y-empleos", "#dudas-cloud-oci", "#dudas-langgraph", "#feedback-cursos", "#proyectos-showcase"],
        )
    with col_f1_3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Vaciar Lotes Locales", help="Elimina los archivos de sesión temporal (paquete_procesado_*.json)", use_container_width=True):
            for fpath in ["data/paquete_procesado_python.json", "data/paquete_procesado_n8n.json", "data/paquete_procesado.json"]:
                p = Path(fpath)
                if p.exists():
                    p.unlink()
            st.toast("Lotes locales temporales eliminados.")
            st.rerun()
    with col_f1_4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        with st.popover("⚠️ Vaciar Histórico OCI", help="Elimina permanentemente los paquetes guardados en el histórico de OCI", use_container_width=True):
            st.warning("⚠️ **¿Vaciar Histórico OCI?**")
            st.caption("Esta acción eliminará de forma irreversible todos los paquetes JSON persistidos en el almacenamiento.")
            conf_oci_v2 = st.checkbox("Confirmo que deseo vaciar el histórico", key="chk_conf_v2")
            if st.button("🚨 Sí, vaciar permanentemente", type="primary", disabled=not conf_oci_v2, key="btn_vaciar_hist_v2", use_container_width=True):
                n_del = vaciar_historico_oci()
                st.toast(f"Histórico de OCI vaciado correctamente ({n_del} objetos eliminados).")
                st.rerun()

    # Fila 2: Controles de ejecución OCI y deduplicación
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_chk1, c_chk2 = st.columns([1, 1])
    with c_chk1:
        subir_oci = st.checkbox(
            "Subir a OCI Storage (Motor Python)",
            value=True,
            help="Sube automáticamente los 4 archivos temáticos especializados (logros, showcase, faqs, feedback) al bucket de OCI, igual que n8n.",
        )
    with c_chk2:
        omitir_ya_procesados = st.checkbox(
            "Omitir interacciones ya procesadas en OCI",
            value=True,
            help="Si está marcado, consulta OCI Object Storage para excluir los registros procesados previamente y toma los siguientes nuevos del dataset.",
        )

    # -------------------------------------------------------------------------
    # SELECCIÓN DE MOTOR DE ORQUESTACIÓN CON DISEÑO NOVAEDU
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 🎛️ Selección y Ejecución del Motor Dual")
    st.caption("Compara la orquestación visual en n8n frente a la velocidad compilada de Python Nativo.")

    col_n8n, col_py = st.columns(2)

    # -------------------------------------------------------------------------
    # COLUMNA 1: ORQUESTADOR N8N (MOTOR 1)
    # -------------------------------------------------------------------------
    with col_n8n:
        st.markdown(
            """
            <div class="engine-card n8n">
                <div class="engine-header">
                    <div class="engine-title">
                        <span>🔄</span>
                        <span>Motor 1: n8n Flow</span>
                    </div>
                    <span class="engine-badge n8n">Visual Webhook</span>
                </div>
                <div class="engine-description">
                    Orquestación visual basada en flujos de nodos automatizados con bucles por interacción y bifurcación Switch hacia OCI.
                </div>
                <ul class="engine-features-list">
                    <li>⚡ <b>Instancia:</b> OCI VM / Local (<code>:5678</code>)</li>
                    <li>🧠 <b>LLM:</b> Basic LLM Chain + Groq / Gemini</li>
                    <li>🔀 <b>Enrutamiento:</b> 4 ramales especializados</li>
                    <li>☁️ <b>Persistencia:</b> Nodos OCI REST integrados</li>
                </ul>
                <div class="telemetry-card">
                    <div class="telemetry-item">
                        <span class="telemetry-label">Tipo</span>
                        <span class="telemetry-value" style="color: #D97706;">No-Code Flow</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="telemetry-label">Latencia Prom.</span>
                        <span class="telemetry-value" style="color: #D97706;">~1.8s/item</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="telemetry-label">Estado</span>
                        <span class="telemetry-value" style="color: #10B981;">Online</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        webhook_default = get_n8n_webhook_url()
        with st.expander("⚙️ Configuración Endpoint Webhook n8n", expanded=False):
            webhook_url = st.text_input("URL Webhook:", value=webhook_default)

        if st.button("⚡ Ejecutar con Orquestador n8n", type="primary", use_container_width=True):
            canal_val = None if canal_filtro == "Todos" else canal_filtro
            limite_val = None if limite == 0 else int(limite)
            ids_omitir = obtener_ids_procesados_sesion() if omitir_ya_procesados else None

            with st.spinner("Enviando interacciones al Webhook de n8n en OCI..."):
                t_ini = time.time()
                try:
                    paquete_n8n = procesar_archivo_n8n_ui(
                        ruta_archivo=ruta_a_procesar,
                        webhook_url=webhook_url,
                        limite=limite_val,
                        canal_filtro=canal_val,
                        upload_oci=False,  # n8n ya persiste sus 4 archivos especializados en OCI
                        ids_a_omitir=ids_omitir,
                    )
                    t_total = time.time() - t_ini

                    es_asincrono = paquete_n8n.get("metadata_paquete", {}).get("modo_ejecucion") == "asincrono"

                    if not es_asincrono:
                        st.success(f"¡Flujo n8n completado exitosamente en **{t_total:.2f}s**!")
                        st.json(paquete_n8n.get("metricas", {}))
                        st.info("Los 4 archivos especializados fueron actualizados en OCI Object Storage. Selecciónalos en **'✨ Posts con IA'**.")
                    else:
                        st.success(f"🚀 ¡Lote recibido por n8n en **{t_total:.2f}s**!")
                        st.info(f"ℹ️ {paquete_n8n['metadata_paquete'].get('mensaje_n8n')}")
                        st.markdown(
                            """
                            > **Nota:** n8n está procesando el lote con el LLM y subirá los **4 archivos especializados a OCI Object Storage**. 
                            > Cuando finalice en n8n, encuéntralos y curálos directamente en **'✨ Posts con IA'** o en **'☁️ Histórico OCI'**.
                            """
                        )
                except ValueError as ve:
                    st.info(f"ℹ️ {ve}")
                except Exception as e:
                    st.error(f"{e}")
                finally:
                    if temp_path and temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception:
                            pass

    # -------------------------------------------------------------------------
    # COLUMNA 2: MOTOR PYTHON NATIVO (MOTOR 2)
    # -------------------------------------------------------------------------
    with col_py:
        st.markdown(
            """
            <div class="engine-card python">
                <div class="engine-header">
                    <div class="engine-title">
                        <span>🐍</span>
                        <span>Motor 2: Pipeline Python</span>
                    </div>
                    <span class="engine-badge python">Native Code</span>
                </div>
                <div class="engine-description">
                    Código modular de alto rendimiento en <code>src/</code> con tipado Pydantic estricto y conmutación automática de modelos Gemini.
                </div>
                <ul class="engine-features-list">
                    <li>⚡ <b>LLM:</b> Gemini 3.6 Flash (fallback 3.5 Lite)</li>
                    <li>🛡️ <b>Resiliencia:</b> Retry exponencial + Circuit Breaker</li>
                    <li>🧪 <b>Testing:</b> 71 tests unitarios en pytest (100% pass)</li>
                    <li>🚀 <b>Rendimiento:</b> Paralelismo asíncrono y caché local</li>
                </ul>
                <div class="telemetry-card">
                    <div class="telemetry-item">
                        <span class="telemetry-label">Tipo</span>
                        <span class="telemetry-value" style="color: #635BFF;">Pydantic / SDK</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="telemetry-label">Latencia Prom.</span>
                        <span class="telemetry-value" style="color: #635BFF;">~0.6s/item</span>
                    </div>
                    <div class="telemetry-item">
                        <span class="telemetry-label">Test Suite</span>
                        <span class="telemetry-value" style="color: #10B981;">71/71 Pass</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        if st.button("🚀 Ejecutar con Python Nativo", type="primary", use_container_width=True):
            canal_val = None if canal_filtro == "Todos" else canal_filtro
            limite_val = None if limite == 0 else int(limite)
            ids_omitir = obtener_ids_procesados_sesion() if omitir_ya_procesados else None

            with st.spinner("Procesando con Pipeline Python (Gemini 3.6 / 3.5)..."):
                t_ini = time.time()
                try:
                    paquete = procesar_archivo_ui(
                        ruta_archivo=ruta_a_procesar,
                        limite=limite_val,
                        canal_filtro=canal_val,
                        upload_oci=subir_oci,
                        delay_segundos=0.5,
                        ids_a_omitir=ids_omitir,
                    )
                    t_total = time.time() - t_ini

                    # Guardar una copia local para que esté disponible de inmediato en la vista de curaduría
                    import json
                    from pathlib import Path
                    Path("data/paquete_procesado_python.json").write_text(
                        json.dumps(paquete, ensure_ascii=False, indent=2),
                        encoding="utf-8"
                    )

                    st.success(f"¡Pipeline Python completado exitosamente en **{t_total:.2f}s**!")
                    st.json(paquete.get("metricas", {}))
                    st.info("El paquete fue actualizado y está listo para curar en **'✨ Posts con IA'**.")
                except ValueError as ve:
                    st.info(f"ℹ️ {ve}")
                except Exception as e:
                    st.error(f"Error en Pipeline Python: {e}")
                finally:
                    if temp_path and temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception:
                            pass

    # -------------------------------------------------------------------------
    # SECCIÓN: REGISTRO DE LOGS EN VIVO (logs/communitylab.log)
    # -------------------------------------------------------------------------
    st.markdown("---")
    with st.expander("📋 Ver Registro de Logs en Vivo (logs/communitylab.log)", expanded=False):
        c_log1, c_log2, c_log3 = st.columns([4, 1, 1])
        with c_log1:
            st.caption("Monitorea las llamadas a Gemini, rate-limits, inferencia y persistencia en tiempo real.")
        with c_log2:
            if st.button("🔄 Refrescar"):
                st.rerun()
        with c_log3:
            if st.button("🧹 Limpiar Log"):
                limpiar_archivo_log()
                st.toast("Archivo de log vaciado.")
                st.rerun()

        logs_recientes = obtener_ultimas_lineas_log(num_lineas=40)
        st.code("".join(logs_recientes) if logs_recientes else "No hay entradas en el archivo de log aún.", language="log")

# -----------------------------------------------------------------------------
# VISTA 3: HISTÓRICO OCI
# -----------------------------------------------------------------------------
elif "Histórico" in modo or modo == VISTA_HISTORICO:
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader("☁️ Repositorio Histórico en Oracle Cloud Infrastructure")
        st.caption("Objetos y paquetes de contenido persistidos en el Bucket Always Free de OCI Object Storage.")
    with c_head2:
        with st.popover("🗑️ Vaciar Bucket", help="Elimina permanentemente los paquetes guardados en el histórico"):
            st.warning("⚠️ **¿Vaciar Histórico de OCI?**")
            st.caption("Esta acción eliminará de forma permanente todos los paquetes almacenados en el storage.")
            conf_oci_v3 = st.checkbox("Confirmo eliminar el histórico", key="chk_conf_v3")
            if st.button("🚨 Sí, vaciar almacenamiento", type="primary", disabled=not conf_oci_v3, key="btn_vaciar_hist_v3", use_container_width=True):
                n_del = vaciar_historico_oci()
                st.toast(f"Histórico de OCI vaciado exitosamente ({n_del} objetos eliminados).")
                st.rerun()

    paquetes = obtener_ultimos_paquetes(limite=50)

    # 1. Panel Superior de Estadísticas del Almacenamiento
    total_objs = len(paquetes)
    total_bytes = sum(p.get("size", 0) for p in paquetes)
    total_kb = total_bytes / 1024.0

    st.markdown(
        f"""
        <div class="storage-stat-container">
            <div class="storage-stat-card">
                <div class="storage-stat-title">📦 Total Objetos Persistidos</div>
                <div class="storage-stat-val">{total_objs}</div>
            </div>
            <div class="storage-stat-card">
                <div class="storage-stat-title">💾 Volumen Almacenado</div>
                <div class="storage-stat-val">{total_kb:.1f} <span style="font-size: 13px; font-weight: 500; color: #64748B;">KB</span></div>
            </div>
            <div class="storage-stat-card">
                <div class="storage-stat-title">☁️ Estado del Bucket</div>
                <div class="storage-stat-val" style="color: #10B981; font-size: 18px;">OCI Always Free Active</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not paquetes:
        st.info("ℹ️ No hay paquetes registrados aún en el almacenamiento. Procesa un lote en **'⚡ Orquestador Dual'** para poblar el histórico.")
    else:
        st.markdown("### 🗂️ Lotes y Archivos Especializados Disponibles")

        for idx_p, p in enumerate(paquetes):
            nom = p["name"]
            size_kb = p.get("size", 0) / 1024.0
            fecha_str = p.get("created_at", "N/A")[:19].replace("T", " ") if p.get("created_at") else "Local Almacenado"

            # Detectar tipo de activo para badge visual
            badge_tipo_cls = "general"
            badge_tipo_lbl = "Paquete Consolidado"
            if "logros" in nom:
                badge_tipo_cls = "logros"
                badge_tipo_lbl = "Logros & Empleos"
            elif "dudas" in nom or "faq" in nom:
                badge_tipo_cls = "dudas"
                badge_tipo_lbl = "Dudas Técnicas / FAQ"
            elif "showcase" in nom or "proyectos" in nom:
                badge_tipo_cls = "showcase"
                badge_tipo_lbl = "Showcase & Proyectos"
            elif "feedback" in nom:
                badge_tipo_cls = "feedback"
                badge_tipo_lbl = "Feedback Comunidad"
            elif "curaduria" in nom:
                badge_tipo_cls = "showcase"
                badge_tipo_lbl = "Curaduría Humana"

            c_info, c_action = st.columns([3.2, 0.8])
            with c_info:
                st.markdown(
                    f"""
                    <div class="storage-asset-card">
                        <div class="storage-asset-info">
                            <div class="storage-asset-name">📄 {nom}</div>
                            <div class="storage-asset-meta">
                                <span class="storage-badge-type {badge_tipo_cls}">{badge_tipo_lbl}</span>
                                <span><b>{size_kb:.2f} KB</b></span>
                                <span>🕒 {fecha_str}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_action:
                st.write("")
                if st.button("🔗 Enlace PAR", key=f"par_btn_{nom}_{idx_p}", use_container_width=True, help="Genera una Pre-Authenticated Request de 24 horas en Oracle Cloud"):
                    from src.cloud_oci.storage_client import OCIStorageManager
                    sm = OCIStorageManager(allow_local_fallback=True)
                    par = sm.create_preauthenticated_request(nom, expires_in_hours=24)
                    st.session_state[f"url_{nom}"] = par["access_url"]

            # Si se generó el PAR, mostrar caja con enlace y visualizador JSON
            par_key = f"url_{nom}"
            if par_key in st.session_state:
                par_url = st.session_state[par_key]
                st.markdown(
                    f"""
                    <div class="storage-par-box">
                        <div>
                            <span style="font-size: 12px; font-weight: 700; color: #4F46E5;">⚡ Pre-Authenticated Request (Válido 24h):</span><br>
                            <a href="{par_url}" target="_blank" style="font-size: 12px; color: #0284C7; text-decoration: underline; word-break: break-all;">{par_url}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander(f"👁️ Inspeccionar contenido JSON de {nom}", expanded=False):
                    from src.ui.services import cargar_paquete
                    raw_content = cargar_paquete(nom)
                    if raw_content:
                        st.json(raw_content)
                    else:
                        st.caption("No fue posible previsualizar el contenido del objeto.")
