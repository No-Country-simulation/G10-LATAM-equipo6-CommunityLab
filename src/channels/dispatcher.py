"""Dispatcher universal para procesar mensajes de canales digitales con Gemini."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from src.ai_engine.gemini_service import GeminiService
from src.cloud_oci.storage_client import OCIStorageManager
from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.utils.config import get_channel_processing_engine, get_n8n_channel_webhook_url
import requests

from src.utils.logger import setup_logger
logger = setup_logger("CommunityLab.Channels.Dispatcher")


class ChannelMessageDispatcher:
    """Enruta, normaliza y procesa mensajes entrantes de Telegram, Discord y Slack."""

    def __init__(
        self,
        ai_service: Optional[GeminiService] = None,
        persist_locally: bool = True,
        storage_path: Optional[Path] = None,
        storage_manager: Optional[OCIStorageManager] = None,
        persist_oci: bool = True,
    ) -> None:
        """Inicializa el dispatcher con el servicio de IA y configuración de persistencia.

        Args:
            ai_service: Instancia de GeminiService. Si es None, inicializa uno nuevo.
            persist_locally: Si es True, acumula las interacciones en archivo local.
            storage_path: Ruta del archivo JSON acumulativo.
            storage_manager: Instancia de OCIStorageManager para persistencia cloud directa.
            persist_oci: Si es True, actualiza automáticamente los 4 archivos temáticos en OCI.
        """
        self.ai_service = ai_service or GeminiService()
        self.persist_locally = persist_locally
        self.storage_path = storage_path or Path("data/paquete_procesado_canales_python.json")
        self.persist_oci = persist_oci
        self._storage_manager = storage_manager

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

        engine = get_channel_processing_engine()
        logger.info(
            "Dispatcher procesando mensaje [%s] de '%s' en '%s' (%d chars) | Motor: %s",
            id_final,
            autor,
            canal_formateado,
            len(texto),
            engine,
        )

        # ---------------------------------------------------------------------
        # MODALIDAD A: MOTOR N8N (Webhook de flujo visual)
        # ---------------------------------------------------------------------
        if engine == "N8N":
            try:
                activo_procesado, respuestas = self._process_via_n8n(
                    interaccion=interaccion,
                    canal_origen=canal_origen,
                    metadata=metadata,
                )
                if self.persist_locally:
                    self._save_interaction_locally(activo_procesado, canal_origen, metadata)
                if self.persist_oci:
                    self._save_interaction_to_oci(activo_procesado, canal_origen)
                return activo_procesado, respuestas
            except Exception as e_n8n:
                logger.warning(
                    "[Dispatcher] Falló el procesamiento vía n8n (%s). Aplicando fallback automático a Python Gemini.",
                    e_n8n,
                )

        # ---------------------------------------------------------------------
        # MODALIDAD B: MOTOR PYTHON NATIVO (Gemini SDK Pydantic)
        # ---------------------------------------------------------------------
        # Inferencia con IA (Structured Output Pydantic)
        activo_procesado = self.ai_service.process_interaction(interaccion)

        # Formatear respuestas optimizadas para cada tipo de cliente
        respuestas = self._build_formatted_responses(activo_procesado, metadata)

        # Persistir acumulativamente si está habilitado
        if self.persist_locally:
            self._save_interaction_locally(activo_procesado, canal_origen, metadata)

        # Persistir directamente en OCI Object Storage en los 4 archivos temáticos
        if self.persist_oci:
            self._save_interaction_to_oci(activo_procesado, canal_origen)

        return activo_procesado, respuestas

    def _process_via_n8n(
        self,
        interaccion: CommunityInteraction,
        canal_origen: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[ProcessedCommunityAsset, Dict[str, Any]]:
        """Envía el mensaje entrante al Webhook de n8n para procesamiento visual y persistencia en OCI.

        Args:
            interaccion: Objeto CommunityInteraction estandarizado.
            canal_origen: Canal del bot ('#telegram-general', '#dudas-discord', '#slack').
            metadata: Diccionario opcional de metadatos del cliente.

        Returns:
            Tupla (ProcessedCommunityAsset, respuestas_formateadas).
        """
        webhook_url = get_n8n_channel_webhook_url(canal_origen)
        logger.info("[Dispatcher -> n8n] Despachando mensaje [%s] a Webhook: %s", interaccion.id, webhook_url)

        payload = {
            "id": interaccion.id,
            "autor": interaccion.autor,
            "canal": interaccion.canal,
            "tipo": interaccion.tipo,
            "texto": interaccion.texto,
            "metadata": metadata or {},
            # Campos de compatibilidad con Discord Webhook Trigger de n8n
            "author": interaccion.autor,
            "content": interaccion.texto,
            "channel": interaccion.canal,
        }

        resp = requests.post(webhook_url, json=payload, timeout=45.0)
        resp.raise_for_status()
        n8n_res = resp.json()

        # Extraer datos procesados desde la respuesta del webhook de n8n
        # Puede venir como dict directo, dentro de 'json', o en lista
        data_item = n8n_res[0] if isinstance(n8n_res, list) and n8n_res else n8n_res
        if isinstance(data_item, dict) and "json" in data_item:
            data_item = data_item["json"]

        raw_output = data_item.get("raw_output") or data_item.get("activo") or data_item

        # Si viene formateado como payload de webhook de Discord (con embeds/fields)
        sentimiento_str = raw_output.get("sentimiento")
        tipo_str = raw_output.get("tipo_contenido")
        temas_list = raw_output.get("temas_clave")
        post_linkedin = raw_output.get("post_linkedin")
        tip_faq = raw_output.get("tip_tecnico_faq")

        if not sentimiento_str and "embeds" in data_item and isinstance(data_item["embeds"], list):
            embed = data_item["embeds"][0] if data_item["embeds"] else {}
            for field in embed.get("fields", []):
                fname = field.get("name", "").lower()
                fval = field.get("value", "")
                if "sentimiento" in fname:
                    sentimiento_str = fval.lower().replace("🟢", "").replace("🔴", "").replace("⚪", "").strip()
                elif "categoría" in fname or "categoria" in fname:
                    tipo_str = fval.lower().strip()
                elif "temas" in fname:
                    temas_list = [t.strip() for t in fval.split(",") if t.strip()]
                elif "tip" in fname or "faq" in fname:
                    tip_faq = fval
                elif "linkedin" in fname:
                    post_linkedin = fval

        sentimiento_str = sentimiento_str or "neutro"
        tipo_str = tipo_str or "feedback_general"
        temas_list = temas_list or ["Comunidad"]
        if not isinstance(temas_list, list):
            temas_list = [str(temas_list)]

        # Extraer respuesta conversacional directa de n8n si existe
        respuesta_chat = raw_output.get("respuesta_chat") or data_item.get("content")
        metadata_completa = dict(metadata or {})
        if respuesta_chat:
            metadata_completa["respuesta_directa"] = respuesta_chat

        asset_output = CommunityLabAssetOutput(
            sentimiento=sentimiento_str,
            tipo_contenido=tipo_str,
            temas_clave=temas_list,
            post_linkedin=post_linkedin or raw_output.get("post_linkedin"),
            tip_tecnico_faq=tip_faq or raw_output.get("tip_tecnico_faq"),
        )

        activo_procesado = ProcessedCommunityAsset(
            interaccion=interaccion,
            activo=asset_output,
        )

        respuestas = self._build_formatted_responses(activo_procesado, metadata_completa)
        logger.info("[Dispatcher <- n8n] Mensaje [%s] procesado exitosamente por n8n.", interaccion.id)
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

        resp_directa = (metadata or {}).get("respuesta_directa")

        # 1. Formato Markdown para Telegram
        texto_tg = (
            f"🤖 *CommunityLab IA Assistant*\n\n"
        )
        if resp_directa:
            texto_tg += f"💬 *Respuesta:* {resp_directa}\n\n"
        elif activo.tip_tecnico_faq:
            tip_limpio = activo.tip_tecnico_faq.replace("_", "\\_")
            texto_tg += f"💡 *Solución / Pasos a seguir:*\n{tip_limpio}\n\n"

        texto_tg += (
            f"📊 *Sentimiento:* {sentimiento_emoji} | 🏷️ *Temas:* `{temas_str}` | 📌 *Tipo:* `{tipo_val}`\n"
        )
        if activo.post_linkedin:
            post_limpio = activo.post_linkedin.replace("_", "\\_")
            texto_tg += f"\n💼 *Propuesta de Publicación (LinkedIn):*\n{post_limpio}\n"

        # 2. Formato Embed para Discord
        color_hex = 0x10B981 if sentimiento_val == "positivo" else 0x6B7280
        if sentimiento_val == "negativo":
            color_hex = 0xEF4444

        desc_discord = f"**Autor:** {interaccion.autor} | **Canal:** `{interaccion.canal}`"
        if resp_directa:
            desc_discord += f"\n\n💬 **Respuesta:**\n{resp_directa}"

        embed_discord = {
            "title": "🤖 CommunityLab Assistant",
            "description": desc_discord,
            "color": color_hex,
            "fields": [
                {"name": "Sentimiento", "value": sentimiento_emoji, "inline": True},
                {"name": "Tipo Contenido", "value": tipo_val, "inline": True},
                {"name": "Temas Identificados", "value": temas_str, "inline": False},
            ],
            "footer": {"text": f"ID: {interaccion.id} • CommunityLab Hackathon Oracle ONE"},
        }
        if activo.tip_tecnico_faq and not resp_directa:
            embed_discord["fields"].append({
                "name": "💡 Pasos / Solución Técnica",
                "value": activo.tip_tecnico_faq[:1024],
                "inline": False,
            })
        if activo.post_linkedin:
            embed_discord["fields"].append({
                "name": "💼 Propuesta LinkedIn",
                "value": activo.post_linkedin[:1024],
                "inline": False,
            })

        # 3. Formato Bloques para Slack
        bloques_slack = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🤖 CommunityLab Assistant", "emoji": True},
            },
        ]

        if resp_directa:
            bloques_slack.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"💬 *Respuesta a tu consulta:*\n{resp_directa}"},
            })
        elif activo.tip_tecnico_faq:
            bloques_slack.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*💡 Solución / Pasos a seguir:*\n>{activo.tip_tecnico_faq}"},
            })

        bloques_slack.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Autor:* {interaccion.autor} | *Sentimiento:* {sentimiento_emoji} | *Categoría:* `{tipo_val}` | *Temas:* {temas_str}",
                }
            ],
        })

        if activo.post_linkedin:
            bloques_slack.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*💼 Propuesta para LinkedIn:*\n>{activo.post_linkedin}"},
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
            logger.info("[Dispatcher] Activo guardado localmente en '%s' (Total acumulado: %d)", self.storage_path, len(paquete["activos"]))

        except Exception as e:
            logger.error("Error persistiendo interacción de canal localmente: %s", e)

    def _save_interaction_to_oci(
        self,
        item: ProcessedCommunityAsset,
        canal_origen: str,
    ) -> None:
        """Persiste la interacción procesada en los 4 archivos temáticos especializados de OCI Object Storage.

        Mapea el tipo de interacción a uno de los 4 archivos temáticos oficiales:
        1. marketing_linkedin_logros.json (logro_contratacion)
        2. marketing_showcase.json (showcase)
        3. faqs_soporte_tecnico.json (duda_tecnica)
        4. metricas_feedback_comunidad.json (feedback_general u otros)
        """
        try:
            if not self._storage_manager:
                self._storage_manager = OCIStorageManager(allow_local_fallback=True)

            sm = self._storage_manager
            now = datetime.now(timezone.utc)
            date_folder = now.strftime("%Y-%m-%d")
            iso_now = now.isoformat()

            inter = item.interaccion
            act = item.activo
            tipo_val = act.tipo_contenido.value if hasattr(act.tipo_contenido, "value") else str(act.tipo_contenido)
            sent_val = act.sentimiento.value if hasattr(act.sentimiento, "value") else str(act.sentimiento)

            # Estructurar elemento plano
            item_plano: Dict[str, Any] = {
                "id": inter.id,
                "autor": inter.autor,
                "canal": inter.canal,
                "canal_origen_bot": canal_origen,
                "tipo_contenido": tipo_val,
                "sentimiento": sent_val,
                "temas_clave": act.temas_clave or [],
                "procesado_el": iso_now,
            }

            if tipo_val == "logro_contratacion":
                nombre_archivo = "marketing_linkedin_logros.json"
                categoria = "logros_contratacion"
                item_plano["comentario"] = inter.texto
                item_plano["post_linkedin"] = act.post_linkedin
            elif tipo_val == "showcase":
                nombre_archivo = "marketing_showcase.json"
                categoria = "proyectos_showcase"
                item_plano["descripcion_proyecto"] = inter.texto
                item_plano["post_linkedin"] = act.post_linkedin
            elif tipo_val == "duda_tecnica":
                nombre_archivo = "faqs_soporte_tecnico.json"
                categoria = "dudas_tecnicas_faqs"
                item_plano["pregunta_original"] = inter.texto
                item_plano["tip_tecnico_faq"] = act.tip_tecnico_faq
            else:
                nombre_archivo = "metricas_feedback_comunidad.json"
                categoria = "feedback_metricas"
                item_plano["comentario"] = inter.texto

            remote_path = f"activos/{date_folder}/{nombre_archivo}"

            # Cargar objeto existente si ya existe en OCI o fallback local
            doc_existente = None
            try:
                doc_existente = sm.get_asset(remote_path)
            except Exception:
                doc_existente = None

            if not isinstance(doc_existente, dict) or "activos" not in doc_existente:
                doc_existente = {
                    "nombre_archivo": nombre_archivo,
                    "metadata": {
                        "version": "1.0.0",
                        "plataforma": "CommunityLab",
                        "motor_orquestacion": "python_dynamic_channels",
                        "fecha_generacion": iso_now,
                        "origen_comunidad": f"Bot {canal_origen}",
                        "categoria": categoria,
                        "total_interacciones": 0,
                    },
                    "activos": [],
                }
                if nombre_archivo == "metricas_feedback_comunidad.json":
                    doc_existente["metricas_salud"] = {
                        "sentimientos": {"positivo": 0, "neutro": 0, "negativo": 0},
                        "total_feedback": 0,
                    }

            # Evitar duplicados por id_interaccion
            activos_list = doc_existente.setdefault("activos", [])
            activos_filtrados = [a for a in activos_list if a.get("id") != inter.id]
            activos_filtrados.append(item_plano)
            doc_existente["activos"] = activos_filtrados
            doc_existente["metadata"]["total_interacciones"] = len(activos_filtrados)
            doc_existente["metadata"]["ultima_actualizacion"] = iso_now

            # Si es archivo de feedback, actualizar métricas acumuladas
            if "metricas_salud" in doc_existente:
                dist = {"positivo": 0, "neutro": 0, "negativo": 0}
                for a in activos_filtrados:
                    s = a.get("sentimiento", "neutro")
                    dist[s] = dist.get(s, 0) + 1
                doc_existente["metricas_salud"]["sentimientos"] = dist
                doc_existente["metricas_salud"]["total_feedback"] = len(activos_filtrados)

            # Subir a OCI Object Storage
            res = sm.upload_json_asset(data=doc_existente, object_name=remote_path)
            logger.info("☁️ [Dispatcher -> OCI] Interacción [%s] persistida en '%s' (Status: %s)", inter.id, remote_path, res.get("status"))

        except Exception as e_oci:
            logger.error("Error persistiendo interacción de canal en OCI Object Storage: %s", e_oci)
