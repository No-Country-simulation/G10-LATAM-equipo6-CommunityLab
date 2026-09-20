"""Capa de servicios y contratos de datos para la interfaz de usuario (Streamlit).

Desacopla la lógica de backend (ingesta, Gemini y persistencia OCI) para que
la Célula Frontend pueda consumir datos limpios y disparar acciones sin acoplamiento.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.ai_engine.schemas import CommunityInteraction, ProcessedCommunityAsset
from src.cloud_oci.storage_client import OCIStorageManager
from src.pipeline import CommunityLabPipeline

logger = logging.getLogger(__name__)


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


def procesar_archivo_ui(
    ruta_archivo: Union[str, Path],
    limite: Optional[int] = None,
    canal_filtro: Optional[str] = None,
    tipo_filtro: Optional[str] = None,
    upload_oci: bool = False,
    delay_segundos: float = 1.0,
) -> Dict[str, Any]:
    """Ejecuta el pipeline desde la interfaz gráfica sobre un archivo JSON dado.

    Args:
        ruta_archivo: Ruta local al archivo a procesar.
        limite: Límite opcional de registros para pruebas rápidas en la UI.
        canal_filtro: Filtro por canal específico si se seleccionó en la UI.
        tipo_filtro: Filtro por tipo de interacción.
        upload_oci: Si es True, sube el paquete resultante a OCI Object Storage.
        delay_segundos: Pausa entre llamadas a la IA.

    Returns:
        Diccionario consolidado con el paquete de distribución y métricas.
    """
    pipeline = CommunityLabPipeline(delay_between_calls=delay_segundos)
    paquete = pipeline.procesar_archivo(
        ruta_input=ruta_archivo,
        canal_filtro=canal_filtro,
        tipo_filtro=tipo_filtro,
        limite=limite,
    )

    if upload_oci:
        try:
            oci_res = pipeline.subir_a_oci(paquete)
            paquete["metadata_paquete"]["persistencia_oci"] = oci_res
        except Exception as e:
            logger.warning("No se pudo persistir en OCI desde la UI: %s", e)
            paquete["metadata_paquete"]["persistencia_oci"] = {"status": "failed", "error": str(e)}

    return paquete


def guardar_curaduria_humana(
    id_interaccion: str,
    copy_aprobado: str,
    estado_aprobacion: str = "aprobado",
    notas: str = "",
    ruta_registro: Union[str, Path] = "data/curaduria_aprobados.json",
) -> Dict[str, Any]:
    """Registra la aprobación, edición o rechazo de un copy por parte del Community Manager."""
    path = Path(ruta_registro)
    path.parent.mkdir(parents=True, exist_ok=True)

    registros: List[Dict[str, Any]] = []
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

    with open(path, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)

    logger.info("Curaduría registrada para '%s': estado=%s", id_interaccion, estado_aprobacion)
    return nuevo_registro
