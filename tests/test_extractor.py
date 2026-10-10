import numpy as np

from src.extractor import Extractor

FS = 16000


def seno(frecuencia, duracion=1.0, fs=FS):
    t = np.arange(int(duracion * fs)) / fs
    return np.sin(2 * np.pi * frecuencia * t)


def test_autocorrelacion_detecta_seno_de_150_hz():
    frecuencia = Extractor().autocorrelacion_pitch(seno(150), FS)
    assert abs(frecuencia - 150) < 3


def test_autocorrelacion_de_silencio_devuelve_none():
    assert Extractor().autocorrelacion_pitch(np.zeros(FS), FS) is None


def test_autocorrelacion_de_silencio_con_vectores_devuelve_tupla_de_none():
    resultado = Extractor().autocorrelacion_pitch(
        np.zeros(FS), FS, devolver_vectores=True
    )
    assert resultado == (None, None, None, None)


def test_autocorrelacion_segmento_vacio_devuelve_none_sin_vectores():
    # Señal más corta que lag_min: el segmento de correlación queda vacío.
    assert Extractor().autocorrelacion_pitch(np.ones(10), FS) is None


def test_autocorrelacion_segmento_vacio_con_vectores_devuelve_tupla_de_none():
    resultado = Extractor().autocorrelacion_pitch(
        np.ones(10), FS, devolver_vectores=True
    )
    assert resultado == (None, None, None, None)


def test_extrae_seno_devuelve_frecuencias_cercanas():
    freqAC, freqPC = Extractor().extrae(seno(150), FS)
    assert abs(freqAC - 150) < 3
    assert abs(freqPC - 150) < 20
