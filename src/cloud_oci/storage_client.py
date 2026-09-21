"""Cliente y administrador de almacenamiento en Oracle Cloud Infrastructure (OCI) Object Storage.

Provee operaciones de subida, descarga, listado y generación de solicitudes
pre-autenticadas (PAR) para activos de marketing y reportes de CommunityLab.
"""

from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import oci
from dotenv import load_dotenv

# Cargar variables de entorno si no están cargadas
load_dotenv()


class OCIStorageManager:
    """Administrador de operaciones en OCI Object Storage."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        bucket_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        user_ocid: Optional[str] = None,
        tenancy_ocid: Optional[str] = None,
        fingerprint: Optional[str] = None,
        key_file: Optional[str] = None,
        region: Optional[str] = None,
    ) -> None:
        """Inicializa el cliente de OCI Object Storage.
        
        Permite recibir un diccionario `config` directo (compatible con tests y mocks)
        o construirlo mediante argumentos / variables de entorno.
        """
        if config:
            self.config = config
            self.user_ocid = config.get("user")
            self.tenancy_ocid = config.get("tenancy")
            self.fingerprint = config.get("fingerprint")
            self.key_file = config.get("key_file")
            self.region = config.get("region", "us-ashburn-1")
        else:
            self.user_ocid = user_ocid or os.getenv("OCI_USER_OCID")
            self.tenancy_ocid = tenancy_ocid or os.getenv("OCI_TENANCY_OCID")
            self.fingerprint = fingerprint or os.getenv("OCI_FINGERPRINT")
            self.region = region or os.getenv("OCI_REGION", "us-ashburn-1")

            raw_key_file = key_file or os.getenv("OCI_KEY_FILE", "~/.oci/oci_api_key.pem")
            self.key_file = os.path.expanduser(raw_key_file)

            self.config = {
                "user": self.user_ocid,
                "fingerprint": self.fingerprint,
                "key_file": self.key_file,
                "tenancy": self.tenancy_ocid,
                "region": self.region,
            }

        self.bucket_name = bucket_name or os.getenv("OCI_BUCKET_NAME")
        self.namespace = namespace_name or os.getenv("OCI_NAMESPACE")

        self.client = oci.object_storage.ObjectStorageClient(self.config)

    def get_namespace(self) -> str:
        """Obtiene el namespace de Object Storage actual."""
        if not self.namespace:
            self.namespace = self.client.get_namespace().data
        return self.namespace

    def upload_json_asset(
        self,
        data: Union[Dict[str, Any], List[Any], str],
        object_name: str,
        content_type: str = "application/json; charset=utf-8",
    ) -> Dict[str, Any]:
        """Sube un activo en formato JSON al bucket de OCI.

        Args:
            data: Datos en formato dict, list o str.
            object_name: Nombre completo de la ruta/objeto en OCI (ej: 'activos/2026-09-21/paquete.json').
            content_type: Tipo de contenido MIME.

        Returns:
            Diccionario con estado, etag, tamaño y nombre del objeto.
        """
        if isinstance(data, (dict, list)):
            payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        elif isinstance(data, str):
            payload = data.encode("utf-8")
        elif isinstance(data, bytes):
            payload = data
        else:
            raise TypeError("data debe ser dict, list, str o bytes")

        ns = self.get_namespace()
        response = self.client.put_object(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            object_name=object_name,
            put_object_body=payload,
            content_type=content_type,
        )

        etag = None
        if hasattr(response, "headers") and response.headers:
            etag = response.headers.get("etag")

        return {
            "status": "success",
            "object_name": object_name,
            "etag": etag,
            "size_bytes": len(payload),
        }

    def upload_asset_package(
        self,
        data: Union[Dict[str, Any], List[Any], str],
        filename: Optional[str] = None,
        date_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Guarda un paquete de distribución con convención activos/{fecha}/{filename}."""
        if date_folder is None:
            date_folder = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        if filename is None:
            filename = "paquete-distribucion.json"

        remote_name = f"activos/{date_folder}/{filename}"
        return self.upload_json_asset(data=data, object_name=remote_name)

    def upload_file(
        self,
        local_path: Union[str, Path],
        remote_name: str,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, Any]:
        """Sube un archivo del sistema local al bucket."""
        path = Path(local_path)
        if not path.is_file():
            raise FileNotFoundError(f"El archivo local no existe: {path}")

        ns = self.get_namespace()
        with open(path, "rb") as f:
            response = self.client.put_object(
                namespace_name=ns,
                bucket_name=self.bucket_name,
                object_name=remote_name,
                put_object_body=f,
                content_type=content_type,
            )

        etag = response.headers.get("etag") if hasattr(response, "headers") else None
        return {
            "status": "success",
            "object_name": remote_name,
            "etag": etag,
            "size_bytes": path.stat().st_size,
        }

    def get_asset(self, object_name: str) -> Any:
        """Descarga un objeto JSON y lo deserializa a objeto Python."""
        ns = self.get_namespace()
        response = self.client.get_object(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            object_name=object_name,
        )
        content = response.data.content
        return json.loads(content.decode("utf-8"))

    def get_asset_package(self, object_name: str) -> Any:
        """Alias de compatibilidad para get_asset."""
        return self.get_asset(object_name)

    def get_object_content(self, object_name: str) -> bytes:
        """Descarga el contenido binario/bytes en bruto de un objeto."""
        ns = self.get_namespace()
        response = self.client.get_object(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            object_name=object_name,
        )
        return response.data.content

    def list_assets(self, prefix: str = "activos") -> List[Dict[str, Any]]:
        """Lista los objetos bajo un prefijo."""
        ns = self.get_namespace()
        response = self.client.list_objects(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            prefix=prefix,
        )

        results = []
        objects = response.data.objects if hasattr(response.data, "objects") else []
        for item in objects:
            results.append({
                "name": item.name,
                "size": getattr(item, "size", None),
                "md5": getattr(item, "md5", None),
                "time_created": getattr(item, "time_created", None),
            })
        return results

    def delete_object(self, object_name: str) -> bool:
        """Elimina un objeto del bucket."""
        ns = self.get_namespace()
        self.client.delete_object(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            object_name=object_name,
        )
        return True

    def create_preauthenticated_request(
        self,
        object_name: str,
        name: Optional[str] = None,
        expires_in_hours: int = 24,
        access_type: str = "ObjectRead",
    ) -> Dict[str, str]:
        """Genera una URL pre-autenticada (PAR) para acceder al objeto."""
        ns = self.get_namespace()
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expires_in_hours)
        par_name = name or f"par-{object_name.replace('/', '_')}-{int(now.timestamp())}"

        par_details = oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name=par_name,
            object_name=object_name,
            access_type=access_type,
            time_expires=expires_at,
        )

        par_response = self.client.create_preauthenticated_request(
            namespace_name=ns,
            bucket_name=self.bucket_name,
            create_preauthenticated_request_details=par_details,
        )

        access_uri = par_response.data.access_uri
        full_url = f"https://objectstorage.{self.region}.oraclecloud.com{access_uri}"

        return {
            "id": par_response.data.id,
            "access_url": full_url,
            "expires_at": expires_at.isoformat(),
        }
