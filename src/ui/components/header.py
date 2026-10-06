"""Barra superior con título, búsqueda global, alternador de tema y stepper."""
import streamlit as st

from scripts.state import get_active_view, toggle_theme
from scripts.utils import H


def render():
    view = get_active_view()
    titles = {
        "dashboard": ("📊 Dashboard de la comunidad", "Panorama de interacciones, sentimiento y salud general de la comunidad."),
        "live_channels": ("📡 Fuentes activas", "Recepción y actividad en tiempo real de Telegram, Discord y Slack."),
        "batch_processing": ("📦 Procesamiento por lotes", "Ejecución del pipeline E2E dual (Python Gemini 2.5 y n8n)."),
        "pending_review": ("📋 Pendientes de revisión", "Curaduría humana: edita, clasifica y aprueba los activos generados."),
        "approved_assets": ("🟢 Historias y aprobados", "Casos, testimonios y activos aprobados listos para distribuir."),
        "faqs": ("💡 FAQ & dudas técnicas", "Respuestas técnicas generadas por IA a partir de dudas de estudiantes."),
        "cloud_explorer": ("📁 Almacenamiento OCI", "Explorador de objetos persistidos en Oracle Cloud Infrastructure Always Free."),
        "par_links": ("🔗 Activos generados", "Historial de distribución y generación de URLs PAR temporales de 24 horas."),
        "bot_status": ("🤖 Estado de automatizaciones", "Conectividad y estado de salud de bots en segundo plano."),
        "webhooks_tunnel": ("🌐 Webhooks & distribución", "Endpoints n8n, túnel ngrok y conectividad del pipeline."),
        "flow_diagram": ("🗺️ Flujo del pipeline", "Diagrama de arquitectura dual de transformación de interacciones."),
        "live_logs": ("📜 Logs y eventos", "Visor en vivo de eventos del backend en logs/communitylab.log."),
        "settings": ("🔐 Settings / Configuración", "Credenciales de servicios, variables .env y parámetros del sistema."),
        "support": ("❔ Soporte", "Documentación, stack tecnológico y asistencia del equipo."),
        # Alias en español
        "fuentes-activas": ("📡 Fuentes activas", "Recepción y actividad en tiempo real de Telegram, Discord y Slack."),
        "pendientes-revision": ("📋 Pendientes de revisión", "Curaduría humana: edita, clasifica y aprueba los activos generados."),
        "almacenamiento-oci": ("📁 Almacenamiento OCI", "Explorador de objetos persistidos en Oracle Cloud Infrastructure Always Free."),
        "estado-automatizaciones": ("🤖 Estado de automatizaciones", "Conectividad y estado de salud de bots en segundo plano."),
        "flujo-pipeline": ("🗺️ Flujo del pipeline", "Diagrama de arquitectura dual de transformación de interacciones."),
        "configuracion": ("🔐 Settings / Configuración", "Credenciales de servicios, variables .env y parámetros del sistema."),
    }

    title, subtitle = titles.get(view, titles["dashboard"])

    top_l, top_pulse, top_r = st.columns([3.2, 2.2, 1.2])
    with top_l:
        st.text_input(
            "buscar",
            placeholder="🔍 Buscar interacciones, activos o canales…",
            label_visibility="collapsed",
            key="global_search",
        )
    with top_pulse:
        H("""
        <div class="latency-bar">
            <span class="latency-pill"><span class="live-pulse"></span> <b>Groq:</b> 138ms</span>
            <span>•</span>
            <span class="latency-pill"><b>OCI:</b> 82ms</span>
            <span>•</span>
            <span class="latency-pill"><b>Bots:</b> 3/3 OK</span>
        </div>
        """)
    with top_r:
        theme_label = "☀️ Claro" if st.session_state.dark_mode else "🌙 Oscuro"
        if st.button(theme_label, key="theme_toggle", use_container_width=True):
            toggle_theme()
            st.rerun()

    H(f'<div class="title">{title}</div>')
    H(f'<div class="subtitle">{subtitle}</div>')

    if view == "pending_review":
        H("""
        <div class="stepper">
          <div class="step done"><i>✓</i> Ingesta</div><div class="line"></div>
          <div class="step done"><i>✓</i> Análisis IA</div><div class="line"></div>
          <div class="step on"><i>3</i> Curaduría Humana</div><div class="line"></div>
          <div class="step"><i>4</i> Distribución OCI</div>
        </div>
        """)
