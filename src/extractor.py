import numpy as np
from scipy.signal import butter, filtfilt, correlate

class Extractor:
    def __init__(self, min = 80, max = 300):
        self.fmin = min
        self.fmax = max

    def pasabanda(self,datos, frec_baja, frec_alta, fs, orden=4):
        nyquist = fs / 2
        baja = frec_baja / nyquist
        alta = frec_alta / nyquist
        
        if not (0 < baja < 1) or not (0 < alta < 1):
            raise ValueError(f"Frecuencias fuera de rango: baja={frec_baja}, alta={frec_alta}, nyquist={nyquist}")
        
        b, a = butter(orden, [baja, alta], btype='band')
        filtrada = filtfilt(b, a, datos)
        
        return filtrada

    def autocorrelacion_pitch(self,datos, fs, frec_min=50, frec_max=300, devolver_vectores=False):
        """
        Calcula la autocorrelación de la señal y busca el pico
        dentro del rango de lags correspondiente a [frec_min, frec_max] Hz.
        
        datos: señal de audio (array 1D)
        fs: frecuencia de muestreo (Hz)
        frec_min, frec_max: rango de frecuencias de interés (Hz)
        devolver_vectores: si es True, también devuelve los arrays de lags
                            y correlación (útil para graficar)
        
        Devuelve siempre:
            lag_pico, frecuencia_estimada
        Si devolver_vectores=True, además devuelve:
            lags (array de lags evaluados, en muestras)
            segmento (valores de correlación para cada lag)
        """
        lag_min = int(fs / frec_max)
        lag_max = int(fs / frec_min)

        n = len(datos)

        corr = correlate(datos, datos, mode='full', method='auto')
        corr = corr[n - 1:]  # mitad de lags >= 0

        segmento = corr[lag_min:lag_max]

        if len(segmento) == 0:
            if devolver_vectores:
                return None, None, None, None
            return None, None

        lag_pico = np.argmax(segmento) + lag_min
        frecuencia_estimada = fs / lag_pico

        if devolver_vectores:
            lags = np.arange(lag_min, lag_max)
            return lag_pico, frecuencia_estimada, lags, segmento

        return frecuencia_estimada

    def frecuencia_media_primera_colina(self,sennal, fs, ancho_hz=80, concentracion=3, umbral=0.4):
        """
        Calcula la frecuencia media de la primera "colina" del espectro concentrado.
        
        sennal: señal de audio (array 1D)
        fs: frecuencia de muestreo (Hz)
        ancho_hz: ancho en Hz del tramo a considerar a partir del punto donde
                el espectro concentrado supera el umbral (por defecto 80 Hz)
        concentracion: exponente usado para concentrar el espectro (por defecto 3)
        umbral: altura normalizada que debe superar el espectro concentrado
                para marcar el inicio de la colina (por defecto 0.3)
        
        Devuelve: frecuencia media (Hz) dentro del tramo [f_inicio, f_inicio + ancho_hz]
        """
        frecuencias = np.fft.rfftfreq(len(sennal), d=1/fs)
        espectro = np.abs(np.fft.rfft(sennal))
        espectro = espectro / np.max(espectro)
        espectro_concentrado = espectro ** concentracion

        # Encontrar el primer punto que supera el umbral
        indices_sobre_umbral = np.where(espectro_concentrado > umbral)[0]

        if len(indices_sobre_umbral) == 0:
            return None

        indice_inicio = indices_sobre_umbral[0]
        f_inicio = frecuencias[indice_inicio]
        f_fin = f_inicio + ancho_hz

        # Restringir al tramo [f_inicio, f_inicio + ancho_hz]
        mascara = (frecuencias >= f_inicio) & (frecuencias <= f_fin)

        if not np.any(mascara):
            return None

        frecuencia_media = np.average(frecuencias[mascara], weights=espectro_concentrado[mascara])

        return frecuencia_media

    def extrae(self,sennal, fs):
        sennal = self.pasabanda(sennal,self.fmin,self.fmax,fs,orden =4)
        freqAutoC = self.autocorrelacion_pitch(sennal,fs,self.fmin,self.fmax,False)
        freqPCol = self.frecuencia_media_primera_colina(sennal, fs, ancho_hz=70, concentracion=3, umbral=0.4)
        return freqAutoC, freqPCol