"""Módulo de validación programática y parseo de respuestas del LLM para CommunityLab."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import ValidationError

try:
    from .schemas import (
        CommunityInteraction,
        CommunityLabAssetOutput,
        ProcessedCommunityAsset,
    )
except ImportError:
    from schemas import (
        CommunityInteraction,
        CommunityLabAssetOutput,
        ProcessedCommunityAsset,
    )



def extract_json_payload(raw_text: str) -> str:
    """Limpia la respuesta del LLM extrayendo el contenido JSON, removiendo delimitadores markdown si existen."""
    text = raw_text.strip()
    # Buscar bloque de código markdown ```json ... ``` o ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    
    # Si no hay delimitadores, buscar el primer '{' y el último '}'
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace : last_brace + 1].strip()

    return text


def validate_asset_output(
    data: Union[str, Dict[str, Any]]
) -> Tuple[Optional[CommunityLabAssetOutput], Optional[str]]:
    """Valida un payload JSON o string contra el esquema CommunityLabAssetOutput.

    Retorna:
        Tuple[Optional[CommunityLabAssetOutput], Optional[str]]: (instancia_validada, error_mensaje)
    """
    try:
        if isinstance(data, str):
            json_str = extract_json_payload(data)
            parsed_dict = json.loads(json_str)
        elif isinstance(data, dict):
            parsed_dict = data
        else:
            return None, f"Tipo de dato no soportado para validación: {type(data).__name__}"

        validated_model = CommunityLabAssetOutput.model_validate(parsed_dict)
        return validated_model, None

    except json.JSONDecodeError as jde:
        return None, f"Error al decodificar JSON: {jde}"
    except ValidationError as ve:
        return None, f"Error de validación Pydantic: {ve}"
    except Exception as e:
        return None, f"Error inesperado: {str(e)}"


def validate_interaction(
    data: Union[str, Dict[str, Any]]
) -> Tuple[Optional[CommunityInteraction], Optional[str]]:
    """Valida una interacción cruda contra el esquema CommunityInteraction."""
    try:
        if isinstance(data, str):
            parsed_dict = json.loads(data)
        elif isinstance(data, dict):
            parsed_dict = data
        else:
            return None, f"Tipo de dato no soportado: {type(data).__name__}"

        model = CommunityInteraction.model_validate(parsed_dict)
        return model, None
    except Exception as e:
        return None, str(e)


def validate_batch_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Carga y valida un archivo de dataset de interacciones o salidas procesadas."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)

    results = {
        "archivo": str(path),
        "total": 0,
        "validos": 0,
        "fallidos": 0,
        "detalles": []
    }

    # Si contiene una lista en la raíz o bajo la clave "interacciones"
    items = content.get("interacciones", content) if isinstance(content, dict) else content
    if not isinstance(items, list):
        items = [items]

    results["total"] = len(items)

    for idx, item in enumerate(items):
        interaction, error = validate_interaction(item)
        if interaction:
            results["validos"] += 1
            results["detalles"].append({"indice": idx, "id": interaction.id, "estado": "valido"})
        else:
            results["fallidos"] += 1
            results["detalles"].append({"indice": idx, "estado": "error", "mensaje": error})

    return results


if __name__ == "__main__":
    import sys
    
    # Prueba rápida ejecutando sobre el dataset de ejemplo si no se especifican argumentos
    default_path = Path(__file__).parents[2] / "data" / "interacciones_ejemplo.json"
    target_path = sys.argv[1] if len(sys.argv) > 1 else default_path
    
    print(f"=== Validando archivo: {target_path} ===")
    summary = validate_batch_file(target_path)
    print(f"Total analizados: {summary['total']}")
    print(f"Válidos: {summary['validos']}")
    print(f"Fallidos: {summary['fallidos']}")
