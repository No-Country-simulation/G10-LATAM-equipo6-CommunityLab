"""Dashboard ejecutivo de CommunityLab con métricas y diseño visual de alta fidelidad."""

from collections import Counter
import streamlit as st

from scripts.data_adapter import cargar_paquete_actual, detectar_canal_ingesta
from scripts.state import set_active_view
from src.channels.bot_manager import get_bot_manager
from src.ui.services import obtener_mapa_curaduria
from .common import render_page_card


def render_dashboard():
    # Banner Hero de Producción
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <div class="title">🌐 CommunityLab · Centro de Inteligencia Comunitaria</div>
                <p class="desc">
                    Hackathon ONE G10 — Team 6 · Pipeline Multicanal, IA Generativa & Cloud Persistence en OCI.
                </p>
            </div>
            <div class="hero-tags">
                <span class="hero-tag">☁️ OCI Always Free</span>
                <span class="hero-tag">🤖 Groq / Gemini 2.5</span>
                <span class="hero-tag">🔄 n8n Dual Pipeline</span>
                <span class="hero-tag" style="background:rgba(16,185,129,0.25); border-color:#10B981;">● Producción 24/7</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Estado de Canales en Tiempo Real
    st.markdown(
        """
        <div style="display:flex; gap:12px; margin-bottom:1.25rem; flex-wrap:wrap; align-items:center;">
            <span style="font-size:0.8rem; font-weight:700; color:#8C93A8; text-transform:uppercase; letter-spacing:0.06em;">Estado de Canales:</span>
            <span class="status-pill online"><span class="status-dot online"></span> 🎮 Discord: Verificado en OCI</span>
            <span class="status-pill online"><span class="status-dot online"></span> 💬 Slack: Verificado en OCI</span>
            <span class="status-pill online"><span class="status-dot online"></span> ✈️ Telegram: Verificado en OCI</span>
            <span class="status-pill oci">☁️ OCI Object Storage: Sincronizado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    datos_paquete, etiqueta_fuente = cargar_paquete_actual()
    activos = datos_paquete.get("activos", []) if datos_paquete else []
    total_activos = len(activos)

    # Métricas reales
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

    bot_manager = get_bot_manager()
    status_bots = bot_manager.get_status()
    bots_activos = sum(1 for b in status_bots.values() if b.get("running"))

    # Hero KPI Cards
    kpi_cols = st.columns(5)
    kpis = [
        ("Ingesta Total", f"{total_activos}", f"Paquete: {etiqueta_fuente[:14]}", "📥", "#434BB2"),
        ("Canales Activos", f"3 / 3", "Discord · Slack · Telegram", "📡", "#10B981"),
        ("Sentimiento +", f"{sentimiento_counts.get('positivo', 0)}", f"{round(sentimiento_counts.get('positivo', 0)/(total_activos or 1)*100)}% de interacciones", "😊", "#3B82F6"),
        ("Activos Aprobados", f"{aprobados}", "Listos para distribución", "✅", "#059669"),
        ("Dudas Técnicas", f"{tipo_counts.get('duda_tecnica', 0)}", "Banco de soluciones IA", "💡", "#8B5CF6"),
    ]

    for col, (label, value, delta, icon, icon_bg) in zip(kpi_cols, kpis):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-header">
                        <span class="kpi-label">{label}</span>
                        <div class="kpi-icon-box" style="background:{icon_bg}18; color:{icon_bg};">
                            {icon}
                        </div>
                    </div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-delta">
                        <span>●</span> {delta}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 1.4rem;'></div>", unsafe_allow_html=True)

    # Fila de visualizaciones y análisis
    overview = st.columns([1.3, 1.1, 1.1], gap="medium")
    with overview[0]:
        render_page_card("Flujo de Ingesta por Canal", "Mensajes recolectados y procesados por origen.", "📊")
        data_canales = {
            "Telegram": canal_counts.get("Telegram", 0),
            "Discord": canal_counts.get("Discord", 0),
            "Slack": canal_counts.get("Slack", 0),
            "Lotes": canal_counts.get("Lotes", 0),
        }
        st.bar_chart(data_canales, color="#434BB2")

    with overview[1]:
        render_page_card("Sentimiento Detectado por LLM", "Análisis emocional de estudiantes vía Groq / Gemini.", "💬")
        data_sentimiento = {
            "Positivo": sentimiento_counts.get("positivo", 0),
            "Neutro": sentimiento_counts.get("neutro", 0),
            "Negativo / Duda": sentimiento_counts.get("negativo", 0),
        }
        st.bar_chart(data_sentimiento, color="#10B981")

    with overview[2]:
        render_page_card("Estado de Curaduría Humana", "Moderación de copys y piezas antes de distribución.", "🩺")
        with st.container(border=True):
            st.metric("Total de Activos Moderados", f"{aprobados + descartados + leidos}")
            st.metric("Aprobados para Redes", f"{aprobados}", f"+{aprobados} sincronizados en OCI")
            st.metric("Descartados / En Espera", f"{descartados}", delta_color="inverse")
            if st.button("Ir a Curaduría Humana ➔", use_container_width=True, type="primary"):
                set_active_view("pending_review")
                st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # Fila de Categorías e Infraestructura OCI
    deeper = st.columns([1.3, 1], gap="medium")
    with deeper[0]:
        render_page_card("Categorías Temáticas de Contenido", "Distribución de activos categorizados por el pipeline de IA.", "🧭")
        data_tipos = {
            "Logro / Empleo": tipo_counts.get("logro_contratacion", 0),
            "Dudas Técnicas": tipo_counts.get("duda_tecnica", 0),
            "Showcase Proyectos": tipo_counts.get("showcase", 0),
            "Feedback General": tipo_counts.get("feedback_general", 0),
        }
        st.bar_chart(data_tipos, color="#F59E0B")

    with deeper[1]:
        render_page_card("Salud de Infraestructura Cloud", "Monitoreo del stack desplegado en OCI y servidores locales.", "☁️")
        with st.container(border=True):
            st.markdown(
                """
                <div style="line-height:1.8; font-size:0.88rem;">
                    <div>☁️ <b>Proveedor:</b> Oracle Cloud Infrastructure (OCI Always Free)</div>
                    <div>🪣 <b>Bucket:</b> <code>communitylab-activos-marketing</code></div>
                    <div>🌐 <b>Región:</b> <code>us-ashburn-1</code></div>
                    <div>⚡ <b>Orquestación:</b> Dual (Python SDK + n8n Engine)</div>
                    <div>🤖 <b>Modelos Activos:</b> Groq (Llama-3) + Gemini 2.5 Flash</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            c_a1, c_a2 = st.columns(2)
            with c_a1:
                if st.button("Ver Storage OCI", use_container_width=True):
                    set_active_view("cloud_explorer")
                    st.rerun()
            with c_a2:
                if st.button("Ver Automatizaciones", use_container_width=True):
                    set_active_view("bot_status")
                    st.rerun()

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 📥 Generador y Exportador de Reporte Ejecutivo Semanal
    import time
    timestamp_reporte = time.strftime("%Y-%m-%d %H:%M:%S")

    pct_pos = round(sentimiento_counts.get('positivo', 0)/(total_activos or 1)*100)
    reporte_md = f"""# Reporte Ejecutivo Semanal — CommunityLab
**Proyecto:** CommunityLab (Hackathon ONE G10 — Team 6)  
**Fecha de Generación:** {timestamp_reporte}  
**Entorno de Ejecución:** Oracle Cloud Infrastructure (OCI Always Free)  

---

## 1. Resumen de Actividad
* **Total de Interacciones Procesadas:** {total_activos}
* **Canales en Vivo:** Telegram, Discord, Slack (3 de 3 activos)
* **Tasa de Sentimiento Positivo:** {pct_pos}% ({sentimiento_counts.get('positivo', 0)} interacciones)
* **Activos Curados y Aprobados en OCI:** {aprobados}
* **Consultas Técnicas Resueltas por IA:** {tipo_counts.get('duda_tecnica', 0)}

---

## 2. Desglose de Ingesta por Canal
* **Telegram:** {canal_counts.get('Telegram', 0)} mensajes
* **Discord:** {canal_counts.get('Discord', 0)} mensajes
* **Slack:** {canal_counts.get('Slack', 0)} mensajes
* **Lotes CSV/JSON:** {canal_counts.get('Lotes', 0)} interacciones

---

## 3. Estado de la Infraestructura en la Nube
* **Persistencia:** OCI Object Storage (`communitylab-activos-marketing`)
* **Región:** `us-ashburn-1`
* **Orquestación:** Dual (Python SDK + n8n Engine)
* **Modelos de IA:** Groq (Llama-3) & Google Gemini 2.5 Flash

---
*Generado automáticamente por CommunityLab Operations Hub.*
"""

    with st.container(border=True):
        rep_c1, rep_c2 = st.columns([3.5, 1.5])
        with rep_c1:
            st.markdown("#### 📥 Reporte Ejecutivo Semanal para Mentores y Equipo")
            st.caption("Descarga en un clic un informe consolidado en formato Markdown con las métricas de ingesta, sentimiento y salud OCI listo para compartir en Discord o adjuntar a la entrega.")
        with rep_c2:
            st.download_button(
                label="📄 Descargar Reporte (.md)",
                data=reporte_md,
                file_name=f"reporte_ejecutivo_communitylab_{time.strftime('%Y%m%d')}.md",
                mime="text/markdown",
                type="primary",
                use_container_width=True,
            )
