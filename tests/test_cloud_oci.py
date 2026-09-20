"""Pruebas unitarias para el cliente de OCI Object Storage (src/cloud_oci)."""

import json
from pathlib import Path
from unittest.mock import MagicMock
import pytest

from src.cloud_oci.storage_client import OCIStorageManager


@pytest.fixture
def sample_payload() -> dict:
    return {
        "metadata_paquete": {"version": "1.0.0", "total": 1},
        "activos": [
            {
                "interaccion": {"id": "msg_001", "autor": "Carlos Test"},
                "activo": {"sentimiento": "positivo", "post_linkedin": "Gran post de prueba"}
            }
        ]
    }


def test_oci_local_fallback_mode_upload_and_read(tmp_path: Path, sample_payload: dict):
    """Verifica que el modo fallback local guarde en disco y permita recuperar el JSON."""
    manager = OCIStorageManager(allow_local_fallback=True)
    manager.LOCAL_FALLBACK_DIR = tmp_path

    # Subida
    res = manager.upload_json_asset(sample_payload, object_name="test/paquete.json")
    assert res["status"] == "success_local_fallback"
    assert res["object_name"] == "test/paquete.json"
    assert (tmp_path / "test/paquete.json").exists()

    # Lectura
    recuperado = manager.get_asset("test/paquete.json")
    assert recuperado["metadata_paquete"]["version"] == "1.0.0"
    assert len(recuperado["activos"]) == 1

    # Listado
    lista = manager.list_assets(prefix="test")
    assert len(lista) == 1
    assert "paquete.json" in lista[0]["name"]


def test_oci_local_fallback_par():
    """Verifica que en modo local se genere una URL PAR simulada."""
    manager = OCIStorageManager(allow_local_fallback=True)
    par = manager.create_preauthenticated_request("activos/paquete.json", expires_in_hours=12)
    assert par["id"] == "par-mock-local-id"
    assert "http://" in par["access_url"]
    assert "expires_at" in par


def test_oci_cloud_mode_upload_mock(sample_payload: dict):
    """Verifica el flujo con el SDK real de OCI simulado con Mocks."""
    mock_client = MagicMock()
    mock_put_response = MagicMock()
    mock_put_response.headers = {"etag": "mock-cloud-etag-1234"}
    mock_client.put_object.return_value = mock_put_response

    mock_ns_response = MagicMock()
    mock_ns_response.data = "my-test-namespace"
    mock_client.get_namespace.return_value = mock_ns_response

    manager = OCIStorageManager(
        client=mock_client,
        allow_local_fallback=False,
        namespace_name="my-test-namespace",
    )
    manager.oci_config = {"region": "sa-bogota-1"}

    result = manager.upload_json_asset(sample_payload, object_name="activos/test.json")

    assert result["status"] == "success"
    assert result["etag"] == "mock-cloud-etag-1234"
    assert mock_client.put_object.called

    # Comprobar llamada
    call_args = mock_client.put_object.call_args[1]
    assert call_args["namespace_name"] == "my-test-namespace"
    assert call_args["object_name"] == "activos/test.json"
    assert call_args["content_type"] == "application/json; charset=utf-8"


def test_oci_cloud_mode_get_asset_mock(sample_payload: dict):
    """Verifica la descarga de un objeto desde OCI usando Mock."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data.content = json.dumps(sample_payload).encode("utf-8")
    mock_client.get_object.return_value = mock_response

    manager = OCIStorageManager(
        client=mock_client,
        allow_local_fallback=False,
        namespace_name="my-namespace",
    )

    asset = manager.get_asset("activos/demo.json")
    assert asset["metadata_paquete"]["total"] == 1
    assert mock_client.get_object.called


def test_oci_cloud_mode_list_assets_mock():
    """Verifica el listado de objetos desde OCI usando Mock."""
    mock_client = MagicMock()
    mock_item = MagicMock()
    mock_item.name = "activos/2026-09-19/paquete-1.json"
    mock_item.size = 2048
    mock_item.time_created = None
    mock_item.etag = "etag-1"

    mock_response = MagicMock()
    mock_response.data.objects = [mock_item]
    mock_client.list_objects.return_value = mock_response

    manager = OCIStorageManager(
        client=mock_client,
        allow_local_fallback=False,
        namespace_name="my-namespace",
    )

    lista = manager.list_assets(prefix="activos")
    assert len(lista) == 1
    assert lista[0]["name"] == "activos/2026-09-19/paquete-1.json"
    assert lista[0]["size"] == 2048


def test_oci_upload_invalid_type_raises():
    """Verifica que tipos no soportados lancen TypeError."""
    manager = OCIStorageManager(allow_local_fallback=True)
    with pytest.raises(TypeError, match="Tipo de dato no soportado"):
        manager.upload_json_asset(12345)
