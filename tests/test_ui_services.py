"""Pruebas unitarias para la capa de servicios de la interfaz (src/ui/services.py)."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.ui.services import (
    cargar_paquete,
    construir_payload_imagen_post,
    generar_imagen_post,
    guardar_curaduria_humana,
    obtener_ultimos_paquetes,
    procesar_archivo_ui,
    sanitizar_url_imagen,
    validar_url_imagen,
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
        persistir_oci=False,
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


@patch("httpx.Client.post")
def test_procesar_archivo_n8n_ui_exito(mock_post, tmp_path: Path):
    """Verifica que procesar_archivo_n8n_ui normalice la respuesta de n8n correctamente."""
    from src.ui.services import procesar_archivo_n8n_ui

    # Crear archivo de prueba
    test_file = tmp_path / "test_n8n.json"
    test_file.write_text(
        json.dumps({
            "interacciones": [
                {
                    "id": "msg_001",
                    "autor": "Ana Tester",
                    "canal": "#logros-y-empleos",
                    "tipo": "testimonio",
                    "texto": "Conseguí empleo gracias a Oracle ONE!",
                }
            ]
        }),
        encoding="utf-8",
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            "id": "msg_001",
            "autor": "Ana Tester",
            "canal": "#logros-y-empleos",
            "texto_original": "Conseguí empleo gracias a Oracle ONE!",
            "sentimiento": "positivo",
            "tipo_contenido": "logro_contratacion",
            "temas_clave": ["Oracle", "ONE"],
            "post_linkedin": "Copy exitoso desde n8n!",
            "tip_tecnico_faq": None,
        }
    ]
    mock_post.return_value = mock_resp

    paquete = procesar_archivo_n8n_ui(
        ruta_archivo=test_file,
        webhook_url="http://mock-n8n:5678/webhook/test",
        limite=1,
    )

    assert paquete["metadata_paquete"]["motor_orquestacion"] == "n8n_oci_cloud"
    assert paquete["metadata_paquete"]["total_procesados_exitosamente"] == 1
    assert paquete["metricas"]["total_posts_linkedin_generados"] == 1
    assert len(paquete["activos"]) == 1
    assert paquete["activos"][0]["activo"]["post_linkedin"] == "Copy exitoso desde n8n!"


@patch("httpx.Client.post")
def test_procesar_archivo_n8n_ui_404(mock_post, tmp_path: Path):
    """Verifica el mensaje guiado cuando el Webhook aún no está activo en n8n (404)."""
    from src.ui.services import procesar_archivo_n8n_ui

    test_file = tmp_path / "test_404.json"
    test_file.write_text(
        json.dumps({
            "interacciones": [
                {"id": "msg_1", "autor": "User", "canal": "#gen", "tipo": "test", "texto": "Hola"}
            ]
        }),
        encoding="utf-8",
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_post.return_value = mock_resp

    with pytest.raises(RuntimeError) as exc_info:
        procesar_archivo_n8n_ui(
            ruta_archivo=test_file,
            webhook_url="http://mock-n8n:5678/webhook/inactivo",
        )

    assert "404 Not Found" in str(exc_info.value)
    assert "communitylab-ingesta" in str(exc_info.value)


def test_fusionar_paquetes():
    """Verifica que fusionar_paquetes combine activos y recalcule métricas correctamente."""
    from src.ui.services import fusionar_paquetes

    paquete_1 = {
        "metadata_paquete": {
            "total_procesados_exitosamente": 1,
            "total_registros_origen": 1,
        },
        "metricas": {
            "distribucion_sentimiento": {"positivo": 1, "neutro": 0, "negativo": 0},
            "distribucion_tipo_contenido": {"logro_contratacion": 1},
            "total_posts_linkedin_generados": 1,
            "total_tips_faq_generados": 0,
        },
        "activos": [
            {
                "interaccion": {"id": "msg_001"},
                "activo": {
                    "sentimiento": "positivo",
                    "tipo_contenido": "logro_contratacion",
                    "post_linkedin": "Post 1",
                },
            }
        ],
        "fallidos": [],
    }

    paquete_2 = {
        "metadata_paquete": {
            "total_procesados_exitosamente": 2,
            "total_registros_origen": 2,
        },
        "metricas": {
            "distribucion_sentimiento": {"positivo": 1, "neutro": 1, "negativo": 0},
            "distribucion_tipo_contenido": {"duda_tecnica": 2},
            "total_posts_linkedin_generados": 1,
            "total_tips_faq_generados": 1,
        },
        "activos": [
            {
                "interaccion": {"id": "msg_002"},
                "activo": {
                    "sentimiento": "positivo",
                    "tipo_contenido": "duda_tecnica",
                    "post_linkedin": "Post 2",
                },
            },
            {
                "interaccion": {"id": "msg_003"},
                "activo": {
                    "sentimiento": "neutro",
                    "tipo_contenido": "duda_tecnica",
                    "tip_tecnico_faq": "Tip 3",
                },
            },
        ],
        "fallidos": [],
    }

    fusionado = fusionar_paquetes(paquete_1, paquete_2)

    assert len(fusionado["activos"]) == 3
    assert fusionado["metadata_paquete"]["total_procesados_exitosamente"] == 3
    assert fusionado["metricas"]["total_posts_linkedin_generados"] == 2
    assert fusionado["metricas"]["total_tips_faq_generados"] == 1
    assert fusionado["metricas"]["distribucion_sentimiento"]["positivo"] == 2
    assert fusionado["metricas"]["distribucion_sentimiento"]["neutro"] == 1


def test_logger_sistema(tmp_path: Path, monkeypatch):
    """Verifica que el logger cree archivos y registre información detallada."""
    from src.utils.logger import (
        get_log_file_path,
        is_detailed_log_enabled,
        limpiar_archivo_log,
        obtener_ultimas_lineas_log,
        setup_logger,
    )

    test_log = tmp_path / "test_community.log"
    monkeypatch.setenv("ENABLE_DETAILED_LOG", "true")
    monkeypatch.setenv("LOG_FILE_PATH", str(test_log))

    assert is_detailed_log_enabled() is True
    log_path = get_log_file_path()
    assert "test_community-" in log_path.name

    logger = setup_logger("TestLogger")
    logger.info("Mensaje de prueba INFO")
    logger.debug("Mensaje de prueba DEBUG detallado")

    lineas = obtener_ultimas_lineas_log(num_lineas=10)
    assert any("Mensaje de prueba INFO" in l for l in lineas)
    assert any("Mensaje de prueba DEBUG" in l for l in lineas)

    # Probar limpieza
    limpiar_archivo_log()
    assert log_path.read_text(encoding="utf-8") == ""


def test_vaciar_historico_oci_local(tmp_path: Path):
    """Verifica que vaciar_historico_oci_local elimine archivos y carpetas del storage."""
    from src.ui.services import vaciar_historico_oci_local

    storage_dir = tmp_path / "activos"
    date_dir = storage_dir / "2026-09-20"
    date_dir.mkdir(parents=True)
    (date_dir / "paquete-1.json").write_text("{}", encoding="utf-8")
    (storage_dir / "paquete-raiz.json").write_text("{}", encoding="utf-8")

    assert len(list(storage_dir.iterdir())) == 2
    eliminados = vaciar_historico_oci_local(storage_dir)
    assert eliminados == 2
    assert len(list(storage_dir.iterdir())) == 0


def test_obtener_ids_procesados_sesion(tmp_path: Path, monkeypatch):
    """Verifica la recolección de IDs de las sesiones guardadas."""
    from src.ui.services import obtener_ids_procesados_sesion

    p1 = tmp_path / "paquete_procesado_python.json"
    p1.write_text(
        json.dumps({
            "activos": [
                {"interaccion": {"id": "msg_001"}},
                {"interaccion": {"id": "msg_002"}},
            ]
        }),
        encoding="utf-8",
    )

    p2 = tmp_path / "paquete_procesado_n8n.json"
    p2.write_text(
        json.dumps({
            "activos": [
                {"interaccion": {"id": "msg_002"}},
                {"interaccion": {"id": "msg_003"}},
            ]
        }),
        encoding="utf-8",
    )

    with patch("src.ui.services.Path") as mock_path:
        def side_effect(path_str):
            if "python" in str(path_str):
                return p1
            elif "n8n" in str(path_str):
                return p2
            return tmp_path / "inexistente.json"

        mock_path.side_effect = side_effect
        ids = obtener_ids_procesados_sesion(consultar_oci=False)
        assert ids == {"msg_001", "msg_002", "msg_003"}


def test_construir_payload_imagen_post_omite_opcionales_vacios():
    payload = construir_payload_imagen_post(
        id_post="dc_1553172781007642635",
        solucion_tecnica="  Copy del editor  ",
        temas_clave=[" #LangChain ", "", "OCI"],
        instruccion_custom="   ",
    )
    assert payload["id_post"] == "dc_1553172781007642635"
    assert payload["solucion_tecnica"] == "Copy del editor"
    assert payload["temas_clave"] == ["#LangChain", "OCI"]
    assert "instruccion_custom" not in payload
    assert payload["bucket_name"] == "communitylab-activos-marketing"
    assert "region" in payload


def test_generar_imagen_post_devuelve_url(monkeypatch):
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {
                "status": "success",
                "id_post": "dc_155",
                "image_url": "https://objectstorage.example/preview_dc_155.png",
            }

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, json, headers):
            assert url.endswith("/webhook/generar-imagen-post")
            assert json["id_post"] == "dc_155"
            assert json["solucion_tecnica"] == "Texto del editor"
            assert json["instruccion_custom"] == "estilo 3D"
            assert headers["Content-Type"] == "application/json"
            return FakeResponse()

    monkeypatch.setattr("httpx.Client", FakeClient)
    resultado = generar_imagen_post(
        id_post="dc_155",
        solucion_tecnica="Texto del editor",
        temas_clave=["#OCI"],
        instruccion_custom="estilo 3D",
        webhook_url="http://147.15.9.116:5678/webhook/generar-imagen-post",
    )
    assert resultado["status"] == "success"
    assert resultado["image_url"].endswith("preview_dc_155.png")


def test_sanitizar_url_imagen_quita_igual_inicial():
    cruda = "=https://objectstorage.example/n/ns/b/bucket/o/previews/preview_dc_155.png"
    assert sanitizar_url_imagen(cruda).startswith("https://")
    assert validar_url_imagen(cruda).endswith("preview_dc_155.png")


def test_validar_url_imagen_codifica_barra_del_objeto_oci():
    cruda = (
        "https://objectstorage.sa-saopaulo-1.oraclecloud.com/n/gr8ogb5hbroe/"
        "b/communitylab-activos-marketing/o/previews/preview_post_001.png"
    )
    assert validar_url_imagen(cruda).endswith("/o/previews%2Fpreview_post_001.png")


def test_validar_url_imagen_rechaza_objeto_undefined():
    cruda = "=https://objectstorage.sa-saopaulo-1.oraclecloud.com/n/tu_namespace_oci/b/communitylab-activos-marketing/o/undefined"
    with pytest.raises(RuntimeError, match="undefined"):
        validar_url_imagen(cruda)

def test_generar_imagen_post_python_dual_engine(monkeypatch):
    from src.ai_engine.gemini_service import GeminiService
    from src.cloud_oci.storage_client import OCIStorageManager

    def mock_prompt(self, solucion_tecnica, instruccion_custom="", temas_clave=None):
        return "3D isometric tech concept in blue and purple"

    monkeypatch.setattr(GeminiService, "generate_image_prompt", mock_prompt)

    class FakeResponse:
        status_code = 200
        content = b"fake_png_binary_data"

        def raise_for_status(self):
            return None

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url):
            assert "image.pollinations.ai" in url
            return FakeResponse()

    monkeypatch.setattr("httpx.Client", FakeClient)

    def mock_upload_bytes(self, data, remote_name, content_type="image/png"):
        assert data == b"fake_png_binary_data"
        assert remote_name == "previews/preview_post_python_01.png"
        return {"status": "success", "object_name": remote_name}

    def mock_get_public_url(self, remote_name):
        return f"https://objectstorage.us-ashburn-1.oraclecloud.com/n/ns/b/bucket/o/{remote_name}"

    monkeypatch.setattr(OCIStorageManager, "upload_bytes", mock_upload_bytes)
    monkeypatch.setattr(OCIStorageManager, "get_public_url", mock_get_public_url)

    resultado = generar_imagen_post(
        id_post="post_python_01",
        solucion_tecnica="Solución para comunidad",
        temas_clave=["Python", "Cloud"],
        motor="python",
    )

    assert resultado["status"] == "success"
    assert resultado["motor"] == "python_gemini"
    assert resultado["id_post"] == "post_python_01"
    assert resultado["image_url"].endswith("previews/preview_post_python_01.png")


def test_storage_manager_upload_bytes_and_public_url(tmp_path, monkeypatch):
    from src.cloud_oci.storage_client import OCIStorageManager

    sm = OCIStorageManager(region="us-ashburn-1")
    sm.LOCAL_FALLBACK_DIR = tmp_path
    sm.is_local_mode = True

    res = sm.upload_bytes(b"hello image bytes", "previews/preview_test.png", "image/png")
    assert res["status"] == "success_local_fallback"
    assert (tmp_path / "previews" / "preview_test.png").read_bytes() == b"hello image bytes"

    url = sm.get_public_url("previews/preview_test.png")
    assert str(tmp_path) in url

