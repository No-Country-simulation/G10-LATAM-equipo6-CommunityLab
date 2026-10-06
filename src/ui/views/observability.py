"""Vistas de arquitectura, flujo de datos y observabilidad en tiempo real."""

from __future__ import annotations

import streamlit as st

from src.utils.logger import get_log_file_path, is_detailed_log_enabled, limpiar_archivo_log, obtener_ultimas_lineas_log
from .common import render_page_card


def render_flow_diagram():
    """Diagrama interactivo de arquitectura del backend pipeline de CommunityLab."""
    render_page_card(
        "Arquitectura de Referencia y Diagrama de Flujo del Pipeline",
        "Traza visual de extremo a extremo: desde la ingesta multicanal (Telegram, Discord, Slack, Lotes) hasta el almacenamiento seguro en OCI y la curaduría humana.",
        "🗺️",
    )

    # Banner de Arquitectura
    st.markdown(
        """
        <div style="background:linear-gradient(135deg,#1E293B,#0F172A); border:1px solid #334155; border-radius:14px; padding:14px 18px; margin-bottom:14px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#F8FAFC;">🗺️ Blueprint Arquitectónico Oficial · CommunityLab E2E</span>
                <div style="font-size:0.83rem; color:#94A3B8; margin-top:3px;">
                    Flujo de datos de 6 capas: Ingesta ➔ Buffer ➔ Orquestación Dual ➔ IA Generativa ➔ OCI Storage ➔ Curaduría.
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="status-pill online"><span class="status-dot online"></span> 6 Capas Activas</span>
                <span class="status-pill oci">OCI Cloud Native</span>
                <span class="status-pill online">Pipeline Dual</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🔄 Diagrama de Flujo End-to-End")
    
    mermaid_code = """
    graph TD
        subgraph INGESTA["1. Ingesta Omnicanal (Producción OCI)"]
            TG["✈️ Telegram Bot (@G10_Latam_06_bot)"]
            DC["🎮 Discord Bot (#general-g10 Team 6)"]
            SL["💬 Slack Bot (@G10-LATAM-06 Socket Mode)"]
            CSV["📄 Lotes CSV / JSON (Alura & ONE)"]
        end

        subgraph DISPATCHER["2. Buffer & Normalización"]
            BM["🤖 OmnichannelBotManager (Daemon)"]
            CMD["⚡ ChannelMessageDispatcher"]
            NORM["📦 Modelo Canónico de Interacción"]
            DEDUP["🛡️ Deduplicación por Hash MD5"]
            TG --> BM
            DC --> BM
            SL --> BM
            CSV --> NORM
            BM --> CMD --> NORM --> DEDUP
        end

        subgraph ORQUESTACION["3. Orquestador Dual Resiliente"]
            PY["🐍 Pipeline Python Nativo (src/pipeline)"]
            N8N["🔄 Flujo n8n (Docker / Local / OCI)"]
            DEDUP --> PY
            DEDUP --> N8N
        end

        subgraph INTELIGENCIA["4. Motor de IA Generativa"]
            GROQ["⚡ Groq LLM (Inferencia Ultra-rápida)"]
            GEMINI["✨ Google Gemini 2.5 Flash"]
            CLF["🏷️ Clasificación Temática (4 tipos)"]
            SNT["🎭 Análisis de Sentimiento Emocional"]
            CPY["✍️ Generación de Copys Multired & FAQs"]
            PY --> GROQ
            PY --> GEMINI
            N8N --> GROQ
            GROQ --> CLF
            GEMINI --> SNT
            GEMINI --> CPY
        end

        subgraph PERSISTENCIA["5. Nube & Almacenamiento Seguro"]
            OCI["☁️ Oracle Cloud Infrastructure (OCI)"]
            BUCKET["🪣 Bucket Always Free (communitylab-activos-marketing)"]
            PAR["🔗 Enlaces Pre-Autenticados (PAR)"]
            CPY --> OCI --> BUCKET --> PAR
        end

        subgraph CURADURIA["6. Curaduría Humana & Distribución"]
            ST_UI["💻 Streamlit Operations Hub"]
            REV["👁️ Revisión Humana Tri-Panel"]
            PUB["🚀 Aprobación & Distribución Multicanal"]
            BUCKET --> ST_UI --> REV --> PUB
        end

        classDef cloud fill:#c2410c,stroke:#ea580c,stroke-width:2px,color:#fff;
        classDef ia fill:#4338ca,stroke:#4f46e5,stroke-width:2px,color:#fff;
        classDef ui fill:#0369a1,stroke:#0284c7,stroke-width:2px,color:#fff;
        classDef channel fill:#15803d,stroke:#16a34a,stroke-width:2px,color:#fff;
        class OCI,BUCKET,PAR cloud;
        class GROQ,GEMINI,CLF,SNT,CPY ia;
        class ST_UI,REV,PUB ui;
        class TG,DC,SL,CSV channel;
    """

    st.markdown(f"```mermaid\n{mermaid_code}\n```")

    st.markdown("---")
    st.subheader("Desglose Técnico de las 4 Fases Clave")

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        with st.container(border=True):
            st.markdown("#### 📡 1. Ingesta Omnicanal 24/7")
            st.markdown(
                """
                - **Discord:** Gateway WebSocket nativo escuchando `#general-g10`.
                - **Slack:** Socket Mode con `slack-bolt` bidireccional sin necesidad de IP pública estática.
                - **Telegram:** Long Polling resiliente con reconexión automática.
                - **Lotes:** Soporte de archivos JSON/CSV representativos de retos pasados.
                """
            )
        with st.container(border=True):
            st.markdown("#### 🧠 3. Inferencia de IA Híbrida")
            st.markdown(
                """
                - **Groq (Llama-3):** Inferencia ultrarrápida en menos de 200 ms para respuesta en tiempo real.
                - **Gemini 2.5 Flash:** Razonamiento complejo, análisis de sentimiento y generación de copys adaptados a LinkedIn, Twitter y FAQs.
                - **Deduplicación:** Hash MD5 sobre cuerpo del mensaje para evitar procesar duplicados.
                """
            )

    with b_col2:
        with st.container(border=True):
            st.markdown("#### 🔄 2. Orquestador Dual")
            st.markdown(
                """
                - **Pipeline Python:** Código modular con servicios asíncronos y tipado estricto.
                - **Flujo n8n:** Motor visual con webhooks, nodos de transformación y logs visuales.
                - **Failover:** Si un motor experimenta problemas, el otro asume el flujo de trabajo sin pérdida de datos.
                """
            )
        with st.container(border=True):
            st.markdown("#### ☁️ 4. Persistencia en Oracle Cloud (OCI)")
            st.markdown(
                """
                - **Bucket:** `communitylab-activos-marketing` (Región `us-ashburn-1`).
                - **Costo Cero:** Tier *Always Free* de Oracle Cloud de hasta 10 GB y 50,000 requests/mes.
                - **Enlaces PAR:** Generación de Pre-Authenticated Requests con caducidad programada para compartir activos sin exponer llaves privadas.
                """
            )


def render_live_logs():
    """Visor en tiempo real del archivo rotativo diario de logs."""
    render_page_card(
        "Visor de Trazas y Logs de Aplicación",
        "Inspecciona eventos, advertencias, llamadas a Gemini y operaciones OCI registradas por el backend.",
        "📜",
    )

    log_path = get_log_file_path()
    detailed_active = is_detailed_log_enabled()

    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Archivo de Log Activo", log_path.name)
    c_m2.metric("Ruta Física", str(log_path.parent))
    c_m3.metric("Nivel Detallado", "DEBUG" if detailed_active else "INFO")

    st.markdown("---")

    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with col_ctrl1:
        num_lineas = st.selectbox("Líneas a mostrar", [50, 100, 200, 500], index=1)
    with col_ctrl2:
        filtro_nivel = st.selectbox("Filtrar nivel", ["TODOS", "INFO", "WARNING", "ERROR", "DEBUG"])
    with col_ctrl3:
        if st.button("🔄 Refrescar Logs", use_container_width=True):
            st.rerun()
    with col_ctrl4:
        if st.button("🧹 Limpiar Log Actual", use_container_width=True):
            if limpiar_archivo_log():
                st.toast("Archivo de log vaciado.", icon="🧹")
                st.rerun()

    lineas = obtener_ultimas_lineas_log(num_lineas=num_lineas)

    if filtro_nivel != "TODOS":
        lineas = [l for l in lineas if f"[{filtro_nivel}]" in l or f"{filtro_nivel}:" in l or filtro_nivel in l]

    texto_log = "".join(lineas) if lineas else "No hay eventos en el archivo de log."

    st.text_area(
        "Salida de Consola / Log",
        value=texto_log,
        height=450,
        disabled=True,
        label_visibility="collapsed",
    )
