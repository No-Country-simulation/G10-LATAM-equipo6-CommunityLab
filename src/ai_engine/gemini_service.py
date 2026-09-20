"""Servicio de inferencia con Google Gemini para CommunityLab.

Utiliza el SDK oficial 'google-genai' con el modelo Gemini 1.5 Flash,
garantizando salidas estructuradas en JSON validadas con Pydantic y
resiliencia mediante reintentos con backoff exponencial.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from src.ai_engine.schemas import (
    CommunityInteraction,
    CommunityLabAssetOutput,
    ProcessedCommunityAsset,
)
from src.ai_engine.validator import validate_asset_output

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env si existe
load_dotenv()


class GeminiService:
    """Motor de inferencia y transformación de contenido usando Google Gemini."""

    DEFAULT_MODEL = "gemini-3.6-flash"
    FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        prompt_templates_path: Optional[Path] = None,
    ):
        """Inicializa el cliente de Gemini y carga las plantillas oficiales.

        Args:
            api_key: API Key de Google AI Studio. Si es None, busca GEMINI_API_KEY en .env.
            model: Nombre del modelo (por defecto 'gemini-1.5-flash').
            prompt_templates_path: Ruta a prompt_templates.json.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)

        # Cargar plantillas de prompts
        tpl_path = prompt_templates_path or (Path(__file__).parent / "prompt_templates.json")
        self.templates = self._load_templates(tpl_path)
        self.system_instruction = self.templates.get("prompts", {}).get(
            "system_curator", {}
        ).get("template", "")

        # Inicialización diferida del cliente
        self._client = None

    def _load_templates(self, path: Path) -> Dict[str, Any]:
        """Carga el archivo JSON con las plantillas de prompts del equipo."""
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de plantillas en: {path.resolve()}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def client(self):
        """Instancia autenticada del cliente google-genai (Lazy loading)."""
        if self._client is None:
            if not self.api_key or self.api_key == "tu_gemini_api_key_aqui":
                raise ValueError(
                    "GEMINI_API_KEY no está configurada. Define la variable en tu archivo .env "
                    "o pásala directamente al inicializar GeminiService."
                )
            from google import genai

            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def build_user_prompt(self, interaction: CommunityInteraction) -> str:
        """Construye el prompt de usuario inyectando los datos de la interacción."""
        user_tpl = self.templates.get("prompts", {}).get(
            "user_message_analysis", {}
        ).get("template", "")

        # Reemplazar variables según la plantilla oficial
        prompt = (
            user_tpl.replace("{{ $json.id }}", interaction.id)
            .replace("{{ $json.autor }}", interaction.autor)
            .replace("{{ $json.canal }}", interaction.canal)
            .replace("{{ $json.tipo }}", interaction.tipo)
            .replace("{{ $json.texto }}", interaction.texto)
        )
        return prompt

    def generate_asset(
        self,
        interaction: CommunityInteraction,
        max_retries: int = 3,
        base_delay: float = 2.0,
    ) -> CommunityLabAssetOutput:
        """Envía la interacción a Gemini y devuelve un CommunityLabAssetOutput validado.

        Implementa reintentos automáticos con retroceso exponencial para mitigar
        errores de cuota (429 / Rate Limit / ResourceExhausted).

        Args:
            interaction: Interacción cruda validada.
            max_retries: Cantidad máxima de reintentos antes de fallar.
            base_delay: Tiempo base en segundos para el cálculo del backoff.

        Returns:
            Instancia validada de CommunityLabAssetOutput.
        """
        from google.genai import types

        user_content = self.build_user_prompt(interaction)
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            response_mime_type="application/json",
            temperature=0.2,
        )

        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Enviando interacción %s a %s (intento %d/%d)...",
                    interaction.id,
                    self.model_name,
                    attempt,
                    max_retries,
                )

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_content,
                    config=config,
                )

                raw_text = response.text
                if not raw_text:
                    raise ValueError("El modelo devolvió una respuesta vacía.")

                # Validar con el esquema Pydantic oficial
                validated_asset, err_msg = validate_asset_output(raw_text)
                if validated_asset is None:
                    raise ValueError(f"Fallo en validación de esquema: {err_msg}")

                logger.info(
                    "Procesamiento exitoso para %s: tipo=%s, sentimiento=%s",
                    interaction.id,
                    validated_asset.tipo_contenido.value,
                    validated_asset.sentimiento.value,
                )
                return validated_asset

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                is_rate_limit = (
                    "429" in error_str
                    or "resourceexhausted" in error_str
                    or "quota" in error_str
                    or "rate" in error_str
                )
                is_model_not_found = "404" in error_str or "not found" in error_str
                is_unavailable = (
                    "503" in error_str
                    or "unavailable" in error_str
                    or "high demand" in error_str
                )

                if (is_model_not_found or is_unavailable) and attempt < max_retries:
                    for fallback in self.FALLBACK_MODELS:
                        if fallback != self.model_name:
                            logger.warning(
                                "Modelo '%s' con error (%s). Cambiando automáticamente al modelo '%s'...",
                                self.model_name,
                                "404 No Encontrado" if is_model_not_found else "503 Alta Demanda",
                                fallback,
                            )
                            self.model_name = fallback
                            break
                    time.sleep(2.0)
                elif attempt < max_retries and is_rate_limit:
                    sleep_time = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        "Límite de cuota detectado para %s. Reintentando en %.1fs (intento %d)...",
                        interaction.id,
                        sleep_time,
                        attempt,
                    )
                    time.sleep(sleep_time)
                elif attempt < max_retries:
                    logger.warning("Error en intento %d para %s: %s. Reintentando...", attempt, interaction.id, e)
                    time.sleep(base_delay)
                else:
                    logger.error("Se agotaron los %d intentos para %s.", max_retries, interaction.id)

        raise RuntimeError(
            f"No fue posible procesar la interacción {interaction.id} tras {max_retries} intentos: {last_error}"
        ) from last_error

    def process_interaction(
        self,
        interaction: CommunityInteraction,
        max_retries: int = 3,
    ) -> ProcessedCommunityAsset:
        """Procesa una interacción y devuelve el modelo enriquecido consolidado."""
        asset = self.generate_asset(interaction, max_retries=max_retries)
        return ProcessedCommunityAsset(interaccion=interaction, activo=asset)
