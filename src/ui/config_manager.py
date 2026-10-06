"""Módulo de gestión de configuración centralizada para CommunityLab.

Sincroniza de forma bidireccional y segura entre:
1. `config/settings.json`: Estructura JSON tipada y jerárquica por dominios.
2. `.env`: Archivo de entorno plano compatible con Docker, bots y SDKs,
   preservando el 100% de los comentarios (#), encabezados y formato original.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


def get_project_root() -> Path:
    """Devuelve la ruta raíz del repositorio."""
    return Path(__file__).resolve().parents[2]


def get_config_dir() -> Path:
    """Devuelve la ruta al directorio de configuración."""
    config_dir = get_project_root() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_json_config_path() -> Path:
    return get_config_dir() / "settings.json"


def get_example_json_config_path() -> Path:
    return get_config_dir() / "settings.example.json"


def get_env_path() -> Path:
    return get_project_root() / ".env"


# Mapeo de grupos a categorías para el JSON estructurado (coincide exactamente con .env)
DOMAIN_MAPPING: Dict[str, List[str]] = {
    "servicios_activos": [
        "TELEGRAM_ENABLED",
        "DISCORD_ENABLED",
        "SLACK_ENABLED",
    ],
    "procesamiento_por_lotes": [
        "PROCESSING_N8N_ENABLED",
        "PROCESSING_PYTHON_ENABLED",
    ],
    "llm_engines": [
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "GROQ_API_KEY",
        "GROQ_MODEL",
    ],
    "oci_cloud": [
        "OCI_USER_OCID",
        "OCI_TENANCY_OCID",
        "OCI_FINGERPRINT",
        "OCI_KEY_FILE",
        "OCI_REGION",
        "OCI_NAMESPACE",
        "OCI_BUCKET_NAME",
    ],
    "canales_produccion": [
        "TELEGRAM_BOT_TOKEN",
        "DISCORD_BOT_TOKEN",
        "DISCORD_WEBHOOK_URL",
        "SLACK1_BOT_TOKEN",
        "SLACK1_APP_TOKEN",
        "SLACK2_BOT_TOKEN",
        "SLACK2_APP_TOKEN",
    ],
    "canales_local": [
        "TELEGRAM_LOCAL_BOT_TOKEN",
        "DISCORD_LOCAL_BOT_TOKEN",
        "SLACK1_LOCAL_BOT_TOKEN",
        "SLACK1_LOCAL_APP_TOKEN",
        "SLACK2_LOCAL_BOT_TOKEN",
        "SLACK2_LOCAL_APP_TOKEN",
    ],
    "n8n_produccion": [
        "N8N_WEBHOOK_URL",
        "N8N_HOST",
        "N8N_PORT",
    ],
    "n8n_local": [
        "N8N_LOCAL_WEBHOOK_URL",
        "N8N_LOCAL_HOST",
        "N8N_LOCAL_PORT",
        "N8N_LOCAL_WEBHOOK_BASE",
    ],
    "tunel": [
        "NGROK_AUTHTOKEN",
    ],
    "app_infra": [
        "ENTORNO_DEPLOY",
        "APP_ENV",
        "STREAMLIT_SERVER_PORT",
        "ENABLE_DETAILED_LOG",
        "LOG_FILE_PATH",
        "SETTINGS_ADMIN_KEY",
    ],
}


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on", "enabled", "habilitado"}


def _normalize_string_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value).strip()


def load_raw_env() -> Dict[str, str]:
    """Carga variables desde el archivo .env sin perder claves vacías."""
    env_path = get_env_path()
    if not env_path.exists():
        return {}

    values: Dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        values[key.strip()] = val.strip()
    return values


def load_settings() -> Dict[str, Any]:
    """Carga la configuración combinada.

    Prioridad:
    1. settings.json si existe.
    2. .env existente.
    3. os.environ.
    """
    json_path = get_json_config_path()
    env_values = load_raw_env()

    flat_config: Dict[str, Any] = {}

    # Si existe el JSON, aplanarlo
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                for section, fields in json_data.items():
                    if isinstance(fields, dict):
                        for k, v in fields.items():
                            flat_config[k.upper()] = v
                    else:
                        flat_config[section.upper()] = fields
        except Exception:
            pass

    # Combinar con .env para cualquier clave faltante
    for k, v in env_values.items():
        if k not in flat_config:
            flat_config[k] = v

    return flat_config


def structure_config(flat_config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Estructura un diccionario plano en dominios temáticos JSON."""
    structured: Dict[str, Dict[str, Any]] = {}
    consumed_keys = set()

    for domain, keys in DOMAIN_MAPPING.items():
        structured[domain] = {}
        for key in keys:
            val = flat_config.get(key, "")
            # Tipado nativo booleano para toggles conocidos
            if "ENABLED" in key:
                structured[domain][key.lower()] = _parse_bool(val)
            else:
                structured[domain][key.lower()] = val
            consumed_keys.add(key)

    # Otras variables del .env que no pertenezcan a los dominios estándar
    extra_keys = {k: v for k, v in flat_config.items() if k not in consumed_keys}
    if extra_keys:
        structured["otras_variables"] = {k.lower(): v for k, v in extra_keys.items()}

    return structured


def mask_secret_for_example(key: str, val: Any) -> Any:
    """Enmascara valores sensibles para generar settings.example.json de forma segura."""
    if isinstance(val, bool):
        return val
    upper_k = key.upper()
    if any(s in upper_k for s in ["KEY", "TOKEN", "SECRET", "PASSWORD", "AUTHTOKEN"]):
        return f"tu_{key.lower()}_aqui"
    if "OCID" in upper_k:
        return "ocid1.user.oc1..aaaaaaaaxxx" if "USER" in upper_k else "ocid1.tenancy.oc1..aaaaaaaaxxx"
    if "FINGERPRINT" in upper_k:
        return "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
    if "NAMESPACE" in upper_k:
        return "tu_namespace_aqui"
    if "WEBHOOK" in upper_k and "URL" in upper_k and "DISCORD" in upper_k:
        return "https://discord.com/api/webhooks/tu_webhook_id/tu_webhook_token_aqui"
    return val


def sync_to_env(flat_config: Dict[str, Any]) -> Path:
    """Actualiza el archivo .env preservando comentarios, saltos de línea y estructura."""
    env_path = get_env_path()
    if not env_path.exists():
        env_path.touch()

    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated_lines: List[str] = []
    keys_written = set()

    # Normalizar valores a string
    norm_config = {k: _normalize_string_value(v) for k, v in flat_config.items()}

    for line in lines:
        stripped = line.strip()
        # Conservar intactos comentarios y líneas vacías
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            updated_lines.append(line)
            continue

        key, _ = line.split("=", 1)
        key = key.strip()

        if key in norm_config:
            # Reemplazar valor in-place conservando la línea en su posición original
            updated_lines.append(f"{key}={norm_config[key]}")
            keys_written.add(key)
        else:
            updated_lines.append(line)

    # Si hay claves nuevas que no estaban en el .env, agregarlas al final organizadas
    missing_keys = [k for k in norm_config if k not in keys_written and norm_config[k] != ""]
    if missing_keys:
        updated_lines.append("")
        updated_lines.append("# ==============================================================================")
        updated_lines.append("# VARIABLES AGREGADAS DESDE UI SETTINGS")
        updated_lines.append("# ==============================================================================")
        for k in sorted(missing_keys):
            updated_lines.append(f"{k}={norm_config[k]}")

    env_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    return env_path


def save_settings(flat_config: Dict[str, Any]) -> Tuple[Path, Path]:
    """Guarda en settings.json y vuelca en .env preservando comentarios."""
    json_path = get_json_config_path()
    example_path = get_example_json_config_path()

    # 1. Estructurar y guardar settings.json
    structured = structure_config(flat_config)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)

    # 2. Generar/actualizar settings.example.json con secretos enmascarados
    example_structured: Dict[str, Dict[str, Any]] = {}
    for dom, flds in structured.items():
        example_structured[dom] = {k: mask_secret_for_example(k, v) for k, v in flds.items()}

    with open(example_path, "w", encoding="utf-8") as f:
        json.dump(example_structured, f, indent=2, ensure_ascii=False)

    # 3. Volcado inteligente a .env
    env_path = sync_to_env(flat_config)

    # 4. Sincronizar memoria en os.environ para el proceso actual
    for k, v in flat_config.items():
        val_str = _normalize_string_value(v)
        os.environ[k] = val_str

    return json_path, env_path
