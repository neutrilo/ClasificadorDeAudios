import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def carga():
    with (RAIZ / "pyproject.toml").open("rb") as archivo:
        return tomllib.load(archivo)


def test_metadatos_del_proyecto():
    proyecto = carga()["project"]
    assert proyecto["name"] == "clasificador-de-audios"
    assert proyecto["requires-python"] == ">=3.12"


def test_dependencias_base_no_incluyen_extras():
    dependencias = " ".join(carga()["project"]["dependencies"]).lower()
    for requerida in ("numpy", "scipy", "soundfile"):
        assert requerida in dependencias
    assert "sounddevice" not in dependencias
    assert "matplotlib" not in dependencias


def test_extras_opcionales():
    extras = carga()["project"]["optional-dependencies"]
    assert extras["microfono"] == ["sounddevice"]
    assert extras["graficas"] == ["matplotlib"]
    assert extras["dev"] == ["pytest"]


def test_el_paquete_src_se_incluye_sin_renombrar():
    assert carga()["tool"]["setuptools"]["packages"] == ["src"]
