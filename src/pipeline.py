"""Orquestador E2E del Pipeline de CommunityLab.

Integra el módulo de ingesta, el motor de inferencia de Gemini y la consolidación
de paquetes de distribución con métricas para persistencia en OCI y curaduría en Streamlit.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Union

from src.ai_engine.gemini_service import GeminiService
from src.ai_engine.schemas import (
    CommunityInteraction,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.cloud_oci.storage_client import OCIStorageManager
from src.ingestion.data_loader import (
    cargar_interacciones_desde_json,
    filtrar_omitir_ids,
    filtrar_por_canal,
    filtrar_por_tipo,
    generar_lotes,
)

from src.utils.logger import setup_logger

logger = setup_logger("CommunityLabPipeline")


class CommunityLabPipeline:
    """Pipeline orquestador para procesar interacciones orgánicas de la comunidad."""

    def __init__(
        self,
        ai_service: Optional[GeminiService] = None,
        storage_manager: Optional[OCIStorageManager] = None,
        delay_between_calls: float = 2.0,
    ):
        """Inicializa el pipeline orquestador.

        Args:
            ai_service: Instancia de GeminiService. Si es None, se crea una por defecto.
            storage_manager: Instancia de OCIStorageManager para persistencia cloud.
            delay_between_calls: Segundos de pausa entre cada llamada a la API
                                 para respetar cuotas de Rate Limit (por defecto 2.0s).
        """
        self.ai_service = ai_service or GeminiService()
        self.storage_manager = storage_manager or OCIStorageManager(allow_local_fallback=True)
        self.delay_between_calls = delay_between_calls

    def procesar_interaccion(
        self,
        interaccion: CommunityInteraction,
    ) -> ProcessedCommunityAsset:
        """Procesa una única interacción con el motor de IA."""
        return self.ai_service.process_interaction(interaccion)

    def procesar_archivo(
        self,
        ruta_input: Union[str, Path],
        canal_filtro: Optional[str] = None,
        tipo_filtro: Optional[str] = None,
        limite: Optional[int] = None,
        ids_a_omitir: Optional[Union[Set[str], List[str]]] = None,
    ) -> Dict[str, Any]:
        """Ejecuta el pipeline completo sobre un archivo JSON de interacciones.

        Args:
            ruta_input: Ruta al archivo JSON con las interacciones crudas.
            canal_filtro: Opcional, canal a filtrar (ej. '#logros-y-empleos').
            tipo_filtro: Opcional, tipo a filtrar (ej. 'testimonio').
            limite: Cantidad máxima de registros a procesar (útil para pruebas).
            ids_a_omitir: Conjunto opcional de IDs de interacción a excluir (ej. ya procesados).

        Returns:
            Diccionario estructurado con el Paquete de Distribución y métricas.
        """
        path = Path(ruta_input)
        logger.info("Iniciando pipeline sobre archivo: %s", path.name)

        interacciones = cargar_interacciones_desde_json(path)
        total_cargados = len(interacciones)

        if canal_filtro:
            interacciones = filtrar_por_canal(interacciones, canal_filtro)
            logger.info("Filtro canal '%s': %d restantes.", canal_filtro, len(interacciones))

        if tipo_filtro:
            interacciones = filtrar_por_tipo(interacciones, tipo_filtro)
            logger.info("Filtro tipo '%s': %d restantes.", tipo_filtro, len(interacciones))

        if ids_a_omitir:
            interacciones = filtrar_omitir_ids(interacciones, ids_a_omitir)
            logger.info("Omitiendo %d IDs previos de la sesión: %d disponibles.", len(ids_a_omitir), len(interacciones))

        if limite and limite > 0:
            interacciones = interacciones[:limite]
            logger.info("Límite aplicado: procesando primeros %d registros.", len(interacciones))

        activos_procesados: List[ProcessedCommunityAsset] = []
        fallidos: List[Dict[str, str]] = []

        total_a_procesar = len(interacciones)
        logger.info("Procesando lote de %d interacciones...", total_a_procesar)

        for idx, lote in enumerate(generar_lotes(interacciones, tamano_lote=1), start=1):
            item = lote[0]
            try:
                logger.info(
                    "[%d/%d] Procesando ID='%s' (Autor: %s, Canal: %s)...",
                    idx,
                    total_a_procesar,
                    item.id,
                    item.autor,
                    item.canal,
                )
                logger.debug("Texto interacción [%d chars]: '%s'", len(item.texto), item.texto[:140])
                resultado = self.procesar_interaccion(item)
                activos_procesados.append(resultado)
                logger.debug(
                    "Resultado ID='%s' -> Sentimiento=%s, Tipo=%s, Temas=%s, PostLinkedIn=%s",
                    item.id,
                    resultado.activo.sentimiento.value,
                    resultado.activo.tipo_contenido.value,
                    resultado.activo.temas_clave,
                    bool(resultado.activo.post_linkedin),
                )

            except Exception as e:
                logger.error("Error al procesar registro %s: %s", item.id, e, exc_info=True)
                fallidos.append({"id": item.id, "autor": item.autor, "error": str(e)})

            # Pausa preventiva entre llamadas (excepto en el último ítem)
            if idx < total_a_procesar and self.delay_between_calls > 0:
                logger.debug("Pausa preventiva rate-limit de %.2fs...", self.delay_between_calls)
                time.sleep(self.delay_between_calls)

        # Consolidación de métricas y paquete final
        paquete = self._construir_paquete(
            activos_procesados=activos_procesados,
            fallidos=fallidos,
            archivo_origen=path.name,
            total_cargados=total_cargados,
        )

        logger.info(
            "Pipeline completado: %d exitosos, %d fallidos.",
            len(activos_procesados),
            len(fallidos),
        )
        return paquete

    def _construir_paquete(
        self,
        activos_procesados: List[ProcessedCommunityAsset],
        fallidos: List[Dict[str, str]],
        archivo_origen: str,
        total_cargados: int,
    ) -> Dict[str, Any]:
        """Calcula métricas y genera el esquema consolidado del Paquete de Distribución."""
        conteo_sentimientos = {
            SentimientoEnum.POSITIVO.value: 0,
            SentimientoEnum.NEUTRO.value: 0,
            SentimientoEnum.NEGATIVO.value: 0,
        }

        conteo_tipos = {
            TipoContenidoEnum.LOGRO_CONTRATACION.value: 0,
            TipoContenidoEnum.DUDA_TECNICA.value: 0,
            TipoContenidoEnum.FEEDBACK_GENERAL.value: 0,
            TipoContenidoEnum.SHOWCASE.value: 0,
        }

        total_posts_linkedin = 0
        total_tips_faq = 0

        for item in activos_procesados:
            activo = item.activo
            # Sentimiento
            if activo.sentimiento.value in conteo_sentimientos:
                conteo_sentimientos[activo.sentimiento.value] += 1

            # Tipo
            if activo.tipo_contenido.value in conteo_tipos:
                conteo_tipos[activo.tipo_contenido.value] += 1

            # Contenidos generados
            if activo.post_linkedin:
                total_posts_linkedin += 1
            if activo.tip_tecnico_faq:
                total_tips_faq += 1

        ahora = datetime.now(timezone.utc)

        return {
            "metadata_paquete": {
                "version": "1.0.0",
                "generado_en": ahora.isoformat(),
                "archivo_origen": archivo_origen,
                "total_registros_origen": total_cargados,
                "total_procesados_exitosamente": len(activos_procesados),
                "total_fallidos": len(fallidos),
            },
            "metricas": {
                "distribucion_sentimiento": conteo_sentimientos,
                "distribucion_tipo_contenido": conteo_tipos,
                "total_posts_linkedin_generados": total_posts_linkedin,
                "total_tips_faq_generados": total_tips_faq,
            },
            "activos": [
                {
                    "lote_id": f"py_{ahora.strftime('%H%M%S')}",
                    "procesado_en": ahora.isoformat(),
                    "motor_orquestacion": "python_gemini",
                    "interaccion": item.interaccion.model_dump(),
                    "activo": item.activo.model_dump(),
                }
                for item in activos_procesados
            ],
            "fallidos": fallidos,
        }

    def guardar_paquete_json(
        self,
        paquete: Dict[str, Any],
        ruta_salida: Union[str, Path],
    ) -> Path:
        """Guarda el paquete procesado en un archivo JSON formateado."""
        out_path = Path(ruta_salida)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(paquete, f, ensure_ascii=False, indent=2)

        logger.info("Paquete guardado exitosamente en: %s", out_path.resolve())
        return out_path

    def subir_a_oci(
        self,
        paquete: Dict[str, Any],
        object_name: Optional[str] = None,
        object_name_suffix: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sube los 4 archivos temáticos especializados a OCI Object Storage homologados con n8n.

        1. marketing_linkedin_logros.json
        2. marketing_showcase.json
        3. faqs_soporte_tecnico.json
        4. metricas_feedback_comunidad.json
        """
        now = datetime.now(timezone.utc)
        date_folder = now.strftime("%Y-%m-%d")
        iso_now = now.isoformat()
        archivo_origen = paquete.get("metadata_paquete", {}).get("archivo_origen", "interacciones.json")
        activos = paquete.get("activos", [])
        total_items = len(activos)

        # 1. Separar por categorías
        logros_items = []
        showcase_items = []
        faqs_items = []
        feedback_items = []

        for item in activos:
            inter = item.get("interaccion", {})
            act = item.get("activo", {})
            tipo = act.get("tipo_contenido", "")

            # Formato estándar plano por interacción
            item_plano = {
                "id": inter.get("id"),
                "autor": inter.get("autor"),
                "canal": inter.get("canal"),
                "tipo_contenido": tipo,
                "sentimiento": act.get("sentimiento"),
                "temas_clave": act.get("temas_clave", []),
            }

            if tipo == "logro_contratacion":
                item_plano["comentario"] = inter.get("texto")
                item_plano["post_linkedin"] = act.get("post_linkedin")
                logros_items.append(item_plano)
            elif tipo == "showcase":
                item_plano["descripcion_proyecto"] = inter.get("texto")
                item_plano["post_linkedin"] = act.get("post_linkedin")
                showcase_items.append(item_plano)
            elif tipo == "duda_tecnica":
                item_plano["pregunta_original"] = inter.get("texto")
                item_plano["tip_tecnico_faq"] = act.get("tip_tecnico_faq")
                faqs_items.append(item_plano)
            else:
                item_plano["comentario"] = inter.get("texto")
                feedback_items.append(item_plano)

        # 2. Estructurar los 4 archivos
        base_meta = {
            "version": "1.0.0",
            "plataforma": "CommunityLab",
            "motor_orquestacion": "python_gemini",
            "fecha_generacion": iso_now,
            "origen_comunidad": archivo_origen,
            "total_interacciones": total_items,
        }

        archivos = {
            "marketing_linkedin_logros.json": {
                "nombre_archivo": "marketing_linkedin_logros.json",
                "metadata": {**base_meta, "categoria": "logros_contratacion"},
                "activos": logros_items,
            },
            "marketing_showcase.json": {
                "nombre_archivo": "marketing_showcase.json",
                "metadata": {**base_meta, "categoria": "proyectos_showcase"},
                "activos": showcase_items,
            },
            "faqs_soporte_tecnico.json": {
                "nombre_archivo": "faqs_soporte_tecnico.json",
                "metadata": {**base_meta, "categoria": "dudas_tecnicas_faqs"},
                "activos": faqs_items,
            },
            "metricas_feedback_comunidad.json": {
                "nombre_archivo": "metricas_feedback_comunidad.json",
                "metadata": {**base_meta, "categoria": "feedback_metricas"},
                "metricas_salud": {
                    "sentimientos": paquete.get("metricas", {}).get("distribucion_sentimiento", {}),
                    "total_feedback": len(feedback_items),
                },
                "activos": feedback_items,
            },
        }

        # 3. Subir los 4 archivos a OCI Object Storage
        subidos = {}
        for fname, data in archivos.items():
            remote_path = f"activos/{date_folder}/{fname}"
            res = self.storage_manager.upload_json_asset(
                data=data,
                object_name=remote_path,
            )
            subidos[fname] = res

        logger.info("☁️ [Python Pipeline] 4 archivos temáticos subidos exitosamente a OCI bajo activos/%s/", date_folder)
        return {
            "status": "success",
            "date_folder": date_folder,
            "archivos_subidos": list(archivos.keys()),
            "detalles": subidos,
        }



def main():
    """Punto de entrada de línea de comandos (CLI) para ejecutar el pipeline."""
    parser = argparse.ArgumentParser(
        description="CommunityLab — Pipeline E2E de Procesamiento con IA y Persistencia OCI"
    )
    parser.add_argument(
        "--input",
        "-i",
        default="data/interacciones_ejemplo.json",
        help="Ruta al archivo JSON de interacciones de entrada.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="data/paquete_procesado.json",
        help="Ruta donde se guardará el paquete JSON resultante localmente.",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Límite máximo de registros a procesar (ej. --limit 3).",
    )
    parser.add_argument(
        "--canal",
        "-c",
        default=None,
        help="Filtrar por canal específico (ej. #logros-y-empleos).",
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=2.0,
        help="Segundos de pausa entre llamadas a la API (por defecto 2.0s).",
    )
    parser.add_argument(
        "--upload-oci",
        action="store_true",
        help="Sube automáticamente el paquete procesado a OCI Object Storage.",
    )

    args = parser.parse_args()

    pipeline = CommunityLabPipeline(delay_between_calls=args.delay)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    try:
        paquete = pipeline.procesar_archivo(
            ruta_input=args.input,
            canal_filtro=args.canal,
            limite=args.limit,
        )
        pipeline.guardar_paquete_json(paquete, args.output)

        oci_info = None
        if args.upload_oci:
            oci_info = pipeline.subir_a_oci(paquete)

        print("\n" + "=" * 60)
        print("  [OK] RESUMEN DE EJECUCION DEL PIPELINE COMMUNITYLAB")
        print("=" * 60)
        meta = paquete["metadata_paquete"]
        metricas = paquete["metricas"]
        print(f"Archivo origen:       {meta['archivo_origen']}")
        print(f"Total procesados:     {meta['total_procesados_exitosamente']}")
        print(f"Fallidos:             {meta['total_fallidos']}")
        print(f"Posts LinkedIn:       {metricas['total_posts_linkedin_generados']}")
        print(f"Tips Técnicos / FAQ:  {metricas['total_tips_faq_generados']}")
        print(f"Sentimiento:          {metricas['distribucion_sentimiento']}")
        print(f"Archivo guardado en:  {args.output}")
        if oci_info:
            print(f"Persistencia OCI:     {oci_info.get('status')} -> {oci_info.get('object_name')}")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error("Error fatal durante la ejecución del pipeline: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
