"""Pruebas unitarias para el módulo de ingesta y carga de datos (src/ingestion)."""

import json
from pathlib import Path
import pytest

from src.ai_engine.schemas import CommunityInteraction
from src.ingestion.data_loader import (
    cargar_interacciones_desde_json,
    filtrar_omitir_ids,
    filtrar_por_canal,
    filtrar_por_tipo,
    generar_lotes,
    obtener_canales_unicos,
    obtener_tipos_unicos,
)


@pytest.fixture
def dataset_oficial_path() -> Path:
    """Ruta al dataset oficial de pruebas del repositorio."""
    return Path(__file__).parents[1] / "data" / "interacciones_ejemplo.json"


@pytest.fixture
def tmp_json_custom(tmp_path: Path) -> Path:
    """Crea un archivo JSON temporal con datos válidos e inválidos."""
    data = {
        "interacciones": [
            {
                "id": "t_01",
                "autor": "Usuario Valido 1",
                "canal": "#logros-y-empleos",
                "tipo": "testimonio",
                "texto": "¡Conseguí empleo en tecnología gracias a Oracle ONE!"
            },
            {
                "id": "t_02",
                "autor": "Usuario Valido 2",
                "canal": "#dudas-cloud-oci",
                "tipo": "pregunta_tecnica",
                "texto": "¿Cómo configurar el bucket de OCI?"
            },
            {
                "id": "t_invalido",
                "autor": "Incompleto",
                # Falta 'canal', 'tipo', 'texto'
            }
        ]
    }
    file_path = tmp_path / "custom_interacciones.json"
    file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return file_path


def test_carga_dataset_oficial_15_registros(dataset_oficial_path: Path):
    """Verifica que el dataset oficial cargue exactamente 15 interacciones válidas."""
    assert dataset_oficial_path.exists(), "El dataset oficial data/interacciones_ejemplo.json debe existir"
    
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    assert len(interacciones) == 15, "Deben cargarse exactamente 15 interacciones"
    
    primer_registro = interacciones[0]
    assert isinstance(primer_registro, CommunityInteraction)
    assert primer_registro.id == "msg_001"
    assert primer_registro.autor == "Mariana Souza"
    assert primer_registro.canal == "#logros-y-empleos"
    assert primer_registro.tipo == "testimonio"
    assert "Desarrolladora Junior de IA" in primer_registro.texto


def test_carga_archivo_inexistente_lanza_error():
    """Verifica que se lance FileNotFoundError al indicar una ruta inexistente."""
    with pytest.raises(FileNotFoundError):
        cargar_interacciones_desde_json("data/no_existe_archivo.json")


def test_carga_modo_no_estricto_omite_invalidos(tmp_json_custom: Path):
    """En modo strict=False (default), los registros corruptos se omiten y se cargan los válidos."""
    interacciones = cargar_interacciones_desde_json(tmp_json_custom, strict=False)
    assert len(interacciones) == 2
    assert interacciones[0].id == "t_01"
    assert interacciones[1].id == "t_02"


def test_carga_modo_estricto_lanza_error(tmp_json_custom: Path):
    """En modo strict=True, un registro corrupto debe lanzar ValueError."""
    with pytest.raises(ValueError, match="Error al validar registro"):
        cargar_interacciones_desde_json(tmp_json_custom, strict=True)


def test_filtrar_por_canal(dataset_oficial_path: Path):
    """Verifica el filtrado correcto por canal (case insensitive)."""
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    
    logros = filtrar_por_canal(interacciones, "#logros-y-empleos")
    assert len(logros) > 0
    assert all(i.canal == "#logros-y-empleos" for i in logros)
    
    # Comprobar case insensitivity
    logros_mayusc = filtrar_por_canal(interacciones, "#LOGROS-Y-EMPLEOS")
    assert len(logros_mayusc) == len(logros)


def test_filtrar_por_tipo(dataset_oficial_path: Path):
    """Verifica el filtrado por tipo de interacción."""
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    
    preguntas = filtrar_por_tipo(interacciones, "pregunta_tecnica")
    assert len(preguntas) > 0
    assert all(i.tipo == "pregunta_tecnica" for i in preguntas)
    
    showcases = filtrar_por_tipo(interacciones, "showcase")
    assert len(showcases) > 0
    assert all(i.tipo == "showcase" for i in showcases)


def test_obtener_canales_y_tipos_unicos(dataset_oficial_path: Path):
    """Verifica la extracción de canales y tipos únicos sin duplicados."""
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    
    canales = obtener_canales_unicos(interacciones)
    assert isinstance(canales, list)
    assert "#logros-y-empleos" in canales
    assert len(canales) == len(set(canales)), "No debe haber canales duplicados"
    
    tipos = obtener_tipos_unicos(interacciones)
    assert "testimonio" in tipos
    assert "pregunta_tecnica" in tipos
    assert len(tipos) == len(set(tipos)), "No debe haber tipos duplicados"


def test_generar_lotes_batching(dataset_oficial_path: Path):
    """Verifica el particionado correcto en lotes de tamaño configurable."""
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    assert len(interacciones) == 15
    
    # Lotes de tamaño 1 (ideal para Rate Limits de LLM)
    lotes_1 = list(generar_lotes(interacciones, tamano_lote=1))
    assert len(lotes_1) == 15
    assert len(lotes_1[0]) == 1
    
    # Lotes de tamaño 5
    lotes_5 = list(generar_lotes(interacciones, tamano_lote=5))
    assert len(lotes_5) == 3
    assert len(lotes_5[0]) == 5
    assert len(lotes_5[1]) == 5
    assert len(lotes_5[2]) == 5
    
    # Lotes de tamaño inválido (< 1)
    with pytest.raises(ValueError):
        list(generar_lotes(interacciones, tamano_lote=0))


def test_filtrar_omitir_ids(dataset_oficial_path: Path):
    """Verifica que filtrar_omitir_ids excluya correctamente los IDs indicados."""
    interacciones = cargar_interacciones_desde_json(dataset_oficial_path)
    assert len(interacciones) == 15

    ids_a_excluir = {"msg_001", "msg_002", "msg_003"}
    filtradas = filtrar_omitir_ids(interacciones, ids_a_excluir)

    assert len(filtradas) == 12
    assert all(i.id not in ids_a_excluir for i in filtradas)
    assert filtradas[0].id == "msg_004"

