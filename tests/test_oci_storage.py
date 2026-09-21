"""Pruebas unitarias y de integración para OCIStorageManager."""

import json
import os
import pytest
from pathlib import Path
from dotenv import load_dotenv

from src.cloud_oci.storage_client import OCIStorageManager

load_dotenv()


def has_valid_oci_env() -> bool:
    """Valida si el entorno cuenta con credenciales OCI para pruebas de integración."""
    keys = [
        "OCI_USER_OCID",
        "OCI_TENANCY_OCID",
        "OCI_FINGERPRINT",
        "OCI_KEY_FILE",
        "OCI_REGION",
        "OCI_NAMESPACE",
        "OCI_BUCKET_NAME",
    ]
    for k in keys:
        val = os.getenv(k)
        if not val or "tu_" in val or "xx:xx" in val:
            return False
    key_path = Path(os.path.expanduser(os.getenv("OCI_KEY_FILE", "")))
    return key_path.exists()


@pytest.fixture(scope="module")
def oci_manager():
    """Fixture que retorna una instancia de OCIStorageManager."""
    if not has_valid_oci_env():
        pytest.skip("Credenciales de OCI no configuradas en el entorno.")
    return OCIStorageManager()


class TestOCIStorageManagerIntegration:
    """Suite de pruebas de integración directa con OCI Object Storage."""

    def test_client_initialization(self, oci_manager):
        """Verifica que el cliente se inicialice correctamente."""
        assert oci_manager.client is not None
        assert oci_manager.bucket_name is not None
        assert oci_manager.namespace is not None

    def test_upload_and_get_asset_package(self, oci_manager):
        """Prueba ciclo completo: guardar paquete JSON, descargarlo y verificar igualdad."""
        test_filename = f"test-asset-{os.urandom(4).hex()}.json"
        sample_data = {
            "sentimiento": "positivo",
            "tipo_contenido": "showcase",
            "temas_clave": ["FastAPI", "Oracle Cloud"],
            "post_linkedin": "¡Increíble avance en CommunityLab!",
            "tip_tecnico_faq": None,
        }

        # 1. Subida
        upload_res = oci_manager.upload_asset_package(
            data=sample_data,
            filename=test_filename,
            date_folder="test-folder",
        )
        remote_name = upload_res["object_name"]
        assert remote_name == f"activos/test-folder/{test_filename}"
        assert upload_res["status"] in ("success", 200)

        try:
            # 2. Listado
            assets = oci_manager.list_assets(prefix="activos/test-folder/")
            names = [a["name"] for a in assets]
            assert remote_name in names

            # 3. Descarga y deserialización
            retrieved_data = oci_manager.get_asset_package(remote_name)
            assert retrieved_data == sample_data

            # 4. Creación de URL pre-autenticada (PAR)
            par_info = oci_manager.create_preauthenticated_request(
                object_name=remote_name,
                expires_in_hours=1,
            )
            assert "access_url" in par_info
            assert par_info["access_url"].startswith("https://objectstorage.")
            assert oci_manager.region in par_info["access_url"]

        finally:
            # 5. Limpieza
            oci_manager.delete_object(remote_name)

            # Verificar borrado
            assets_after = oci_manager.list_assets(prefix="activos/test-folder/")
            names_after = [a["name"] for a in assets_after]
            assert remote_name not in names_after
