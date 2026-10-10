import numpy as np
import json
import os

class Analizador:
    def __init__(self):
        pass

    @classmethod
    def analizaCarpeta(cls, carpeta, extractor):
        """Analiza todos los .wav (sin distinguir mayúsculas) de una carpeta.

        Los archivos cuya frecuencia no se pudo medir (None) se excluyen de las
        estadísticas y se cuentan aparte.

        Devuelve [fmedAC, desvAC, fmedPC, desvPC, n_usados, n_descartados].
        Lanza ValueError si no hay ningún archivo utilizable.
        """
        from .lector import Lector
        archivos = sorted(f for f in os.listdir(carpeta) if f.lower().endswith('.wav'))
        if not archivos:
            raise ValueError(f"No hay archivos .wav en la carpeta: {carpeta}")

        freqAutoC = []
        freqPCol = []
        descartados = 0
        for archivo in archivos:
            ruta = os.path.join(carpeta, archivo)
            sennal, sr = Lector.lee(ruta)
            freqAC, freqPC = extractor.extrae(sennal, sr)
            if freqAC is None or freqPC is None:
                descartados += 1
                continue
            freqAutoC.append(freqAC)
            freqPCol.append(freqPC)

        if descartados:
            print(f"Se descartaron {descartados} archivo(s) sin frecuencia medible en {carpeta}")

        if not freqAutoC:
            raise ValueError(
                f"Ningún archivo utilizable en la carpeta (todos sin frecuencia medible): {carpeta}"
            )

        freqAutoC = np.array(freqAutoC)
        freqPCol = np.array(freqPCol)
        return [freqAutoC.mean(), freqAutoC.std(),
                freqPCol.mean(), freqPCol.std(),
                len(freqAutoC), descartados]

    @classmethod
    def analizaYGuarda(cls, carpetaFeme, carpetaMasc, extractor, nombreArchivo="modelo.json"):
        datosFeme = cls.analizaCarpeta(carpetaFeme, extractor)
        datosMasc = cls.analizaCarpeta(carpetaMasc, extractor)

        fmedACFeme, desvACFeme, fmedPCFeme, desvPCFeme, nFeme, _ = datosFeme
        fmedACMasc, desvACMasc, fmedPCMasc, desvPCMasc, nMasc, _ = datosMasc

        modelo = {
            "fmedACFeme": float(fmedACFeme),
            "desvAcFeme": float(desvACFeme),
            "fmedPCFeme": float(fmedPCFeme),
            "desvPCFeme": float(desvPCFeme),
            "nFemeAC": int(nFeme),
            "nFemePC": int(nFeme),

            "fmedACMasc": float(fmedACMasc),
            "desvAcMasc": float(desvACMasc),
            "fmedPCMasc": float(fmedPCMasc),
            "desvPCMasc": float(desvPCMasc),
            "nMascAC": int(nMasc),
            "nMascPC": int(nMasc),
        }

        # Carpeta "modelo" al mismo nivel que "data" y "src"
        carpetaModelo = os.path.join(os.path.dirname(__file__), "..", "modelo")
        carpetaModelo = os.path.abspath(carpetaModelo)
        os.makedirs(carpetaModelo, exist_ok=True)

        rutaArchivo = os.path.join(carpetaModelo, nombreArchivo)
        with open(rutaArchivo, "w", encoding="utf-8") as archivo:
            json.dump(modelo, archivo, indent=4)

        return modelo
            
