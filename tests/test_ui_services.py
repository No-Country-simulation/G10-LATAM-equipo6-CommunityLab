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
        ids = obtener_ids_procesados_sesion()
        assert ids == {"msg_001", "msg_002", "msg_003"}


