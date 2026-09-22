"""Pruebas unitarias para el pipeline orquestador E2E (src/pipeline.py)."""

from pathlib import Path
from unittest.mock import MagicMock
import pytest

from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.pipeline import CommunityLabPipeline


@pytest.fixture
def dataset_oficial() -> Path:
    return Path(__file__).parents[1] / "data" / "interacciones_ejemplo.json"


@pytest.fixture
def mock_ai_service():
    """Mock del servicio de IA que responde coherentemente según el tipo de interacción."""
    service = MagicMock()

    def fake_process(interaction: CommunityInteraction) -> ProcessedCommunityAsset:
        if interaction.tipo == "testimonio":
            activo = CommunityLabAssetOutput(
                sentimiento=SentimientoEnum.POSITIVO,
                tipo_contenido=TipoContenidoEnum.LOGRO_CONTRATACION,
                temas_clave=["Java", "Oracle"],
                post_linkedin=f"¡Felicidades a {interaction.autor}! Gran testimonio de superación.",
                tip_tecnico_faq=None,
            )
        elif interaction.tipo == "pregunta_tecnica":
            activo = CommunityLabAssetOutput(
                sentimiento=SentimientoEnum.NEUTRO,
                tipo_contenido=TipoContenidoEnum.DUDA_TECNICA,
                temas_clave=["OCI", "Docker"],
                post_linkedin=None,
                tip_tecnico_faq="### Solución paso a paso a la duda planteada.",
            )
        else:
            activo = CommunityLabAssetOutput(
                sentimiento=SentimientoEnum.NEUTRO,
                tipo_contenido=TipoContenidoEnum.FEEDBACK_GENERAL,
                temas_clave=["Comunidad"],
                post_linkedin=None,
                tip_tecnico_faq=None,
            )

        return ProcessedCommunityAsset(interaccion=interaction, activo=activo)

    service.process_interaction.side_effect = fake_process
    return service


def test_pipeline_procesar_archivo_con_limite(dataset_oficial: Path, mock_ai_service):
    """Verifica que el pipeline procese correctamente un lote respetando el límite."""
    pipeline = CommunityLabPipeline(ai_service=mock_ai_service, delay_between_calls=0.0)
    
    paquete = pipeline.procesar_archivo(dataset_oficial, limite=3)
    
    meta = paquete["metadata_paquete"]
    assert meta["total_registros_origen"] == 15
    assert meta["total_procesados_exitosamente"] == 3
    assert meta["total_fallidos"] == 0
    assert len(paquete["activos"]) == 3


def test_pipeline_metricas_consolidadas(dataset_oficial: Path, mock_ai_service):
    """Verifica el cálculo preciso de métricas de sentimiento y contenidos generados."""
    pipeline = CommunityLabPipeline(ai_service=mock_ai_service, delay_between_calls=0.0)
    
    # Procesar archivo completo (15 interacciones)
    paquete = pipeline.procesar_archivo(dataset_oficial)
    metricas = paquete["metricas"]
    
    assert metricas["total_posts_linkedin_generados"] > 0
    assert metricas["total_tips_faq_generados"] > 0
    
    sentimientos = metricas["distribucion_sentimiento"]
    assert sentimientos["positivo"] > 0
    assert sentimientos["neutro"] > 0
    assert sentimientos["positivo"] + sentimientos["neutro"] + sentimientos["negativo"] == 15


def test_pipeline_filtro_por_canal(dataset_oficial: Path, mock_ai_service):
    """Verifica que el pipeline filtre por canal antes de procesar."""
    pipeline = CommunityLabPipeline(ai_service=mock_ai_service, delay_between_calls=0.0)
    
    paquete = pipeline.procesar_archivo(
        dataset_oficial,
        canal_filtro="#logros-y-empleos"
    )
    
    for item in paquete["activos"]:
        assert item["interaccion"]["canal"] == "#logros-y-empleos"


def test_pipeline_guardar_paquete_json(dataset_oficial: Path, mock_ai_service, tmp_path: Path):
    """Verifica que el archivo JSON de salida se guarde correctamente y sea parseable."""
    pipeline = CommunityLabPipeline(ai_service=mock_ai_service, delay_between_calls=0.0)
    
    paquete = pipeline.procesar_archivo(dataset_oficial, limite=2)
    out_file = tmp_path / "resultado.json"
    
    saved_path = pipeline.guardar_paquete_json(paquete, out_file)
    assert saved_path.exists()
    assert saved_path.stat().st_size > 0


def test_pipeline_resiliencia_continua_ante_fallas_individuales(dataset_oficial: Path):
    """Verifica que un fallo en un ítem específico no interrumpa el procesamiento del resto del lote."""
    mock_service = MagicMock()
    
    # Simular que el primer ítem falla y el segundo es exitoso
    activo_exitoso = CommunityLabAssetOutput(
        sentimiento=SentimientoEnum.POSITIVO,
        tipo_contenido=TipoContenidoEnum.LOGRO_CONTRATACION,
        temas_clave=["Python"],
        post_linkedin="Post exitoso",
        tip_tecnico_faq=None,
    )
    
    def side_effect(interaction):
        if interaction.id == "msg_001":
            raise RuntimeError("Error temporal simulado en IA")
        return ProcessedCommunityAsset(interaccion=interaction, activo=activo_exitoso)
        
    mock_service.process_interaction.side_effect = side_effect
    
    pipeline = CommunityLabPipeline(ai_service=mock_service, delay_between_calls=0.0)
    paquete = pipeline.procesar_archivo(dataset_oficial, limite=2)
    
    meta = paquete["metadata_paquete"]
    assert meta["total_procesados_exitosamente"] == 1
    assert meta["total_fallidos"] == 1
    assert len(paquete["fallidos"]) == 1
    assert paquete["fallidos"][0]["id"] == "msg_001"


def test_pipeline_subir_a_oci_4_archivos_especializados(dataset_oficial: Path, mock_ai_service):
    """Verifica que el pipeline Python suba los 4 archivos temáticos consistentes con n8n."""
    mock_storage = MagicMock()
    mock_storage.upload_json_asset.return_value = {"status": "success"}

    pipeline = CommunityLabPipeline(
        ai_service=mock_ai_service,
        storage_manager=mock_storage,
        delay_between_calls=0.0,
    )
    paquete = pipeline.procesar_archivo(dataset_oficial, limite=3)
    res = pipeline.subir_a_oci(paquete)

    assert res["status"] == "success"
    assert len(res["archivos_subidos"]) == 4
    assert "marketing_linkedin_logros.json" in res["archivos_subidos"]
    assert "marketing_showcase.json" in res["archivos_subidos"]
    assert "faqs_soporte_tecnico.json" in res["archivos_subidos"]
    assert "metricas_feedback_comunidad.json" in res["archivos_subidos"]
    assert mock_storage.upload_json_asset.call_count == 4

