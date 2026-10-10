import numpy as np
import soundfile as sf


class Lector:

    formatos_soportados = [".wav", ".mp3", ".flac"]
    
    def __init__(self):
        pass
    
    @staticmethod
    def stereoAMono(arreglo):
        if len(arreglo.shape) == 2: # Es un arreglo bidimensional
            if arreglo.shape[1] == 2: # Tiene dos columnas
                return (arreglo[:,0]+ arreglo[:,1])/2
        return arreglo.ravel()

    @classmethod
    def lee(cls, ruta):
        if ruta.lower().endswith(tuple(cls.formatos_soportados)):
            sennal, sr = sf.read(ruta)
            sennal = cls.stereoAMono(sennal)
            return sennal, sr
        raise ValueError(
            f"Formato no válido: {ruta!r}. Formatos soportados: {', '.join(cls.formatos_soportados)}"
        )

        
