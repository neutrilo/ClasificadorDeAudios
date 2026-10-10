import numpy as np
import pytest
import soundfile as sf

from src.lector import Lector


def test_lee_wav_devuelve_sennal_y_frecuencia(tmp_path):
    ruta = tmp_path / "a.wav"
    sf.write(str(ruta), np.zeros(100), 8000, format="WAV")
    sennal, sr = Lector.lee(str(ruta))
    assert sr == 8000 and sennal.shape == (100,)


def test_lee_estereo_lo_pasa_a_mono(tmp_path):
    ruta = tmp_path / "e.wav"
    sf.write(str(ruta), np.ones((50, 2)) * 0.25, 8000, format="WAV")
    sennal, _ = Lector.lee(str(ruta))
    assert sennal.shape == (50,)


def test_formato_no_soportado_lanza_value_error(tmp_path):
    with pytest.raises(ValueError, match="Formato no válido"):
        Lector.lee(str(tmp_path / "audio.ogg"))
