<h1 id="index">Índice</h1>

1. **[Detección de Objetos](#deteccion-de-objetos)**
   1. [Funcionamiento](#funcionamiento)
      1. [Preprocesamiento de Imágenes](#funcionamiento-preprocesamiento-de-imagenes)
      2. [Arquitectura del Modelo](#funcionamiento-arquitectura-del-modelo)
      3. [Evaluación de Métricas](#funcionamiento-evaluacion-de-metricas)
   2. [YOLO](#yolo)
   3. [NPU](#npu)
      1. [Características Clave de las NPU](#npu-caracteristicas-clave)
2. **[Montaje del Modelo de Detección de Objetos](#montaje-del-modelo-de-deteccion-de-objetos)**
   1. [Creación del Conjunto de Datos](#creacion-del-conjunto-de-datos)
   2. [Instalación de Hailo AI HAT+](#instalacion-de-hailo-ai-hat)
   3. [Entrenamiento del Modelo](#entrenamiento-del-modelo)
   4. [Conversión del Modelo](#conversion-del-modelo)
   5. [Inferencia del Modelo](#inferencia-del-modelo)
3. **[Recursos Externos](#recursos-externos)**

<h1 id="deteccion-de-objetos">Detección de Objetos</h1>

Para la presente competencia, debido a la necesidad de poder reconocer distintos prismas de diferentes colores, específicamente en el Desafío con Obstáculos, se optó por utilizar un modelo de detección de objetos.

Dicha detección de objetos, es una tarea de visión por computadora que emplea redes neuronales para identificar y localizar objetos en imágenes o videos, al enmarcarlos con cuadros delimitadores y asignarles etiquetas. 

A través de esta técnica, se pueden clasificar y localizar múltiples objetos dentro de una sola imagen. Además, se considera una parte de la inteligencia artificial, ya que permite a las máquinas interpretar y comprender el contenido visual de manera similar a los humanos.

<h2 id="funcionamiento">Funcionamiento</h2>

Primeramente, debemos comprender distintos conceptos relacionados con la detección de objetos, como el preprocesamiento de imágenes, la arquitectura del modelo y las métricas de evaluación para la detección de objetos. A continuación, se presentan estos conceptos:

<h3 id="funcionamiento-preprocesamiento-de-imagenes">Preprocesamiento de Imágenes</h3>

Para la visión por computadora, las imágenes se expresan como funciones continuas en un plano de coordenadas 2D representadas como f(x, y). Cuando se digitalizan, las imágenes pasan por dos procesos primarios llamados muestreo y cuantización, que, en resumen, convierten la función de imagen continua en una estructura de cuadrícula discreta de elementos que representan píxeles [[1](#object-detection-ibm)]. 

<p align="center">
  <img src="https://assets-global.website-files.com/5d7b77b063a9066d83e1209c/627d121f86896a59aad78407_60f49c3f218440673e6baa97_apples1.png" alt="Imagen con distintas anotaciones de manzanas" width="400">
</p>
<p align="center">
    <i>Imagen con distintas anotaciones de manzanas</i>
</p>

Al ser anotada la imagen, el modelo de detección de objetos puede reconocer regiones con características similares a las definidas en el conjunto de datos de entrenamiento como el mismo objeto. Los modelos de detección de objetos no reconocen objetos per se, sino agregados de propiedades como tamaño, forma, color, etc., y clasifican regiones según patrones visuales inferidos a partir de datos de entrenamiento anotados manualmente [[1](#object-detection-ibm)].

<h3 id="funcionamiento-arquitectura-del-modelo">Arquitectura del Modelo</h3>

Los modelos de detección de objetos siguen una estructura general que incluye un modelo de fondo, cuello y cabeza [[1](#object-detection-ibm)].

El modelo de fondo extrae características de una imagen de entrada. A menudo, el modelo de fondo se deriva de parte de un modelo de clasificación preentrenado. La extracción de características produce una miríada de mapas de características de diferentes resoluciones que el modelo de fondo pasa al cuello. Esta última parte de la estructura concatena los mapas de características para cada imagen. Luego, la arquitectura pasa los mapas de características en capas a la cabeza, que predice cuadros delimitadores y puntuaciones de clasificación para cada conjunto de características [[1](#object-detection-ibm)].

<h3 id="funcionamiento-evaluacion-de-metricas">Evaluación de Métricas</h3>

La evaluación de métricas es un paso crucial en el proceso de detección de objetos, ya que permite medir la precisión y efectividad del modelo. Existen varias métricas utilizadas para evaluar modelos de detección de objetos, entre las cuales se encuentran:

- **Precisión**: Mide la proporción de verdaderos positivos (TP) entre el total de predicciones positivas (TP + FP). Es decir, cuántas de las predicciones realizadas por el modelo son correctas.
- **Exhaustividad (Recall)**: Mide la proporción de verdaderos positivos (TP) entre el total de casos positivos reales (TP + FN). Es decir, cuántos de los objetos que realmente están presentes en la imagen fueron detectados por el modelo.
- **F1 Score**: Es la media armónica entre precisión y exhaustividad. Se utiliza para evaluar el rendimiento del modelo en situaciones donde hay un desbalance entre las clases.
- **Mean Average Precision (mAP)**: Es una métrica que combina precisión y exhaustividad en un solo valor. Se calcula promediando la precisión a diferentes niveles de exhaustividad. El mAP se utiliza comúnmente para evaluar modelos de detección de objetos, ya que proporciona una medida más completa del rendimiento del modelo.

<h2 id="yolo">YOLO</h2>

YOLO, o "You Only Look Once" ("Solo Miras Una Vez"), consiste en una familia de modelos de una sola etapa que realizan detección de objetos en tiempo real. A diferencia de otros modelos de detección de objetos que utilizan un enfoque de dos etapas, YOLO divide la imagen en una cuadrícula y predice simultáneamente los cuadros delimitadores y las probabilidades de clase para cada celda de la cuadrícula. Esto permite que YOLO sea extremadamente rápido y eficiente [[1](#object-detection-ibm)].

Para Klevor, la detección de objetos se basa en el modelo YOLOv11; la última versión de YOLO hasta la fecha [[9](#models-ultralytics)].

<h2 id="npu">NPU</h2>

Una unidad de procesamiento neuronal (NPU) es un microprocesador especializado diseñado para imitar la función de procesamiento del cerebro humano. Están optimizados para tareas y aplicaciones de inteligencia artificial (IA), redes neuronales, aprendizaje profundo y aprendizaje automático [[2](#npu-ibm)].

<p align="center">
  <img src="https://i.postimg.cc/6399NRt6/raspberry-pi-ai-hat-raspberry-pi-71328528531841-removebg-preview.png" alt="Raspberry Pi AI HAT+ 26 TOPS" width="400">
</p>
<p align="center">
    <i>Raspberry Pi AI HAT+ 26 TOPS</i>
</p>

A diferencia de las unidades de procesamiento gráfico (GPU) y las unidades de procesamiento central (CPU), que son procesadores de propósito general, las NPUs están diseñadas para acelerar tareas y cargas de trabajo de IA, como el cálculo de capas de redes neuronales compuestas por matemáticas escalares, vectoriales y tensoriales [[2](#npu-ibm)].

<h3 id="npu-caracteristicas-clave">Características Clave de las NPU</h3>

Las NPUs están diseñadas para realizar tareas que requieran una baja latencia y un alto rendimiento en paralelo, lo que las hace ideales para aplicaciones de inteligencia artificial. Estas tareas incluyen el procesamiento de algoritmos de aprendizaje profundo, reconocimiento de voz, procesamiento de lenguaje natural, procesamiento de fotos y videos, y detección de objetos [[2](#npu-ibm)].

Entre las características clave de las NPUs se encuentran:

- **Procesamiento paralelo**: Las NPUs están diseñadas para realizar cálculos en paralelo, lo que les permite procesar múltiples operaciones simultáneamente. Esto es especialmente útil para tareas de aprendizaje profundo, donde se requieren grandes cantidades de cálculos en matrices y tensores.

- **Baja precisión aritmética**: Las NPUs a menudo admiten operaciones de 8 bits (o menos) para reducir la complejidad computacional y aumentar la eficiencia energética.

- **Memoria de alto ancho de banda**: Muchas NPUs cuentan con memoria de alto ancho de banda en el chip para realizar eficientemente tareas de procesamiento de IA que requieren grandes conjuntos de datos.

- **Aceleración por hardware**: Los avances en el diseño de NPUs han llevado a la incorporación de técnicas de aceleración por hardware, como arquitecturas de matriz sistólica o procesamiento tensorial mejorado para optimizar el rendimiento de las cargas de trabajo de IA.

<h1 id="montaje-del-modelo-de-deteccion-de-objetos">Montaje del Modelo de Detección de Objetos</h1>

Para el montaje del modelo de detección de objetos, se deben seguir los siguientes pasos:

<h2 id="creacion-del-conjunto-de-datos">Creación del Conjunto de Datos</h2>

Para la creación del conjunto de datos, primeramente tomamos imágenes de los prismas que se utilizarán en la competencia. Estas imágenes fueron tomadas con los distintos dispositivos de nuestro equipo, en distintas condiciones de luz y ángulos, y las cuales guardamos en la carpeta [```dataset/general/original/to_process```](dataset/general/original/to_process). Seguidamente, ejecutamos el script [```resize.py```](resize.py) para redimensionar las imágenes a un tamaño de 640 × 640 píxeles, que es el tamaño de entrada del modelo YOLOv11. Este script utiliza la biblioteca OpenCV para redimensionar las imágenes y guardarlas en la carpeta [```dataset/general/resized/to_process```](dataset/general/resized/to_process).

<p align="center">
   <img src="https://i.postimg.cc/RFBvkzPz/IMG-20250221-135320.jpg" alt="Imagen sin redimensionar del conjunto de datos" width="400">
   <i>Imagen sin redimensionar del conjunto de datos</i>
</p>

<p align="center">
   <img src="https://i.postimg.cc/B6r7YqNx/IMG-20250221-135449.jpg" alt="Imagen redimensionada del conjunto de datos" width="400">
   <i>Imagen redimensionada del conjunto de datos</i>
</p>

Posteriormente, se realizó la anotación de las imágenes, donde se etiquetaron los prismas con sus respectivos colores. Para ello, se utilizó la herramienta Label Studio, una herramienta de etiquetado de datos de código abierto que permite crear conjuntos de datos personalizados para el entrenamiento de modelos de aprendizaje automático [[3](#label-studio)]. En esta, creamos tres etiquetas: ```green rectangular prism```, ```magenta rectangular prism``` y ```red rectangular prism```, los cuales representan el prisma verde, magenta y rojo, respectivamente.

Durante el proceso, manejamos conjunto de datos de 2, 3, 4 clases, las cuales fuimos variando a lo largo del desarrollo del proyecto. Primeramente, desarrollamos un modelo de 4 clases, sin embargo, no logró un buen rendimiento para todas las clases, ya que incluía, además del prisma rojo y verde, la línea naranja y la línea azul, que finalmente, debido a nuestros componentes, se podían inferir mediante el RPLIDAR C1. Posteriormente, se decidió omitir las clases relacionadas con las líneas de la pista, las cuales no eran necesarias para la detección de los prismas. Finalmente, se optó por un modelo de 2 clases, el cual fue capaz de detectar los prismas rojo y verde. Cómo se observó anteriormente, se optó por un conjunto de datos de 3 clases, ya que añadimos una clase adicional, el prisma magenta, para poder realizar la detección del estacionamiento. 

Cabe destacar que, así como variamos el número de clases, también variamos el número de imágenes por clase, desde un dataset de alrededor de 350 imágenes antes de realizar el *data augmentation*, hasta un dataset de alrededor de 1100 imágenes antes de realizar el *data augmentation*, donde cada una fue anotada por algún integrante del equipo de forma manual para entrenar el modelo de la forma más precisa posible.

Después de haber anotado las imágenes con la plataforma Label Studio, se exportaron las anotaciones en formato YOLO y se guardaron, en el caso del modelo de 3 clases, en la carpeta [```dataset/3c/labeled/to_process```](dataset/3c/labeled/to_process). Posteriormente, se ejecutó el script [```augment.py```](augment.py) para generar alrededor de 10 imágenes por cada imagen del conjunto de datos, utilizando la biblioteca OpenCV. Este script aplica distintas transformaciones a las imágenes, como rotación, escalado, traslación y cambio de brillo y contraste, para aumentar la variabilidad del conjunto de datos y mejorar el rendimiento del modelo. Las imágenes generadas se guardaron en la carpeta [```dataset/3c/augmented/to_process```](dataset/3c/augmented/to_process).

Luego, se ejecutó el script [```split.py```](split.py) para dividir el conjunto de datos en un conjunto de entrenamiento [```dataset/3c/organized/train```](dataset/3c/organized/to_process/train), un conjunto de validación [```dataset/3c/organized/val```](dataset/3c/organized/to_process/val) y un conjunto de testing [```dataset/3c/organized/test```](dataset/3c/organized/to_process/test), con una distribución del 70%, 20% y 10%, respectivamente. Este script utiliza la biblioteca ```os``` para crear las carpetas necesarias y mover las imágenes a las carpetas correspondientes.

*NOTA: Se puede observar, que en cada una de las rutas, se encuentra la carpeta ```to_process```, la cual es una carpeta temporal, que se utiliza para guardar las imágenes que se están procesando. Una vez que se han procesado las imágenes, los archivos dentro de las mismas se mueven a una carpeta ```processed``` correspondiente, la cual se encuentra en la misma ruta. De esta forma, se evita que las imágenes procesadas se mezclen con las imágenes por procesar, así como permite a futuro seguir entrenando el mismo modelo, sin necesidad de volver a procesar las mismas imágenes.*

<p align="center">
   <img src="https://i.postimg.cc/B6kkr5ZP/Figure-2.png" alt="Imagen con distintas inferencias realizadas (modelo de 3 clases)" width="400">
   <i>Imagen con distintas inferencias realizadas (modelo de 3 clases)</i>
</p>


<h1 id="recursos-externos">Recursos Externos</h1>

1. Murel, J., Kavlakoglu, E. *What is object detection?*. (3 de enero de 2024) IBM. <a id="object-detection-ibm">https://www.ibm.com/topics/object-detection</a>
2. Schneider, J., Smalley, I. *What is neural processing unit (NPU)?*. (27 de septiembre de 2024). IBM. <a id="npu-ibm">https://www.ibm.com/topics/neural-processing-unit</a>
3. *Label Studio*. (2025). Label Studio. <a id="label-studio">https://labelstud.io/</a>
4. *AI Kit and AI HAT+ software*. (2025). Raspberry Pi. <a id="getting-started-raspberry-pi">https://www.raspberrypi.com/documentation/computers/ai.html#getting-started</a>
5. *AI Hat+*. (2025). Raspberry Pi. <a id="ai-hat-plus-raspberry-pi">https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html#ai-hat-plus</a>
6. Hailo AI. (2025). *Hailo Application Code Examples*. GitHub. <a id="hailo-ai-examples-github">https://github.com/hailo-ai/Hailo-Application-Code-Examples</a>
7. d'Oleron, L. (23 de abril de 2025). *Custom dataset with Hailo AI Hat, Yolo, Raspberry PI 5, and Docker*. Medium. <a id="custom-dataset-medium">https://pub.towardsai.net/custom-dataset-with-hailo-ai-hat-yolo-raspberry-pi-5-and-docker-0d88ef5eb70f</a>
8. *Google Colab*. (2025). Google Colab. <a id="google-colab">https://colab.research.google.com/</a>
9. *Models*. (2025). Ultralytics. <a id="models-ultralytics">https://docs.ultralytics.com/models/</a>
