"""Vistas de administración y consulta de almacenamiento en OCI Object Storage."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
import streamlit as st

from src.cloud_oci.storage_client import OCIStorageManager
from src.ui.services import cargar_paquete, obtener_ultimos_paquetes, vaciar_historico_oci
from .common import render_page_card


def render_cloud_explorer():
    """Explorador de paquetes y activos persistidos en Oracle Cloud Infrastructure Object Storage."""
    render_page_card(
        "Almacenamiento Cloud: Oracle Cloud Infrastructure (OCI Object Storage)",
        "Visualiza, descarga y administra los paquetes de activos generados y persistidos en el bucket de la nube (Tier Always Free).",
        "☁️",
    )

    sm = OCIStorageManager()
    oci_active = sm.is_configured()
    paquetes = obtener_ultimos_paquetes(limite=30)
    total_bytes = sum(int(p.get("size") or 0) for p in paquetes)
    total_kb = round(total_bytes / 1024, 2)

    # Banner Oficial OCI
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#312E81,#1E1B4B); border:1px solid #4338CA; border-radius:14px; padding:14px 18px; margin-bottom:14px; color:#fff; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-weight:800; font-size:1.1rem; color:#F8FAFC;">☁️ Oracle Cloud Object Storage · Producción</span>
                <div style="font-size:0.83rem; color:#C7D2FE; margin-top:3px;">
                    Tenancy de producción de la Hackathon ONE · Bucket <code>{sm.bucket_name or 'communitylab-activos-marketing'}</code>
                </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <span class="status-pill oci">Tier Always Free</span>
                <span class="status-pill {'online' if oci_active else 'standby'}">
                    <span class="status-dot {'online' if oci_active else 'standby'}"></span>
                    {'OCI SDK Conectado' if oci_active else 'Modo Híbrido Local'}
                </span>
                <span class="status-pill online">Región: {sm.region or 'us-ashburn-1'}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 KPI Cards
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-label">Proveedor Cloud</span><div class="kpi-icon-box">☁️</div></div>
                <div class="kpi-value" style="font-size:1.4rem;">Oracle OCI</div>
                <div class="kpi-delta"><span>●</span> Tier Always Free</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-label">Bucket Oficial</span><div class="kpi-icon-box">🪣</div></div>
                <div class="kpi-value" style="font-size:1.15rem; word-break:break-all;">activos-mkt</div>
                <div class="kpi-delta"><span>●</span> Cifrado en reposo</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-label">Paquetes Totales</span><div class="kpi-icon-box">📦</div></div>
                <div class="kpi-value">{len(paquetes)}</div>
                <div class="kpi-delta"><span>●</span> JSON Versionados</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-header"><span class="kpi-label">Espacio Ocupado</span><div class="kpi-icon-box">💾</div></div>
                <div class="kpi-value">{total_kb} <small style="font-size:0.9rem;">KB</small></div>
                <div class="kpi-delta"><span>●</span> Optimizado en gzip/json</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

    # Botones de Acción
    col_btn1, col_btn2, _ = st.columns([1.3, 1.3, 3])
    with col_btn1:
        if st.button("🔄 Refrescar Storage", use_container_width=True, type="primary"):
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Vaciar Histórico OCI", type="secondary", use_container_width=True):
            vaciar_historico_oci()
            st.toast("Histórico vaciado correctamente.", icon="🗑️")
            st.rerun()

    if not paquetes:
        st.info("No se encontraron paquetes en OCI Storage ni localmente. Ejecuta una ingesta por lotes o canales para generar el primer paquete.")
        return

    st.markdown("---")
    st.subheader(f"📦 Paquetes Almacenados en OCI ({len(paquetes)})")

    for idx, pkg in enumerate(paquetes):
        with st.container(border=True):
            c_info, c_action = st.columns([3.2, 1.3])
            with c_info:
                nombre = pkg.get("name", "sin_nombre.json")
                raw_size = pkg.get("size")
                size_kb = round((int(raw_size) if raw_size is not None else 0) / 1024, 2)
                fecha = pkg.get("time_created", "Reciente")
                source = pkg.get("source", "local").upper()
                st.markdown(f"**📄 `{nombre}`**")
                st.markdown(
                    f"""
                    <div style="display:flex; gap:8px; align-items:center; font-size:0.78rem; color:#64748B;">
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
                    label="⬇️ Descargar JSON",
                    data=json_str,
                    file_name=nombre.split("/")[-1],
                    mime="application/json",
                    key=f"dl_{idx}_{nombre}",
                    use_container_width=True,
                )

            with st.expander(f"🔍 Inspeccionar estructura y metadata de `{nombre.split('/')[-1]}`", expanded=False):
                if datos:
                    num_activos = len(datos.get("activos", []))
                    meta = datos.get("metadata_paquete", {})
                    st.write(f"**Total Activos:** {num_activos} | **Motor:** `{meta.get('motor_orquestacion', 'N/A')}`")
                    st.json(datos)
                else:
                    st.warning("No se pudo cargar el detalle del objeto.")


def render_par_links():
    """Generador y gestor de enlaces pre-autenticados (PAR) para acceso seguro a activos."""
    render_page_card(
        "Enlaces Pre-Autenticados (PAR - Pre-Authenticated Requests)",
        "Genera URLs seguras y temporales con caducidad definida para compartir activos de OCI Object Storage sin exponer credenciales.",
        "🔗",
    )

    sm = OCIStorageManager()
    oci_active = sm.is_configured()

    paquetes = obtener_ultimos_paquetes(limite=20)
    nombres_objetos = [p["name"] for p in paquetes]

    if not nombres_objetos:
        st.info("No hay objetos almacenados en el storage para generar enlaces PAR.")
        return

    if not oci_active:
        st.info("ℹ️ Oracle Cloud no tiene credenciales `.pem` activas en este momento; el sistema generará una URL representativa con caducidad simulada.")

    st.subheader("Crear nuevo enlace temporal PAR")
    with st.form("form_par"):
        obj_sel = st.selectbox("Selecciona el objeto:", nombres_objetos)
        duracion_horas = st.slider("Duración del enlace (horas):", min_value=1, max_value=168, value=24, step=1)
        submitted = st.form_submit_button("⚡ Generar Enlace PAR", type="primary")

        if submitted:
            with st.spinner("Creando Pre-Authenticated Request..."):
                try:
                    par_resp = sm.create_preauthenticated_request(obj_sel, expires_in_hours=duracion_horas)
                    url_par = par_resp.get("access_url") if isinstance(par_resp, dict) else str(par_resp)
                    if url_par:
                        exp_dt = datetime.now() + timedelta(hours=duracion_horas)
                        st.success("¡Enlace PAR generado con éxito!")
                        st.text_input("URL del Enlace PAR (Lectura Segura):", value=url_par)
                        st.caption(f"Válido hasta: **{exp_dt.strftime('%Y-%m-%d %H:%M:%S')}** ({duracion_horas} horas)")
                        st.markdown(f"[Abrir activo en nueva pestaña]({url_par})")
                    else:
                        st.error("No se pudo generar el enlace PAR. Revisa los permisos de la API Key.")
                except Exception as e:
                    st.error(f"Error al generar enlace PAR: {e}")
