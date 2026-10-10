import warnings

import numpy as np

from src.extractor import Extractor

FS = 16000


def test_extrae_silencio_devuelve_none_sin_nan_ni_avisos():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        resultado = Extractor().extrae(np.zeros(2 * FS), FS)
    assert resultado == (None, None)


def test_primera_colina_de_silencio_devuelve_none_sin_avisos():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert Extractor().frecuencia_media_primera_colina(np.zeros(FS), FS) is None
