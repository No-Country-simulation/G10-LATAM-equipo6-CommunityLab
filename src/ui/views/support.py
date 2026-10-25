"""Vista de soporte, información institucional y centro de ayuda para CommunityLab."""

from __future__ import annotations

import platform
import sys
import streamlit as st

from scripts.icons import icon_svg
from src.channels.bot_manager import OmnichannelBotManager
from src.cloud_oci.storage_client import OCIStorageManager
from .common import render_page_card


def render_support():
    """Vista de ayuda, estado del sistema y créditos del proyecto."""
    render_page_card(
        "Centro de Ayuda y Documentación del Proyecto",
        "Información institucional, diagnóstico en tiempo real de los servicios y guías de uso del sistema.",
        "help-circle",
    )

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Versión de la App", "1.0.0", "Edición Hackathon")
    s2.metric("Motor Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    s3.metric("Sistema Operativo", platform.system())
    s4.metric("Equipo Desarrollador", "G10-LATAM-06", "Oracle ONE")

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)

    col_diag, col_faq = st.columns([1.2, 1.8], gap="medium")

    with col_diag:
        with st.container(border=True):
            diag_icon = icon_svg("activity", size=18, color="#4F46E5", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:1.05rem; color:#1E293B; display:flex; align-items:center;'>{diag_icon} Diagnóstico de Servicios</div>", unsafe_allow_html=True)
            st.write("")
            
            # OCI
            sm = OCIStorageManager()
            if sm.is_configured():
                st.success("Oracle Cloud (OCI): Conectado y operativo")
            else:
                st.info("Oracle Cloud (OCI): Modo de almacenamiento local activo")

            # Bots
            bm = OmnichannelBotManager.get_instance()
            if bm.is_running():
                st.success("Asistentes de Mensajería: Activos en segundo plano")
            else:
                st.info("Asistentes de Mensajería: En reposo (listos para iniciar)")

            # Streamlit
            st.success("Interfaz Visual: Operativa y en línea")

    with col_faq:
        with st.container(border=True):
            faq_icon = icon_svg("help-circle", size=18, color="#4F46E5", extra_style="margin-right:6px;")
            st.markdown(f"<div style='font-weight:700; font-size:1.05rem; color:#1E293B; display:flex; align-items:center;'>{faq_icon} Preguntas Frecuentes y Guía de Uso</div>", unsafe_allow_html=True)
            st.write("")
            
            with st.expander("¿Cómo iniciar la captura de mensajes en vivo?", expanded=False):
                st.write(
                    "1. Dirígete a **Conexiones y Bots -> Estado de Bots** o **Captura de Mensajes -> Mensajes en Vivo**.\n"
                    "2. Haz clic en **Iniciar Asistentes**.\n"
                    "3. Envía mensajes desde Telegram (@G10_Latam_06_bot), Discord o Slack.\n"
                    "4. También puedes usar el **Simulador de Mensajes** para probarlo con un solo clic."
                )

            with st.expander("¿Cómo procesar un archivo con mensajes acumulados?", expanded=False):
                st.write(
                    "1. Ingresa a **Captura de Mensajes -> Procesar Archivos**.\n"
                    "2. Carga un archivo JSON o utiliza el archivo de prueba predeterminado.\n"
                    "3. Selecciona si deseas procesarlo con **Pipeline Python Nativo** o mediante **Orquestador n8n**.\n"
                    "4. Revisa las publicaciones generadas en **Revisión de Contenido -> Pendientes de Revisión**."
                )

            with st.expander("¿Dónde se guardan las publicaciones y datos?", expanded=False):
                st.write(
                    "Todos los paquetes procesados se sincronizan en **Oracle Cloud Infrastructure Object Storage** "
                    "(cubeta `communitylab-activos-marketing`), con respaldo local en la carpeta `data/` "
                    "y control automático de duplicados."
                )

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
    st.caption("CommunityLab · Plataforma desarrollada para la Hackathon Oracle Next Education (ONE) y Alura Latam por el Equipo 6.")
