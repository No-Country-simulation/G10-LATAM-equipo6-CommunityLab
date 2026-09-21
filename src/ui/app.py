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
    fusionar_paquetes,
    vaciar_historico_oci_local,
    obtener_ids_procesados_sesion,
)
from src.utils.logger import obtener_ultimas_lineas_log, limpiar_archivo_log

# Configuración de la página
st.set_page_config(
    page_title="CommunityLab — Panel de Curaduría",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos personalizados sutiles
st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F3F4F6; border-radius: 8px; padding: 15px; border-left: 4px solid #3B82F6; }
    .card-title { font-size: 0.9rem; color: #6B7280; font-weight: 600; text-transform: uppercase; }
    .card-value { font-size: 1.8rem; font-weight: 700; color: #111827; }
    .tag-chip { display: inline-block; background-color: #E0E7FF; color: #3730A3; border-radius: 12px; padding: 2px 10px; font-size: 0.8rem; font-weight: 600; margin-right: 5px; }
    /* Evitar truncamiento con puntos suspensivos en checkboxes */
    div[data-testid="stCheckbox"] label p { white-space: nowrap !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown('<div class="main-header">🚀 CommunityLab — Motor de Curaduría</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Transformación de actividad orgánica de comunidades técnicas en activos de alto valor para Oracle ONE & Alura.</div>',
    unsafe_allow_html=True,
)

# Sidebar de navegación
st.sidebar.title("Navegación")
modo = st.sidebar.radio(
    "Selecciona una vista:",
    ["💼 Curaduría de Activos", "⚡ Ejecutar Pipeline", "☁️ Histórico OCI Object Storage"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Rol Activo:** Backend & Pipeline \n\n"
    "**Célula 1 & 3:** IA, Pipeline y Curaduría Streamlit."
)

# -----------------------------------------------------------------------------
# VISTA 1: CURADURÍA DE ACTIVOS
# -----------------------------------------------------------------------------
if modo == "💼 Curaduría de Activos":
    st.subheader("📋 Revisión y Aprobación de Copys para Publicación")

    # Cargar paquetes disponibles
    paquetes_disponibles = obtener_ultimos_paquetes(limite=20)

    default_paquete_path = Path("data/paquete_procesado.json")
    python_paquete_path = Path("data/paquete_procesado_python.json")
    n8n_paquete_path = Path("data/paquete_procesado_n8n.json")
    opciones_fuente = []

    # 1. Opción Consolidada si existen ambos
    if python_paquete_path.exists() and n8n_paquete_path.exists():
        opciones_fuente.append("🔥 Vista Consolidada: Todos los Activos (Python + n8n)")

    # 2. Opciones individuales
    if python_paquete_path.exists():
        opciones_fuente.append("🐍 Python: data/paquete_procesado_python.json")
    if n8n_paquete_path.exists():
        opciones_fuente.append("🔄 n8n: data/paquete_procesado_n8n.json")
    if default_paquete_path.exists():
        opciones_fuente.append("📁 Último Lote Generado: data/paquete_procesado.json")

    for p in paquetes_disponibles:
        opciones_fuente.append(f"Storage: {p['name']}")

    if not opciones_fuente:
        st.warning(
            "⚠️ Aún no se han generado paquetes de distribución. "
            "Ve a la pestaña **'⚡ Ejecutar Pipeline'** para procesar el dataset de ejemplo."
        )
    else:
        fuente_seleccionada = st.selectbox("Selecciona el lote a inspeccionar:", opciones_fuente)

        # Cargar datos del paquete
        datos_paquete = None
        if fuente_seleccionada.startswith("🔥 Vista Consolidada:"):
            with open(python_paquete_path, "r", encoding="utf-8") as f:
                d_py = json.load(f)
            with open(n8n_paquete_path, "r", encoding="utf-8") as f:
                d_n8n = json.load(f)

            activos_py = d_py.get("activos", [])
            for a in activos_py:
                a["motor_orquestacion"] = a.get("motor_orquestacion") or "python_gemini"

            activos_n8n = d_n8n.get("activos", [])
            for a in activos_n8n:
                a["motor_orquestacion"] = a.get("motor_orquestacion") or "n8n_local"

            activos_todos = activos_py + activos_n8n

            m_py = d_py.get("metricas", {})
            m_n8n = d_n8n.get("metricas", {})
            total_posts = m_py.get("total_posts_linkedin_generados", 0) + m_n8n.get("total_posts_linkedin_generados", 0)
            total_tips = m_py.get("total_tips_faq_generados", 0) + m_n8n.get("total_tips_faq_generados", 0)

            sent_dist = {"positivo": 0, "neutro": 0, "negativo": 0}
            for s in ["positivo", "neutro", "negativo"]:
                sent_dist[s] = (
                    m_py.get("distribucion_sentimiento", {}).get(s, 0)
                    + m_n8n.get("distribucion_sentimiento", {}).get(s, 0)
                )

            datos_paquete = {
                "metadata_paquete": {
                    "total_procesados_exitosamente": len(activos_todos),
                    "motor_orquestacion": "Consolidado Dual (Python + n8n)",
                },
                "metricas": {
                    "distribucion_sentimiento": sent_dist,
                    "total_posts_linkedin_generados": total_posts,
                    "total_tips_faq_generados": total_tips,
                },
                "activos": activos_todos,
            }
        elif fuente_seleccionada.startswith("🐍 Python:"):
            with open(python_paquete_path, "r", encoding="utf-8") as f:
                datos_paquete = json.load(f)
        elif fuente_seleccionada.startswith("🔄 n8n:"):
            with open(n8n_paquete_path, "r", encoding="utf-8") as f:
                datos_paquete = json.load(f)
        elif fuente_seleccionada.startswith("📁 Último") or fuente_seleccionada.startswith("Local:"):
            with open(default_paquete_path, "r", encoding="utf-8") as f:
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
            meta = datos_paquete.get("metadata_paquete", {})
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

            # Filtros interactivos
            filtro_col1, filtro_col2, filtro_col3 = st.columns(3)
            with filtro_col1:
                tipo_filtro = st.selectbox(
                    "Filtrar por tipo de contenido:",
                    ["Todos", "logro_contratacion", "duda_tecnica", "showcase", "feedback_general"],
                )
            with filtro_col2:
                sentimiento_filtro = st.selectbox(
                    "Filtrar por sentimiento:",
                    ["Todos", "positivo", "neutro", "negativo"],
                )
            with filtro_col3:
                motor_filtro = st.selectbox(
                    "Filtrar por motor ejecutor:",
                    ["Todos", "🐍 Python Nativo", "🔄 n8n Local"],
                )

            activos = datos_paquete.get("activos", [])

            # Aplicar filtros
            if tipo_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["tipo_contenido"] == tipo_filtro]
            if sentimiento_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["sentimiento"] == sentimiento_filtro]
            if motor_filtro == "🐍 Python Nativo":
                activos = [a for a in activos if "python" in (a.get("motor_orquestacion") or meta.get("motor_orquestacion", "")).lower()]
            elif motor_filtro == "🔄 n8n Local":
                activos = [a for a in activos if "n8n" in (a.get("motor_orquestacion") or meta.get("motor_orquestacion", "")).lower()]

            c_info1, c_info2 = st.columns([3, 2])
            with c_info1:
                st.write(f"Mostrando **{len(activos)}** activos filtrados:")
            with c_info2:
                orden_recientes = st.toggle("⏱️ Mostrar más recientes primero", value=True)

            if orden_recientes:
                activos_a_mostrar = list(reversed(activos))
            else:
                activos_a_mostrar = list(activos)

            # Renderizado de tarjetas de activos
            for idx, item in enumerate(activos_a_mostrar, start=1):
                interaccion = item["interaccion"]
                activo = item["activo"]
                motor_val = (item.get("motor_orquestacion") or meta.get("motor_orquestacion", "")).lower()
                if "python" in motor_val:
                    badge_motor = "🐍 PYTHON"
                elif "n8n" in motor_val:
                    badge_motor = "🔄 N8N"
                else:
                    badge_motor = "⚙️ MOTOR"

                proc_time = item.get("procesado_en", "")
                hora_str = proc_time[11:19] if len(proc_time) >= 19 else "Sesión"
                lote_tag = item.get("lote_id", "")
                badge_lote = f"[{lote_tag}] " if lote_tag else ""

                with st.expander(
                    f"#{idx} | [{badge_motor}] {badge_lote}[{activo['tipo_contenido'].upper()}] {interaccion['autor']} ({interaccion['canal']}) — ⏱️ {hora_str}",
                    expanded=(idx == 1),
                ):
                    c_left, c_right = st.columns([1, 1])

                    with c_left:
                        st.markdown("#### 💬 Interacción Original")
                        st.info(f"\"{interaccion['texto']}\"")
                        st.caption(
                            f"Motor: **{badge_motor}** | ID: `{interaccion['id']}` | "
                            f"Lote: `{lote_tag or 'previo'}` | ⏱️ Hora: **{hora_str}** | "
                            f"Sentimiento: **{activo['sentimiento']}**"
                        )

                        # Etiquetas / Temas clave
                        tags_html = "".join([f'<span class="tag-chip">#{t}</span>' for t in activo.get("temas_clave", [])])
                        st.markdown(f"**Temas Clave:** {tags_html}", unsafe_allow_html=True)

                    with c_right:
                        st.markdown("#### ✍️ Activo Generado")

                        if activo.get("post_linkedin"):
                            st.markdown("**Copy para LinkedIn:**")
                            copy_editado = st.text_area(
                                "Editar copy antes de aprobar:",
                                value=activo["post_linkedin"],
                                height=150,
                                key=f"copy_{interaccion['id']}_{motor_val}_{idx}",
                            )

                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("✅ Aprobar Copy", key=f"btn_ap_{interaccion['id']}_{motor_val}_{idx}"):
                                    guardar_curaduria_humana(
                                        id_interaccion=f"{interaccion['id']} ({badge_motor})",
                                        copy_aprobado=copy_editado,
                                        estado_aprobacion="aprobado",
                                    )
                                    st.success("¡Copy registrado como Aprobado!")
                            with btn_col2:
                                if st.button("❌ Descartar", key=f"btn_desc_{interaccion['id']}_{motor_val}_{idx}"):
                                    guardar_curaduria_humana(
                                        id_interaccion=f"{interaccion['id']} ({badge_motor})",
                                        copy_aprobado=copy_editado,
                                        estado_aprobacion="rechazado",
                                    )
                                    st.warning("Copy descartado.")

                        elif activo.get("tip_tecnico_faq"):
                            st.markdown("**Tip Técnico / Respuesta FAQ:**")
                            st.markdown(activo["tip_tecnico_faq"])
                        else:
                            st.markdown("_No requiere generación de post ni FAQ (Feedback General)._")

# -----------------------------------------------------------------------------
# VISTA 2: EJECUTAR PIPELINE
# -----------------------------------------------------------------------------
elif modo == "⚡ Ejecutar Pipeline":
    st.subheader("⚡ Disparador de Ejecución del Pipeline E2E")
    st.write("Ejecuta el procesamiento sobre el lote oficial de interacciones o sube un archivo personalizado.")

    dataset_defecto = "data/interacciones_ejemplo.json"
    archivo_subido = st.file_uploader("Opcional: Sube un archivo JSON con nuevas interacciones", type=["json"])

    ruta_a_procesar = dataset_defecto
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
                vaciar_historico_oci_local()
                st.toast("Histórico de OCI vaciado correctamente.")
                st.rerun()

    # Fila 2: Los 3 checks distribuidos a lo largo de toda la fila para lectura completa
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    c_chk1, c_chk2, c_chk3 = st.columns([1, 1, 1])
    with c_chk1:
        subir_oci = st.checkbox(
            "Subir a OCI Storage (Motor Python)",
            value=True,
            help="Persiste el paquete resultante del motor Python en OCI Object Storage. n8n ya sube sus 4 archivos especializados automáticamente.",
        )
    with c_chk2:
        acumular_lote = st.checkbox(
            "Acumular con previos",
            value=True,
            help="Si está marcado, los nuevos activos procesados se suman a los anteriores sin sobrescribirlos.",
        )
    with c_chk3:
        omitir_ya_procesados = st.checkbox(
            "Omitir ya procesados",
            value=True,
            help="Si está marcado, excluye los registros procesados previamente en esta sesión y toma los siguientes nuevos.",
        )

    st.markdown("---")
    st.markdown("### 🎛️ Selección de Motor de Orquestación")
    st.caption("Ejecuta el procesamiento con cualquiera de los dos motores para comparar velocidad, formato y precisión.")

    col_n8n, col_py = st.columns(2)

    # -------------------------------------------------------------------------
    # COLUMNA 1: ORQUESTADOR N8N (MOTOR 1)
    # -------------------------------------------------------------------------
    with col_n8n:
        st.markdown(
            """
            <div style="background-color: #0F172A; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
                <h4 style="margin: 0; color: #F59E0B;">🔄 Motor 1: Orquestador n8n (Local / OCI)</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 6px;">
                    Flujo visual de n8n orquestado en contenedor local (<code>http://localhost:5678</code>) o VM en OCI.
                </p>
                <ul style="color: #CBD5E1; font-size: 0.85rem; padding-left: 18px;">
                    <li><b>Instancia:</b> n8n Local (<code>http://localhost:5678</code>)</li>
                    <li><b>Cadena:</b> Basic LLM Chain + Groq / Gemini</li>
                    <li><b>Flujo:</b> Loop Over Items + Wait + Switch</li>
                    <li><b>Canal:</b> Endpoint Webhook HTTP en tiempo real</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        webhook_default = os.getenv(
            "N8N_LOCAL_WEBHOOK_URL",
            os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/communitylab-ingesta"),
        )
        with st.expander("⚙️ Configuración Endpoint Webhook n8n", expanded=False):
            webhook_url = st.text_input("URL Webhook:", value=webhook_default)

        if st.button("🌐 Ejecutar con Orquestador n8n", type="primary", use_container_width=True):
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

                    # Modo acumulativo si está activo
                    if acumular_lote:
                        p_n8n_path = Path("data/paquete_procesado_n8n.json")
                        d_prev_n8n = json.loads(p_n8n_path.read_text(encoding="utf-8")) if p_n8n_path.exists() else None
                        paquete_n8n = fusionar_paquetes(d_prev_n8n, paquete_n8n)

                    # Guardar tanto en paquete específico de n8n como en el general
                    with open("data/paquete_procesado_n8n.json", "w", encoding="utf-8") as f:
                        json.dump(paquete_n8n, f, ensure_ascii=False, indent=2)
                    with open("data/paquete_procesado.json", "w", encoding="utf-8") as f:
                        json.dump(paquete_n8n, f, ensure_ascii=False, indent=2)

                    st.success(f"¡Flujo n8n completado exitosamente en **{t_total:.2f}s**!")
                    st.json(paquete_n8n.get("metricas", {}))
                    st.info("Revisa los copys generados en **'💼 Curaduría de Activos'**.")
                except ValueError as ve:
                    st.info(f"ℹ️ {ve}")
                except Exception as e:
                    st.error(f"{e}")

    # -------------------------------------------------------------------------
    # COLUMNA 2: MOTOR PYTHON NATIVO (MOTOR 2)
    # -------------------------------------------------------------------------
    with col_py:
        st.markdown(
            """
            <div style="background-color: #0F172A; padding: 16px; border-radius: 8px; border: 1px solid #334155;">
                <h4 style="margin: 0; color: #38BDF8;">🐍 Motor 2: Pipeline Python Nativo</h4>
                <p style="color: #94A3B8; font-size: 0.9rem; margin-top: 6px;">
                    Desarrollado en código nativo (<code>src/</code>) con tipado estricto Pydantic y conmutación automática de modelos.
                </p>
                <ul style="color: #CBD5E1; font-size: 0.85rem; padding-left: 18px;">
                    <li><b>LLM:</b> Google Gemini 3.6 Flash (fallback 3.5 Lite)</li>
                    <li><b>Resiliencia:</b> Reintentos con retroceso exponencial</li>
                    <li><b>Testing:</b> 37 tests unitarios en pytest (100% passing)</li>
                    <li><b>Velocidad:</b> Máximo rendimiento en milisegundos</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("🚀 Ejecutar con Python Nativo", type="secondary", use_container_width=True):
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

                    # Modo acumulativo si está activo
                    if acumular_lote:
                        p_py_path = Path("data/paquete_procesado_python.json")
                        d_prev = json.loads(p_py_path.read_text(encoding="utf-8")) if p_py_path.exists() else None
                        paquete = fusionar_paquetes(d_prev, paquete)

                    # Guardar tanto en paquete específico de Python como en el general
                    with open("data/paquete_procesado_python.json", "w", encoding="utf-8") as f:
                        json.dump(paquete, f, ensure_ascii=False, indent=2)
                    with open("data/paquete_procesado.json", "w", encoding="utf-8") as f:
                        json.dump(paquete, f, ensure_ascii=False, indent=2)

                    st.success(f"¡Pipeline Python completado exitosamente en **{t_total:.2f}s**!")
                    st.json(paquete.get("metricas", {}))
                    st.info("Revisa los copys generados en **'💼 Curaduría de Activos'**.")
                except ValueError as ve:
                    st.info(f"ℹ️ {ve}")
                except Exception as e:
                    st.error(f"Error en Pipeline Python: {e}")

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
elif modo == "☁️ Histórico OCI Object Storage":
    c_head1, c_head2 = st.columns([3, 1])
    with c_head1:
        st.subheader("☁️ Objetos Persistidos en OCI Object Storage Always Free")
    with c_head2:
        with st.popover("🗑️ Vaciar Histórico", help="Elimina permanentemente los paquetes guardados en el histórico"):
            st.warning("⚠️ **¿Vaciar Histórico de OCI?**")
            st.caption("Esta acción eliminará de forma permanente todos los paquetes almacenados en el storage.")
            conf_oci_v3 = st.checkbox("Confirmo eliminar el histórico", key="chk_conf_v3")
            if st.button("🚨 Sí, vaciar almacenamiento", type="primary", disabled=not conf_oci_v3, key="btn_vaciar_hist_v3"):
                vaciar_historico_oci_local()
                st.toast("Histórico de OCI vaciado exitosamente.")
                st.rerun()

    paquetes = obtener_ultimos_paquetes(limite=50)

    if not paquetes:
        st.info("No hay paquetes registrados aún en el almacenamiento.")
    else:
        st.write(f"Se encontraron **{len(paquetes)}** paquetes almacenados:")

        for p in paquetes:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                with c1:
                    st.code(p["name"])
                with c2:
                    st.write(f"{p['size']} bytes")
                with c3:
                    st.caption(p.get("created_at", "N/A")[:19] if p.get("created_at") else "Local")
                with c4:
                    if st.button("🔗 Generar PAR", key=f"par_{p['name']}"):
                        from src.cloud_oci.storage_client import OCIStorageManager
                        sm = OCIStorageManager(allow_local_fallback=True)
                        par = sm.create_preauthenticated_request(p["name"], expires_in_hours=24)
                        st.session_state[f"url_{p['name']}"] = par["access_url"]

                par_key = f"url_{p['name']}"
                if par_key in st.session_state:
                    par_url = st.session_state[par_key]
                    st.success(f"URL de acceso temporal: [Abrir Activo]({par_url})")
                    st.caption(par_url)
