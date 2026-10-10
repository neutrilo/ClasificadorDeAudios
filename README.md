# Identificador de voces

Proyecto orientado al desarrollo de un sistema capaz de **captar audio en tiempo real y clasificar una voz según sus características**.

La primera versión del proyecto tiene como objetivo distinguir entre:

* **Voz masculina**
* **Voz femenina**
* **Indistinguible / baja confianza**

La posibilidad de utilizar una categoría de "indistinguible" busca evitar que el sistema fuerce una clasificación cuando las características del audio no permiten realizar una predicción con suficiente confianza.

> **Estado del proyecto:** desarrollo de la primera versión.

## Objetivo

El objetivo general es desarrollar un identificador de voces que pueda recibir un audio, analizar sus características y determinar a qué categoría pertenece.

En esta primera etapa se busca construir una base funcional que permita posteriormente ampliar el sistema hacia otras características de clasificación y análisis de voz.

El proyecto está diseñado teniendo en cuenta su **escalabilidad**. Por esta razón se utiliza **programación orientada a objetos (POO)**, separando las diferentes responsabilidades del sistema en clases independientes.

Aunque una implementación inicial mediante programación funcional podría resultar más sencilla, la utilización de POO busca facilitar la incorporación de nuevas funcionalidades y componentes a medida que el proyecto crezca.

## Instalación

Requiere Python 3.12 o superior. Desde la raíz del proyecto:

```bash
pip install .                    # dependencias base: numpy, scipy, soundfile
pip install ".[microfono]"       # añade sounddevice (grabación desde el micrófono)
pip install ".[graficas]"        # añade matplotlib (grafica_modelo.py)
pip install ".[dev]"             # añade pytest
```

También se puede instalar directamente desde el repositorio:

```bash
pip install "git+https://github.com/neutrilo/ClasificadorDeAudios.git"
```

El paquete `src` puede importarse sin `sounddevice`: `grabador` y `predictor` se cargan solo cuando se usan.

Para ejecutar las pruebas (no usan el micrófono ni modifican `data/` ni `modelo/`):

```bash
pip install ".[dev]"
python -m pytest
```

## Estructura del proyecto

La estructura inicial del proyecto es:

```text
/
├── src/
│   ├── ...
│   └── ...
│
├── data/
│   ├── ...
│   └── ...
│
├── modelo/
│   ├── ...
│   └── ...
│
├── analisis.py
├── compara.py
├── grafica_modelo.py
├── main.py
└── README.md
```

### `src/`

Contiene los recursos y las clases que forman parte del sistema.

Cada clase se encuentra definida en un archivo independiente, con el objetivo de mantener una estructura ordenada y facilitar el mantenimiento y la posterior ampliación del proyecto.

A medida que el proyecto avance, esta carpeta contendrá las diferentes clases necesarias para tareas como la captura, procesamiento, análisis y clasificación del audio.

### `data/`

Esta carpeta almacena los audios de referencia. Para ejecutar `analisis.py`, organiza los archivos WAV en estas subcarpetas:

```text
data/
├── feme/
└── masc/
```

La estructura definitiva de los datos podrá modificarse a medida que se definan las necesidades del proyecto.

Los audios almacenados en esta carpeta constituyen los **datos originales** a partir de los cuales se realizará el estudio necesario para construir el modelo.

### `modelo/`

Esta carpeta almacenará la **información derivada de los datos de `data/` que sea necesaria para realizar nuevas clasificaciones**.

La idea es separar el proceso de estudio de los datos del proceso de clasificación de nuevos audios.

Inicialmente, el sistema analizará los audios disponibles en `data/` para obtener la información relevante para la clasificación. Este análisis se realizará durante una etapa de preparación del modelo y sus resultados serán almacenados en `modelo/`.

De esta manera, cuando se quiera clasificar un nuevo audio, el sistema no tendrá que volver a analizar todos los audios originales de `data/`. En su lugar, utilizará la información previamente calculada y almacenada en `modelo/`.

El flujo conceptual es:

```text
              ETAPA DE PREPARACIÓN

data/
  │
  ├── audios masculinos
  └── audios femeninos
          │
          ↓
    Análisis de los datos
          │
          ↓
       modelo/
          │
          └── información derivada
```

Posteriormente:

```text
              CLASIFICACIÓN

Nuevo audio
     │
     ↓
Procesamiento
     │
     ↓
Información almacenada en modelo/
     │
     ↓
Clasificación
     │
     ├── Masculino
     ├── Femenino
     └── Indistinguible / baja confianza
```

El archivo `modelo/modelo.json` almacena las medias, desviaciones estándar y cantidades de muestras utilizadas para clasificar y graficar las frecuencias.

### `main.py`

Es el punto de entrada de la aplicación y presenta un menú para elegir qué proceso ejecutar.

El programa deberá ejecutarse desde la **carpeta raíz del proyecto**:

```bash
python main.py
```

## Scripts disponibles

### `analisis.py`

Analiza los archivos WAV de las carpetas `data/feme/` y `data/masc/`, y guarda los resultados en `modelo/modelo.json`.

> **Advertencia:** este proceso sobrescribe `modelo/modelo.json`. La información incorporada al modelo durante las comparaciones, que no esté representada por los audios de `data/`, puede perderse al volver a generar el análisis. El menú de `main.py` solicita dos confirmaciones antes de ejecutarlo.

### `compara.py`

Usa el micrófono para capturar y clasificar una voz en memoria, sin guardar la grabación como archivo de audio. Si el resultado es masculino o femenino, pregunta si se desea agregar esa muestra a los datos del modelo JSON.

### `grafica_modelo.py`

Lee `modelo/modelo.json` y muestra en una misma figura dos gráficas: las distribuciones gaussianas de las frecuencias obtenidas por autocorrelación y por primera colina. Cada gráfica compara las curvas masculina y femenina.

### `main.py`

Ofrece un menú para ejecutar `analisis.py`, `compara.py` o `grafica_modelo.py`. Antes de iniciar el análisis exige dos confirmaciones porque este sobrescribe el JSON del modelo.


## Funcionamiento previsto

El proyecto contempla conceptualmente dos procesos diferentes.

### 1. Preparación del modelo

Los datos disponibles en `data/` serán estudiados para obtener la información necesaria para la clasificación.

Este proceso podrá realizarse cuando se incorporen nuevos datos o cuando sea necesario reconstruir el modelo.

```text
data/
   ↓
Análisis
   ↓
modelo/
```

### 2. Clasificación de nuevos audios

Una vez preparada la información de `modelo/`, un nuevo audio podrá ser procesado y clasificado sin necesidad de volver a recorrer todos los audios originales.

```text
Nuevo audio
    ↓
Procesamiento
    ↓
Comparación / clasificación
    ↓
modelo/
    ↓
Resultado
```

El resultado deberá incluir no solamente una clasificación, sino también la posibilidad de indicar que el audio **no puede clasificarse con suficiente confianza**.

Por ejemplo:

```text
Resultado: Voz masculina
Confianza: 92 %
```

o:

```text
Resultado: Indistinguible
Confianza: 54 %
```

La forma exacta en que se calculará y presentará la confianza todavía forma parte del desarrollo del proyecto.

## Programación orientada a objetos

El proyecto utiliza POO principalmente como una decisión de diseño orientada a la **escalabilidad**.

Cada componente del sistema tendrá una responsabilidad definida y será implementado mediante clases independientes.

Esta separación permitirá, por ejemplo, modificar posteriormente el método de análisis o clasificación sin tener que reconstruir completamente el resto del sistema.

La arquitectura se encuentra todavía en desarrollo, por lo que la organización definitiva de las clases y sus relaciones podrá cambiar durante la implementación de la primera versión.

## Estado actual

El proyecto se encuentra en una etapa inicial de desarrollo.

Actualmente:

* La estructura básica del repositorio está definida.
* La carpeta `src/` está destinada a las clases del sistema.
* La carpeta `data/` está preparada para incorporar posteriormente los conjuntos de datos.
* La carpeta `modelo/` está destinada a almacenar la información derivada del estudio de los datos.
* `main.py` permite elegir entre analizar los audios de referencia, comparar una voz desde el micrófono o visualizar las distribuciones del modelo.
* El proceso de análisis vuelve a generar el archivo JSON del modelo a partir de los audios WAV disponibles.

La arquitectura y las responsabilidades de las clases se irán definiendo progresivamente durante el desarrollo.

## Próximas etapas

Entre las tareas previstas para el desarrollo se encuentran:

1. Definir las clases principales del sistema.
2. Implementar la captura y lectura de audio.
3. Implementar el procesamiento de las señales.
4. Determinar las características utilizadas para diferenciar las voces.
5. Implementar el proceso de estudio de los datos.
6. Definir qué información debe almacenarse en `modelo/`.
7. Implementar el sistema de clasificación.
8. Incorporar un mecanismo para identificar resultados de baja confianza.
9. Organizar los datos de entrenamiento y prueba.
10. Implementar `main.py` como punto de entrada.
11. Realizar pruebas con audios reales.
12. Evaluar posibles ampliaciones del sistema.

## Alcance de la primera versión

La primera versión estará limitada a la clasificación entre **voz masculina, voz femenina e indistinguible/baja confianza**.

El objetivo inicial no es construir un sistema definitivo de identificación de personas, sino desarrollar una base sobre la cual puedan incorporarse posteriormente nuevas funcionalidades y categorías de análisis.

La separación entre `data/` y `modelo/` busca además establecer desde el principio una arquitectura en la que el **procesamiento de los datos de referencia y la clasificación de nuevos audios sean procesos independientes**.
