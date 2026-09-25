"""Cliente de persistencia para Oracle Cloud Infrastructure (OCI) Object Storage.

Gestiona el almacenamiento de paquetes de distribución generados por el pipeline,
soportando autenticación por variables de entorno (.env), archivos de configuración
locales (~/.oci/config), diccionario explícito y modo fallback local para desarrollo offline.
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
        bucket_name: Optional[str] = None,
        namespace_name: Optional[str] = None,
        allow_local_fallback: bool = True,
        user_ocid: Optional[str] = None,
        tenancy_ocid: Optional[str] = None,
        fingerprint: Optional[str] = None,
        key_file: Optional[str] = None,
        region: Optional[str] = None,
    ):
        """Inicializa el cliente de OCI Object Storage.

        Args:
            config: Diccionario opcional de configuración de OCI SDK.
            bucket_name: Nombre del bucket en OCI Object Storage.
            namespace_name: Namespace del Tenancy (opcional, se autodescubre si es None).
            allow_local_fallback: Si es True, permite guardar localmente cuando OCI no esté disponible.
            user_ocid: OCID de usuario explícito.
            tenancy_ocid: OCID de tenancy explícito.
            fingerprint: Fingerprint de la clave API.
            key_file: Ruta al archivo .pem.
            region: Región de OCI (por defecto lee de .env o us-ashburn-1).
        """
        self.bucket_name = bucket_name or os.getenv("OCI_BUCKET_NAME", "communitylab-activos-marketing")
        self._namespace_override = namespace_name or os.getenv("OCI_NAMESPACE")
        self.namespace = self._namespace_override
        self.allow_local_fallback = allow_local_fallback

        self.client: Optional[Any] = None
        self.is_local_mode: bool = False
        self._cached_namespace: Optional[str] = self._namespace_override

        # Resolver región preferida
        self.region = region or (config.get("region") if config else None) or os.getenv("OCI_REGION", "us-ashburn-1")

        if config:
            self.oci_config = config
            self.user_ocid = config.get("user")
            self.tenancy_ocid = config.get("tenancy")
            self.fingerprint = config.get("fingerprint")
            self.key_file = config.get("key_file")
            self.region = config.get("region", self.region)
        else:
            self.user_ocid = user_ocid or os.getenv("OCI_USER_OCID")
            self.tenancy_ocid = tenancy_ocid or os.getenv("OCI_TENANCY_OCID")
            self.fingerprint = fingerprint or os.getenv("OCI_FINGERPRINT")
            raw_key_file = key_file or os.getenv("OCI_KEY_FILE", "~/.oci/oci_api_key.pem")
            self.key_file = os.path.expanduser(raw_key_file) if raw_key_file else None

            self.oci_config = {
                "user": self.user_ocid,
                "fingerprint": self.fingerprint,
                "key_file": self.key_file,
                "tenancy": self.tenancy_ocid,
                "region": self.region,
            }

        self._inicializar_cliente(self.oci_config)

    def _inicializar_cliente(self, config_dict: Optional[Dict[str, Any]] = None) -> None:
        """Intenta inicializar el cliente oficial del SDK de OCI o activa el modo fallback local."""
        if not HAS_OCI:
            self._activar_modo_local("Librería oficial 'oci' no disponible.")
            return

        if config_dict:
            try:
                self.client = oci.object_storage.ObjectStorageClient(config_dict)
                self.is_local_mode = False
                logger.info("Cliente OCI inicializado correctamente con configuración provista.")
                return
            except Exception as e:
                logger.warning("Fallo al inicializar cliente OCI con dict provisto: %s", e)

        # Intentar cargar desde archivo estándar ~/.oci/config
        oci_config_file = Path(os.path.expanduser("~/.oci/config"))
        if oci_config_file.exists():
            try:
                cfg = oci.config.from_file(file_location=str(oci_config_file))
                self.client = oci.object_storage.ObjectStorageClient(cfg)
                self.oci_config = cfg
                self.is_local_mode = False
                logger.info("Cliente OCI inicializado con éxito desde ~/.oci/config.")
                return
            except Exception as e:
                logger.warning("Error leyendo ~/.oci/config: %s", e)

        # Si no se pudo conectar y está permitido el fallback
        if self.allow_local_fallback:
            self._activar_modo_local("Credenciales OCI no encontradas o inválidas. Usando almacenamiento local.")
        else:
            raise RuntimeError("No se pudo autenticar con OCI y allow_local_fallback está desactivado.")

    def _activar_modo_local(self, razon: str) -> None:
        """Activa el modo de persistencia local en disco."""
        self.is_local_mode = True
        self.client = None
        self.LOCAL_FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Activado modo almacenamiento local: %s (directorio: %s)", razon, self.LOCAL_FALLBACK_DIR)

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
        data: Union[Dict[str, Any], List[Any], str, bytes],
        object_name: Optional[str] = None,
        prefix: str = "activos",
        object_name_suffix: Optional[str] = None,
        content_type: str = "application/json; charset=utf-8",
    ) -> Dict[str, Any]:
        """Sube un paquete JSON a OCI Object Storage o a almacenamiento local fallback.

        Args:
            data: Diccionario, lista, string o bytes a guardar.
            object_name: Nombre exacto del objeto. Si es None, se genera automáticamente.
            prefix: Carpeta virtual dentro del bucket (por defecto 'activos').
            object_name_suffix: Sufijo opcional para diferenciar el motor generador.
            content_type: Tipo MIME.

        Returns:
            Dict con metadata de la operación (status, object_name, etag, size_bytes).
        """
        now = datetime.now(timezone.utc)
        date_folder = now.strftime("%Y-%m-%d")
        time_tag = now.strftime("%H%M%S")
        suffix_str = f"-{object_name_suffix}" if object_name_suffix else ""

        if not object_name:
            object_name = f"{prefix}/{date_folder}/paquete-distribucion{suffix_str}-{time_tag}.json"

        if isinstance(data, (dict, list)):
            body_bytes = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        elif isinstance(data, str):
            body_bytes = data.encode("utf-8")
        elif isinstance(data, bytes):
            body_bytes = data
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
            content_type=content_type,
        )

        etag = None
        if hasattr(response, "headers") and response.headers:
            etag = response.headers.get("etag")

        logger.info("☁️ [OCI Cloud] Objeto '%s' subido exitosamente al bucket '%s'", object_name, self.bucket_name)
        return {
            "status": "success",
            "bucket_name": self.bucket_name,
            "object_name": object_name,
            "etag": etag,
            "size_bytes": len(body_bytes),
            "uploaded_at": now.isoformat(),
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

        if self.is_local_mode:
            dest = self.LOCAL_FALLBACK_DIR / remote_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(path.read_bytes())
            return {
                "status": "success_local_fallback",
                "object_name": remote_name,
                "etag": "local_mock_etag",
                "size_bytes": path.stat().st_size,
            }

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
        raw_content = response.data.content
        if isinstance(raw_content, bytes):
            raw_content = raw_content.decode("utf-8")
        return json.loads(raw_content)

    def get_asset_package(self, object_name: str) -> Any:
        """Alias de compatibilidad para get_asset."""
        return self.get_asset(object_name)

    def get_object_content(self, object_name: str) -> bytes:
        """Descarga el contenido binario/bytes en bruto de un objeto."""
        if self.is_local_mode:
            local_path = self.LOCAL_FALLBACK_DIR / object_name
            if not local_path.exists():
                raise FileNotFoundError(f"Objeto no encontrado en almacenamiento local: {local_path}")
            return local_path.read_bytes()

        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        namespace = self.get_namespace()
        response = self.client.get_object(
            namespace_name=namespace,
            bucket_name=self.bucket_name,
            object_name=object_name,
        )
        content = response.data.content
        return content if isinstance(content, bytes) else content.encode("utf-8")

    def list_assets(self, prefix: str = "activos", limit: int = 100) -> List[Dict[str, Any]]:
        """Lista los objetos bajo un prefijo en el bucket o carpeta local."""
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
                    "time_created": datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc).isoformat(),
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
        )

        results = []
        objects = response.data.objects if hasattr(response.data, "objects") else []
        for item in objects:
            iso_time = item.time_created.isoformat() if getattr(item, "time_created", None) else None
            results.append({
                "name": item.name,
                "size": getattr(item, "size", 0) or 0,
                "md5": getattr(item, "md5", None),
                "time_created": iso_time,
                "created_at": iso_time,
                "etag": getattr(item, "etag", None),
            })
        return results

    def delete_object(self, object_name: str) -> bool:
        """Elimina un objeto del bucket o almacenamiento local."""
        if self.is_local_mode:
            local_path = self.LOCAL_FALLBACK_DIR / object_name
            if local_path.exists():
                local_path.unlink()
            return True

        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

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
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(hours=expires_in_hours)

        if self.is_local_mode:
            return {
                "id": "par-mock-local-id",
                "object_name": object_name,
                "access_url": f"http://localhost:8501/local-files/{object_name}",
                "expires_at": expires_at.isoformat(),
            }

        if not self.client:
            raise RuntimeError("Cliente OCI no inicializado.")

        ns = self.get_namespace()
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
        region = self.region or "us-ashburn-1"
        full_url = f"https://objectstorage.{region}.oraclecloud.com{access_uri}"

        return {
            "id": par_response.data.id,
            "object_name": object_name,
            "access_url": full_url,
            "expires_at": expires_at.isoformat(),
        }
