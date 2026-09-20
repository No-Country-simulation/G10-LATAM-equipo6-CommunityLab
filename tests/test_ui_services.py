"""Pruebas unitarias para la capa de servicios de la interfaz (src/ui/services.py)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.ui.services import (
    cargar_paquete,
    guardar_curaduria_humana,
    obtener_ultimos_paquetes,
    procesar_archivo_ui,
)


def test_guardar_curaduria_humana(tmp_path: Path):
    """Verifica que la decisión del Community Manager se persista correctamente."""
    registro_path = tmp_path / "curaduria_test.json"

    res = guardar_curaduria_humana(
        id_interaccion="msg_001",
        copy_aprobado="Texto editado y aprobado por el curador.",
        estado_aprobacion="aprobado",
        notas="Excelente gancho",
        ruta_registro=registro_path,
    )

    assert res["id_interaccion"] == "msg_001"
    assert res["estado"] == "aprobado"
    assert registro_path.exists()

    # Verificar lectura
    datos = json.loads(registro_path.read_text(encoding="utf-8"))
    assert len(datos) == 1
    assert datos[0]["copy_aprobado"] == "Texto editado y aprobado por el curador."


def test_obtener_ultimos_paquetes_mock():
    """Verifica el listado ordenado de paquetes disponibles para la UI."""
    mock_sm = MagicMock()
    mock_sm.list_assets.return_value = [
        {"name": "activos/2026-09-18/paquete-1.json", "created_at": "2026-09-18T10:00:00"},
        {"name": "activos/2026-09-19/paquete-2.json", "created_at": "2026-09-19T10:00:00"},
    ]

    paquetes = obtener_ultimos_paquetes(storage_manager=mock_sm, limite=5)
    assert len(paquetes) == 2
    # El más reciente primero
    assert paquetes[0]["name"] == "activos/2026-09-19/paquete-2.json"


def test_cargar_paquete_mock():
    """Verifica la carga del contenido de un paquete específico."""
    mock_sm = MagicMock()
    mock_sm.get_asset.return_value = {
        "metadata_paquete": {"version": "1.0.0"},
        "activos": [{"interaccion": {"id": "msg_01"}}],
    }

    contenido = cargar_paquete("activos/demo.json", storage_manager=mock_sm)
    assert contenido is not None
    assert contenido["metadata_paquete"]["version"] == "1.0.0"


@patch("src.ui.services.CommunityLabPipeline")
def test_procesar_archivo_ui_mock(mock_pipeline_class, tmp_path: Path):
    """Verifica que la función disparada desde Streamlit llame a CommunityLabPipeline."""
    mock_instance = MagicMock()
    mock_instance.procesar_archivo.return_value = {
        "metadata_paquete": {"total_procesados_exitosamente": 2},
        "metricas": {},
        "activos": [],
    }
    mock_instance.subir_a_oci.return_value = {"status": "success"}
    mock_pipeline_class.return_value = mock_instance

    dummy_input = tmp_path / "dummy.json"
    dummy_input.write_text("{}", encoding="utf-8")

    paquete = procesar_archivo_ui(
        ruta_archivo=dummy_input,
        limite=2,
        upload_oci=True,
    )

    assert paquete["metadata_paquete"]["total_procesados_exitosamente"] == 2
    assert paquete["metadata_paquete"]["persistencia_oci"]["status"] == "success"
    assert mock_instance.procesar_archivo.called
    assert mock_instance.subir_a_oci.called
