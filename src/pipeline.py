"""Orquestador E2E del Pipeline de CommunityLab.

Integra el módulo de ingesta, el motor de inferencia de Gemini y la consolidación
de paquetes de distribución con métricas para persistencia y curaduría.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Union

from src.ai_engine.gemini_service import GeminiService
from src.ai_engine.schemas import (
    CommunityInteraction,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.ingestion.data_loader import (
    cargar_interacciones_desde_json,
    filtrar_por_canal,
    filtrar_por_tipo,
    generar_lotes,
)

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("CommunityLabPipeline")


class CommunityLabPipeline:
    """Pipeline orquestador para procesar interacciones orgánicas de la comunidad."""

    def __init__(
        self,
        ai_service: Optional[GeminiService] = None,
        delay_between_calls: float = 2.0,
    ):
        """Inicializa el pipeline orquestador.

        Args:
            ai_service: Instancia de GeminiService. Si es None, se crea una por defecto.
            delay_between_calls: Segundos de pausa entre cada llamada a la API
                                 para respetar cuotas de Rate Limit (por defecto 2.0s).
        """
        self.ai_service = ai_service or GeminiService()
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
    ) -> Dict[str, Any]:
        """Ejecuta el pipeline completo sobre un archivo JSON de interacciones.

        Args:
            ruta_input: Ruta al archivo JSON con las interacciones crudas.
            canal_filtro: Opcional, canal a filtrar (ej. '#logros-y-empleos').
            tipo_filtro: Opcional, tipo a filtrar (ej. 'testimonio').
            limite: Cantidad máxima de registros a procesar (útil para pruebas).

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
                resultado = self.procesar_interaccion(item)
                activos_procesados.append(resultado)

            except Exception as e:
                logger.error("Error al procesar registro %s: %s", item.id, e)
                fallidos.append({"id": item.id, "autor": item.autor, "error": str(e)})

            # Pausa preventiva entre llamadas (excepto en el último ítem)
            if idx < total_a_procesar and self.delay_between_calls > 0:
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


def main():
    """Punto de entrada de línea de comandos (CLI) para ejecutar el pipeline."""
    parser = argparse.ArgumentParser(
        description="CommunityLab — Pipeline E2E de Procesamiento con IA"
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
        help="Ruta donde se guardará el paquete JSON resultante.",
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

    args = parser.parse_args()

    pipeline = CommunityLabPipeline(delay_between_calls=args.delay)

    try:
        paquete = pipeline.procesar_archivo(
            ruta_input=args.input,
            canal_filtro=args.canal,
            limite=args.limit,
        )
        pipeline.guardar_paquete_json(paquete, args.output)

        print("\n" + "=" * 60)
        print("  🎉 RESUMEN DE EJECUCIÓN DEL PIPELINE COMMUNITYLAB")
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
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error("Error fatal durante la ejecución del pipeline: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
