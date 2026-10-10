import numpy as np
import pytest
import soundfile as sf

from src.analizador import Analizador
from src.extractor import Extractor

FS = 16000


def escribe_seno(ruta, frecuencia, duracion=1.0):
    t = np.arange(int(duracion * FS)) / FS
    sf.write(str(ruta), 0.5 * np.sin(2 * np.pi * frecuencia * t), FS, format="WAV")


def escribe_silencio(ruta):
    sf.write(str(ruta), np.zeros(FS), FS, format="WAV")


def test_analiza_carpeta_calcula_estadisticas(tmp_path):
    escribe_seno(tmp_path / "a.wav", 120)
    escribe_seno(tmp_path / "b.wav", 140)
    fmedAC, desvAC, fmedPC, desvPC, n, descartados = Analizador.analizaCarpeta(
        str(tmp_path), Extractor()
    )
    assert n == 2 and descartados == 0
    assert abs(fmedAC - 130) < 5
    assert desvAC > 0
    assert np.isfinite([fmedPC, desvPC]).all()


def test_acepta_extension_wav_en_mayusculas(tmp_path):
    escribe_seno(tmp_path / "a.WAV", 120)
    escribe_seno(tmp_path / "b.Wav", 130)
    resultado = Analizador.analizaCarpeta(str(tmp_path), Extractor())
    assert resultado[4] == 2


def test_acepta_carpeta_con_y_sin_separador_final(tmp_path):
    escribe_seno(tmp_path / "a.wav", 120)
    con = Analizador.analizaCarpeta(str(tmp_path) + "/", Extractor())
    sin = Analizador.analizaCarpeta(str(tmp_path), Extractor())
    assert con == sin


def test_excluye_archivos_sin_frecuencia_y_los_cuenta(tmp_path):
    escribe_seno(tmp_path / "a.wav", 120)
    escribe_seno(tmp_path / "b.wav", 140)
    escribe_silencio(tmp_path / "silencio.wav")
    fmedAC, desvAC, fmedPC, desvPC, n, descartados = Analizador.analizaCarpeta(
        str(tmp_path), Extractor()
    )
    assert n == 2 and descartados == 1
    assert np.isfinite([fmedAC, desvAC, fmedPC, desvPC]).all()


def test_error_claro_si_no_queda_ningun_archivo_util(tmp_path):
    escribe_silencio(tmp_path / "silencio.wav")
    with pytest.raises(ValueError, match="archivo"):
        Analizador.analizaCarpeta(str(tmp_path), Extractor())


def test_error_claro_si_la_carpeta_no_tiene_wav(tmp_path):
    (tmp_path / "nota.txt").write_text("hola")
    with pytest.raises(ValueError, match="archivo"):
        Analizador.analizaCarpeta(str(tmp_path), Extractor())
