"""Vista de soporte, información institucional y créditos para CommunityLab."""

from __future__ import annotations

import platform
import sys
import streamlit as st

from src.channels.bot_manager import OmnichannelBotManager
from src.cloud_oci.storage_client import OCIStorageManager
from .common import render_page_card


def render_support():
    """Vista de ayuda, estado del sistema y créditos del proyecto."""
    render_page_card(
        "Centro de Soporte & Documentación de Proyecto",
        "Información institucional, diagnóstico rápido de componentes y créditos del equipo participante en la Hackathon.",
        "❔",
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Versión App", "1.0.0", "Release Hackathon")
    s2.metric("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    s3.metric("Plataforma", platform.system())
    s4.metric("Equipo", "G10-LATAM-06", "No-Country")

    st.markdown("---")

    col_diag, col_faq = st.columns([1.2, 1.8], gap="medium")

    with col_diag:
        with st.container(border=True):
            st.markdown("### 🔍 Diagnóstico de Servicios")
            
            # OCI
            sm = OCIStorageManager()
            if sm.is_configured():
                st.success("☁️ **Oracle Cloud (OCI):** Conectado")
            else:
                st.warning("☁️ **Oracle Cloud (OCI):** Modo Local Fallback")

            # Bots
            bm = OmnichannelBotManager.get_instance()
            if bm.is_running():
                st.success("🤖 **Omnichannel Bots:** Activos")
            else:
                st.info("🤖 **Omnichannel Bots:** En reposo")

            # Streamlit
            st.success("💻 **Streamlit UI:** Operativa")

    with col_faq:
        with st.container(border=True):
            st.markdown("### ❓ Preguntas Frecuentes y Guía de Demostración")
            
            with st.expander("¿Cómo iniciar la ingesta en vivo?", expanded=False):
                st.write(
                    "1. Ve a **Conexiones -> Estado de Bots** o **Ingesta -> Canales Digitales**.\n"
                    "2. Haz clic en **🟢 Iniciar Todos los Bots**.\n"
                    "3. Envía mensajes de prueba desde Telegram (@G10_Latam_06_bot), Discord o Slack.\n"
                    "4. Haz clic en **Procesar Mensajes del Buffer** para ejecutar el pipeline."
                )

            with st.expander("¿Cómo procesar un archivo por lotes?", expanded=False):
                st.write(
                    "1. Ve a **Ingesta -> Procesamiento por Lotes**.\n"
                    "2. Arrastra tu archivo CSV o JSON (ej. `data/interacciones_estudiantes.json`).\n"
                    "3. Selecciona si deseas procesarlo con **Python Nativo** o enviarlo a **n8n**.\n"
                    "4. Revisa los resultados generados en **Curaduría -> Revisión Pendiente**."
                )

            with st.expander("¿Dónde se guardan los datos procesados?", expanded=False):
                st.write(
                    "Los paquetes generados se guardan localmente en la carpeta `data/` y se replican "
                    "automáticamente en el bucket de **Oracle Cloud Infrastructure (OCI) Object Storage** "
                    "con deduplicación por hash MD5."
                )

    st.markdown("---")
    st.caption("CommunityLab · Solución desarrollada para el reto de Hackathon Oracle ONE / Alura Latam por el equipo G10-LATAM-06.")
