"""CommunityLab — Panel de Curaduría y Orquestación en Streamlit.

Permite al equipo de Marketing y Community Managers de Oracle ONE / Alura
inspeccionar los activos generados, editar copys, aprobar publicaciones
y disparar ejecuciones del pipeline en tiempo real.
"""

from pathlib import Path
import json
import streamlit as st

from src.ui.services import (
    obtener_ultimos_paquetes,
    cargar_paquete,
    procesar_archivo_ui,
    guardar_curaduria_humana,
)

# Configuración de la página
st.set_page_config(
    page_title="CommunityLab — Panel de Curaduría",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos personalizados sutiles
st.markdown(
    """
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F3F4F6; border-radius: 8px; padding: 15px; border-left: 4px solid #3B82F6; }
    .card-title { font-size: 0.9rem; color: #6B7280; font-weight: 600; text-transform: uppercase; }
    .card-value { font-size: 1.8rem; font-weight: 700; color: #111827; }
    .tag-chip { display: inline-block; background-color: #E0E7FF; color: #3730A3; border-radius: 12px; padding: 2px 10px; font-size: 0.8rem; font-weight: 600; margin-right: 5px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown('<div class="main-header">🚀 CommunityLab — Motor de Curaduría</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Transformación de actividad orgánica de comunidades técnicas en activos de alto valor para Oracle ONE & Alura.</div>',
    unsafe_allow_html=True,
)

# Sidebar de navegación
st.sidebar.title("Navegación")
modo = st.sidebar.radio(
    "Selecciona una vista:",
    ["💼 Curaduría de Activos", "⚡ Ejecutar Pipeline", "☁️ Histórico OCI Object Storage"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Rol Activo:** Backend & Pipeline (Max Ferrer)\n\n"
    "**Célula 1 & 3:** IA, Pipeline y Curaduría Streamlit."
)

# -----------------------------------------------------------------------------
# VISTA 1: CURADURÍA DE ACTIVOS
# -----------------------------------------------------------------------------
if modo == "💼 Curaduría de Activos":
    st.subheader("📋 Revisión y Aprobación de Copys para Publicación")

    # Cargar paquetes disponibles
    paquetes_disponibles = obtener_ultimos_paquetes(limite=20)

    # También revisar si existe el paquete local por defecto
    default_paquete_path = Path("data/paquete_procesado.json")
    opciones_fuente = []

    if default_paquete_path.exists():
        opciones_fuente.append("Local: data/paquete_procesado.json")

    for p in paquetes_disponibles:
        opciones_fuente.append(f"Storage: {p['name']}")

    if not opciones_fuente:
        st.warning(
            "⚠️ Aún no se han generado paquetes de distribución. "
            "Ve a la pestaña **'⚡ Ejecutar Pipeline'** para procesar el dataset de ejemplo."
        )
    else:
        fuente_seleccionada = st.selectbox("Selecciona el lote a inspeccionar:", opciones_fuente)

        # Cargar datos del paquete
        datos_paquete = None
        if fuente_seleccionada.startswith("Local:"):
            with open(default_paquete_path, "r", encoding="utf-8") as f:
                datos_paquete = json.load(f)
        else:
            nombre_obj = fuente_seleccionada.replace("Storage: ", "")
            datos_paquete = cargar_paquete(nombre_obj)

        if datos_paquete and "activos" in datos_paquete:
            meta = datos_paquete.get("metadata_paquete", {})
            metricas = datos_paquete.get("metricas", {})

            # Métricas resumen en columnas
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Procesados", meta.get("total_procesados_exitosamente", 0))
            with col2:
                st.metric("Posts LinkedIn", metricas.get("total_posts_linkedin_generados", 0))
            with col3:
                st.metric("Tips Técnicos / FAQ", metricas.get("total_tips_faq_generados", 0))
            with col4:
                sentimientos = metricas.get("distribucion_sentimiento", {})
                st.metric("Positivos", sentimientos.get("positivo", 0))

            st.markdown("---")

            # Filtros interactivos
            filtro_col1, filtro_col2 = st.columns(2)
            with filtro_col1:
                tipo_filtro = st.selectbox(
                    "Filtrar por tipo de contenido:",
                    ["Todos", "logro_contratacion", "duda_tecnica", "showcase", "feedback_general"],
                )
            with filtro_col2:
                sentimiento_filtro = st.selectbox(
                    "Filtrar por sentimiento:",
                    ["Todos", "positivo", "neutro", "negativo"],
                )

            activos = datos_paquete.get("activos", [])

            # Aplicar filtros
            if tipo_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["tipo_contenido"] == tipo_filtro]
            if sentimiento_filtro != "Todos":
                activos = [a for a in activos if a["activo"]["sentimiento"] == sentimiento_filtro]

            st.write(f"Mostrando **{len(activos)}** activos filtrados:")

            # Renderizado de tarjetas de activos
            for idx, item in enumerate(activos, start=1):
                interaccion = item["interaccion"]
                activo = item["activo"]

                with st.expander(
                    f"#{idx} | [{activo['tipo_contenido'].upper()}] {interaccion['autor']} ({interaccion['canal']})",
                    expanded=(idx <= 2),
                ):
                    c_left, c_right = st.columns([1, 1])

                    with c_left:
                        st.markdown("#### 💬 Interacción Original")
                        st.info(f"\"{interaccion['texto']}\"")
                        st.caption(f"ID: `{interaccion['id']}` | Sentimiento: **{activo['sentimiento']}**")

                        # Etiquetas / Temas clave
                        tags_html = "".join([f'<span class="tag-chip">#{t}</span>' for t in activo.get("temas_clave", [])])
                        st.markdown(f"**Temas Clave:** {tags_html}", unsafe_allow_html=True)

                    with c_right:
                        st.markdown("#### ✍️ Activo Generado")

                        if activo.get("post_linkedin"):
                            st.markdown("**Copy para LinkedIn:**")
                            copy_editado = st.text_area(
                                "Editar copy antes de aprobar:",
                                value=activo["post_linkedin"],
                                height=150,
                                key=f"copy_{interaccion['id']}",
                            )

                            btn_col1, btn_col2 = st.columns(2)
                            with btn_col1:
                                if st.button("✅ Aprobar Copy", key=f"btn_ap_{interaccion['id']}"):
                                    guardar_curaduria_humana(
                                        id_interaccion=interaccion["id"],
                                        copy_aprobado=copy_editado,
                                        estado_aprobacion="aprobado",
                                    )
                                    st.success("¡Copy registrado como Aprobado!")
                            with btn_col2:
                                if st.button("❌ Descartar", key=f"btn_desc_{interaccion['id']}"):
                                    guardar_curaduria_humana(
                                        id_interaccion=interaccion["id"],
                                        copy_aprobado=copy_editado,
                                        estado_aprobacion="rechazado",
                                    )
                                    st.warning("Copy descartado.")

                        elif activo.get("tip_tecnico_faq"):
                            st.markdown("**Tip Técnico / Respuesta FAQ:**")
                            st.markdown(activo["tip_tecnico_faq"])
                        else:
                            st.markdown("_No requiere generación de post ni FAQ (Feedback General)._")

# -----------------------------------------------------------------------------
# VISTA 2: EJECUTAR PIPELINE
# -----------------------------------------------------------------------------
elif modo == "⚡ Ejecutar Pipeline":
    st.subheader("⚡ Disparador de Ejecución del Pipeline E2E")
    st.write("Ejecuta el procesamiento sobre el lote oficial de interacciones o sube un archivo personalizado.")

    dataset_defecto = "data/interacciones_ejemplo.json"
    archivo_subido = st.file_uploader("Opcional: Sube un archivo JSON con nuevas interacciones", type=["json"])

    ruta_a_procesar = dataset_defecto
    if archivo_subido is not None:
        temp_path = Path(f"data/temp_{archivo_subido.name}")
        temp_path.write_bytes(archivo_subido.read())
        ruta_a_procesar = str(temp_path)
        st.success(f"Archivo subido: `{archivo_subido.name}`")

    st.markdown("---")
    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        limite = st.number_input("Límite de registros a procesar (0 para todos):", min_value=0, max_value=100, value=3)
    with col_cfg2:
        canal_filtro = st.selectbox(
            "Filtrar por canal:",
            ["Todos", "#logros-y-empleos", "#dudas-cloud-oci", "#dudas-langgraph", "#feedback-cursos", "#proyectos-showcase"],
        )
    with col_cfg3:
        subir_oci = st.checkbox("Subir automáticamente a OCI Object Storage", value=True)

    if st.button("🚀 Iniciar Procesamiento con Gemini 1.5 Flash", type="primary"):
        canal_val = None if canal_filtro == "Todos" else canal_filtro
        limite_val = None if limite == 0 else int(limite)

        with st.spinner("Procesando interacciones con Google Gemini y validando con Pydantic..."):
            try:
                paquete = procesar_archivo_ui(
                    ruta_archivo=ruta_a_procesar,
                    limite=limite_val,
                    canal_filtro=canal_val,
                    upload_oci=subir_oci,
                    delay_segundos=0.5,
                )

                # Guardar copia local principal
                with open("data/paquete_procesado.json", "w", encoding="utf-8") as f:
                    json.dump(paquete, f, ensure_ascii=False, indent=2)

                st.success("¡Pipeline ejecutado exitosamente!")
                st.json(paquete.get("metricas", {}))
                st.info("Puedes ver y curar los copys generados en la pestaña **'💼 Curaduría de Activos'**.")

            except Exception as e:
                st.error(f"Error durante la ejecución del pipeline: {e}")

# -----------------------------------------------------------------------------
# VISTA 3: HISTÓRICO OCI
# -----------------------------------------------------------------------------
elif modo == "☁️ Histórico OCI Object Storage":
    st.subheader("☁️ Objetos Persistidos en OCI Object Storage Always Free")

    paquetes = obtener_ultimos_paquetes(limite=50)

    if not paquetes:
        st.info("No hay paquetes registrados aún en el almacenamiento.")
    else:
        st.write(f"Se encontraron **{len(paquetes)}** paquetes almacenados:")

        for p in paquetes:
            with st.container():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.code(p["name"])
                with c2:
                    st.write(f"{p['size']} bytes")
                with c3:
                    st.caption(p.get("created_at", "N/A")[:19] if p.get("created_at") else "Local")
