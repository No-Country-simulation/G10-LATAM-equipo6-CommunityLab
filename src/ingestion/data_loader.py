"""Módulo de ingesta, validación y normalización de datos de la comunidad.

Permite cargar interacciones desde archivos JSON, validar su estructura con Pydantic
y proporcionar utilidades de filtrado y particionado en lotes (batching) para el pipeline.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from src.ai_engine.schemas import CommunityInteraction

logger = logging.getLogger(__name__)


def cargar_interacciones_desde_json(
    ruta_archivo: Union[str, Path],
    strict: bool = False,
) -> List[CommunityInteraction]:
    """Carga y valida interacciones desde un archivo JSON.

    Args:
        ruta_archivo: Ruta al archivo JSON con las interacciones.
        strict: Si es True, cualquier error de validación lanzará una excepción.
                Si es False, los registros inválidos se omiten y se reportan en el log.

    Returns:
        Lista de instancias validadas de CommunityInteraction.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el contenido del archivo no es JSON válido o no contiene una lista.
    """
    path = Path(ruta_archivo)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de interacciones: {path.resolve()}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            contenido = json.load(f)
    except json.JSONDecodeError as jde:
        raise ValueError(f"El archivo '{path.name}' no contiene un JSON válido: {jde}") from jde

    # Soporte tanto si la lista está en la raíz como bajo la clave 'interacciones'
    if isinstance(contenido, dict):
        items = contenido.get("interacciones", [])
    elif isinstance(contenido, list):
        items = contenido
    else:
        raise ValueError(f"Estructura JSON inesperada en '{path.name}'. Se esperaba lista o diccionario.")

    if not isinstance(items, list):
        raise ValueError("El campo 'interacciones' debe ser una lista de registros.")

    interacciones_validadas: List[CommunityInteraction] = []

    for idx, item in enumerate(items):
        try:
            if not isinstance(item, dict):
                raise ValueError(f"El elemento en el índice {idx} debe ser un objeto JSON.")
            registro = CommunityInteraction.model_validate(item)
            interacciones_validadas.append(registro)
        except Exception as e:
            msg = f"Error al validar registro en índice {idx} (id={item.get('id', 'N/A') if isinstance(item, dict) else 'N/A'}): {e}"
            if strict:
                raise ValueError(msg) from e
            logger.warning(msg)

    logger.info(
        "Carga finalizada para '%s': %d interacciones válidas de %d analizadas.",
        path.name,
        len(interacciones_validadas),
        len(items),
    )
    return interacciones_validadas


def filtrar_por_canal(
    interacciones: List[CommunityInteraction],
    canal: str,
) -> List[CommunityInteraction]:
    """Filtra una lista de interacciones por canal (ej. '#logros-y-empleos')."""
    canal_limpio = canal.strip().lower()
    return [i for i in interacciones if i.canal.strip().lower() == canal_limpio]


def filtrar_por_tipo(
    interacciones: List[CommunityInteraction],
    tipo: str,
) -> List[CommunityInteraction]:
    """Filtra una lista de interacciones por tipo (ej. 'testimonio', 'pregunta_tecnica')."""
    tipo_limpio = tipo.strip().lower()
    return [i for i in interacciones if i.tipo.strip().lower() == tipo_limpio]


def obtener_canales_unicos(interacciones: List[CommunityInteraction]) -> List[str]:
    """Devuelve la lista ordenada de canales presentes en la colección."""
    return sorted(list({i.canal for i in interacciones}))


def obtener_tipos_unicos(interacciones: List[CommunityInteraction]) -> List[str]:
    """Devuelve la lista ordenada de tipos declarados en la colección."""
    return sorted(list({i.tipo for i in interacciones}))


def generar_lotes(
    interacciones: List[CommunityInteraction],
    tamano_lote: int = 1,
) -> Generator[List[CommunityInteraction], None, None]:
    """Generador que divide la lista de interacciones en lotes de tamaño especificado.

    Útil para procesar registros de forma controlada y respetar las cuotas de Rate Limit
    de los proveedores de LLM (Gemini / Groq).

    Args:
        interacciones: Lista de interacciones a particionar.
        tamano_lote: Cantidad de elementos por lote (por defecto 1).

    Yields:
        Lote con hasta 'tamano_lote' elementos.
    """
    if tamano_lote < 1:
        raise ValueError("El tamaño de lote debe ser al menos 1.")

    for i in range(0, len(interacciones), tamano_lote):
        yield interacciones[i : i + tamano_lote]
