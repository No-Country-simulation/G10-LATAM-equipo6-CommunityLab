"""Vistas de administración y consulta de almacenamiento en Oracle Cloud Infrastructure."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
import streamlit as st

from scripts.icons import icon_svg
from src.cloud_oci.storage_client import OCIStorageManager
from src.ui.services import cargar_paquete, invalidar_cache_datos, obtener_ultimos_paquetes, vaciar_historico_oci
from .common import render_page_card


def render_cloud_explorer():
    """Explorador de paquetes y archivos persistidos en Oracle Cloud Infrastructure Object Storage."""
    render_page_card(
        "Almacenamiento en la Nube (Oracle Cloud Infrastructure)",
        "Visualiza, descarga y administra los paquetes de publicaciones y datos guardados de forma segura en la nube.",
        "cloud",
    )

    sm = OCIStorageManager()
    oci_active = sm.is_configured()
    paquetes = obtener_ultimos_paquetes(limite=30)
    total_bytes = sum(int(p.get("size") or 0) for p in paquetes)
    total_kb = round(total_bytes / 1024, 2)

    # Banner Oficial OCI
    cloud_icon = icon_svg("cloud", size=20, color="#FFFFFF", extra_style="margin-right:8px;")
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#312E81 0%,#1E1B4B 100%); border:1px solid #4338CA; border-radius:14px; padding:16px 20px; margin-bottom:16px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#F8FAFC; display:flex; align-items:center;">{cloud_icon} Contenedor Cloud en Producción</span>
                <div style="font-size:0.83rem; color:#C7D2FE; margin-top:3px;">
                    Instancia oficial de la comunidad · Contenedor: <code>{sm.bucket_name or 'communitylab-activos-marketing'}</code>
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="status-pill oci">Oracle Always Free</span>
                <span class="status-pill {'online' if oci_active else 'standby'}">
                    {'Conectado a la Nube' if oci_active else 'Almacenamiento Local'}
                </span>
                <span class="status-pill online">Región: {sm.region or 'us-ashburn-1'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Tarjetas de Estado
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        svg_c = icon_svg("cloud", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Proveedor Cloud</span><div class="kpi-icon-box">{svg_c}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">Oracle Cloud</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Tier Always Free</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        svg_b = icon_svg("package", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Contenedor</span><div class="kpi-icon-box">{svg_b}</div></div>
                <div class="kpi-value" style="font-size:1.15rem; font-weight:800; color:#1E293B;">activos-mkt</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Cifrado seguro</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        svg_p = icon_svg("layers", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Archivos Guardados</span><div class="kpi-icon-box">{svg_p}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">{len(paquetes)}</div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#64748B;">● Formato JSON</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        svg_d = icon_svg("server", size=20, color="#4F46E5")
        st.markdown(
            f"""
            <div class="kpi-card" style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:14px 16px;">
                <div class="kpi-header" style="display:flex; justify-content:space-between; margin-bottom:6px;"><span class="kpi-label" style="font-size:0.75rem; font-weight:700; color:#64748B;">Espacio Total</span><div class="kpi-icon-box">{svg_d}</div></div>
                <div class="kpi-value" style="font-size:1.3rem; font-weight:800; color:#1E293B;">{total_kb} <small style="font-size:0.85rem;">KB</small></div>
                <div class="kpi-delta" style="font-size:0.75rem; color:#059669;">● Optimizado</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 3])
    with col_btn1:
        if st.button("Actualizar Archivos", icon=":material/refresh:", use_container_width=True, type="primary"):
            invalidar_cache_datos()
            st.rerun()
    with col_btn2:
        if st.button("Vaciar Histórico Cloud", icon=":material/delete:", type="secondary", use_container_width=True):
            vaciar_historico_oci()
            invalidar_cache_datos()
            st.toast("Histórico vaciado correctamente.", icon=":material/check:")
            st.rerun()

    if not paquetes:
        st.info("No se encontraron archivos en la nube ni localmente. Ejecuta una prueba de procesamiento para generar el primer paquete.")
        return

    st.markdown("<hr style='margin:16px 0; border:0; border-top:1px solid #E2E8F0;' />", unsafe_allow_html=True)
    st.markdown(f"<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:12px;'>Archivos Disponibles en la Nube ({len(paquetes)})</div>", unsafe_allow_html=True)

    for idx, pkg in enumerate(paquetes):
        with st.container(border=True):
            c_info, c_action = st.columns([3.2, 1.4])
            with c_info:
                nombre = pkg.get("name", "sin_nombre.json")
                raw_size = pkg.get("size")
                size_kb = round((int(raw_size) if raw_size is not None else 0) / 1024, 2)
                fecha = pkg.get("time_created", "Reciente")
                source = pkg.get("source", "local").upper()
                file_icon = icon_svg("file-text", size=16, color="#4F46E5", extra_style="margin-right:6px;")
                st.markdown(f"<div style='font-weight:700; font-size:0.95rem; display:flex; align-items:center;'>{file_icon} <code>{nombre}</code></div>", unsafe_allow_html=True)
                st.markdown(
                    f"""
                    <div style="display:flex; gap:10px; align-items:center; font-size:0.78rem; color:#64748B; margin-top:4px;">
                        <span class="status-pill {'oci' if source == 'OCI' else 'standby'}">Fuente: {source}</span>
                        <span>Tamaño: <b>{size_kb} KB</b></span>
                        <span>•</span>
                        <span>Fecha: <b>{fecha}</b></span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c_action:
                datos = cargar_paquete(nombre)
                json_str = json.dumps(datos, indent=2, ensure_ascii=False) if datos else "{}"
                st.download_button(
                    label="Descargar JSON",
                    icon=":material/download:",
                    data=json_str,
                    file_name=nombre.split("/")[-1],
                    mime="application/json",
                    key=f"dl_{idx}_{nombre}",
                    use_container_width=True,
                )

            with st.expander(f"Ver contenido estructurado de `{nombre.split('/')[-1]}`", expanded=False):
                if datos:
                    num_activos = len(datos.get("activos", []))
                    meta = datos.get("metadata_paquete", {})
                    st.write(f"**Total de elementos:** {num_activos} | **Motor:** `{meta.get('motor_orquestacion', 'N/A')}`")
                    st.json(datos)
                else:
                    st.warning("No se pudo cargar el detalle del objeto.")


def render_par_links():
    """Generador y gestor de enlaces seguros temporales para acceso a los archivos."""
    render_page_card(
        "Enlaces Seguros Temporales para Compartir Archivos",
        "Genera enlaces protegidos con caducidad definida para compartir o descargar publicaciones de Oracle Cloud sin compartir contraseñas.",
        "link",
    )

    sm = OCIStorageManager()
    oci_active = sm.is_configured()

    paquetes = obtener_ultimos_paquetes(limite=20)
    nombres_objetos = [p["name"] for p in paquetes]

    if not nombres_objetos:
        st.info("No hay archivos almacenados en la nube para generar enlaces seguros.")
        return

    if not oci_active:
        st.info("El sistema está operando en modo local; se generará un enlace de demostración con caducidad simulada.")

    st.markdown("<div style='font-weight:700; font-size:1.05rem; color:#1E293B; margin-bottom:12px;'>Crear nuevo enlace de acceso seguro</div>", unsafe_allow_html=True)
    with st.form("form_par"):
        obj_sel = st.selectbox("Selecciona el archivo:", nombres_objetos)
        duracion_horas = st.slider("Duración del enlace (en horas):", min_value=1, max_value=168, value=24, step=1)
        submitted = st.form_submit_button("Generar Enlace Seguro", icon=":material/link:", type="primary")

        if submitted:
            with st.spinner("Generando enlace seguro con caducidad..."):
                try:
                    par_resp = sm.create_preauthenticated_request(obj_sel, expires_in_hours=duracion_horas)
                    url_par = par_resp.get("access_url") if isinstance(par_resp, dict) else str(par_resp)
                    if url_par:
                        exp_dt = datetime.now() + timedelta(hours=duracion_horas)
                        st.success("Enlace seguro generado exitosamente.")
                        st.text_input("Dirección web del enlace:", value=url_par)
                        st.caption(f"Válido hasta: **{exp_dt.strftime('%Y-%m-%d %H:%M:%S')}** ({duracion_horas} horas)")
                        st.markdown(f"[Abrir archivo en nueva pestaña]({url_par})")
                    else:
                        st.error("No se pudo generar el enlace. Revisa los permisos de la cuenta cloud.")
                except Exception as e:
                    st.error(f"Error al generar enlace seguro: {e}")
