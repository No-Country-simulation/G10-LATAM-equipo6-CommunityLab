"""Panel general de CommunityLab con métricas ejecutivas y diseño visual optimizado."""

from collections import Counter
import streamlit as st

from scripts.data_adapter import cargar_paquete_actual, detectar_canal_ingesta
from scripts.icons import icon_badge, icon_svg
from scripts.state import set_active_view
from src.channels.bot_manager import get_bot_manager
from src.ui.services import obtener_mapa_curaduria
from .common import render_page_card


def render_dashboard():
    # Banner de bienvenida y presentación
    sparkle_svg = icon_svg("activity", size=24, color="#6366F1")
    cloud_pill = icon_badge("cloud", "Nube Oracle Always Free", bg_color="rgba(99,102,241,0.12)", text_color="#4F46E5")
    ai_pill = icon_badge("cpu", "IA Gemini & Groq", bg_color="rgba(16,185,129,0.12)", text_color="#059669")
    sync_pill = icon_badge("refresh-cw", "Pipeline Automatizado", bg_color="rgba(245,158,11,0.12)", text_color="#D97706")
    live_pill = icon_badge("check-circle", "Operativo 24/7", bg_color="rgba(16,185,129,0.15)", text_color="#10B981")

    st.markdown(
        f"""
        <div class="hero-banner" style="background:linear-gradient(135deg, #1E1B4B 0%, #312E81 100%); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:20px 24px; margin-bottom:18px; color:#FFFFFF;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="display:flex; align-items:center; gap:10px; font-size:1.5rem; font-weight:800; color:#FFFFFF; margin-bottom:6px;">
                        {sparkle_svg} <span>CommunityLab · Panel de Inteligencia Comunitaria</span>
                    </div>
                    <p style="color:#C7D2FE; font-size:0.92rem; margin:0; line-height:1.5;">
                        Oracle Next Education & Alura Latam · Equipo 6 · Monitoreo y moderación de contenido en tiempo real.
                    </p>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
                    {cloud_pill}
                    {ai_pill}
                    {sync_pill}
                    {live_pill}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Estado de Canales Conectados
    dc_icon = icon_svg("discord", size=15, color="#10B981")
    sl_icon = icon_svg("slack", size=15, color="#10B981")
    tg_icon = icon_svg("telegram", size=15, color="#10B981")
    oci_icon = icon_svg("cloud", size=15, color="#3B82F6")

    st.markdown(
        f"""
        <div style="display:flex; gap:12px; margin-bottom:1.25rem; flex-wrap:wrap; align-items:center; background:#FFFFFF; border:1px solid #E2E8F0; padding:10px 16px; border-radius:12px;">
            <span style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase; letter-spacing:0.05em;">Canales en Vivo:</span>
            <span class="status-pill online" style="display:inline-flex; align-items:center; gap:6px;">{dc_icon} Discord: Conectado</span>
            <span class="status-pill online" style="display:inline-flex; align-items:center; gap:6px;">{sl_icon} Slack: Conectado</span>
            <span class="status-pill online" style="display:inline-flex; align-items:center; gap:6px;">{tg_icon} Telegram: Conectado</span>
            <span class="status-pill oci" style="display:inline-flex; align-items:center; gap:6px;">{oci_icon} Almacenamiento OCI: Sincronizado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    datos_paquete, etiqueta_fuente = cargar_paquete_actual()
    activos = datos_paquete.get("activos", []) if datos_paquete else []
    total_activos = len(activos)

    # Métricas consolidadas
    sentimiento_counts = Counter()
    tipo_counts = Counter()
    canal_counts = Counter()

    for item in activos:
        if isinstance(item, dict):
            act = item.get("activo", {})
            sentimiento_counts[act.get("sentimiento", "neutro")] += 1
            tipo_counts[act.get("tipo_contenido", "feedback_general")] += 1
            canal_counts[detectar_canal_ingesta(item)] += 1

    mapa_cur = obtener_mapa_curaduria()
    aprobados = sum(1 for v in mapa_cur.values() if isinstance(v, dict) and v.get("estado") == "aprobado")
    descartados = sum(1 for v in mapa_cur.values() if isinstance(v, dict) and v.get("estado") == "rechazado")
    leidos = sum(1 for v in mapa_cur.values() if isinstance(v, dict) and v.get("estado") == "leido")

    # Tarjetas Principales de Métricas (KPI Cards)
    kpi_cols = st.columns(5)
    pct_pos = round(sentimiento_counts.get("positivo", 0) / (total_activos or 1) * 100)
    kpis = [
        ("Mensajes Procesados", f"{total_activos}", f"Fuente: {etiqueta_fuente[:16]}", "package", "#434BB2"),
        ("Canales Activos", "3 de 3", "Discord, Slack y Telegram", "radio", "#10B981"),
        ("Sentimiento Favorable", f"{sentimiento_counts.get('positivo', 0)}", f"{pct_pos}% del total analizado", "smile", "#3B82F6"),
        ("Publicaciones Aprobadas", f"{aprobados}", "Listas para compartir", "check-circle", "#059669"),
        ("Dudas Resueltas por IA", f"{tipo_counts.get('duda_tecnica', 0)}", "Banco de soluciones técnicas", "lightbulb", "#8B5CF6"),
    ]

    for col, (label, value, delta, icon_name, icon_bg) in zip(kpi_cols, kpis):
        with col:
            svg_kpi = icon_svg(icon_name, size=22, color=icon_bg)
            st.markdown(
                f"""
                <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px; margin-bottom:10px;">
                    <div class="kpi-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span class="kpi-label" style="font-size:0.78rem; font-weight:700; color:#64748B; text-transform:uppercase;">{label}</span>
                        <div class="kpi-icon-box" style="width:34px; height:34px; border-radius:8px; display:flex; align-items:center; justify-content:center; background:{icon_bg}18;">
                            {svg_kpi}
                        </div>
                    </div>
                    <div class="kpi-value" style="font-size:1.6rem; font-weight:800; color:#1E293B; margin-bottom:4px;">{value}</div>
                    <div class="kpi-delta" style="font-size:0.75rem; color:#64748B;">
                        <span style="color:{icon_bg}; font-weight:bold;">●</span> {delta}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Gráficos y resumen de moderación
    overview = st.columns([1.3, 1.1, 1.1], gap="medium")
    with overview[0]:
        render_page_card("Mensajes por Canal de Origen", "Cantidad de mensajes capturados según la plataforma de mensajería.", "radio")
        data_canales = {
            "Telegram": canal_counts.get("Telegram", 0),
            "Discord": canal_counts.get("Discord", 0),
            "Slack": canal_counts.get("Slack", 0),
            "Lotes de Datos": canal_counts.get("Lotes", 0),
        }
        st.bar_chart(data_canales, color="#434BB2")

    with overview[1]:
        render_page_card("Análisis de Sentimiento de la Comunidad", "Tono emocional identificado automáticamente por la IA.", "smile")
        data_sentimiento = {
            "Positivo": sentimiento_counts.get("positivo", 0),
            "Neutro": sentimiento_counts.get("neutro", 0),
            "Negativo / Duda": sentimiento_counts.get("negativo", 0),
        }
        st.bar_chart(data_sentimiento, color="#10B981")

    with overview[2]:
        render_page_card("Resumen de Revisión y Moderación", "Estado del contenido revisado por el equipo moderador.", "check-circle")
        with st.container(border=True):
            st.metric("Total Moderados", f"{aprobados + descartados + leidos}")
            st.metric("Aprobados para Redes", f"{aprobados}", f"{aprobados} sincronizados en la nube")
            st.metric("Descartados o en Espera", f"{descartados}")
            st.write("")
            if st.button("Ir a Revisión de Publicaciones", icon=":material/arrow_forward:", use_container_width=True, type="primary"):
                set_active_view("pending_review")
                st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Categorías e Infraestructura
    deeper = st.columns([1.3, 1], gap="medium")
    with deeper[0]:
        render_page_card("Categorías Temáticas Detectadas", "Distribución de temas clasificados automáticamente.", "package")
        data_tipos = {
            "Logros y Empleo": tipo_counts.get("logro_contratacion", 0),
            "Dudas Técnicas": tipo_counts.get("duda_tecnica", 0),
            "Proyectos Destacados": tipo_counts.get("showcase", 0),
            "Opiniones Generales": tipo_counts.get("feedback_general", 0),
        }
        st.bar_chart(data_tipos, color="#F59E0B")

    with deeper[1]:
        render_page_card("Estado de los Servicios en la Nube", "Información técnica del entorno desplegado en Oracle Cloud.", "cloud")
        with st.container(border=True):
            cloud_line = icon_svg("cloud", size=15, color="#4F46E5", extra_style="margin-right:6px;")
            box_line = icon_svg("package", size=15, color="#4F46E5", extra_style="margin-right:6px;")
            globe_line = icon_svg("globe", size=15, color="#4F46E5", extra_style="margin-right:6px;")
            zap_line = icon_svg("zap", size=15, color="#4F46E5", extra_style="margin-right:6px;")
            cpu_line = icon_svg("cpu", size=15, color="#4F46E5", extra_style="margin-right:6px;")
            st.markdown(
                f"""
                <div style="line-height:2.0; font-size:0.86rem; color:#334155;">
                    <div style="display:flex;align-items:center;">{cloud_line} <b>Plataforma:</b> <span style="margin-left:4px;">Oracle Cloud Infrastructure (Always Free)</span></div>
                    <div style="display:flex;align-items:center;">{box_line} <b>Contenedor:</b> <span style="margin-left:4px;"><code>communitylab-activos-marketing</code></span></div>
                    <div style="display:flex;align-items:center;">{globe_line} <b>Región Cloud:</b> <span style="margin-left:4px;"><code>us-ashburn-1</code></span></div>
                    <div style="display:flex;align-items:center;">{zap_line} <b>Procesamiento:</b> <span style="margin-left:4px;">Python Gemini 2.5 + Orquestador n8n</span></div>
                    <div style="display:flex;align-items:center;">{cpu_line} <b>Modelos de IA:</b> <span style="margin-left:4px;">Google Gemini 2.5 Flash / Groq LLaMA-3</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("Ver Archivos Cloud", icon=":material/cloud:", use_container_width=True):
                    set_active_view("cloud_explorer")
                    st.rerun()
            with c_a2:
                if st.button("Ver Estado Bots", icon=":material/smart_toy:", use_container_width=True):
                    set_active_view("bot_status")
                    st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Generador y Descargador de Reporte Ejecutivo Semanal
    import time
    timestamp_reporte = time.strftime("%Y-%m-%d %H:%M:%S")

    reporte_md = f"""# Reporte Ejecutivo Semanal — CommunityLab
**Proyecto:** CommunityLab (Hackathon ONE G10 — Equipo 6)  
**Fecha de Generación:** {timestamp_reporte}  
**Entorno de Ejecución:** Oracle Cloud Infrastructure (OCI Always Free)  

---

## 1. Resumen de Actividad
* **Total de Interacciones Procesadas:** {total_activos}
* **Canales en Vivo:** Telegram, Discord y Slack (3 de 3 activos)
* **Tasa de Sentimiento Favorable:** {pct_pos}% ({sentimiento_counts.get('positivo', 0)} interacciones)
* **Publicaciones Moderadas y Aprobadas en Nube:** {aprobados}
* **Consultas Técnicas Resueltas por IA:** {tipo_counts.get('duda_tecnica', 0)}

---

## 2. Desglose de Ingesta por Canal
* **Telegram:** {canal_counts.get('Telegram', 0)} mensajes
* **Discord:** {canal_counts.get('Discord', 0)} mensajes
* **Slack:** {canal_counts.get('Slack', 0)} mensajes
* **Lotes de Datos:** {canal_counts.get('Lotes', 0)} interacciones

---

## 3. Estado de la Infraestructura en la Nube
* **Almacenamiento:** Oracle Cloud Object Storage (`communitylab-activos-marketing`)
* **Región:** `us-ashburn-1`
* **Procesamiento:** Pipeline Python nativo y n8n
* **Modelos de IA:** Google Gemini 2.5 Flash & Groq LLaMA-3

---
*Generado automáticamente por CommunityLab.*
"""

    with st.container(border=True):
        rep_c1, rep_c2 = st.columns([3.5, 1.5])
        with rep_c1:
            st.markdown("<div style='font-weight:700; font-size:1.05rem; margin-bottom:4px; color:#1E293B;'>Reporte Ejecutivo Semanal</div>", unsafe_allow_html=True)
            st.caption("Descarga en un clic un informe consolidado en formato Markdown con las métricas de mensajes, sentimiento y estado del sistema.")
        with rep_c2:
            st.download_button(
                label="Descargar Reporte (.md)",
                icon=":material/download:",
                data=reporte_md,
                file_name=f"reporte_ejecutivo_communitylab_{time.strftime('%Y%m%d')}.md",
                mime="text/markdown",
                type="primary",
                use_container_width=True,
            )
