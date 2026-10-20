"""Capa de servicios y contratos de datos para la interfaz de usuario (Streamlit).

Desacopla la lógica de backend (ingesta, Gemini y persistencia OCI) para que
la Célula Frontend pueda consumir datos limpios y disparar acciones sin acoplamiento.
"""

from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from src.ai_engine.schemas import CommunityInteraction, ProcessedCommunityAsset
from src.cloud_oci.storage_client import OCIStorageManager
from src.ingestion.data_loader import (
    cargar_interacciones_desde_json,
    filtrar_omitir_ids,
    filtrar_por_canal,
    filtrar_por_tipo,
)
from src.pipeline import CommunityLabPipeline
from src.utils.logger import setup_logger
from src.utils.config import get_generar_imagen_webhook_url, get_n8n_webhook_url, is_production

logger = setup_logger("CommunityLabUIServices")


def fusionar_paquetes(
    paquete_existente: Optional[Dict[str, Any]],
    nuevo_paquete: Dict[str, Any],
) -> Dict[str, Any]:
    """Fusiona un nuevo paquete procesado con uno existente acumulando activos y recalculando métricas.

    Args:
        paquete_existente: Paquete previamente guardado (puede ser None si no existe).
        nuevo_paquete: Paquete recién procesado.

    Returns:
        Diccionario consolidado con todos los activos y métricas acumuladas.
    """
    if not paquete_existente or not isinstance(paquete_existente, dict):
        return nuevo_paquete

    activos_viejos = paquete_existente.get("activos", [])
    activos_nuevos = nuevo_paquete.get("activos", [])
    activos_totales = list(activos_viejos) + list(activos_nuevos)

    # Recalcular distribución de sentimientos y tipos
    sentimiento_dist = {"positivo": 0, "neutro": 0, "negativo": 0}
    tipo_dist: Dict[str, int] = {}
    posts_count = 0
    tips_count = 0

    for item in activos_totales:
        activo = item.get("activo", {})
        sent = activo.get("sentimiento", "neutro")
        sentimiento_dist[sent] = sentimiento_dist.get(sent, 0) + 1

        tipo = activo.get("tipo_contenido", "feedback_general")
        tipo_dist[tipo] = tipo_dist.get(tipo, 0) + 1

        if activo.get("post_linkedin"):
            posts_count += 1
        if activo.get("tip_tecnico_faq"):
            tips_count += 1

    fallidos_totales = paquete_existente.get("fallidos", []) + nuevo_paquete.get("fallidos", [])

    meta_fusionada = dict(nuevo_paquete.get("metadata_paquete", {}))
    meta_fusionada["total_procesados_exitosamente"] = len(activos_totales)
    meta_fusionada["total_fallidos"] = len(fallidos_totales)
    meta_fusionada["total_registros_origen"] = (
        paquete_existente.get("metadata_paquete", {}).get("total_registros_origen", len(activos_viejos))
        + nuevo_paquete.get("metadata_paquete", {}).get("total_registros_origen", len(activos_nuevos))
    )

    logger.debug(
        "Paquete acumulado: %d anteriores + %d nuevos = %d totales",
        len(activos_viejos),
        len(activos_nuevos),
        len(activos_totales),
    )

    return {
        "metadata_paquete": meta_fusionada,
        "metricas": {
            "distribucion_sentimiento": sentimiento_dist,
            "distribucion_tipo_contenido": tipo_dist,
            "total_posts_linkedin_generados": posts_count,
            "total_tips_faq_generados": tips_count,
        },
        "activos": activos_totales,
        "fallidos": fallidos_totales,
    }


def obtener_ids_procesados_sesion(consultar_oci: bool = True) -> Set[str]:
    """Recopila todos los IDs de interacciones ya presentes en OCI Object Storage o en almacenamiento local."""
    ids: Set[str] = set()

    # 1. Intentar consultar directamente desde OCI Object Storage si está habilitado
    if consultar_oci:
        try:
            sm = OCIStorageManager(allow_local_fallback=True)
            if not sm.is_local_mode:
                paquetes = sm.list_assets(prefix="activos", limit=50)
                for p in paquetes:
                    nombre = p.get("name", "")
                    if nombre.endswith(".json"):
                        try:
                            data = sm.get_asset(nombre)
                            if isinstance(data, dict):
                                for act in data.get("activos", []):
                                    if isinstance(act, dict):
                                        id_val = act.get("id") or act.get("interaccion", {}).get("id")
                                        if id_val:
                                            ids.add(id_val)
                        except Exception:
                            pass
        except Exception as e_oci:
            logger.warning("No se pudieron consultar IDs previos de OCI: %s", e_oci)

    # 2. Fallback a archivos locales si existen
    for fpath in ["data/paquete_procesado_python.json", "data/paquete_procesado_n8n.json", "data/paquete_procesado.json"]:
        p = Path(fpath)
        if p.exists():
            try:
                datos = json.loads(p.read_text(encoding="utf-8"))
                for item in datos.get("activos", []):
                    inter = item.get("interaccion", {})
                    if "id" in inter and inter["id"]:
                        ids.add(inter["id"])
            except Exception:
                pass
    return ids


def obtener_ultimos_paquetes(
    storage_manager: Optional[OCIStorageManager] = None,
    prefix: str = "activos",
    limite: int = 10,
) -> List[Dict[str, Any]]:
    """Obtiene la lista de paquetes de distribución disponibles (en OCI o almacenamiento local).

    Returns:
        Lista de diccionarios con metadatos de los paquetes ordenados del más reciente al más antiguo.
    """
    sm = storage_manager or OCIStorageManager(allow_local_fallback=True)
    try:
        objetos = sm.list_assets(prefix=prefix, limit=limite)
        # Ordenar por fecha de creación o nombre descendente
        return sorted(objetos, key=lambda x: x.get("created_at") or x.get("name"), reverse=True)
    except Exception as e:
        logger.error("Error al listar paquetes para la UI: %s", e)
        return []


def cargar_paquete(
    nombre_objeto: str,
    storage_manager: Optional[OCIStorageManager] = None,
) -> Optional[Dict[str, Any]]:
    """Carga el contenido completo de un paquete para la vista de detalle en la interfaz."""
    sm = storage_manager or OCIStorageManager(allow_local_fallback=True)
    try:
        return sm.get_asset(nombre_objeto)
    except Exception as e:
        logger.error("Error al cargar el paquete '%s': %s", nombre_objeto, e)
        return None


def vaciar_historico_oci(prefix: str = "activos") -> int:
    """Elimina los paquetes persistidos tanto en OCI Object Storage real como en almacenamiento local.

    Args:
        prefix: Prefijo a vaciar en el storage (por defecto 'activos').

    Returns:
        Cantidad de elementos eliminados.
    """
    eliminados = 0
    try:
        sm = OCIStorageManager(allow_local_fallback=True)
        if not sm.is_local_mode:
            # Eliminar en el bucket de OCI Cloud
            items = sm.list_assets(prefix=prefix, limit=1000)
            for item in items:
                nombre = item.get("name")
                if nombre:
                    try:
                        sm.delete_object(nombre)
                        eliminados += 1
                        logger.info("🗑️ Objeto '%s' eliminado de OCI Cloud.", nombre)
                    except Exception as err:
                        logger.warning("No se pudo eliminar '%s' en OCI: %s", nombre, err)
    except Exception as e_oci:
        logger.warning("Error al intentar vaciar OCI Cloud: %s", e_oci)

    # También limpiar carpeta local de fallback si existe
    local_p = Path("data/oci_local_storage") / prefix
    if local_p.exists():
        import shutil
        for item in list(local_p.iterdir()):
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    eliminados += 1
                elif item.is_file():
                    item.unlink()
                    eliminados += 1
            except Exception as e:
                logger.warning("No se pudo eliminar local '%s': %s", item, e)

    logger.info("Almacenamiento histórico de OCI vaciado: %d elementos eliminados.", eliminados)
    return eliminados


def vaciar_historico_oci_local(ruta: Union[str, Path] = "data/oci_local_storage/activos") -> int:
    """Elimina todos los paquetes JSON persistidos en el almacenamiento local de OCI.

    Args:
        ruta: Directorio raíz de los activos de OCI en modo local.

    Returns:
        Cantidad de elementos eliminados.
    """
    p = Path(ruta)
    eliminados = 0
    if p.exists():
        import shutil
        for item in list(p.iterdir()):
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    eliminados += 1
                elif item.is_file():
                    item.unlink()
                    eliminados += 1
            except Exception as e:
                logger.warning("No se pudo eliminar '%s': %s", item, e)
    logger.info("Almacenamiento local de OCI vaciado: %d elementos eliminados.", eliminados)
    return eliminados


def procesar_archivo_ui(
    ruta_archivo: Union[str, Path],
    limite: Optional[int] = None,
    canal_filtro: Optional[str] = None,
    tipo_filtro: Optional[str] = None,
    upload_oci: bool = False,
    delay_segundos: float = 1.0,
    ids_a_omitir: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Ejecuta el pipeline desde la interfaz gráfica sobre un archivo JSON dado.

    Args:
        ruta_archivo: Ruta local al archivo a procesar.
        limite: Límite opcional de registros para pruebas rápidas en la UI.
        canal_filtro: Filtro por canal específico si se seleccionó en la UI.
        tipo_filtro: Filtro por tipo de interacción.
        upload_oci: Si es True, sube el paquete resultante a OCI Object Storage.
        delay_segundos: Pausa entre llamadas a la IA.
        ids_a_omitir: Conjunto opcional de IDs a excluir (ej. ya procesados en la sesión).

    Returns:
        Diccionario consolidado con el paquete de distribución y métricas.
    """
    pipeline = CommunityLabPipeline(delay_between_calls=delay_segundos)
    paquete = pipeline.procesar_archivo(
        ruta_input=ruta_archivo,
        canal_filtro=canal_filtro,
        tipo_filtro=tipo_filtro,
        limite=limite,
        ids_a_omitir=ids_a_omitir,
    )

    if upload_oci:
        try:
            oci_res = pipeline.subir_a_oci(paquete, object_name_suffix="python")
            paquete["metadata_paquete"]["persistencia_oci"] = oci_res
        except Exception as e:
            logger.warning("No se pudo persistir en OCI desde la UI: %s", e)
            paquete["metadata_paquete"]["persistencia_oci"] = {"status": "failed", "error": str(e)}

    # Etiquetar explícitamente el motor y trazabilidad en el paquete y en cada activo individual
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.isoformat()
    lote_tag = f"py_{now_utc.strftime('%H%M%S')}"

    paquete.setdefault("metadata_paquete", {})["motor_orquestacion"] = "python_gemini"
    for item in paquete.get("activos", []):
        item["motor_orquestacion"] = "python_gemini"
        item.setdefault("procesado_en", now_str)
        item.setdefault("lote_id", lote_tag)

    return paquete


def procesar_archivo_n8n_ui(
    ruta_archivo: Union[str, Path],
    webhook_url: Optional[str] = None,
    limite: Optional[int] = None,
    canal_filtro: Optional[str] = None,
    tipo_filtro: Optional[str] = None,
    upload_oci: bool = False,
    timeout_segundos: float = 600.0,
    ids_a_omitir: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Ejecuta el procesamiento a través del orquestador n8n (vía Webhook HTTP).

    Envía el lote de interacciones filtrado al webhook de n8n desplegado en la VM de
    OCI Always Free o localmente, esperando los activos generados con Groq/Gemini.

    Args:
        ruta_archivo: Archivo JSON con interacciones a procesar.
        webhook_url: URL del Webhook de n8n. Si no se pasa, lee N8N_WEBHOOK_URL de .env.
        limite: Cantidad máxima de interacciones a enviar.
        canal_filtro: Filtro opcional por canal.
        tipo_filtro: Filtro opcional por tipo.
        upload_oci: Si es True, persiste el paquete resultante en OCI Object Storage.
        timeout_segundos: Tiempo límite en segundos para la respuesta del webhook.
        ids_a_omitir: Conjunto opcional de IDs a excluir (ej. ya procesados en la sesión).

    Returns:
        Diccionario consolidado con el paquete de distribución generado por n8n.
    """
    interacciones = cargar_interacciones_desde_json(ruta_archivo)
    if canal_filtro and canal_filtro != "Todos":
        interacciones = filtrar_por_canal(interacciones, canal_filtro)
    if tipo_filtro and tipo_filtro != "Todos":
        interacciones = filtrar_por_tipo(interacciones, tipo_filtro)
    if ids_a_omitir:
        interacciones = filtrar_omitir_ids(interacciones, ids_a_omitir)
        logger.info("n8n UI omitiendo %d IDs previos de la sesión: %d disponibles.", len(ids_a_omitir), len(interacciones))
    if limite and limite > 0:
        interacciones = interacciones[:limite]

    if not interacciones:
        raise ValueError("No hay interacciones nuevas para procesar: todas las de este criterio ya fueron procesadas en esta sesión.")

    url = webhook_url or get_n8n_webhook_url()

    payload = {
        "origen": "CommunityLab-Streamlit",
        "total": len(interacciones),
        "interacciones": [i.model_dump() for i in interacciones],
    }

    try:
        import httpx

        with httpx.Client(timeout=timeout_segundos) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 404:
                raise RuntimeError(
                    f"El Webhook no fue encontrado en n8n (404 Not Found) en: '{url}'.\n\n"
                    "💡 Causa: El workflow 'communitylab_ingesta_llm' en la VM de OCI (http://147.15.9.116:5678) "
                    "aún no tiene un nodo 'Webhook' activado en modo producción para esa URL.\n\n"
                    "Para activarlo en n8n:\n"
                    "1. Ingresa a la interfaz de n8n (http://147.15.9.116:5678).\n"
                    "2. En el workflow, reemplaza el nodo 'Manual Trigger' por un nodo 'Webhook' (POST).\n"
                    "3. En 'Path', escribe 'communitylab-ingesta' y activa el switch 'Active' del workflow."
                )
            resp.raise_for_status()
            resultado_raw = resp.json()

    except httpx.ConnectError:
        raise ConnectionError(
            f"No fue posible conectar con la instancia de n8n en '{url}'.\n"
            "Verifica que la máquina virtual de OCI (http://147.15.9.116:5678) o el contenedor Docker local estén en ejecución."
        )

    # Si n8n respondió de forma asíncrona inmediata (Opción A)
    if isinstance(resultado_raw, dict) and resultado_raw.get("status") in ["recibido", "procesando_en_segundo_plano"]:
        tot = resultado_raw.get("total_recibidos", len(interacciones))
        msg = resultado_raw.get("mensaje", f"Lote de {tot} interacciones recibido por n8n.")
        return {
            "metadata_paquete": {
                "version": "1.0.0",
                "motor_orquestacion": "n8n_asincrono_oci",
                "webhook_origen": url,
                "generado_en": datetime.now(timezone.utc).isoformat(),
                "archivo_origen": Path(ruta_archivo).name,
                "total_registros_origen": len(interacciones),
                "total_procesados_exitosamente": tot,
                "total_fallidos": 0,
                "modo_ejecucion": "asincrono",
                "mensaje_n8n": msg,
            },
            "metricas": {
                "total_interacciones_enviadas": tot,
                "estado_pipeline": "procesando_en_background_n8n",
            },
            "activos": [],
            "resultado_webhook": resultado_raw,
        }

    # Si n8n devolvió una lista pero el primer item ya es el paquete estructurado (ej. All Incoming Items de n8n)
    if isinstance(resultado_raw, list) and len(resultado_raw) > 0:
        primer_item = resultado_raw[0]
        if isinstance(primer_item, dict) and ("activos" in primer_item or "metadata_paquete" in primer_item):
            resultado_raw = primer_item

    # Si n8n ya devolvió un paquete estructurado
    if isinstance(resultado_raw, dict) and "activos" in resultado_raw:
        paquete = resultado_raw
        paquete.setdefault("metadata_paquete", {})["motor_orquestacion"] = "n8n_oci_cloud"
    else:
        # Si n8n devolvió una lista de registros planos del loop
        items = resultado_raw if isinstance(resultado_raw, list) else resultado_raw.get("data", [resultado_raw])
        activos_formateados = []
        posts_count = 0
        tips_count = 0
        sentimiento_dist = {"positivo": 0, "neutro": 0, "negativo": 0}
        tipo_dist = {"logro_contratacion": 0, "duda_tecnica": 0, "feedback_general": 0, "showcase": 0}

        for item in items:
            raw_data = item.get("json", item) if isinstance(item, dict) else {}
            sent = raw_data.get("sentimiento", "neutro")
            tipo = raw_data.get("tipo_contenido", "feedback_general")
            sentimiento_dist[sent] = sentimiento_dist.get(sent, 0) + 1
            tipo_dist[tipo] = tipo_dist.get(tipo, 0) + 1

            post = raw_data.get("post_linkedin")
            tip = raw_data.get("tip_tecnico_faq")
            if post:
                posts_count += 1
            if tip:
                tips_count += 1

            now_utc = datetime.now(timezone.utc)
            activos_formateados.append({
                "motor_orquestacion": "n8n_produccion" if is_production() else "n8n_local",
                "procesado_en": now_utc.isoformat(),
                "lote_id": f"n8n_{now_utc.strftime('%H%M%S')}",
                "interaccion": {
                    "id": raw_data.get("id", "msg_n8n"),
                    "autor": raw_data.get("autor", "Comunidad"),
                    "canal": raw_data.get("canal", "#general"),
                    "tipo": raw_data.get("tipo", "mensaje"),
                    "texto": raw_data.get("texto_original") or raw_data.get("texto", ""),
                },
                "activo": {
                    "sentimiento": sent,
                    "tipo_contenido": tipo,
                    "temas_clave": raw_data.get("temas_clave", []),
                    "post_linkedin": post,
                    "tip_tecnico_faq": tip,
                },
            })

        paquete = {
            "metadata_paquete": {
                "version": "1.0.0",
                "motor_orquestacion": "n8n_oci_cloud",
                "webhook_origen": url,
                "generado_en": datetime.now(timezone.utc).isoformat(),
                "archivo_origen": Path(ruta_archivo).name,
                "total_registros_origen": len(interacciones),
                "total_procesados_exitosamente": len(activos_formateados),
                "total_fallidos": max(0, len(interacciones) - len(activos_formateados)),
            },
            "metricas": {
                "distribucion_sentimiento": sentimiento_dist,
                "distribucion_tipo_contenido": tipo_dist,
                "total_posts_linkedin_generados": posts_count,
                "total_tips_faq_generados": tips_count,
            },
            "activos": activos_formateados,
            "fallidos": [],
        }

    if upload_oci:
        try:
            sm = OCIStorageManager(allow_local_fallback=True)
            res_oci = sm.upload_json_asset(
                data=paquete,
                prefix="activos",
                object_name_suffix="n8n",
            )
            paquete["metadata_paquete"]["persistencia_oci"] = res_oci
        except Exception as e:
            logger.warning("No se pudo persistir en OCI desde n8n UI: %s", e)
            paquete["metadata_paquete"]["persistencia_oci"] = {"status": "failed", "error": str(e)}

    return paquete


def construir_payload_imagen_post(
    id_post: str,
    solucion_tecnica: str,
    temas_clave: Optional[List[str]] = None,
    instruccion_custom: str = "",
    region: Optional[str] = None,
    namespace: Optional[str] = None,
    bucket_name: Optional[str] = None,
) -> Dict[str, Any]:
    """Arma el JSON que espera el webhook de generación de imagen, desacoplado vía .env."""
    payload: Dict[str, Any] = {
        "id_post": str(id_post).strip(),
        "solucion_tecnica": solucion_tecnica.strip(),
    }
    temas = [str(t).strip() for t in (temas_clave or []) if str(t).strip()]
    if temas:
        payload["temas_clave"] = temas
    instruccion = (instruccion_custom or "").strip()
    if instruccion:
        payload["instruccion_custom"] = instruccion

    # Inyectar variables de entorno de OCI para no depender de valores fijos en el flujo
    payload["region"] = (region or os.getenv("OCI_REGION", "us-ashburn-1")).strip()
    payload["bucket_name"] = (bucket_name or os.getenv("OCI_BUCKET_NAME", "communitylab-activos-marketing")).strip()
    ns = (namespace or os.getenv("OCI_NAMESPACE", "")).strip()
    if ns:
        payload["namespace"] = ns
    return payload


def sanitizar_url_imagen(url: str) -> str:
    """Quita el '=' inicial que a veces antepone n8n y espacios o comillas."""
    limpia = str(url or "").strip().strip("'\"")
    while limpia.startswith("="):
        limpia = limpia[1:].strip()
    return limpia


def _codificar_objeto_oci(url: str) -> str:
    """Codifica el nombre del objeto después de /o/, como hace la consola de OCI (`previews%2F...`)."""
    partes = urlsplit(url)
    marcador = "/o/"
    indice = partes.path.find(marcador)
    if indice == -1:
        return url
    prefijo = partes.path[: indice + len(marcador)]
    objeto = quote(unquote(partes.path[indice + len(marcador) :]), safe="")
    return urlunsplit((partes.scheme, partes.netloc, prefijo + objeto, partes.query, partes.fragment))


def validar_url_imagen(url: str) -> str:
    """Devuelve una URL http(s) usable en el editor, o explica por qué no se puede mostrar."""
    cruda = sanitizar_url_imagen(url)
    if cruda.startswith("data:image/"):
        return cruda
    limpia = _codificar_objeto_oci(cruda)
    if not limpia.startswith(("http://", "https://")):
        raise RuntimeError(
            "n8n no devolvió una URL de imagen válida. "
            f"Respuesta recibida: {url or '(vacía)'}"
        )

    problemas: List[str] = []
    if "undefined" in limpia.rstrip("/").split("/")[-1]:
        problemas.append(
            "el archivo quedó como 'undefined' porque el flujo no usó id_post para nombrar preview_{id_post}.png"
        )
    if "tu_namespace" in limpia:
        problemas.append("el namespace sigue siendo el ejemplo 'tu_namespace_oci'")
    if problemas:
        raise RuntimeError(
            "n8n devolvió una URL que no se puede mostrar: "
            + "; ".join(problemas)
            + f". URL recibida: {limpia}"
        )
    return limpia


def _normalizar_respuesta_imagen(resultado_raw: Any) -> Dict[str, Any]:
    """Acepta el JSON directo de n8n o el envoltorio de items (`[{json: ...}]`)."""
    data = resultado_raw
    if isinstance(data, list):
        data = data[0] if data else {}
    if isinstance(data, dict) and isinstance(data.get("json"), dict):
        data = data["json"]
    if not isinstance(data, dict):
        raise RuntimeError("El webhook de imagen no devolvió un objeto JSON.")
    return data


def _url_visible_oci(url: str) -> str:
    """Convierte una URL directa de OCI (bucket privado) en una PAR visible desde el navegador.

    Si la URL ya es una PAR (`/p/`), no apunta al bucket configurado o falla la
    generación, se devuelve sin cambios.
    """
    try:
        partes = urlsplit(url)
        if "objectstorage." not in partes.netloc or "/p/" in partes.path:
            return url
        from src.cloud_oci.storage_client import OCIStorageManager

        sm = OCIStorageManager()
        if sm.is_local_mode:
            return url
        marcador = f"/b/{sm.bucket_name}/o/"
        indice = partes.path.find(marcador)
        if indice == -1:
            return url
        objeto = unquote(partes.path[indice + len(marcador):])
        return sm.get_display_url(objeto)
    except Exception as exc:
        logger.warning("No fue posible generar URL visible para %s: %s", url, exc)
        return url


def generar_imagen_post_python(
    id_post: str,
    solucion_tecnica: str,
    temas_clave: Optional[List[str]] = None,
    instruccion_custom: str = "",
    timeout_segundos: float = 120.0,
) -> Dict[str, Any]:
    """Genera una imagen mediante el motor nativo de Python (Gemini + Pollinations + OCI SDK)."""
    import random
    from urllib.parse import quote
    import httpx
    from src.ai_engine.gemini_service import GeminiService
    from src.cloud_oci.storage_client import OCIStorageManager

    if not str(id_post).strip():
        raise ValueError("El post no tiene id_post.")
    if not solucion_tecnica or not solucion_tecnica.strip():
        raise ValueError("El copy del editor está vacío. Escribe el texto antes de generar la imagen.")

    # 1. Prompt Engineering con Gemini
    gemini = GeminiService()
    prompt_ingles = gemini.generate_image_prompt(
        solucion_tecnica=solucion_tecnica,
        instruccion_custom=instruccion_custom,
        temas_clave=temas_clave,
    )

    # 2. Descarga de imagen en Pollinations (modelo FLUX)
    clean_prompt = " ".join(prompt_ingles.split())
    seed = random.randint(1, 99999)
    pollinations_url = (
        f"https://image.pollinations.ai/prompt/{quote(clean_prompt)}?"
        f"width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    )

    try:
        with httpx.Client(timeout=timeout_segundos) as client:
            resp = client.get(pollinations_url)
            resp.raise_for_status()
            image_bytes = resp.content
            if not image_bytes:
                raise RuntimeError("Pollinations devolvió un archivo binario vacío.")
    except Exception as exc:
        raise RuntimeError(f"Error al generar imagen con Pollinations.ai: {exc}") from exc

    # 3. Subida directa a OCI Object Storage usando credenciales del .env
    sm = OCIStorageManager()
    remote_path = f"previews/preview_{id_post}.png"
    sm.upload_bytes(image_bytes, remote_name=remote_path, content_type="image/png")
    # El bucket es privado: se entrega una PAR de solo lectura (o data URI en modo local)
    image_url = sm.get_display_url(remote_path)

    return {
        "status": "success",
        "id_post": str(id_post),
        "image_url": image_url,
        "motor": "python_gemini",
        "prompt": clean_prompt,
    }


def generar_imagen_post(
    id_post: str,
    solucion_tecnica: str,
    temas_clave: Optional[List[str]] = None,
    instruccion_custom: str = "",
    webhook_url: Optional[str] = None,
    timeout_segundos: float = 180.0,
    motor: str = "python",
) -> Dict[str, Any]:
    """Generador Dual-Engine de imágenes para posts.

    Soporta motor='python' (Nativo Gemini + OCI) y motor='n8n' (Webhook n8n + Groq).
    """
    es_n8n = bool(webhook_url) or str(motor).strip().lower() in ("n8n", "motor_n8n", "n8n_workflow")
    if not es_n8n:
        return generar_imagen_post_python(
            id_post=id_post,
            solucion_tecnica=solucion_tecnica,
            temas_clave=temas_clave,
            instruccion_custom=instruccion_custom,
            timeout_segundos=timeout_segundos,
        )

    # Motor n8n (Webhooks)
    if not str(id_post).strip():
        raise ValueError("El post no tiene id_post.")
    if not solucion_tecnica or not solucion_tecnica.strip():
        raise ValueError("El copy del editor está vacío. Escribe el texto antes de generar la imagen.")

    url = (webhook_url or get_generar_imagen_webhook_url()).strip()
    payload = construir_payload_imagen_post(
        id_post=id_post,
        solucion_tecnica=solucion_tecnica,
        temas_clave=temas_clave,
        instruccion_custom=instruccion_custom,
    )

    try:
        import httpx

        with httpx.Client(timeout=timeout_segundos) as client:
            resp = client.post(url, json=payload, headers={"Content-Type": "application/json"})
            if resp.status_code == 404:
                raise RuntimeError(
                    f"El webhook de imagen no está activo (404) en '{url}'. "
                    "Si el flujo está abierto en el editor de n8n, usa la ruta /webhook-test/. "
                    "Si ya está publicado, usa /webhook/generar-imagen-post2."
                )
            resp.raise_for_status()
            data = _normalizar_respuesta_imagen(resp.json())
    except httpx.TimeoutException as exc:
        raise TimeoutError(
            "n8n no respondió a tiempo al generar la imagen. Vuelve a intentar en unos segundos."
        ) from exc
    except httpx.ConnectError as exc:
        raise ConnectionError(
            f"No fue posible conectar con n8n en '{url}'. Verifica que la VM (http://147.15.9.116:5678) esté en ejecución."
        ) from exc

    image_url = _url_visible_oci(validar_url_imagen(str(data.get("image_url") or "")))
    status = str(data.get("status") or "").strip().lower()
    if status and status != "success":
        detalle = data.get("message") or data.get("error") or data
        raise RuntimeError(f"n8n no pudo generar la imagen: {detalle}")

    return {
        "status": "success",
        "id_post": str(data.get("id_post") or id_post),
        "image_url": image_url,
        "motor": "n8n_groq",
    }


def guardar_curaduria_humana(
    id_interaccion: str,
    copy_aprobado: str,
    estado_aprobacion: str = "aprobado",
    notas: str = "",
    ruta_registro: Union[str, Path] = "data/curaduria_aprobados.json",
    persistir_oci: bool = True,
) -> Dict[str, Any]:
    """Registra la aprobación, edición o rechazo de un copy por parte del Community Manager en OCI y local."""
    registros: List[Dict[str, Any]] = []
    sm: Optional[OCIStorageManager] = None

    # Intentar leer el historial actual desde OCI Object Storage si persistir_oci es True
    if persistir_oci:
        try:
            sm = OCIStorageManager(allow_local_fallback=True)
            if not sm.is_local_mode:
                try:
                    data_oci = sm.get_asset("curaduria/curaduria_aprobados.json")
                    if isinstance(data_oci, list):
                        registros = data_oci
                    elif isinstance(data_oci, dict) and "aprobados" in data_oci:
                        registros = data_oci["aprobados"]
                except Exception:
                    # El archivo aún no existe en el bucket, empezamos lista vacía
                    registros = []
        except Exception as err:
            logger.warning("No se pudo conectar a OCI para leer curaduría: %s", err)

    # Si no leyó de OCI, verificar si existe local
    if not registros:
        path = Path(ruta_registro)
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    registros = json.load(f)
            except Exception:
                registros = []

    nuevo_registro = {
        "id_interaccion": id_interaccion,
        "copy_aprobado": copy_aprobado,
        "estado": estado_aprobacion,
        "notas": notas,
        "fecha_curaduria": datetime.now(timezone.utc).isoformat(),
    }

    # Actualizar si ya existía o añadir nuevo
    registros = [r for r in registros if r.get("id_interaccion") != id_interaccion]
    registros.append(nuevo_registro)

    sincronizado_en_oci = False
    # Persistir en OCI Object Storage
    if persistir_oci:
        try:
            if not sm:
                sm = OCIStorageManager(allow_local_fallback=True)
            if not sm.is_local_mode:
                sm.upload_json_asset(
                    data=registros,
                    object_name="curaduria/curaduria_aprobados.json",
                )
                sincronizado_en_oci = True
                logger.info("Curaduría sincronizada en OCI Object Storage: curaduria/curaduria_aprobados.json")
        except Exception as e_oci:
            logger.warning("No se pudo sincronizar curaduría en OCI: %s", e_oci)

    # Si OCI no está activo o falló, o si persistir_oci es False (modo offline o tests), guardar en disco local
    if not sincronizado_en_oci:
        path = Path(ruta_registro)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        logger.info("Curaduría guardada localmente (modo fallback/offline): %s", ruta_registro)

    logger.info("Curaduría registrada para '%s': estado=%s (OCI=%s)", id_interaccion, estado_aprobacion, sincronizado_en_oci)
    return nuevo_registro


def obtener_mapa_curaduria() -> Dict[str, Dict[str, Any]]:
    """Obtiene el historial de curaduría de OCI Object Storage indexado por ID de interacción."""
    registros: List[Dict[str, Any]] = []
    try:
        sm = OCIStorageManager(allow_local_fallback=True)
        if not sm.is_local_mode:
            data = sm.get_asset("curaduria/curaduria_aprobados.json")
            if isinstance(data, list):
                registros = data
            elif isinstance(data, dict) and "aprobados" in data:
                registros = data["aprobados"]
    except Exception:
        registros = []

    if not registros:
        local_p = Path("data/curaduria_aprobados.json")
        if local_p.exists():
            try:
                registros = json.loads(local_p.read_text(encoding="utf-8"))
            except Exception:
                registros = []

    mapa: Dict[str, Dict[str, Any]] = {}
    for r in registros:
        id_int = r.get("id_interaccion", "")
        if id_int:
            mapa[id_int] = r
            # También indexar sin badge por si se guardó con o sin prefijo
            id_limpio = id_int.split(" ")[0]
            mapa[id_limpio] = r
    return mapa
