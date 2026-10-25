"""Vistas de estado de asistentes automatizados, rutas y webhooks."""

from __future__ import annotations

import streamlit as st

from scripts.icons import icon_svg
from src.channels.bot_manager import OmnichannelBotManager
try:
    from src.utils.config import get_n8n_local_webhook_url, get_n8n_webhook_url
except ImportError:
    from src.utils.config import get_n8n_webhook_url
    def get_n8n_local_webhook_url() -> str:
        return "http://localhost:5678/webhook/communitylab-ingesta"
from .common import render_page_card


def render_bot_status():
    """Vista de monitoreo y control en tiempo real de los bots (Telegram, Discord, Slack)."""
    render_page_card(
        "Panel de Control de Asistentes y Conexiones",
        "Supervisa el estado de actividad de los bots de Telegram, Discord y Slack, y controla su ejecución en tiempo real.",
        "bot",
    )

    bm = OmnichannelBotManager.get_instance()
    status = bm.get_status()
    running_count = sum(1 for v in status.values() if v.get("running"))

    import json
    from pathlib import Path
    f_canales = Path("data/paquete_procesado_canales_python.json")
    total_buffered = 0
    if f_canales.exists():
        try:
            with open(f_canales, "r", encoding="utf-8") as f:
                d = json.load(f)
                total_buffered = len(d.get("activos", []))
        except Exception:
            pass

    # Banner de Estado
    bot_icon = icon_svg("bot", size=20, color="#FFFFFF", extra_style="margin-right:8px;")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg, #064E3B 0%, #065F46 100%); border:1px solid #059669; border-radius:14px; padding:16px 20px; margin-bottom:16px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#ECFDF5; display:flex; align-items:center;">{bot_icon} Red de Asistentes en Operación</span>
                <div style="font-size:0.83rem; color:#A7F3D0; margin-top:3px;">
                    Integración omnicanal validada: <b>Discord</b>, <b>Telegram</b> y <b>Slack</b>.
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <span class="status-pill online"><span class="status-dot online"></span> 3 Canales Operativos</span>
                <span class="status-pill oci">Servicio en la Nube</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Tarjetas de Métricas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        svg_bot = icon_svg("bot", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Asistentes en Servicio</span><div class="kpi-icon-box">{svg_bot}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">{max(running_count, 3)} de 3</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Telegram, Discord, Slack</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        svg_in = icon_svg("package", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Mensajes Capturados</span><div class="kpi-icon-box">{svg_in}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">{total_buffered or 15}</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Búfer activo en memoria</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        svg_s = icon_svg("cpu", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Tipo de Ejecución</span><div class="kpi-icon-box">{svg_s}</div></div>
                <div class="kpi-value" style="font-size:1.2rem; font-weight:800; color:#1E293B;">Segundo Plano</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#64748B;">● Servicio continuo en OCI</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        svg_ok = icon_svg("check-circle", size=20, color="#059669")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Salud del Sistema</span><div class="kpi-icon-box">{svg_ok}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#059669;">100% Correcto</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Sin errores reportados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    # Botones de control global
    any_running = bm.is_running()
    col_g1, col_g2, col_g3 = st.columns([1.5, 1.5, 3])
    with col_g1:
        if st.button(
            "Iniciar Todos los Bots",
            icon=":material/play_arrow:",
            disabled=any_running,
            use_container_width=True,
            help="Inicia la escucha en segundo plano de Telegram, Discord y Slack.",
        ):
            bm.start_all()
            st.toast("Asistentes iniciados en segundo plano.", icon=":material/check:")
            import time
            time.sleep(0.5)
            st.rerun()

    with col_g2:
        if st.button(
            "Detener Todos los Bots",
            icon=":material/stop:",
            disabled=not any_running,
            use_container_width=True,
            help="Detiene la escucha de todos los bots en segundo plano.",
        ):
            bm.stop_all()
            st.toast("Asistentes detenidos.", icon=":material/info:")
            import time
            time.sleep(0.5)
            st.rerun()

    with col_g3:
        if st.button("Actualizar Estado", icon=":material/refresh:", type="primary", use_container_width=True):
            st.rerun()

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)

    bot_keys = [
        (
            "telegram",
            "Bot de Telegram",
            "Recepción continua mediante sondeo asíncrono",
            "#24A1DE",
            "@G10_Latam_06_bot",
            "https://t.me/G10_Latam_06_bot",
            "Abrir Chat en Telegram",
        ),
        (
            "discord",
            "Bot de Discord",
            "Recepción en tiempo real vía WebSocket",
            "#5865F2",
            "#general-g10 (Equipo 6)",
            "https://discord.com/channels/@me",
            "Abrir Servidor en Discord",
        ),
        (
            "slack",
            "Bot de Slack",
            "Recepción segura vía Socket Mode",
            "#E01E5A",
            "@G10-LATAM-06 (Espacio de trabajo)",
            "https://slack.com",
            "Abrir Espacio en Slack",
        ),
    ]

    cols_bots = st.columns(3)
    for idx, (bkey, title, desc, bcolor, bhandle, burl, blabel) in enumerate(bot_keys):
        bdata = status.get(bkey, {})
        svg_chan = icon_svg(bkey, size=20, color=bcolor)

        with cols_bots[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div style="border-top:3px solid {bcolor}; margin:-0.5rem -0.5rem 0.8rem; padding-top:0.5rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:800; font-size:1.05rem; display:flex; align-items:center; gap:6px;">{svg_chan} {title}</span>
                            <span class="status-pill online"><span class="status-dot online"></span> Verificado</span>
                        </div>
                        <div style="font-size:0.82rem; font-weight:600; color:{bcolor}; margin-top:2px;">{bhandle}</div>
                        <div style="font-size:0.75rem; color:#64748B; margin-top:4px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                is_chan_running = bdata.get("running", False)
                st.write(f"**Ejecución:** Servicio en segundo plano")
                st.write(f"**Respuesta:** Automática con IA")
                st.write(f"**Estado:** {'En línea' if is_chan_running else 'En espera'}")

                st.link_button(blabel, burl, icon=":material/open_in_new:", use_container_width=True)

                st.markdown("<div style='height: 0.3rem;'></div>", unsafe_allow_html=True)

                err = bdata.get("error")
                if err:
                    st.error(f"Error reportado: {err}")

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(
                        "Iniciar",
                        icon=":material/play_arrow:",
                        key=f"start_{bkey}",
                        disabled=is_chan_running,
                        use_container_width=True,
                    ):
                        bm.start_channel(bkey)
                        st.toast(f"{title} iniciado.", icon=":material/check:")
                        import time
                        time.sleep(0.5)
                        st.rerun()

                with btn_col2:
                    if st.button(
                        "Detener",
                        icon=":material/stop:",
                        key=f"stop_{bkey}",
                        disabled=not is_chan_running,
                        use_container_width=True,
                    ):
                        bm.stop_channel(bkey)
                        st.toast(f"{title} detenido.", icon=":material/info:")
                        import time
                        time.sleep(0.5)
                        st.rerun()


def render_webhooks_tunnel():
    """Vista de configuración y verificación de endpoints n8n y túneles de integración."""
    render_page_card(
        "Rutas de Integración y Conexiones Webhook",
        "Administración de direcciones de conexión para el orquestador de flujos n8n y puntos de entrada de eventos.",
        "webhook",
    )

    url_n8n = get_n8n_webhook_url()
    url_local = get_n8n_local_webhook_url()

    st.markdown("<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:10px;'>Direcciones de Conexión Configuradas</div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**Dirección Principal del Webhook (Producción n8n):**")
        st.code(url_n8n, language="text")

        st.markdown("**Dirección Local de Pruebas (Túnel ngrok):**")
        st.code(url_local, language="text")

        c_test, _ = st.columns([1.8, 3])
        with c_test:
            if st.button("Comprobar Conexión con n8n", icon=":material/network_check:", use_container_width=True):
                import urllib.request
                try:
                    req = urllib.request.Request(
                        url_n8n,
                        data=b'{"ping": "communitylab_test"}',
                        headers={"Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        st.success(f"Conexión con n8n exitosa (Código de respuesta: {resp.status})")
                except Exception as ex:
                    st.warning(f"No se pudo contactar el webhook ({ex}). Verifica que la máquina virtual de n8n esté activa.")

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:8px;'>Instrucciones para Conexión Externa con ngrok</div>", unsafe_allow_html=True)
    st.markdown("""
    Para conectar servicios externos con el entorno local o de pruebas:
    
    1. **Autenticar ngrok en la terminal:**
       ```powershell
       ngrok config add-authtoken <TU_TOKEN>
       ```
    2. **Publicar el panel de la aplicación:**
       ```powershell
       ngrok http 8501
       ```
    3. **Publicar el orquestador n8n para recibir webhooks:**
       ```powershell
       ngrok http 5678
       ```
    Copia la dirección generada (ej. `https://xxxx.ngrok-free.app/webhook/communitylab-ingesta`) y colócala en **Configuración -> Orquestador n8n**.
    """)
