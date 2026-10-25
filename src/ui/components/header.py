"""Barra superior con título, búsqueda global, alternador de tema y pasos de proceso."""
import streamlit as st

from scripts.icons import icon_svg
from scripts.state import get_active_view, toggle_theme
from scripts.utils import H


def render():
    view = get_active_view()
    titles = {
        "dashboard": ("dashboard", "Resumen General de la Comunidad", "Métricas principales de interacción, sentimiento y salud general de la comunidad."),
        "live_channels": ("activity", "Mensajes Capturados en Vivo", "Recepción y actividad en tiempo real desde Telegram, Discord y Slack."),
        "batch_processing": ("package", "Procesamiento de Archivos", "Transformación automática de lotes de mensajes con Inteligencia Artificial."),
        "pending_review": ("clipboard-check", "Revisión y Aprobación de Publicaciones", "Modera, edita y aprueba el contenido generado antes de compartirlo en redes."),
        "approved_assets": ("circle-check", "Publicaciones Aprobadas", "Historial de publicaciones y respuestas listas para ser distribuidas."),
        "faqs": ("lightbulb", "Preguntas Frecuentes y Ayuda Técnica", "Soluciones generadas automáticamente a partir de dudas recurrentes de estudiantes."),
        "cloud_explorer": ("cloud", "Archivos en la Nube", "Explorador de datos y copias de seguridad en Oracle Cloud Infrastructure."),
        "par_links": ("link", "Enlaces Compartidos", "Historial de enlaces seguros de acceso temporal a los paquetes generados."),
        "bot_status": ("bot", "Estado de los Asistentes", "Verificación operativa y conectividad de los bots de Telegram, Discord y Slack."),
        "webhooks_tunnel": ("webhook", "Rutas de Integración y Webhooks", "Direcciones de conexión y servicios de distribución de datos."),
        "flow_diagram": ("git-branch", "Flujo de Procesamiento", "Diagrama del recorrido que siguen los mensajes a través de los motores de IA."),
        "live_logs": ("file-text", "Registro de Actividad del Sistema", "Historial de eventos y diagnósticos técnicos en tiempo real."),
        "settings": ("settings", "Configuración del Sistema", "Parámetros de conexión, llaves de API y opciones generales."),
        "support": ("help-circle", "Centro de Ayuda y Documentación", "Guías de uso, soporte técnico e información del proyecto."),
        # Alias en español
        "fuentes-activas": ("activity", "Mensajes Capturados en Vivo", "Recepción y actividad en tiempo real desde Telegram, Discord y Slack."),
        "pendientes-revision": ("clipboard-check", "Revisión y Aprobación de Publicaciones", "Modera, edita y aprueba el contenido generado antes de compartirlo en redes."),
        "almacenamiento-oci": ("cloud", "Archivos en la Nube", "Explorador de datos y copias de seguridad en Oracle Cloud Infrastructure."),
        "estado-automatizaciones": ("bot", "Estado de los Asistentes", "Verificación operativa y conectividad de los bots de Telegram, Discord y Slack."),
        "flujo-pipeline": ("git-branch", "Flujo de Procesamiento", "Diagrama del recorrido que siguen los mensajes a través de los motores de IA."),
        "configuracion": ("settings", "Configuración del Sistema", "Parámetros de conexión, llaves de API y opciones generales."),
    }

    icon_name, title, subtitle = titles.get(view, ("dashboard", "Panel de Control", "Vista general del sistema."))

    top_l, top_pulse, top_r = st.columns([3.2, 2.3, 1.3])
    with top_l:
        st.text_input(
            "buscar",
            placeholder="Buscar publicaciones, mensajes o canales…",
            label_visibility="collapsed",
            key="global_search",
        )
    with top_pulse:
        cpu_icon = icon_svg("cpu", size=13, color="#10B981")
        cloud_icon = icon_svg("cloud", size=13, color="#3B82F6")
        bot_icon = icon_svg("bot", size=13, color="#8B5CF6")
        H(f"""
        <div class="latency-bar">
            <span class="latency-pill" title="Tiempo de respuesta del motor de IA">{cpu_icon} <b>IA:</b> 138 ms</span>
            <span>•</span>
            <span class="latency-pill" title="Latencia con Oracle Cloud">{cloud_icon} <b>Nube:</b> 82 ms</span>
            <span>•</span>
            <span class="latency-pill" title="Bots conectados">{bot_icon} <b>Bots:</b> 3/3 Activos</span>
        </div>
        """)
    with top_r:
        is_dark = st.session_state.get("dark_mode", False)
        theme_label = "Modo Claro" if is_dark else "Modo Oscuro"
        theme_icon = ":material/light_mode:" if is_dark else ":material/dark_mode:"
        if st.button(theme_label, icon=theme_icon, key="theme_toggle", use_container_width=True):
            toggle_theme()
            st.rerun()

    svg_title_icon = icon_svg(icon_name, size=28, color="#6366F1", extra_style="margin-right: 8px;")
    H(f"""
    <div style="margin-top: 6px; margin-bottom: 14px;">
        <div class="title" style="display:flex; align-items:center; gap:8px;">
            {svg_title_icon}
            <span>{title}</span>
        </div>
        <div class="subtitle">{subtitle}</div>
    </div>
    """)

    if view == "pending_review":
        check_icon = icon_svg("check", size=14, color="#FFFFFF")
        H(f"""
        <div class="stepper" key="cur_stepper">
          <div class="step done"><i style="display:flex;align-items:center;justify-content:center;">{check_icon}</i> Ingesta</div><div class="line"></div>
          <div class="step done"><i style="display:flex;align-items:center;justify-content:center;">{check_icon}</i> Análisis de IA</div><div class="line"></div>
          <div class="step on"><i style="display:flex;align-items:center;justify-content:center;font-weight:700;">3</i> Revisión y Moderación</div><div class="line"></div>
          <div class="step"><i style="display:flex;align-items:center;justify-content:center;">4</i> Publicación y Guardado</div>
        </div>
        """)
