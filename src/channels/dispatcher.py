"""Dispatcher universal para procesar mensajes de canales digitales con Gemini."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.ai_engine.gemini_service import GeminiService
from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)

logger = logging.getLogger("CommunityLab.Channels.Dispatcher")


class ChannelMessageDispatcher:
    """Enruta, normaliza y procesa mensajes entrantes de Telegram, Discord y Slack."""

    def __init__(
        self,
        ai_service: Optional[GeminiService] = None,
        persist_locally: bool = True,
        storage_path: Optional[Path] = None,
    ) -> None:
        """Inicializa el dispatcher con el servicio de IA y configuración de persistencia.

        Args:
            ai_service: Instancia de GeminiService. Si es None, inicializa uno nuevo.
            persist_locally: Si es True, acumula las interacciones en archivo local.
            storage_path: Ruta del archivo JSON acumulativo.
        """
        self.ai_service = ai_service or GeminiService()
        self.persist_locally = persist_locally
        self.storage_path = storage_path or Path("data/paquete_procesado_canales.json")

    def process_incoming_message(
        self,
        canal_origen: str,
        autor: str,
        texto: str,
        mensaje_id_externo: Optional[str] = None,
        tipo_sugerido: str = "consulta_dinamica",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ProcessedCommunityAsset, Dict[str, Any]]:
        """Normaliza el mensaje a CommunityInteraction y lo procesa con Gemini.

        Args:
            canal_origen: Canal emisor (ej: '#telegram-general', '#dudas-discord').
            autor: Nombre o alias del remitente.
            texto: Contenido textual del mensaje.
            mensaje_id_externo: ID asignado por la plataforma (opcional).
            tipo_sugerido: Tipo inicial de interacción para el modelo.
            metadata: Diccionario opcional con información adicional de la plataforma.

        Returns:
            Tupla con (ProcessedCommunityAsset, respuestas_formateadas_por_canal).
        """
        id_final = mensaje_id_externo or f"msg_{uuid.uuid4().hex[:8]}"
        canal_formateado = canal_origen if canal_origen.startswith("#") else f"#{canal_origen}"

        interaccion = CommunityInteraction(
            id=id_final,
            autor=autor or "Usuario Anónimo",
            canal=canal_formateado,
            tipo=tipo_sugerido,
            texto=texto.strip(),
        )

        logger.info(
            "Dispatcher procesando mensaje [%s] de '%s' en '%s' (%d chars)",
            id_final,
            autor,
            canal_formateado,
            len(texto),
        )

        # Inferencia con IA (Structured Output Pydantic)
        activo_procesado = self.ai_service.process_interaction(interaccion)

        # Formatear respuestas optimizadas para cada tipo de cliente
        respuestas = self._build_formatted_responses(activo_procesado, metadata)

        # Persistir acumulativamente si está habilitado
        if self.persist_locally:
            self._save_interaction_locally(activo_procesado, canal_origen, metadata)

        return activo_procesado, respuestas

    def _build_formatted_responses(
        self,
        item: ProcessedCommunityAsset,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Construye respuestas adaptadas a la sintaxis de cada plataforma."""
        interaccion = item.interaccion
        activo = item.activo

        sentimiento_val = activo.sentimiento.value if hasattr(activo.sentimiento, "value") else str(activo.sentimiento)
        sentimiento_emoji = {
            "positivo": "🟢 Positivo",
            "neutro": "⚪ Neutro",
            "negativo": "🔴 Negativo",
        }.get(sentimiento_val, sentimiento_val)

        tipo_val = activo.tipo_contenido.value if hasattr(activo.tipo_contenido, "value") else str(activo.tipo_contenido)
        temas_str = ", ".join(activo.temas_clave) if activo.temas_clave else "General"

        # 1. Formato Markdown para Telegram
        texto_tg = (
            f"🤖 *CommunityLab IA Assistant*\n\n"
            f"📊 *Sentimiento:* {sentimiento_emoji}\n"
            f"🏷️ *Temas:* `{temas_str}`\n"
            f"📌 *Tipo:* `{tipo_val}`\n\n"
        )
        if activo.post_linkedin:
            texto_tg += f"💼 *Propuesta de Publicación (LinkedIn):*\n{activo.post_linkedin}\n\n"
        if activo.tip_tecnico_faq:
            texto_tg += f"💡 *Tip / Solución Técnica:*\n{activo.tip_tecnico_faq}\n"

        # 2. Formato Embed para Discord
        color_hex = 0x10B981 if sentimiento_val == "positivo" else 0x6B7280
        if sentimiento_val == "negativo":
            color_hex = 0xEF4444

        embed_discord = {
            "title": "🔍 Análisis de Interacción - CommunityLab",
            "description": f"**Autor:** {interaccion.autor}\n**Canal:** `{interaccion.canal}`",
            "color": color_hex,
            "fields": [
                {"name": "Sentimiento", "value": sentimiento_emoji, "inline": True},
                {"name": "Tipo Contenido", "value": tipo_val, "inline": True},
                {"name": "Temas Identificados", "value": temas_str, "inline": False},
            ],
            "footer": {"text": f"ID: {interaccion.id} | Procesado con Gemini 2.5 Flash"},
        }
        if activo.post_linkedin:
            embed_discord["fields"].append({
                "name": "💼 Propuesta LinkedIn",
                "value": activo.post_linkedin[:1024],
                "inline": False,
            })
        if activo.tip_tecnico_faq:
            embed_discord["fields"].append({
                "name": "💡 Tip / FAQ Técnico",
                "value": activo.tip_tecnico_faq[:1024],
                "inline": False,
            })

        # 3. Formato Bloques para Slack
        bloques_slack = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 CommunityLab - Análisis de Interacción", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Autor:* {interaccion.autor}"},
                    {"type": "mrkdwn", "text": f"*Sentimiento:* {sentimiento_emoji}"},
                    {"type": "mrkdwn", "text": f"*Tipo:* `{tipo_val}`"},
                    {"type": "mrkdwn", "text": f"*Temas:* `{temas_str}`"},
                ],
            },
        ]
        if activo.post_linkedin:
            bloques_slack.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*💼 Propuesta para LinkedIn:*\n>{activo.post_linkedin}"},
            })
        if activo.tip_tecnico_faq:
            bloques_slack.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*💡 Tip FAQ:*\n>{activo.tip_tecnico_faq}"},
            })

        return {
            "telegram_markdown": texto_tg.strip(),
            "discord_embed": embed_discord,
            "slack_blocks": bloques_slack,
            "raw_asset": item,
        }

    def _save_interaction_locally(
        self,
        item: ProcessedCommunityAsset,
        canal_origen: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Guarda la interacción en el archivo de paquete acumulativo."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            paquete = {
                "metadata_paquete": {
                    "generado_el": datetime.now(timezone.utc).isoformat(),
                    "motor_orquestacion": "python_dynamic_channels",
                    "total_activos": 0,
                },
                "activos": [],
            }

            if self.storage_path.exists():
                try:
                    with open(self.storage_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "activos" in data:
                            paquete = data
                except Exception as ex:
                    logger.warning("No se pudo leer paquete previo de canales: %s", ex)

            activo_dict = item.model_dump()
            activo_dict["canal_origen_bot"] = canal_origen
            if metadata:
                activo_dict["metadata_externa"] = metadata

            paquete["activos"].append(activo_dict)
            paquete["metadata_paquete"]["total_activos"] = len(paquete["activos"])
            paquete["metadata_paquete"]["ultima_actualizacion"] = datetime.now(timezone.utc).isoformat()

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(paquete, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error("Error persistiendo interacción de canal localmente: %s", e)
