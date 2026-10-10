import numpy as np
import sounddevice as sd
from .extractor import Extractor
import json
from types import SimpleNamespace

class predictor:
    def __init__(self, archivoJson):
        self.archivo = archivoJson

        # 1. LEER el JSON y transformarlo en el objeto "modelo"
        with open(archivoJson, "r", encoding="utf-8") as archivo:
            modelo = json.load(archivo, object_hook=lambda d: SimpleNamespace(**d))

        # 2. ASIGNAR Datos Femeninos desde el objeto modelo
        self.fmedACFeme = modelo.fmedACFeme
        self.desvACFeme = modelo.desvAcFeme  # Asegúrate de que en el JSON esté como "desvAcFeme"
        self.fmedPCFeme = modelo.fmedPCFeme
        self.desvPCFeme = modelo.desvPCFeme
        self.nFemeAC = modelo.nFemeAC
        self.nFemePC = modelo.nFemePC

        # 3. ASIGNAR Datos Masculinos desde el objeto modelo
        self.fmedACMasc = modelo.fmedACMasc
        self.desvACMasc = modelo.desvAcMasc  # Asegúrate de que en el JSON esté como "desvAcMasc"
        self.fmedPCMasc = modelo.fmedPCMasc
        self.desvPCMasc = modelo.desvPCMasc
        self.nMascAC = modelo.nMascAC
        self.nMascPC = modelo.nMascPC

        # 4. Inicializar otros componentes
        self.extractor = Extractor()

        # Últimas frecuencias escuchadas (para actualizaDatos)
        self._ultimaFreqAC = None
        self._ultimaFreqPC = None

    def escucha(self, duracion=3, fs=44100, canales=1):
        print("Grabando...")
        grabacion = sd.rec(int(duracion * fs), samplerate=fs, channels=canales)
        sd.wait()
        print("Listo")
        grabacion = grabacion.ravel()  # Evita pasar a filtfilt un arreglo con shape (n, 1).
        freqAC, freqPC = self.extractor.extrae(grabacion, fs)
        self._ultimaFreqAC = freqAC
        self._ultimaFreqPC = freqPC
        return freqAC, freqPC

    @staticmethod
    def _verosimilitud(x, media, desv):
        # Densidad de una normal, sin la constante de normalización
        # (no afecta la comparación entre Feme y Masc)
        return np.exp(-0.5 * ((x - media) / desv) ** 2) / desv

    def _parametros(self, modo):
        """Devuelve (medFeme, desvFeme, medMasc, desvMasc) del modo indicado."""
        if modo == "AC":
            return self.fmedACFeme, self.desvACFeme, self.fmedACMasc, self.desvACMasc
        if modo == "PC":
            return self.fmedPCFeme, self.desvPCFeme, self.fmedPCMasc, self.desvPCMasc
        raise ValueError("modo debe ser 'AC' o 'PC'")

    def decideFrecuencia(self, x, modo="AC"):
        """Decide el género a partir de una frecuencia ya medida (sin micrófono).

        x: frecuencia en Hz, o None si no se pudo medir.
        Devuelve (x, genero).
        """
        medFeme, desvFeme, medMasc, desvMasc = self._parametros(modo)

        if x is None or not np.isfinite(x) or x < 50:
            genero = "demasiado ruido"
            if x is None:
                print(f"Frecuencia detectada ({modo}): ninguna -> {genero}")
            else:
                print(f"Frecuencia detectada ({modo}): {x:.2f} Hz -> {genero}")
            return x, genero

        vFeme = self._verosimilitud(x, medFeme, desvFeme)
        vMasc = self._verosimilitud(x, medMasc, desvMasc)

        if vFeme < 1e-3 and vMasc < 1e-3:
            genero = "Audio extraño"
        elif vMasc == 0:
            genero = "Femenino"
        elif vFeme == 0:
            genero = "Masculino"
        else:
            ratio = vFeme / vMasc
            if 0.5 < ratio < 2:
                genero = "indeciso"
            elif vFeme > vMasc:
                genero = "Femenino"
            else:
                genero = "Masculino"

        print(f"Frecuencia detectada ({modo}): {x:.2f} Hz -> {genero}")
        return x, genero

    def decide(self, modo="AC"):
        self._parametros(modo)  # valida el modo antes de grabar
        freqAC, freqPC = self.escucha()
        x = freqAC if modo == "AC" else freqPC
        return self.decideFrecuencia(x, modo)

    @staticmethod
    def _actualizaMediaDesv(media_vieja, desv_vieja, n_viejo, x):
        # Algoritmo de Welford para actualizar media/desvío con una muestra nueva
        M2_viejo = (desv_vieja ** 2) * n_viejo
        n_nuevo = n_viejo + 1
        delta = x - media_vieja
        media_nueva = media_vieja + delta / n_nuevo
        delta2 = x - media_nueva
        M2_nuevo = M2_viejo + delta * delta2
        desv_nueva = np.sqrt(M2_nuevo / n_nuevo)
        return media_nueva, desv_nueva

    def actualizaDatos(self, genero, xAC, xPC):
        """Incorpora una muestra al modelo y guarda el JSON.

        Devuelve True si se actualizó; False si alguna frecuencia es None
        (o no es finita), en cuyo caso el modelo no se modifica.
        """
        if genero not in ("Femenino", "Masculino"):
            raise ValueError("genero debe ser 'Femenino' o 'Masculino'")

        if not all(x is not None and np.isfinite(x) for x in (xAC, xPC)):
            print("Muestra descartada: no se pudo medir alguna de las frecuencias.")
            return False

        if genero == "Femenino":
            self.fmedACFeme, self.desvACFeme = self._actualizaMediaDesv(
                self.fmedACFeme, self.desvACFeme, self.nFemeAC, xAC)
            self.nFemeAC += 1

            self.fmedPCFeme, self.desvPCFeme = self._actualizaMediaDesv(
                self.fmedPCFeme, self.desvPCFeme, self.nFemePC, xPC)
            self.nFemePC += 1

        elif genero == "Masculino":
            self.fmedACMasc, self.desvACMasc = self._actualizaMediaDesv(
                self.fmedACMasc, self.desvACMasc, self.nMascAC, xAC)
            self.nMascAC += 1

            self.fmedPCMasc, self.desvPCMasc = self._actualizaMediaDesv(
                self.fmedPCMasc, self.desvPCMasc, self.nMascPC, xPC)
            self.nMascPC += 1

        self._guardaJson()
        return True

    def _guardaJson(self):
        modelo = {
            "fmedACFeme": float(self.fmedACFeme),
            "desvAcFeme": float(self.desvACFeme),
            "fmedPCFeme": float(self.fmedPCFeme),
            "desvPCFeme": float(self.desvPCFeme),
            "nFemeAC": int(self.nFemeAC),
            "nFemePC": int(self.nFemePC),

            "fmedACMasc": float(self.fmedACMasc),
            "desvAcMasc": float(self.desvACMasc),
            "fmedPCMasc": float(self.fmedPCMasc),
            "desvPCMasc": float(self.desvPCMasc),
            "nMascAC": int(self.nMascAC),
            "nMascPC": int(self.nMascPC),
        }
        with open(self.archivo, "w", encoding="utf-8") as archivo:
            json.dump(modelo, archivo, indent=4)

    def decideYPregunta(self, modo="AC"):
        x, genero = self.decide(modo)

        if genero in ("Masculino", "Femenino"):
            if self._ultimaFreqAC is None or self._ultimaFreqPC is None:
                print("No se puede agregar la muestra: falta alguna de las frecuencias.")
                return x, genero

            respuesta = input(f"¿Agregar esta muestra a la base de datos como {genero}? (s/n): ")
            if respuesta.strip().lower() == "s":
                if self.actualizaDatos(genero, self._ultimaFreqAC, self._ultimaFreqPC):
                    print("Muestra agregada y JSON actualizado.")

        return x, genero
