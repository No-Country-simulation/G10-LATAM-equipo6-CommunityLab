"""Pruebas unitarias para el cliente de OCI Object Storage usando Mocks."""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.cloud_oci.storage_client import OCIStorageManager


@pytest.fixture
def mock_oci_config():
    return {
        "user": "ocid1.user.oc1..test",
        "tenancy": "ocid1.tenancy.oc1..test",
        "fingerprint": "11:22:33:44:55:66:77:88",
        "key_file": "/tmp/dummy_key.pem",
        "region": "sa-bogota-1"
    }


def test_init_with_explicit_config(mock_oci_config):
    with patch("oci.object_storage.ObjectStorageClient") as mock_client:
        manager = OCIStorageManager(
            config=mock_oci_config,
            bucket_name="test-bucket",
            namespace_name="test-namespace"
        )
        assert manager.bucket_name == "test-bucket"
        assert manager.get_namespace() == "test-namespace"
        mock_client.assert_called_once_with(mock_oci_config)


def test_upload_json_asset_dict(mock_oci_config):
    with patch("oci.object_storage.ObjectStorageClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        mock_instance.put_object.return_value = MagicMock(headers={"etag": "etag12345"})

        manager = OCIStorageManager(
            config=mock_oci_config,
            bucket_name="communitylab-bucket",
            namespace_name="test-namespace"
        )

        sample_data = {
            "metadata": {"origen": "discord"},
            "activos": {"total": 5}
        }

        result = manager.upload_json_asset(
            data=sample_data,
            object_name="activos/2026-09-18/paquete-test.json"
        )

        assert result["status"] == "success"
        assert result["object_name"] == "activos/2026-09-18/paquete-test.json"
        assert result["etag"] == "etag12345"
        assert result["size_bytes"] > 0
        mock_instance.put_object.assert_called_once()


def test_get_asset(mock_oci_config):
    with patch("oci.object_storage.ObjectStorageClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance

        expected_data = {"proyecto": "CommunityLab", "total": 15}
        mock_response = MagicMock()
        mock_response.data.content = json.dumps(expected_data).encode("utf-8")
        mock_instance.get_object.return_value = mock_response

        manager = OCIStorageManager(
            config=mock_oci_config,
            bucket_name="communitylab-bucket",
            namespace_name="test-namespace"
        )

        data = manager.get_asset("activos/2026-09-18/paquete-test.json")
        assert data["proyecto"] == "CommunityLab"
        assert data["total"] == 15
        mock_instance.get_object.assert_called_once_with(
            namespace_name="test-namespace",
            bucket_name="communitylab-bucket",
            object_name="activos/2026-09-18/paquete-test.json"
        )


def test_list_assets(mock_oci_config):
    with patch("oci.object_storage.ObjectStorageClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance

        mock_obj1 = MagicMock(name="obj1", size=1024, time_created=None, etag="etag1")
        mock_obj1.name = "activos/paquete-01.json"
        mock_response = MagicMock()
        mock_response.data.objects = [mock_obj1]
        mock_instance.list_objects.return_value = mock_response

        manager = OCIStorageManager(
            config=mock_oci_config,
            bucket_name="communitylab-bucket",
            namespace_name="test-namespace"
        )

        assets = manager.list_assets(prefix="activos")
        assert len(assets) == 1
        assert assets[0]["name"] == "activos/paquete-01.json"
        assert assets[0]["size"] == 1024


def test_create_preauthenticated_request(mock_oci_config):
    with patch("oci.object_storage.ObjectStorageClient") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance

        mock_par_response = MagicMock()
        mock_par_response.data.id = "par-id-123"
        mock_par_response.data.access_uri = "/p/sample-token/n/test-ns/b/communitylab-bucket/o/activos/paquete.json"
        mock_instance.create_preauthenticated_request.return_value = mock_par_response

        manager = OCIStorageManager(
            config=mock_oci_config,
            bucket_name="communitylab-bucket",
            namespace_name="test-namespace"
        )

        par_result = manager.create_preauthenticated_request(
            object_name="activos/paquete.json",
            expires_in_hours=12
        )

        assert par_result["id"] == "par-id-123"
        assert "access_url" in par_result
        assert "objectstorage.sa-bogota-1.oraclecloud.com" in par_result["access_url"]
        mock_instance.create_preauthenticated_request.assert_called_once()
