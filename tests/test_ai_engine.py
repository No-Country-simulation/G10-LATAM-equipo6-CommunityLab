"""Pruebas unitarias para la validación programática con Pydantic del motor de IA."""

import pytest
from pydantic import ValidationError

from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    SentimientoEnum,
    TipoContenidoEnum,
)
from src.ai_engine.validator import (
    extract_json_payload,
    validate_asset_output,
    validate_batch_file,
)


def test_valid_community_interaction():
    data = {
        "id": "msg_test_01",
        "autor": "Ana Silva",
        "canal": "#general",
        "tipo": "testimonio",
        "texto": "Feliz por terminar el curso de Cloud en OCI!"
    }
    interaction = CommunityInteraction.model_validate(data)
    assert interaction.id == "msg_test_01"
    assert interaction.autor == "Ana Silva"


def test_invalid_community_interaction():
    # Falta el campo requerido 'texto'
    data = {
        "id": "msg_test_02",
        "autor": "Carlos",
        "canal": "#dudas",
        "tipo": "pregunta"
    }
    with pytest.raises(ValidationError):
        CommunityInteraction.model_validate(data)


def test_valid_asset_output_logro():
    data = {
        "sentimiento": "positivo",
        "tipo_contenido": "logro_contratacion",
        "temas_clave": ["OCI", "Docker"],
        "post_linkedin": "Emocionado de anunciar mi nuevo rol como Cloud Architect! #OracleONE",
        "tip_tecnico_faq": None
    }
    asset, error = validate_asset_output(data)
    assert error is None
    assert asset is not None
    assert asset.sentimiento == SentimientoEnum.POSITIVO
    assert asset.tipo_contenido == TipoContenidoEnum.LOGRO_CONTRATACION
    assert len(asset.temas_clave) == 2


def test_valid_asset_output_duda_tecnica():
    data = {
        "sentimiento": "neutro",
        "tipo_contenido": "duda_tecnica",
        "temas_clave": ["Python", "FastAPI"],
        "post_linkedin": None,
        "tip_tecnico_faq": "Para resolver el error 401 en OCI, verifica tus API Keys en ~/.oci/config."
    }
    asset, error = validate_asset_output(data)
    assert error is None
    assert asset is not None
    assert asset.tip_tecnico_faq is not None


def test_invalid_consistency_logro_without_post():
    # Si es logro_contratacion, post_linkedin no puede ser None
    data = {
        "sentimiento": "positivo",
        "tipo_contenido": "logro_contratacion",
        "temas_clave": ["Java"],
        "post_linkedin": None,
        "tip_tecnico_faq": None
    }
    asset, error = validate_asset_output(data)
    assert asset is None
    assert error is not None
    assert "post_linkedin" in error


def test_invalid_consistency_duda_without_faq():
    # Si es duda_tecnica, tip_tecnico_faq no puede ser None
    data = {
        "sentimiento": "negativo",
        "tipo_contenido": "duda_tecnica",
        "temas_clave": ["SQL"],
        "post_linkedin": None,
        "tip_tecnico_faq": None
    }
    asset, error = validate_asset_output(data)
    assert asset is None
    assert error is not None
    assert "tip_tecnico_faq" in error


def test_extract_json_from_markdown_block():
    raw_markdown = """
    Aquí está la respuesta:
    ```json
    {
      "sentimiento": "positivo",
      "tipo_contenido": "feedback_general",
      "temas_clave": ["Alura"],
      "post_linkedin": null,
      "tip_tecnico_faq": null
    }
    ```
    Espero te sirva.
    """
    extracted = extract_json_payload(raw_markdown)
    asset, error = validate_asset_output(extracted)
    assert error is None
    assert asset is not None
    assert asset.tipo_contenido == TipoContenidoEnum.FEEDBACK_GENERAL


def test_validate_sample_dataset_batch():
    summary = validate_batch_file("data/interacciones_ejemplo.json")
    assert summary["total"] == 15
    assert summary["validos"] == 15
    assert summary["fallidos"] == 0
