"""Cliente y Administrador de Oracle Cloud Infrastructure (OCI) Object Storage para CommunityLab.

Gestiona la persistencia, consulta y generación de URLs prefirmadas de paquetes
de activos de distribución en el Bucket de OCI (Always Free).
"""

import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import oci
from dotenv import load_dotenv

# Cargar variables de entorno si existen
load_dotenv()


class OCIStorageManager:
    """Administrador para interactuar con OCI Object Storage mediante el SDK oficial."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        config_file: Optional[str] = None,
        profile_name: str = "DEFAULT",
        bucket_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
    ):
        """Inicializa el cliente de OCI Object Storage.

        Prioridad de configuración:
        1. Diccionario `config` explícito pasado como parámetro.
        2. Variables de entorno (OCI_USER_OCID, OCI_TENANCY_OCID, etc.).
        3. Archivo de configuración estándar de OCI (~/.oci/config).
        """
        self.bucket_name = bucket_name or os.getenv("OCI_BUCKET_NAME", "communitylab-activos-marketing")
        self._namespace_override = namespace_name or os.getenv("OCI_NAMESPACE")

        if config:
            self.oci_config = config
        elif self._has_env_credentials():
            self.oci_config = self._build_config_from_env()
        else:
            cfg_path = config_file or oci.config.DEFAULT_LOCATION
            try:
                self.oci_config = oci.config.from_file(file_location=cfg_path, profile_name=profile_name)
            except Exception as e:
                # Modo fallback: configuración vacía para pruebas o inicialización diferida
                self.oci_config = {}

        # Cliente de OCI Object Storage
        if self.oci_config:
            self.client = oci.object_storage.ObjectStorageClient(self.oci_config)
        else:
            self.client = None

        self._cached_namespace: Optional[str] = None

    def _has_env_credentials(self) -> bool:
        """Verifica si las credenciales mínimas de OCI están en las variables de entorno."""
        required_keys = ["OCI_USER_OCID", "OCI_TENANCY_OCID", "OCI_FINGERPRINT", "OCI_KEY_FILE", "OCI_REGION"]
        return all(os.getenv(k) for k in required_keys)

    def _build_config_from_env(self) -> Dict[str, str]:
        """Construye un diccionario de configuración de OCI a partir de variables de entorno."""
        key_file_path = os.getenv("OCI_KEY_FILE", "")
        expanded_path = os.path.expanduser(key_file_path)

        return {
            "user": os.getenv("OCI_USER_OCID", ""),
            "tenancy": os.getenv("OCI_TENANCY_OCID", ""),
            "fingerprint": os.getenv("OCI_FINGERPRINT", ""),
            "key_file": expanded_path,
            "region": os.getenv("OCI_REGION", "sa-bogota-1"),
        }

    def get_namespace(self) -> str:
        """Obtiene el namespace del Tenancy de OCI con caché local."""
        if self._namespace_override:
            return self._namespace_override

        if self._cached_namespace:
            return self._cached_namespace

        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado con credenciales válidas.")

        response = self.client.get_namespace()
        self._cached_namespace = response.data
        return self._cached_namespace

    def upload_json_asset(
        self,
        data: Union[Dict[str, Any], List[Any], str],
        object_name: Optional[str] = None,
        prefix: str = "activos",
    ) -> Dict[str, Any]:
        """Sube un paquete JSON a OCI Object Storage.

        Args:
            data: Diccionario, lista o string JSON a guardar.
            object_name: Nombre exacto del objeto. Si es None, se genera automáticamente
                         con formato '{prefix}/{YYYY-MM-DD}/paquete-distribucion-{HHMMSS}.json'.
            prefix: Carpeta virtual dentro del bucket (por defecto 'activos').

        Returns:
            Dict con metadata de la operación (object_name, etag, bytes_subidos, timestamp).
        """
        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        now = datetime.now(timezone.utc)
        date_folder = now.strftime("%Y-%m-%d")
        time_tag = now.strftime("%H%M%S")

        if not object_name:
            object_name = f"{prefix}/{date_folder}/paquete-distribucion-{time_tag}.json"

        if isinstance(data, (dict, list)):
            body_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        elif isinstance(data, str):
            body_bytes = data.encode("utf-8")
        else:
            raise TypeError(f"Tipo de dato no soportado para subida: {type(data).__name__}")

        namespace = self.get_namespace()

        response = self.client.put_object(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            object_name=object_name,
            put_object_body=body_bytes,
            content_type="application/json; charset=utf-8",
        )

        return {
            "status": "success",
            "bucket_name": self.bucket_name,
            "object_name": object_name,
            "etag": response.headers.get("etag"),
            "size_bytes": len(body_bytes),
            "uploaded_at": now.isoformat(),
        }

    def get_asset(self, object_name: str) -> Dict[str, Any]:
        """Descarga y decodifica un objeto JSON desde el Bucket de OCI."""
        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        namespace = self.get_namespace()
        response = self.client.get_object(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            object_name=object_name,
        )

        raw_content = response.data.content.decode("utf-8")
        return json.loads(raw_content)

    def list_assets(self, prefix: str = "activos", limit: int = 100) -> List[Dict[str, Any]]:
        """Lista los objetos disponibles en el bucket bajo un prefijo dado."""
        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        namespace = self.get_namespace()
        response = self.client.list_objects(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            prefix=prefix,
            limit=limit,
            fields="name,size,timeCreated,md5,etag",
        )

        results = []
        for obj in response.data.objects:
            results.append({
                "name": obj.name,
                "size": obj.size,
                "created_at": obj.time_created.isoformat() if obj.time_created else None,
                "etag": obj.etag,
            })
        return results

    def create_preauthenticated_request(
        self,
        object_name: str,
        expires_in_hours: int = 24,
        access_type: str = "ObjectRead",
    ) -> Dict[str, str]:
        """Crea una URL prefirmada (PAR - Pre-Authenticated Request) de acceso seguro y temporal.

        Args:
            object_name: Nombre del objeto a compartir.
            expires_in_hours: Horas de validez del enlace (por defecto 24h).
            access_type: Tipo de acceso ('ObjectRead', 'ObjectWrite', etc.).

        Returns:
            Dict con el PAR ID y la URL pública completa de acceso seguro.
        """
        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        namespace = self.get_namespace()
        expiration_time = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        par_details = oci.object_storage.models.CreatePreauthenticatedRequestDetails(
            name=f"PAR-{object_name.replace('/', '-')[:30]}-{int(expiration_time.timestamp())}",
            object_name=object_name,
            access_type=access_type,
            time_expires=expiration_time,
        )

        response = self.client.create_preauthenticated_request(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            create_preauthenticated_request_details=par_details,
        )

        par_data = response.data
        region = self.oci_config.get("region", "sa-bogota-1")
        # Estructura de la URL prefirmada de OCI
        full_url = f"https://objectstorage.{region}.oraclecloud.com{par_data.access_uri}"

        return {
            "id": par_data.id,
            "object_name": object_name,
            "access_url": full_url,
            "expires_at": expiration_time.isoformat(),
        }
