"""Adaptador de datos reales entre el backend de CommunityLab y la UI modular."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

from src.ui.services import (
    cargar_paquete,
    guardar_curaduria_humana,
    obtener_mapa_curaduria,
    obtener_ultimos_paquetes,
)
from .data import POSTS as FALLBACK_POSTS


def detectar_canal_ingesta(item: dict) -> str:
    """Detecta el canal digital de procedencia (Telegram, Discord, Slack o Lotes)."""
    bot_chan = str(item.get("canal_origen_bot") or "").lower()
    inter_chan = str(item.get("interaccion", {}).get("canal") or "").lower()
    inter_id = str(item.get("interaccion", {}).get("id") or "").lower()
    meta_ext = str(item.get("metadata_externa") or "").lower()
    combined = f"{bot_chan} {inter_chan} {inter_id} {meta_ext}"

    if "telegram" in combined or inter_id.startswith("tg_") or "chat_id" in meta_ext:
        return "Telegram"
    elif "discord" in combined or inter_id.startswith("dc_") or inter_id.startswith("disc_"):
        return "Discord"
    elif "slack" in combined or inter_id.startswith("slk_") or inter_id.startswith("slack_"):
        return "Slack"
    else:
        return "Lotes"


def emoji_por_tipo(tipo: str) -> str:
    mapping = {
        "logro_contratacion": "🏆",
        "duda_tecnica": "💡",
        "showcase": "🚀",
        "feedback_general": "💬",
    }
    return mapping.get(tipo, "✨")


def estado_a_badge(estado_cur: str) -> str:
    if estado_cur == "aprobado":
        return "Aprobado"
    elif estado_cur == "rechazado":
        return "Descartado"
    elif estado_cur == "leido":
        return "Leído"
    return "En revisión"


def normalizar_item_si_es_necesario(item: dict, meta_paquete: dict) -> dict:
    """Normaliza un activo si viene en formato aplanado desde OCI Object Storage."""
    if "interaccion" in item and "activo" in item:
        return item

    # Formato aplanado persistido en OCI
    item_id = str(item.get("id") or "item")
    autor = item.get("autor", "Estudiante de Comunidad")
    canal = item.get("canal", "#general")
    texto = (
        item.get("comentario")
        or item.get("pregunta_original")
        or item.get("texto")
        or item.get("post_linkedin")
        or ""
    )
    canal_origen_bot = item.get("canal_origen_bot") or canal

    tipo_contenido = item.get("tipo_contenido") or meta_paquete.get("categoria", "feedback_general")
    sentimiento = item.get(
        "sentimiento",
        "positivo" if tipo_contenido in ("logro_contratacion", "showcase") else "neutro",
    )
    temas = item.get("temas_clave") or ["CommunityLab"]
    motor = item.get("motor_orquestacion") or meta_paquete.get("motor_orquestacion", "Python")

    return {
        "interaccion": {
            "id": item_id,
            "autor": autor,
            "canal": canal,
            "texto": texto,
        },
        "activo": {
            "tipo_contenido": tipo_contenido,
            "sentimiento": sentimiento,
            "temas_clave": temas,
            # Solo contenido generado por IA; nunca el texto original del usuario
            "post_linkedin": item.get("post_linkedin"),
            "tip_tecnico_faq": item.get("tip_tecnico_faq"),
            "respuesta_asistente": item.get("respuesta_asistente"),
        },
        "canal_origen_bot": canal_origen_bot,
        "motor_orquestacion": motor,
        "procesado_en": item.get("procesado_el") or item.get("procesado_en") or "",
        "_raw_oci": item,
    }


def obtener_opciones_fuente() -> list[tuple[str, str, str]]:
    """Devuelve las opciones de fuente disponibles (Etiqueta, Ruta o Nombre, Tipo).
    Prioriza OCI si está configurado.
    """
    opciones = []

    # 1. Fuentes Cloud OCI
    try:
        paquetes_cloud = obtener_ultimos_paquetes(limite=10)
        for p in paquetes_cloud:
            opciones.append((f"☁️ OCI: {p['name']}", p["name"], "oci"))
    except Exception:
        pass

    # 2. Fuentes Locales
    rutas_locales = [
        ("📁 Local: Canales (Python)", Path("data/paquete_procesado_canales_python.json")),
        ("📁 Local: Canales (N8N)", Path("data/paquete_procesado_canales_n8n.json")),
        ("📁 Local: Lotes (Python)", Path("data/paquete_procesado_python.json")),
        ("📁 Local: Lotes (N8N)", Path("data/paquete_procesado_n8n.json")),
        ("📁 Local: Lote General", Path("data/paquete_procesado.json")),
    ]

    for label, p in rutas_locales:
        if p.exists():
            opciones.append((label, str(p), "local"))

    return opciones


def cargar_paquete_actual() -> tuple[Optional[dict], str]:
    """Carga el paquete seleccionado o el más reciente disponible en OCI/disco."""
    opciones = obtener_opciones_fuente()

    if not opciones:
        return None, "Sin datos disponibles"

    sel_label = st.session_state.get("selected_package_label", opciones[0][0])
    selected_tuple = next((opt for opt in opciones if opt[0] == sel_label), opciones[0])

    label, path_or_name, tipo_fuente = selected_tuple
    if tipo_fuente == "local":
        try:
            with open(path_or_name, "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos, label
        except Exception:
            return None, label
    else:
        raw_datos = cargar_paquete(path_or_name)
        if isinstance(raw_datos, dict) and "activos" in raw_datos:
            meta = raw_datos.get("metadata_paquete", {}) or raw_datos.get("metadata", {})
            norm_activos = []
            for item in raw_datos["activos"]:
                if isinstance(item, dict):
                    norm_activos.append(normalizar_item_si_es_necesario(item, meta))
            raw_datos["activos"] = norm_activos
        return raw_datos, label


def transformar_item_a_post(item: dict, meta_paquete: dict, mapa_curaduria: dict) -> dict:
    """Transforma un ítem real de activos en el formato esperado por los componentes visuales."""
    # Asegurar que esté normalizado si vino plano desde OCI
    item = normalizar_item_si_es_necesario(item, meta_paquete)

    interaccion = item.get("interaccion", {})
    activo = item.get("activo", {})
    item_id = str(interaccion.get("id") or "item")

    tipo = activo.get("tipo_contenido", "feedback_general")
    sentimiento = activo.get("sentimiento", "neutro")
    motor_val = (item.get("motor_orquestacion") or meta_paquete.get("motor_orquestacion", "Python")).lower()
    motor = "N8N" if "n8n" in motor_val else "Python"
    canal_ingesta = detectar_canal_ingesta(item)

    cur_info = mapa_curaduria.get(item_id) or mapa_curaduria.get(f"{item_id} (Python)") or mapa_curaduria.get(f"{item_id} (N8N)")
    estado_cur = cur_info.get("estado", "pendiente") if cur_info else "pendiente"
    estado_label = estado_a_badge(estado_cur)

    autor = interaccion.get("autor", "Estudiante de Comunidad")
    canal_origen = interaccion.get("canal", "#general")
    texto_orig = interaccion.get("texto", "")

    # Copy para edición: priorizar la respuesta generada por la IA según el tipo de contenido
    post_ia = activo.get("post_linkedin")
    tip_ia = activo.get("tip_tecnico_faq")
    resp_ia = activo.get("respuesta_asistente")
    if tipo in ("duda_tecnica", "feedback_general"):
        copy_ia = tip_ia or resp_ia or post_ia
    else:
        copy_ia = post_ia or tip_ia or resp_ia

    copy_defecto = (
        cur_info.get("copy_aprobado")
        if (cur_info and cur_info.get("copy_aprobado"))
        else (copy_ia or texto_orig)
    )

    temas = activo.get("temas_clave") or ["CommunityLab"]
    banner_titulo = temas[0].replace("#", "") if temas else "CommunityLab"

    proc_time = item.get("procesado_en", "") or item.get("procesado_el", "")
    hace_str = proc_time[11:16] if len(proc_time) >= 16 else "Reciente"

    return {
        "id": item_id,
        "title": f"[{tipo.upper()}] {autor} ({canal_origen})",
        "canal": "LinkedIn" if tipo in ("logro_contratacion", "showcase") else "Discord",
        "canal_ingesta": canal_ingesta,
        "sentimiento": sentimiento,
        "motor": motor,
        "tipo": tipo,
        "fecha": proc_time[:10] if len(proc_time) >= 10 else "Hoy",
        "estado": estado_label,
        "hace": hace_str,
        "banner": banner_titulo.capitalize(),
        "sub": f"{autor} en {canal_origen}",
        "emoji": emoji_por_tipo(tipo),
        "copy": copy_defecto,
        "_raw": item,
        "_cur_info": cur_info,
    }


def get_real_posts() -> list[dict]:
    """Obtiene la lista completa de posts a partir del paquete de datos real cargado."""
    datos_paquete, _ = cargar_paquete_actual()
    if not datos_paquete or "activos" not in datos_paquete or not datos_paquete["activos"]:
        return FALLBACK_POSTS

    meta = datos_paquete.get("metadata_paquete", {}) or datos_paquete.get("metadata", {})
    mapa_cur = obtener_mapa_curaduria()

    posts = []
    for item in datos_paquete["activos"]:
        if isinstance(item, dict):
            post_dict = transformar_item_a_post(item, meta, mapa_cur)
            posts.append(post_dict)

    return posts if posts else FALLBACK_POSTS


def get_by_id_map() -> dict[str, dict]:
    posts = get_real_posts()
    return {p["id"]: p for p in posts}
