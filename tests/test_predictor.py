import json

import numpy as np
import pytest

from src.predictor import predictor

MODELO = {
    "fmedACFeme": 220.0, "desvAcFeme": 20.0,
    "fmedPCFeme": 210.0, "desvPCFeme": 25.0,
    "nFemeAC": 10, "nFemePC": 10,
    "fmedACMasc": 120.0, "desvAcMasc": 15.0,
    "fmedPCMasc": 125.0, "desvPCMasc": 20.0,
    "nMascAC": 10, "nMascPC": 10,
}


@pytest.fixture
def ruta_modelo(tmp_path):
    ruta = tmp_path / "modelo.json"
    ruta.write_text(json.dumps(MODELO), encoding="utf-8")
    return ruta


@pytest.fixture
def clasificador(ruta_modelo):
    return predictor(str(ruta_modelo))


def test_decide_frecuencia_femenina(clasificador):
    assert clasificador.decideFrecuencia(220.0, "AC") == (220.0, "Femenino")


def test_decide_frecuencia_masculina(clasificador):
    assert clasificador.decideFrecuencia(120.0, "PC") == (120.0, "Masculino")


def test_decide_frecuencia_ruido_por_debajo_de_50_hz(clasificador):
    assert clasificador.decideFrecuencia(30.0, "AC") == (30.0, "demasiado ruido")


def test_decide_frecuencia_none_es_demasiado_ruido(clasificador):
    assert clasificador.decideFrecuencia(None, "AC") == (None, "demasiado ruido")
    assert clasificador.decideFrecuencia(None, "PC") == (None, "demasiado ruido")


def test_decide_frecuencia_modo_invalido(clasificador):
    with pytest.raises(ValueError):
        clasificador.decideFrecuencia(150.0, "XX")


def test_decide_usa_la_frecuencia_del_modo(clasificador, monkeypatch):
    monkeypatch.setattr(clasificador, "escucha", lambda: (220.0, 120.0))
    assert clasificador.decide("AC") == (220.0, "Femenino")
    assert clasificador.decide("PC") == (120.0, "Masculino")


def test_decide_con_silencio_no_lanza_error(clasificador, monkeypatch):
    monkeypatch.setattr(clasificador, "escucha", lambda: (None, None))
    assert clasificador.decide("AC") == (None, "demasiado ruido")


def test_actualiza_datos_no_guarda_none(clasificador, ruta_modelo):
    antes = ruta_modelo.read_text(encoding="utf-8")
    clasificador.actualizaDatos("Femenino", None, 200.0)
    clasificador.actualizaDatos("Masculino", 120.0, None)
    assert ruta_modelo.read_text(encoding="utf-8") == antes
    assert clasificador.nFemeAC == 10 and clasificador.nMascAC == 10


def test_actualiza_datos_guarda_valores_validos(clasificador, ruta_modelo):
    clasificador.actualizaDatos("Femenino", 230.0, 215.0)
    guardado = json.loads(ruta_modelo.read_text(encoding="utf-8"))
    assert guardado["nFemeAC"] == 11
    assert all(np.isfinite(v) for v in guardado.values())


def test_decide_y_pregunta_con_none_no_pregunta_ni_guarda(
    clasificador, ruta_modelo, monkeypatch
):
    def escucha():
        clasificador._ultimaFreqAC, clasificador._ultimaFreqPC = None, None
        return None, None

    monkeypatch.setattr(clasificador, "escucha", escucha)

    def no_debe_preguntar(*args, **kwargs):
        raise AssertionError("no debe preguntar sin una medición válida")

    monkeypatch.setattr("builtins.input", no_debe_preguntar)
    antes = ruta_modelo.read_text(encoding="utf-8")
    assert clasificador.decideYPregunta("AC") == (None, "demasiado ruido")
    assert ruta_modelo.read_text(encoding="utf-8") == antes


def test_decide_y_pregunta_con_pc_faltante_no_guarda_none(
    clasificador, ruta_modelo, monkeypatch
):
    def escucha():
        clasificador._ultimaFreqAC, clasificador._ultimaFreqPC = 220.0, None
        return 220.0, None

    monkeypatch.setattr(clasificador, "escucha", escucha)
    monkeypatch.setattr("builtins.input", lambda *a, **k: "s")
    antes = ruta_modelo.read_text(encoding="utf-8")
    assert clasificador.decideYPregunta("AC") == (220.0, "Femenino")
    assert ruta_modelo.read_text(encoding="utf-8") == antes
