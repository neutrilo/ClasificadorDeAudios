import soundfile as sf

class grabador:
    def __init__(self, sr = 44100,canales = 1):
        self.sr = sr
        self.canales = 1

    def grabar(self,duracion):
        import sounddevice as sd  # se importa aquí para que el paquete funcione sin PortAudio
        print("Grabando...")
        grabacion = sd.rec(int(duracion * self.sr), samplerate=self.sr, channels=self.canales).ravel()
        sd.wait()
        print("Listo")
        return(grabacion)

    def grabarYGuardar(self,duracion,ruta):
        datos = self.grabar(duracion)
        sf.write(ruta, datos, self.sr)
        return(datos)