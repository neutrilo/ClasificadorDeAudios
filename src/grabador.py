import sounddevice as sd
import soundfile as sf

class grabador:
    def __init__(self, sr = 44100,canales = 1):
        self.sr = sr
        self.canales = canales

    def grabar(self,duracion):        
        print("Grabando...")
        grabacion = sd.rec(int(duracion * self.sr), samplerate=self.sr, channels=self.canales)
        sd.wait()
        if self.canales == 1:
            grabacion = grabacion.ravel()  # arreglo 1D para un solo canal
        print("Listo")
        return(grabacion)

    def grabarYGuardar(self,duracion,ruta):
        datos = self.grabar(duracion)
        sf.write(ruta, datos, self.sr)
        return(datos)