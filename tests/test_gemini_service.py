"""Pruebas unitarias para el servicio de inferencia con Google Gemini (src/ai_engine)."""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.ai_engine.gemini_service import GeminiService
from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
    SentimientoEnum,
    TipoContenidoEnum,
)


@pytest.fixture
def sample_interaction_logro() -> CommunityInteraction:
    return CommunityInteraction(
        id="test_001",
        autor="Carlos Test",
        canal="#logros-y-empleos",
        tipo="testimonio",
        texto="¡Conseguí empleo como Backend Developer gracias a Oracle ONE!",
    )


@pytest.fixture
def sample_interaction_duda() -> CommunityInteraction:
    return CommunityInteraction(
        id="test_002",
        autor="Laura Test",
        canal="#dudas-cloud-oci",
        tipo="pregunta_tecnica",
        texto="¿Cómo resolver el error 401 en OCI al conectar el bucket?",
    )


def test_build_user_prompt(sample_interaction_logro: CommunityInteraction):
    """Verifica que el prompt de usuario inyecte correctamente todas las variables."""
    service = GeminiService(api_key="fake-key")
    prompt = service.build_user_prompt(sample_interaction_logro)

    assert "test_001" in prompt
    assert "Carlos Test" in prompt
    assert "#logros-y-empleos" in prompt
    assert "Backend Developer" in prompt


def test_missing_api_key_raises_value_error(sample_interaction_logro: CommunityInteraction):
    """Verifica que al no tener API key configurada se lance ValueError explicativo."""
    with patch.dict("os.environ", {}, clear=True):
        service = GeminiService(api_key=None)
        with pytest.raises(ValueError, match="GEMINI_API_KEY no está configurada"):
            _ = service.client


@patch("google.genai.Client")
def test_generate_asset_logro_success(mock_genai_client_class, sample_interaction_logro: CommunityInteraction):
    """Verifica el flujo exitoso para un testimonio generando post de LinkedIn."""
    mock_client = MagicMock()
    mock_genai_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "sentimiento": "positivo",
        "tipo_contenido": "logro_contratacion",
        "temas_clave": ["Oracle", "Backend", "Java"],
        "post_linkedin": "🎉 ¡Orgullo de comunidad! Carlos Test consiguió su empleo como Backend Developer... #OracleONE",
        "tip_tecnico_faq": None
    })
    mock_client.models.generate_content.return_value = mock_response

    service = GeminiService(api_key="valid-test-key")
    service._client = mock_client

    asset = service.generate_asset(sample_interaction_logro)

    assert isinstance(asset, CommunityLabAssetOutput)
    assert asset.sentimiento == SentimientoEnum.POSITIVO
    assert asset.tipo_contenido == TipoContenidoEnum.LOGRO_CONTRATACION
    assert "Carlos Test" in asset.post_linkedin
    assert asset.tip_tecnico_faq is None


@patch("google.genai.Client")
def test_generate_asset_duda_tecnica_success(mock_genai_client_class, sample_interaction_duda: CommunityInteraction):
    """Verifica el flujo exitoso para una duda técnica generando tip_tecnico_faq."""
    mock_client = MagicMock()
    mock_genai_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "sentimiento": "neutro",
        "tipo_contenido": "duda_tecnica",
        "temas_clave": ["OCI", "Object Storage", "Autenticación"],
        "post_linkedin": None,
        "tip_tecnico_faq": "### Solución al error 401 en OCI:\nVerifica tu archivo ~/.oci/config y que la llave privada tenga permisos 400."
    })
    mock_client.models.generate_content.return_value = mock_response

    service = GeminiService(api_key="valid-test-key")
    service._client = mock_client

    asset = service.generate_asset(sample_interaction_duda)

    assert isinstance(asset, CommunityLabAssetOutput)
    assert asset.tipo_contenido == TipoContenidoEnum.DUDA_TECNICA
    assert asset.post_linkedin is None
    assert "error 401" in asset.tip_tecnico_faq


@patch("google.genai.Client")
def test_generate_asset_retry_on_rate_limit(mock_genai_client_class, sample_interaction_logro: CommunityInteraction):
    """Verifica que el servicio reintente si recibe un error 429 de Rate Limit."""
    mock_client = MagicMock()
    mock_genai_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "sentimiento": "positivo",
        "tipo_contenido": "logro_contratacion",
        "temas_clave": ["Oracle"],
        "post_linkedin": "Post exitoso tras reintento",
        "tip_tecnico_faq": None
    })

    # El primer intento falla con error 429; el segundo responde exitosamente
    mock_client.models.generate_content.side_effect = [
        RuntimeError("Error 429: ResourceExhausted quota exceeded"),
        mock_response
    ]

    service = GeminiService(api_key="valid-test-key")
    service._client = mock_client

    asset = service.generate_asset(sample_interaction_logro, max_retries=2, base_delay=0.01)
    assert asset.post_linkedin == "Post exitoso tras reintento"
    assert mock_client.models.generate_content.call_count == 2


@patch("google.genai.Client")
def test_process_interaction_returns_processed_community_asset(mock_genai_client_class, sample_interaction_logro: CommunityInteraction):
    """Verifica que process_interaction consolide interacción y activo en ProcessedCommunityAsset."""
    mock_client = MagicMock()
    mock_genai_client_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "sentimiento": "positivo",
        "tipo_contenido": "logro_contratacion",
        "temas_clave": ["Python", "Gemini"],
        "post_linkedin": "Gran logro para compartir",
        "tip_tecnico_faq": None
    })
    mock_client.models.generate_content.return_value = mock_response

    service = GeminiService(api_key="valid-test-key")
    service._client = mock_client

    processed = service.process_interaction(sample_interaction_logro)

    assert isinstance(processed, ProcessedCommunityAsset)
    assert processed.interaccion.id == "test_001"
    assert processed.activo.sentimiento == SentimientoEnum.POSITIVO
