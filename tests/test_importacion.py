"""El paquete debe poder importarse sin PortAudio/sounddevice instalado."""

import importlib
import inspect
import sys

import pytest


@pytest.fixture
def sin_sounddevice():
    """Simula una máquina sin sounddevice y con `src` sin importar."""
    guardados = {
        nombre: modulo
        for nombre, modulo in sys.modules.items()
        if nombre == "src" or nombre.startswith("src.")
    }
    previo = sys.modules.get("sounddevice", "ausente")
    for nombre in guardados:
        del sys.modules[nombre]
    sys.modules["sounddevice"] = None  # `import sounddevice` lanza ImportError
    try:
        yield
    finally:
        for nombre in [n for n in sys.modules if n == "src" or n.startswith("src.")]:
            del sys.modules[nombre]
        sys.modules.update(guardados)
        if previo == "ausente":
            del sys.modules["sounddevice"]
        else:
            sys.modules["sounddevice"] = previo


def test_import_src_sin_sounddevice(sin_sounddevice):
    paquete = importlib.import_module("src")
    assert inspect.isclass(paquete.Extractor)
    assert inspect.isclass(paquete.Analizador)
    assert inspect.isclass(paquete.Lector)


def test_import_extractor_sin_sounddevice(sin_sounddevice):
    modulo = importlib.import_module("src.extractor")
    assert inspect.isclass(modulo.Extractor)


def test_grabador_y_predictor_son_clases_sin_sounddevice(sin_sounddevice):
    namespace = {}
    exec("from src import grabador, predictor", namespace)
    assert inspect.isclass(namespace["grabador"])
    assert inspect.isclass(namespace["predictor"])


def test_grabar_sin_sounddevice_lanza_import_error(sin_sounddevice):
    from src import grabador

    with pytest.raises(ImportError):
        grabador().grabar(1)
