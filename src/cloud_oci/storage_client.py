"""Cliente de persistencia para Oracle Cloud Infrastructure (OCI) Object Storage.

Gestiona el almacenamiento de paquetes de distribución generados por el pipeline,
soportando autenticación por variables de entorno (.env), archivos de configuración
locales (~/.oci/config) y un modo de fallback local para desarrollo y pruebas.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()

# Importación condicional del SDK de OCI para evitar fallos si el entorno es mínimo
try:
    import oci
    HAS_OCI = True
except ImportError:
    HAS_OCI = False
    logger.warning("El SDK de OCI ('oci') no está instalado. OCIStorageManager funcionará en modo fallback local.")


class OCIStorageManager:
    """Administrador de persistencia en OCI Object Storage Always Free."""

    LOCAL_FALLBACK_DIR = Path("data/oci_local_storage")

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        config_file: Optional[str] = None,
        profile_name: str = "DEFAULT",
        bucket_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        client: Optional[Any] = None,
        allow_local_fallback: bool = True,
    ):
        """Inicializa el cliente de OCI Object Storage.

        Prioridad de configuración:
        1. Instancia `client` explícita inyectada (útil para pruebas y mocks).
        2. Diccionario `config` explícito pasado como parámetro.
        3. Variables de entorno (OCI_USER_OCID, OCI_TENANCY_OCID, etc.).
        4. Archivo de configuración estándar de OCI (~/.oci/config).
        5. Si no hay credenciales válidas y allow_local_fallback=True, opera en modo local.
        """
        self.bucket_name = bucket_name or os.getenv("OCI_BUCKET_NAME", "communitylab-activos-marketing")
        self._namespace_override = namespace_name or os.getenv("OCI_NAMESPACE")
        self.allow_local_fallback = allow_local_fallback
        self.is_local_mode = False

        self.oci_config: Dict[str, Any] = {}
        self.client = client
        self._cached_namespace: Optional[str] = None

        if self.client is None and HAS_OCI:
            if config:
                self.oci_config = config
            elif self._has_env_credentials():
                self.oci_config = self._build_config_from_env()
            else:
                cfg_path = config_file or oci.config.DEFAULT_LOCATION
                try:
                    self.oci_config = oci.config.from_file(file_location=cfg_path, profile_name=profile_name)
                except Exception:
                    self.oci_config = {}

            if self.oci_config and self._validate_config(self.oci_config):
                try:
                    self.client = oci.object_storage.ObjectStorageClient(self.oci_config)
                except Exception as e:
                    logger.warning("No se pudo instanciar ObjectStorageClient de OCI: %s", e)
                    self.client = None

        if not self.client:
            if self.allow_local_fallback:
                self.is_local_mode = True
                logger.info(
                    "OCIStorageManager operando en MODO LOCAL (fallback). Los archivos se guardarán en '%s'.",
                    self.LOCAL_FALLBACK_DIR,
                )
            else:
                raise RuntimeError("Cliente OCI no inicializado con credenciales válidas.")

    def _has_env_credentials(self) -> bool:
        """Verifica si las credenciales mínimas de OCI están en las variables de entorno sin ser placeholders."""
        required_keys = ["OCI_USER_OCID", "OCI_TENANCY_OCID", "OCI_FINGERPRINT", "OCI_KEY_FILE", "OCI_REGION"]
        values = [os.getenv(k) for k in required_keys]
        if not all(values):
            return False
        # Verificar que no sean los valores plantilla de .env.example
        user_ocid = os.getenv("OCI_USER_OCID", "")
        return not user_ocid.startswith("ocid1.user.oc1..aaaaaaa")

    def _validate_config(self, cfg: Dict[str, Any]) -> bool:
        """Comprueba que la configuración tenga las claves mínimas requeridas."""
        required = ["user", "tenancy", "fingerprint", "key_file", "region"]
        return all(cfg.get(k) for k in required) and not cfg.get("user", "").startswith("ocid1.user.oc1..aaaaaaa")

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

        if self.is_local_mode:
            return "local_dev_namespace"

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
        """Sube un paquete JSON a OCI Object Storage (o a almacenamiento local si está en modo fallback).

        Args:
            data: Diccionario, lista o string JSON a guardar.
            object_name: Nombre exacto del objeto. Si es None, se genera automáticamente
                         con formato '{prefix}/{YYYY-MM-DD}/paquete-distribucion-{HHMMSS}.json'.
            prefix: Carpeta virtual dentro del bucket (por defecto 'activos').

        Returns:
            Dict con metadata de la operación (status, object_name, etag, bytes_subidos, timestamp).
        """
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

        if self.is_local_mode:
            local_path = self.LOCAL_FALLBACK_DIR / object_name
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(body_bytes)

            logger.info("📦 [OCI Local] Archivo guardado localmente: %s (%d bytes)", local_path, len(body_bytes))
            return {
                "status": "success_local_fallback",
                "bucket_name": self.bucket_name,
                "object_name": object_name,
                "local_path": str(local_path.resolve()),
                "etag": "local_mock_etag",
                "size_bytes": len(body_bytes),
                "uploaded_at": now.isoformat(),
            }

        namespace = self.get_namespace()
        response = self.client.put_object(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            object_name=object_name,
            put_object_body=body_bytes,
            content_type="application/json; charset=utf-8",
        )

        logger.info("☁️ [OCI Cloud] Objeto '%s' subido exitosamente al bucket '%s'", object_name, self.bucket_name)
        return {
            "status": "success",
            "bucket_name": self.bucket_name,
            "object_name": object_name,
            "etag": response.headers.get("etag"),
            "size_bytes": len(body_bytes),
            "uploaded_at": now.isoformat(),
        }

    def get_asset(self, object_name: str) -> Dict[str, Any]:
        """Descarga y decodifica un objeto JSON desde el Bucket de OCI o desde la carpeta local."""
        if self.is_local_mode:
            local_path = self.LOCAL_FALLBACK_DIR / object_name
            if not local_path.exists():
                raise FileNotFoundError(f"Objeto no encontrado en almacenamiento local: {local_path}")
            return json.loads(local_path.read_text(encoding="utf-8"))

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
        """Lista los objetos disponibles en el bucket o en la carpeta local bajo un prefijo dado."""
        if self.is_local_mode:
            search_dir = self.LOCAL_FALLBACK_DIR / prefix
            if not search_dir.exists():
                return []
            results = []
            for file_path in search_dir.rglob("*.json"):
                rel_name = str(file_path.relative_to(self.LOCAL_FALLBACK_DIR)).replace("\\", "/")
                results.append({
                    "name": rel_name,
                    "size": file_path.stat().st_size,
                    "created_at": datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat(),
                    "etag": "local_etag",
                })
            return results[:limit]

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
        """Crea una URL prefirmada (PAR - Pre-Authenticated Request) de acceso seguro y temporal."""
        if self.is_local_mode:
            return {
                "id": "par-mock-local-id",
                "object_name": object_name,
                "access_url": f"http://localhost:8501/local-files/{object_name}",
                "expires_at": (datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)).isoformat(),
            }

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
        full_url = f"https://objectstorage.{region}.oraclecloud.com{par_data.access_uri}"

        return {
            "id": par_data.id,
            "object_name": object_name,
            "access_url": full_url,
            "expires_at": expiration_time.isoformat(),
        }
