import importlib
import sys
from types import SimpleNamespace

import numpy as np
import pytest


@pytest.fixture
def modulo_grabador():
    """Recarga `src.grabador` con un sounddevice falso en `sys.modules`.

    Sirve tanto si `sounddevice` se importa al inicio del módulo como si se
    importa dentro de `grabar`. Al terminar restaura el módulo real.
    """
    falso = SimpleNamespace(rec=None, wait=lambda: None)
    previo = sys.modules.get("sounddevice", "ausente")
    sys.modules["sounddevice"] = falso
    try:
        yield importlib.reload(importlib.import_module("src.grabador")), falso
    finally:
        if previo == "ausente":
            del sys.modules["sounddevice"]
        else:
            sys.modules["sounddevice"] = previo
        importlib.reload(importlib.import_module("src.grabador"))


def test_grabador_usa_el_parametro_canales(modulo_grabador):
    modulo, _ = modulo_grabador
    assert modulo.grabador(sr=8000, canales=2).canales == 2
    assert modulo.grabador().canales == 1


def test_grabar_pide_los_canales_configurados(modulo_grabador):
    modulo, falso = modulo_grabador
    llamadas = {}

    def falso_rec(muestras, samplerate, channels):
        llamadas.update(muestras=muestras, samplerate=samplerate, channels=channels)
        return np.zeros((muestras, channels))

    falso.rec = falso_rec
    modulo.grabador(sr=8000, canales=2).grabar(1)
    assert llamadas == {"muestras": 8000, "samplerate": 8000, "channels": 2}


def test_grabar_un_canal_devuelve_arreglo_1d(modulo_grabador):
    modulo, falso = modulo_grabador
    falso.rec = lambda n, samplerate, channels: np.zeros((n, channels))
    assert modulo.grabador(sr=8000).grabar(1).shape == (8000,)


def test_grabar_varios_canales_conserva_las_columnas(modulo_grabador):
    modulo, falso = modulo_grabador
    falso.rec = lambda n, samplerate, channels: np.zeros((n, channels))
    assert modulo.grabador(sr=8000, canales=2).grabar(1).shape == (8000, 2)
