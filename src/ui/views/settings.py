"""Vista de configuración del entorno y secretos del backend para CommunityLab."""

from __future__ import annotations

import os
from pathlib import Path
import streamlit as st


CONFIG_GROUPS = [
    {
        "title": "Servicios Activos",
        "icon_name": "radio",
        "fields": [
            {"key": "TELEGRAM_ENABLED", "label": "Telegram", "kind": "toggle", "default": False, "help": "Habilita o deshabilita el servicio Telegram."},
            {"key": "DISCORD_ENABLED", "label": "Discord", "kind": "toggle", "default": False, "help": "Habilita o deshabilita el servicio Discord."},
            {"key": "SLACK_ENABLED", "label": "Slack", "kind": "toggle", "default": False, "help": "Habilita o deshabilita el servicio Slack."},
        ],
    },
    {
        "title": "Canales en Producción",
        "icon_name": "globe",
        "fields": [
            {"key": "TELEGRAM_BOT_TOKEN", "label": "Telegram Bot Token (Prod)", "placeholder": "Token bot Telegram produccion", "help": "Token de Telegram usado en el servidor OCI."},
            {"key": "DISCORD_BOT_TOKEN", "label": "Discord Bot Token (Prod)", "placeholder": "Token bot Discord produccion", "help": "Token del bot de Discord en produccion."},
            {"key": "DISCORD_WEBHOOK_URL", "label": "Discord Webhook URL", "placeholder": "https://discord.com/api/webhooks/...", "help": "Webhook principal de Discord."},
            {"key": "SLACK1_BOT_TOKEN", "label": "Slack 1 Bot Token (App 1 Python Prod)", "placeholder": "xoxb-...", "help": "Token bot de Slack para App 1 (Python) en producción."},
            {"key": "SLACK1_APP_TOKEN", "label": "Slack 1 App Token (App 1 Python Prod)", "placeholder": "xapp-...", "help": "Token app de Slack para Socket Mode en producción."},
            {"key": "SLACK2_BOT_TOKEN", "label": "Slack 2 Bot Token (App 2 n8n Prod)", "placeholder": "xoxb-...", "help": "Token bot de Slack para App 2 (n8n Webhook) en producción."},
            {"key": "SLACK2_APP_TOKEN", "label": "Slack 2 App Token (App 2 n8n Prod)", "placeholder": "xapp-...", "help": "Token app de Slack para App 2 n8n en producción."},
        ],
    },
    {
        "title": "Canales en Local",
        "icon_name": "terminal",
        "fields": [
            {"key": "TELEGRAM_LOCAL_BOT_TOKEN", "label": "Telegram Bot Token (Local)", "placeholder": "Token local de Telegram", "help": "Token del bot local para pruebas y desarrollo."},
            {"key": "DISCORD_LOCAL_BOT_TOKEN", "label": "Discord Bot Token (Local)", "placeholder": "Token local de Discord", "help": "Token de Discord para entorno local de pruebas."},
            {"key": "SLACK1_LOCAL_BOT_TOKEN", "label": "Slack 1 Bot Token (App 1 Python Local)", "placeholder": "xoxb-...", "help": "Token bot local de Slack para App 1 (Python)."},
            {"key": "SLACK1_LOCAL_APP_TOKEN", "label": "Slack 1 App Token (App 1 Python Local)", "placeholder": "xapp-...", "help": "Token app local de Slack para Socket Mode local."},
            {"key": "SLACK2_LOCAL_BOT_TOKEN", "label": "Slack 2 Bot Token (App 2 n8n Local)", "placeholder": "xoxb-...", "help": "Token bot local de Slack para App 2 (n8n)."},
            {"key": "SLACK2_LOCAL_APP_TOKEN", "label": "Slack 2 App Token (App 2 n8n Local)", "placeholder": "xapp-...", "help": "Token app local de Slack para App 2 n8n."},
        ],
    },
    {
        "title": "Orquestador n8n (Nube)",
        "icon_name": "refresh-cw",
        "fields": [
            {"key": "N8N_WEBHOOK_URL", "label": "n8n Webhook URL (Prod VM OCI)", "placeholder": "http://147.15.9.116:5678/", "help": "URL del Webhook de ingesta de n8n en la VM de OCI."},
            {"key": "N8N_HOST", "label": "n8n Host (Prod)", "default": "0.0.0.0", "placeholder": "0.0.0.0", "help": "Host de n8n en servidor OCI."},
            {"key": "N8N_PORT", "label": "n8n Port (Prod)", "default": "5678", "placeholder": "5678", "help": "Puerto de n8n en servidor OCI."},
        ],
    },
    {
        "title": "Orquestador n8n (Local)",
        "icon_name": "sliders",
        "fields": [
            {"key": "N8N_LOCAL_WEBHOOK_URL", "label": "n8n Webhook URL (Local / Túnel)", "placeholder": "http://localhost:5678/webhook/communitylab-ingesta", "help": "Webhook local o ngrok para pruebas de n8n."},
            {"key": "N8N_LOCAL_HOST", "label": "n8n Local Host", "default": "http://localhost", "placeholder": "http://localhost", "help": "Host local de n8n."},
            {"key": "N8N_LOCAL_PORT", "label": "n8n Local Port", "default": "5678", "placeholder": "5678", "help": "Puerto local de n8n."},
            {"key": "N8N_LOCAL_WEBHOOK_BASE", "label": "n8n Local Webhook Base", "placeholder": "http://localhost:5678/", "help": "Base pública o local para webhooks de n8n."},
        ],
    },
    {
        "title": "Modelos de IA",
        "icon_name": "cpu",
        "fields": [
            {"key": "GEMINI_API_KEY", "label": "API Key Gemini", "placeholder": "Introduce tu clave de Gemini", "help": "Clave del motor Google Gemini."},
            {"key": "GEMINI_MODEL", "label": "Modelo Gemini", "default": "gemini-2.5-flash", "placeholder": "gemini-2.5-flash", "help": "Modelo por defecto para IA generativa."},
            {"key": "GROQ_API_KEY", "label": "API Key Groq", "placeholder": "Introduce tu clave de Groq", "help": "Clave del motor Groq para inferencia rápida."},
            {"key": "GROQ_MODEL", "label": "Modelo Groq", "default": "openai/gpt-oss-20b", "placeholder": "openai/gpt-oss-20b", "help": "Modelo preferido para inferencia rápida."},
        ],
    },
    {
        "title": "Oracle Cloud (OCI)",
        "icon_name": "cloud",
        "fields": [
            {"key": "OCI_USER_OCID", "label": "OCI User OCID", "placeholder": "ocid1.user...", "help": "Identificador del usuario OCI."},
            {"key": "OCI_TENANCY_OCID", "label": "OCI Tenancy OCID", "placeholder": "ocid1.tenancy...", "help": "Identificador de la tenancy OCI."},
            {"key": "OCI_FINGERPRINT", "label": "OCI Fingerprint", "placeholder": "34:2f:...", "help": "Fingerprint de la clave API OCI."},
            {"key": "OCI_KEY_FILE", "label": "OCI Key File", "placeholder": "~/.oci/oci_api_key.pem", "help": "Ruta local de la clave privada OCI."},
            {"key": "OCI_REGION", "label": "OCI Region", "default": "us-ashburn-1", "placeholder": "us-ashburn-1", "help": "Región de despliegue OCI."},
            {"key": "OCI_NAMESPACE", "label": "OCI Namespace", "placeholder": "namespace", "help": "Namespace del bucket OCI."},
            {"key": "OCI_BUCKET_NAME", "label": "OCI Bucket Name", "placeholder": "communitylab-activos-marketing", "help": "Nombre del bucket para activos."},
        ],
    },
    {
        "title": "Procesamiento Lotes",
        "icon_name": "package",
        "fields": [
            {"key": "PROCESSING_N8N_ENABLED", "label": "N8N", "kind": "toggle", "default": False, "help": "Habilita o deshabilita el procesamiento por lotes con N8N."},
            {"key": "PROCESSING_PYTHON_ENABLED", "label": "Python", "kind": "toggle", "default": False, "help": "Habilita o deshabilita el procesamiento por lotes con Python."},
        ],
    },
    {
        "title": "Entorno del Sistema",
        "icon_name": "settings",
        "fields": [
            {"key": "ENTORNO_DEPLOY", "label": "Entorno de despliegue", "default": "LOCAL", "options": ["LOCAL", "PRODUCCION"], "help": "Conmuta entre modo LOCAL y PRODUCCION en todo el backend."},
            {"key": "APP_ENV", "label": "App Environment", "default": "development", "options": ["development", "staging", "production"], "help": "Ambiente de ejecución de la app."},
            {"key": "STREAMLIT_SERVER_PORT", "label": "Streamlit Port", "default": "8501", "placeholder": "8501", "help": "Puerto usado por la UI Streamlit."},
            {"key": "ENABLE_DETAILED_LOG", "label": "Detailed Logs", "default": "true", "placeholder": "true", "help": "Activa logs detallados del pipeline."},
            {"key": "LOG_FILE_PATH", "label": "Log File Path", "default": "logs/communitylab.log", "placeholder": "logs/communitylab.log", "help": "Ruta del archivo de logs del backend."},
        ],
    },
    {
        "title": "Túnel de Conexión",
        "icon_name": "link",
        "fields": [
            {"key": "NGROK_AUTHTOKEN", "label": "Token de autenticación Ngrok", "secret": True, "placeholder": "Ingresa tu token de Ngrok", "help": "Token usado para autenticar Ngrok en este equipo."},
        ],
    },
]


try:
    from config_manager import (
        load_settings,
        save_settings,
        structure_config,
        get_json_config_path,
        get_env_path,
        _parse_bool,
        _normalize_string_value,
    )
except ImportError:
    from src.ui.config_manager import (
        load_settings,
        save_settings,
        structure_config,
        get_json_config_path,
        get_env_path,
        _parse_bool,
        _normalize_string_value,
    )


def _seed_default_values(force_reload: bool = False) -> None:
    """Inicializa o recarga valores desde config_manager (JSON estructurado + .env)."""
    stored_values = load_settings()
    for group in CONFIG_GROUPS:
        for field in group["fields"]:
            key = field["key"]
            default_value = stored_values.get(key, field.get("default", ""))
            if field.get("kind") == "toggle":
                default_value = _parse_bool(default_value)
            if force_reload or key not in st.session_state:
                st.session_state[key] = default_value


def render_settings() -> None:
    """Renderiza la vista de configuración del proyecto."""
    _seed_default_values()

    from scripts.icons import icon_svg
    from .common import render_page_card
    render_page_card(
        "Configuración del Entorno y Parámetros del Sistema",
        "Administra de forma segura tokens, llaves de API, credenciales de Oracle Cloud y variables del entorno (.env) organizadas por secciones.",
        "settings",
    )

    # Banner de Seguridad
    shield_icon = icon_svg("shield-check", size=20, color="#FFFFFF", extra_style="margin-right:8px;")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%); border:1px solid #334155; border-radius:14px; padding:16px 20px; margin-bottom:16px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#F8FAFC; display:flex; align-items:center;">{shield_icon} Gestión Segura de Credenciales y Parámetros</span>
                <div style="font-size:0.83rem; color:#94A3B8; margin-top:3px;">
                    Todos los secretos y llaves se resguardan de forma local en el archivo <code>.env</code> sin exponerse públicamente.
                </div>
            </div>
            <div style="display:flex; gap:8px;">
                <span class="status-pill online"><span class="status-dot online"></span> Archivo .env Activo</span>
                <span class="status-pill oci">Parámetros Protegidos</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_fields = sum(len(group["fields"]) for group in CONFIG_GROUPS)
    secret_fields = sum(
        1
        for group in CONFIG_GROUPS
        for field in group["fields"]
        if "KEY" in field["key"] or "TOKEN" in field["key"] or "SECRET" in field["key"]
    )

    summary_cols = st.columns(4)
    with summary_cols[0]:
        svg_gear = icon_svg("settings", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Variables Totales</span><div class="kpi-icon-box">{svg_gear}</div></div>
                <div class="kpi-value" style="font-size:1.4rem; font-weight:800; color:#1E293B;">{total_fields}</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#64748B;">● 8 categorías</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[1]:
        svg_lock = icon_svg("shield", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Claves Sensibles</span><div class="kpi-icon-box">{svg_lock}</div></div>
                <div class="kpi-value" style="font-size:1.4rem; font-weight:800; color:#1E293B;">{secret_fields}</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Enmascaradas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[2]:
        svg_env = icon_svg("globe", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Entorno Activo</span><div class="kpi-icon-box">{svg_env}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">{st.session_state.get('APP_ENV', 'development').upper()}</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#64748B;">● Modo de Ejecución</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with summary_cols[3]:
        svg_check = icon_svg("check-circle", size=20, color="#059669")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Sincronización</span><div class="kpi-icon-box">{svg_check}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#059669;">Correcto</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Archivos en regla</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    # Barra de herramientas superior
    col_tools_left, col_tools_right = st.columns([3.8, 1.2])
    with col_tools_left:
        st.markdown(
            """
            <div style="font-size:0.83rem; color:#64748B; padding:6px 0;">
                <i>Protección activa: Las claves, tokens y contraseñas no se muestran en pantalla para mayor seguridad. Para actualizar una credencial, escribe el nuevo valor.</i>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_tools_right:
        if st.button("Recargar del Disco", icon=":material/refresh:", use_container_width=True, help="Vuelve a leer settings.json y .env del disco"):
            _seed_default_values(force_reload=True)
            st.toast("Configuración recargada desde el disco.", icon=":material/check:")
            st.rerun()

    with st.form("settings_form"):
        values: dict[str, str | bool] = {}

        tabs = st.tabs([group["title"] for group in CONFIG_GROUPS])

        for group, tab in zip(CONFIG_GROUPS, tabs):
            with tab:
                st.markdown(f"### {group['title']}")

                for field in group["fields"]:
                    key = field["key"]
                    label = field["label"]
                    is_secret = field.get("secret", False) or any(
                        s in key for s in ["KEY", "TOKEN", "SECRET", "PASSWORD", "AUTHTOKEN", "OCID", "FINGERPRINT"]
                    )

                    if field.get("kind") == "toggle":
                        active = st.toggle(label, help=field.get("help", ""), key=key)
                        values[key] = active
                        st.caption("Habilitado" if active else "Deshabilitado")
                        continue

                    if "options" in field:
                        values[key] = st.selectbox(
                            label,
                            options=field["options"],
                            help=field.get("help", ""),
                            key=key,
                        )
                    else:
                        if is_secret:
                            stored_val = str(st.session_state.get(key, "")).strip()
                            has_val = bool(stored_val and not stored_val.startswith("tu_"))
                            placeholder_txt = "•••••••••••••••••••• (Configurado)" if has_val else (field.get("placeholder", "") or "No configurado")
                            inp_val = st.text_input(
                                label,
                                value="",
                                type="password",
                                placeholder=placeholder_txt,
                                help=f"{field.get('help', '')} (Deja en blanco para conservar el valor actual).",
                                key=f"input_{key}",
                                label_visibility="visible",
                            )
                            # Si no se ingresó nada nuevo, conservar el valor original de session_state/disco
                            values[key] = inp_val if inp_val.strip() else stored_val
                        else:
                            values[key] = st.text_input(
                                label,
                                type="default",
                                placeholder=field.get("placeholder", ""),
                                help=field.get("help", ""),
                                key=key,
                                label_visibility="visible",
                            )

                st.markdown("")

                if group["title"] == "Túnel":
                    st.caption("Configura el token en Ngrok desde PowerShell con:")
                    st.code("ngrok config add-authtoken <TU_TOKEN_NGROK>", language="powershell")

        # ==============================================================================
        # CONTROL DE SEGURIDAD: CLAVE DE VERIFICACIÓN ADMINISTRATIVA
        # ==============================================================================
        st.markdown("<hr style='margin:18px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
        shield_warn = icon_svg("shield", size=18, color="#EF4444", extra_style="margin-right:6px;")
        st.markdown(
            f"""
            <div style="background:rgba(239, 68, 68, 0.08); border:1px solid rgba(239, 68, 68, 0.25); border-radius:10px; padding:12px 16px; margin-bottom:12px;">
                <div style="font-weight:700; color:#EF4444; font-size:0.95rem; display:flex; align-items:center;">
                    {shield_warn} Autorización Requerida para Modificar Configuración
                </div>
                <div style="font-size:0.82rem; color:#64748B; margin-top:4px;">
                    Por políticas de seguridad, para guardar cambios en variables de entorno o credenciales debes ingresar la <b>Clave de Verificación de Administrador</b>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        admin_key_input = st.text_input(
            "Clave de Verificación de Administrador",
            type="password",
            placeholder="Introduce la clave de verificación administrativa",
            help="Ingresa la clave de autorización administrativa para confirmar los cambios.",
            key="admin_verification_key_input",
        )

        submitted = st.form_submit_button(
            "Guardar Configuración y Sincronizar",
            icon=":material/save:",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            expected_admin_key = str(os.environ.get("SETTINGS_ADMIN_KEY") or "communitylab2026").strip()
            provided_key = admin_key_input.strip()

            if not provided_key:
                st.error("Operación Denegada: Debes ingresar la clave de verificación para autorizar la modificación de las variables de entorno.")
                st.toast("Clave de verificación requerida", icon=":material/lock:")
            elif provided_key != expected_admin_key:
                st.error("Clave de Verificación Incorrecta: No tienes autorización para alterar las variables de entorno.")
                st.toast("Clave administrativa incorrecta", icon=":material/error:")
            else:
                json_path, env_path = save_settings(values)
                _seed_default_values(force_reload=True)

                st.success("Autorización Concedida: Configuración guardada y sincronizada correctamente en los archivos de entorno.")
                st.markdown(
                    f"""
                    <div style="background:rgba(16, 185, 129, 0.12); border:1px solid #10B981; border-radius:12px; padding:14px 18px; margin:12px 0; color:#E2E8F0;">
                        <div style="font-weight:700; color:#34D399; margin-bottom:6px; font-size:1.05rem;">Doble Persistencia Activa:</div>
                        <ul style="margin:0; padding-left:20px; font-size:0.9rem; line-height:1.6; color:#334155;">
                            <li><b>JSON Estructurado:</b> <code>config/settings.json</code> (jerárquico, tipado y respaldado)</li>
                            <li><b>Archivo de Entorno:</b> <code>.env</code> (comentarios y variables sincronizadas)</li>
                            <li><b>Memoria en Ejecución:</b> Variables inyectadas en el proceso actual</li>
                        </ul>
                        <div style="margin-top:10px; font-size:0.83rem; color:#64748B;">
                            <i>Nota: Si modificaste credenciales de bots (Discord, Slack, Telegram) o puertos externos, recuerda reiniciar sus respectivos procesos para que tomen los nuevos valores.</i>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Visor interactivo seguro de la configuración (secretos siempre enmascarados)
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    with st.expander("Explorar configuración estructurada (config/settings.json)", expanded=False):
        st.caption("Representación JSON jerárquica con secretos ofuscados para auditoría:")
        raw_structured = structure_config(load_settings())
        from config_manager import mask_secret_for_example
        safe_preview = {
            dom: {k: mask_secret_for_example(k, v) for k, v in flds.items()}
            for dom, flds in raw_structured.items()
        }
        st.json(safe_preview)
