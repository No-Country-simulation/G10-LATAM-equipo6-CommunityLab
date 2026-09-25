"""Modelos Pydantic para validación estricta de entradas y salidas del motor de IA.

Basado en el esquema oficial definido en src/ai_engine/prompt_templates.json.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class SentimientoEnum(str, Enum):
    POSITIVO = "positivo"
    NEUTRO = "neutro"
    NEGATIVO = "negativo"


class TipoContenidoEnum(str, Enum):
    LOGRO_CONTRATACION = "logro_contratacion"
    DUDA_TECNICA = "duda_tecnica"
    FEEDBACK_GENERAL = "feedback_general"
    SHOWCASE = "showcase"


class CommunityInteraction(BaseModel):
    """Modelo para representar una interacción cruda de la comunidad."""
    id: str = Field(..., description="Identificador único del mensaje")
    autor: str = Field(..., description="Nombre del autor del mensaje")
    canal: str = Field(..., description="Canal de procedencia (ej. #logros-y-empleos)")
    tipo: str = Field(..., description="Tipo original declarado en la ingesta")
    texto: str = Field(..., min_length=1, description="Contenido textual de la interacción")


class CommunityLabAssetOutput(BaseModel):
    """Modelo de salida estructurada generado por el motor de IA."""
    sentimiento: SentimientoEnum = Field(
        ...,
        description="Sentimiento clasificado: positivo, neutro o negativo"
    )
    tipo_contenido: TipoContenidoEnum = Field(
        ...,
        description="Categoría de contenido identificada"
    )
    temas_clave: List[str] = Field(
        ...,
        min_length=1,
        max_length=4,
        description="Entre 1 y 4 tecnologías o conceptos clave identificados"
    )
    respuesta_chat: Optional[str] = Field(
        None,
        description="Respuesta directa, empática y conversacional para el usuario si proviene de un canal"
    )
    post_linkedin: Optional[str] = Field(
        None,
        description="Copy redactado para LinkedIn (obligatorio para logros y showcase, null en otros casos)"
    )
    tip_tecnico_faq: Optional[str] = Field(
        None,
        description="Solución técnica clara estilo FAQ (obligatorio para dudas técnicas, null en otros casos)"
    )

    @model_validator(mode="after")
    def validate_content_consistency(self) -> "CommunityLabAssetOutput":
        """Valida que los artefactos generados correspondan coherentemente al tipo de contenido."""
        # Validación para posts de LinkedIn
        if self.tipo_contenido in (TipoContenidoEnum.LOGRO_CONTRATACION, TipoContenidoEnum.SHOWCASE):
            if not self.post_linkedin or not self.post_linkedin.strip():
                raise ValueError(
                    f"Para tipo_contenido='{self.tipo_contenido.value}', 'post_linkedin' no puede ser nulo ni vacío."
                )

        # Validación para Tips Técnicos / FAQ
        if self.tipo_contenido == TipoContenidoEnum.DUDA_TECNICA:
            if not self.tip_tecnico_faq or not self.tip_tecnico_faq.strip():
                raise ValueError(
                    "Para tipo_contenido='duda_tecnica', 'tip_tecnico_faq' no puede ser nulo ni vacío."
                )

        return self


class ProcessedCommunityAsset(BaseModel):
    """Modelo enriquecido que combina la interacción original con el activo generado."""
    interaccion: CommunityInteraction
    activo: CommunityLabAssetOutput
