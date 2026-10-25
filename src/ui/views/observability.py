"""Vistas de arquitectura, flujo de datos y observabilidad en tiempo real."""

from __future__ import annotations

import streamlit as st

from scripts.icons import icon_svg
from src.utils.logger import get_log_file_path, is_detailed_log_enabled, limpiar_archivo_log, obtener_ultimas_lineas_log
from .common import render_page_card


def render_flow_diagram():
    """Diagrama de arquitectura del pipeline de CommunityLab."""
    render_page_card(
        "Arquitectura del Sistema y Recorrido de los Datos",
        "Diagrama completo del flujo: desde la recepción de mensajes hasta el procesamiento con Inteligencia Artificial y el guardado en la nube.",
        "git-branch",
    )

    flow_icon = icon_svg("workflow", size=20, color="#FFFFFF", extra_style="margin-right:8px;")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #1E1B4B 0%, #1E293B 100%); border:1px solid #334155; border-radius:14px; padding:16px 20px; margin-bottom:16px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#F8FAFC; display:flex; align-items:center;">{flow_icon} Diagrama de Flujo del Pipeline E2E</span>
                <div style="font-size:0.83rem; color:#94A3B8; margin-top:3px;">
                    Flujo continuo de 6 etapas: Ingesta ➔ Normalización ➔ Orquestación ➔ IA Generativa ➔ Almacenamiento ➔ Moderación.
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="status-pill online"><span class="status-dot online"></span> 6 Capas Activas</span>
                <span class="status-pill oci">Oracle Cloud Native</span>
                <span class="status-pill online">Pipeline Dual</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:10px;'>Diagrama de Procesamiento de Mensajes</div>", unsafe_allow_html=True)
    
    mermaid_code = """
    graph TD
        subgraph INGESTA["1. Captura de Mensajes (Producción)"]
            TG["Bot de Telegram (@G10_Latam_06_bot)"]
            DC["Bot de Discord (#general-g10 Equipo 6)"]
            SL["Bot de Slack (@G10-LATAM-06)"]
            CSV["Archivos de Mensajes JSON / CSV"]
        end

        subgraph DISPATCHER["2. Recepción y Normalización"]
            BM["Gestor Central de Asistentes"]
            CMD["Despachador de Mensajes"]
            NORM["Esquema Canónico de Interacción"]
            DEDUP["Filtro de Mensajes Duplicados"]
            TG --> BM
            DC --> BM
            SL --> BM
            CSV --> NORM
            BM --> CMD --> NORM --> DEDUP
        end

        subgraph ORQUESTACION["3. Orquestación Dual"]
            PY["Pipeline Nativo Python (Gemini 2.5)"]
            N8N["Flujo Automatizado en n8n"]
            DEDUP --> PY
            DEDUP --> N8N
        end

        subgraph INTELIGENCIA["4. Motor de Inteligencia Artificial"]
            GROQ["Inferencia de Alta Velocidad (Groq)"]
            GEMINI["Modelo de Razonamiento (Gemini 2.5)"]
            CLF["Clasificación Automática de Temas"]
            SNT["Detección de Sentimiento"]
            CPY["Generación de Publicaciones y FAQs"]
            PY --> GROQ
            PY --> GEMINI
            N8N --> GROQ
            GROQ --> CLF
            GEMINI --> SNT
            GEMINI --> CPY
        end

        subgraph PERSISTENCIA["5. Almacenamiento en la Nube"]
            OCI["Oracle Cloud Infrastructure"]
            BUCKET["Contenedor Always Free (activos-marketing)"]
            PAR["Enlaces Seguros Temporales"]
            CPY --> OCI --> BUCKET --> PAR
        end

        subgraph CURADURIA["6. Moderación y Publicación"]
            ST_UI["Panel de Operaciones CommunityLab"]
            REV["Revisión y Edición por Moderadores"]
            PUB["Aprobación y Publicación en Redes"]
            BUCKET --> ST_UI --> REV --> PUB
        end

        classDef cloud fill:#312e81,stroke:#4f46e5,stroke-width:2px,color:#fff;
        classDef ia fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff;
        classDef ui fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff;
        classDef channel fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
        class OCI,BUCKET,PAR cloud;
        class GROQ,GEMINI,CLF,SNT,CPY ia;
        class ST_UI,REV,PUB ui;
        class TG,DC,SL,CSV channel;
    """

    st.markdown(f"```mermaid\n{mermaid_code}\n```")

    st.markdown("<hr style='margin:18px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:12px;'>Detalle de las 4 Etapas del Sistema</div>", unsafe_allow_html=True)

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        with st.container(border=True):
            in_icon = icon_svg("radio", size=18, color="#059669", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:0.95rem; display:flex; align-items:center;'>{in_icon} 1. Captura Omnicanal Continua</div>", unsafe_allow_html=True)
            st.markdown(
                """
                - **Discord:** Conexión Gateway WebSocket en tiempo real.
                - **Slack:** Socket Mode seguro sin necesidad de abrir puertos públicos.
                - **Telegram:** Sondeo asíncrono con reconexión automática tolerante a cortes.
                - **Archivos:** Compatibilidad con lotes JSON estructurados.
                """
            )
        with st.container(border=True):
            ai_icon = icon_svg("cpu", size=18, color="#4F46E5", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:0.95rem; display:flex; align-items:center;'>{ai_icon} 3. Inteligencia Artificial Adaptativa</div>", unsafe_allow_html=True)
            st.markdown(
                """
                - **Groq LLaMA-3:** Respuesta ultrarrápida en menos de 200 ms para clasificación inicial.
                - **Gemini 2.5 Flash:** Redacción de publicaciones enriquecidas para LinkedIn y respuestas técnicas a dudas.
                - **Deduplicación:** Verificación automática para evitar procesar mensajes repetidos.
                """
            )

    with b_col2:
        with st.container(border=True):
            flow_icon2 = icon_svg("workflow", size=18, color="#D97706", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:0.95rem; display:flex; align-items:center;'>{flow_icon2} 2. Orquestación Dual</div>", unsafe_allow_html=True)
            st.markdown(
                """
                - **Pipeline Python:** Código modular con tipado Pydantic estricto y ejecución optimizada.
                - **Flujos en n8n:** Automatización visual mediante webhooks y nodos de transformación.
                - **Respaldo automático:** Si un motor no responde, el sistema conmuta automáticamente.
                """
            )
        with st.container(border=True):
            cloud_icon2 = icon_svg("cloud", size=18, color="#2563EB", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:0.95rem; display:flex; align-items:center;'>{cloud_icon2} 4. Almacenamiento en Oracle Cloud</div>", unsafe_allow_html=True)
            st.markdown(
                """
                - **Contenedor:** `communitylab-activos-marketing` (Región `us-ashburn-1`).
                - **Tier Always Free:** Uso de la capa gratuita permanente de Oracle Cloud.
                - **Enlaces de acceso seguro:** Enlaces con caducidad programada para compartir publicaciones.
                """
            )


def render_live_logs():
    """Visor en tiempo real del archivo rotativo de registro de actividad."""
    render_page_card(
        "Registro de Actividad y Diagnóstico Técnico",
        "Inspecciona eventos, mensajes de información y operaciones con la nube registradas por el sistema.",
        "file-text",
    )

    log_path = get_log_file_path()
    detailed_active = is_detailed_log_enabled()

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Archivo de Registro", log_path.name)
    c_m2.metric("Ubicación en Disco", str(log_path.parent))
    c_m3.metric("Nivel de Detalle", "Detallado (DEBUG)" if detailed_active else "Estándar (INFO)")

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)

    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with col_ctrl1:
        num_lineas = st.selectbox("Líneas a mostrar", [50, 100, 200, 500], index=1)
    with col_ctrl2:
        filtro_nivel = st.selectbox("Nivel de evento", ["TODOS", "INFO", "WARNING", "ERROR", "DEBUG"])
    with col_ctrl3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Actualizar Logs", icon=":material/refresh:", use_container_width=True):
            st.rerun()
    with col_ctrl4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Limpiar Registro", icon=":material/delete_sweep:", use_container_width=True):
            if limpiar_archivo_log():
                st.toast("Registro de actividad vaciado.", icon=":material/check:")
                st.rerun()

    lineas = obtener_ultimas_lineas_log(num_lineas=num_lineas)

    if filtro_nivel != "TODOS":
        lineas = [l for l in lineas if f"[{filtro_nivel}]" in l or f"{filtro_nivel}:" in l or filtro_nivel in l]

    texto_log = "".join(lineas) if lineas else "No hay eventos registrados en este momento."

    st.text_area(
        "Salida del registro",
        value=texto_log,
        height=450,
        disabled=True,
        label_visibility="collapsed",
    )
