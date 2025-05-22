<h1 id="index">Índice</h1>

1. **[Machine Learning](#machine-learning)**
2. **[Detección de Objetos](#deteccion-de-objetos)**
   1. [Funcionamiento](#funcionamiento)
      1. [Preprocesamiento de Imágenes](#funcionamiento-preprocesamiento-de-imagenes)
      2. [Arquitectura del Modelo](#funcionamiento-arquitectura-del-modelo)
      3. [Evaluación de Métricas](#funcionamiento-evaluacion-de-metricas)
   2. [YOLO](#yolo)
   3. [NPU](#npu)
      1. [Características Clave de las NPU](#npu-caracteristicas-clave)
3. **[Montaje del Modelo de Detección de Objetos](#montaje-del-modelo-de-deteccion-de-objetos)**
   1. [Creación del Conjunto de Datos](#creacion-del-conjunto-de-datos)
   2. [Entrenamiento del Modelo](#entrenamiento-del-modelo)
   3. [Instalación de Hailo AI HAT+](#instalacion-de-hailo-ai-hat)
   4. [Conversión del Modelo](#conversion-del-modelo)
      1. [Docker](#que-es-docker)
         1. [Dockerfile](#que-es-dockerfile)
         2. [Docker Image](#que-es-docker-image)
         3. [Docker Container](#que-es-docker-container)
      2. [Cómo Convertir el Modelo a un Formato Compatible al Hailo 8](#como-convertir-el-modelo-a-un-formato-compatible-al-hailo-8l) 
4. **[Recursos Externos](#recursos-externos)**

<h1 id="machine-learning">Machine Learning</h1>

El Machine Learning (ML) es una rama de la inteligencia artificial enfocada en imitar la manera en que los humanos piensan en una computadora, para realizar tareas de forma autónoma, y para mejorar el rendimiento y precisión a medida que se expone a un mayor conjunto de datos.

Normalmente, se divide en 3 partes el sistema de aprendizaje de un algoritmo de Machine Learning:

1. **Proceso de decisión**: En general, los algoritmos de Machine Learning son empleados para predecir o clasificar, a través de unos datos de entrada, que pueden ser etiquetados o no etiquetados, los cuales producen un patrón estimado de dicho conjunto de datos.
2. **Función de error**: Una función de error que evalúa las predicciones del modelo. Este emplea conjuntos de datos, de los cuales ya se conoce su resultado, para poder comparar la precisión del modelo.
3. **Proceso de optimización del modelo**: Si el modelo puede encajar mejor al conjunto de los datos en el set de entrenamiento, los pesos son ajustados para reducir la diferencia entre las estimaciones y los resultados conocidos. Este proceso iterativo de evaluación y optimización, se repite de forma autónoma hasta actualizar los pesos a un umbral de aceptación.

<h1 id="deteccion-de-objetos">Detección de Objetos</h1>

Para la presente competencia, debido a la necesidad de poder reconocer distintos prismas de diferentes colores, específicamente en el Desafío con Obstáculos, se optó por utilizar un modelo de detección de objetos.

Dicha detección de objetos, es una tarea de visión por computadora que emplea redes neuronales para identificar y localizar objetos en imágenes o videos, al enmarcarlos con cuadros delimitadores y asignarles etiquetas. 

A través de esta técnica, se pueden clasificar y localizar múltiples objetos dentro de una sola imagen. Además, se considera una parte de la inteligencia artificial, ya que permite a las máquinas interpretar y comprender el contenido visual de manera similar a los humanos.

<h2 id="funcionamiento">Funcionamiento</h2>

Primeramente, debemos comprender distintos conceptos relacionados con la detección de objetos, como el preprocesamiento de imágenes, la arquitectura del modelo y las métricas de evaluación para la detección de objetos. A continuación, se presentan estos conceptos:

<h3 id="funcionamiento-preprocesamiento-de-imagenes">Preprocesamiento de Imágenes</h3>

Para la visión por computadora, las imágenes se expresan como funciones continuas en un plano de coordenadas 2D representadas como f(x, y). Cuando se digitalizan, las imágenes pasan por dos procesos primarios llamados muestreo y cuantización, que, en resumen, convierten la función de imagen continua en una estructura de cuadrícula discreta de elementos que representan píxeles [[2](#object-detection-ibm)]. 

<p align="center">
   <img src="https://assets-global.website-files.com/5d7b77b063a9066d83e1209c/627d121f86896a59aad78407_60f49c3f218440673e6baa97_apples1.png" alt="Imagen con distintas anotaciones de manzanas" width="400">
   <br>
   <i>Imagen con distintas anotaciones de manzanas</i>
</p>

Al ser anotada la imagen, el modelo de detección de objetos puede reconocer regiones con características similares a las definidas en el conjunto de datos de entrenamiento como el mismo objeto. Los modelos de detección de objetos no reconocen objetos per se, sino agregados de propiedades como tamaño, forma, color, etc., y clasifican regiones según patrones visuales inferidos a partir de datos de entrenamiento anotados manualmente [[2](#object-detection-ibm)].

<h3 id="funcionamiento-arquitectura-del-modelo">Arquitectura del Modelo</h3>

Los modelos de detección de objetos siguen una estructura general que incluye un modelo de fondo, cuello y cabeza [[2](#object-detection-ibm)].

El modelo de fondo extrae características de una imagen de entrada. A menudo, el modelo de fondo se deriva de parte de un modelo de clasificación preentrenado. La extracción de características produce una miríada de mapas de características de diferentes resoluciones que el modelo de fondo pasa al cuello. Esta última parte de la estructura concatena los mapas de características para cada imagen. Luego, la arquitectura pasa los mapas de características en capas a la cabeza, que predice cuadros delimitadores y puntuaciones de clasificación para cada conjunto de características [[2](#object-detection-ibm)].

<h3 id="funcionamiento-evaluacion-de-metricas">Evaluación de Métricas</h3>

La evaluación de métricas es un paso crucial en el proceso de detección de objetos, ya que permite medir la precisión y efectividad del modelo. Existen varias métricas utilizadas para evaluar modelos de detección de objetos, entre las cuales se encuentran:

- **Precisión**: Mide la proporción de verdaderos positivos (TP) entre el total de predicciones positivas (TP + FP). Es decir, cuántas de las predicciones realizadas por el modelo son correctas.
- **Exhaustividad (Recall)**: Mide la proporción de verdaderos positivos (TP) entre el total de casos positivos reales (TP + FN). Es decir, cuántos de los objetos que realmente están presentes en la imagen fueron detectados por el modelo.
- **F1 Score**: Es la media armónica entre precisión y exhaustividad. Se utiliza para evaluar el rendimiento del modelo en situaciones donde hay un desbalance entre las clases.
- **Mean Average Precision (mAP)**: Es una métrica que combina precisión y exhaustividad en un solo valor. Se calcula promediando la precisión a diferentes niveles de exhaustividad. El mAP se utiliza comúnmente para evaluar modelos de detección de objetos, ya que proporciona una medida más completa del rendimiento del modelo.

<h2 id="yolo">YOLO</h2>

YOLO, o "You Only Look Once" ("Solo Miras Una Vez"), consiste en una familia de modelos de una sola etapa que realizan detección de objetos en tiempo real. A diferencia de otros modelos de detección de objetos que utilizan un enfoque de dos etapas, YOLO divide la imagen en una cuadrícula y predice simultáneamente los cuadros delimitadores y las probabilidades de clase para cada celda de la cuadrícula. Esto permite que YOLO sea extremadamente rápido y eficiente [[2](#object-detection-ibm)].

Para Klevor, la detección de objetos se basa en el modelo YOLOv11; la última versión de YOLO hasta la fecha [[11](#models-ultralytics)].

<h2 id="npu">NPU</h2>

Una unidad de procesamiento neuronal (NPU) es un microprocesador especializado diseñado para imitar la función de procesamiento del cerebro humano. Están optimizados para tareas y aplicaciones de inteligencia artificial (IA), redes neuronales, aprendizaje profundo y aprendizaje automático [[3](#npu-ibm)].

<p align="center">
   <img src="https://i.postimg.cc/6399NRt6/raspberry-pi-ai-hat-raspberry-pi-71328528531841-removebg-preview.png" alt="Raspberry Pi AI HAT+ 26 TOPS" width="400">
   <br>
   <i>Raspberry Pi AI HAT+ 26 TOPS</i>
</p>

A diferencia de las unidades de procesamiento gráfico (GPU) y las unidades de procesamiento central (CPU), que son procesadores de propósito general, las NPUs están diseñadas para acelerar tareas y cargas de trabajo de IA, como el cálculo de capas de redes neuronales compuestas por matemáticas escalares, vectoriales y tensoriales [[3](#npu-ibm)].

<h3 id="npu-caracteristicas-clave">Características Clave de las NPU</h3>

Las NPUs están diseñadas para realizar tareas que requieran una baja latencia y un alto rendimiento en paralelo, lo que las hace ideales para aplicaciones de inteligencia artificial. Estas tareas incluyen el procesamiento de algoritmos de aprendizaje profundo, reconocimiento de voz, procesamiento de lenguaje natural, procesamiento de fotos y videos, y detección de objetos [[3](#npu-ibm)].

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
   <br>
   <i>Imagen sin redimensionar del conjunto de datos</i>
</p>

<p align="center">
   <img src="https://i.postimg.cc/B6r7YqNx/IMG-20250221-135449.jpg" alt="Imagen redimensionada del conjunto de datos" width="400">
   <br>
   <i>Imagen redimensionada del conjunto de datos</i>
</p>

Posteriormente, se realizó la anotación de las imágenes, donde se etiquetaron los prismas con sus respectivos colores. Para ello, se utilizó la herramienta Label Studio, una herramienta de etiquetado de datos de código abierto que permite crear conjuntos de datos personalizados para el entrenamiento de modelos de aprendizaje automático [[4](#label-studio)].

*TIP: Si el número de imágenes por anotar es muy grande, notaremos que la herramienta Label Studio arrojará un error ```The number of files exceeded settings.DATA_UPLOAD_MAX_NUMBER_FILES```. Para solucionarlo, si Label Studio fue instalado como un paquete de Python, se puede modificar el archivo ```settings.py``` que se encuentra en la carpeta ```label_studio/core/settings.py```, donde se debe cambiar el valor de ```DATA_UPLOAD_MAX_NUMBER_FILES``` a un número mayor al número de imágenes por anotar o ```None``` si se desea un número ilimitado. En caso de no encontrar este archivo, se puede buscar en la carpeta ```site-packages/label_studio/core/settings.py``` dentro del entorno virtual de Python donde fue instalado Label Studio.*

<p align="center">
   <img src="https://i.postimg.cc/DyFZ1ryX/Screenshot-162.png" alt="Anotación de imágenes con Label Studio" width="800">
   <br>
   <i>Anotación de imágenes con Label Studio</i>
</p>

Durante el proceso, manejamos conjunto de datos de 1 (**G**, **M**, **R**), 2 (**GR**), 3 (**GMR**), 4 (**BGOR**) clases, las cuales fuimos variando a lo largo del desarrollo del proyecto, donde **M** proviene de ```magenta rectangular prism```, **G** de ```green rectangular prism```, **R** de ```red rectangular prism```, **B** de ```blue line``` y **O** de ```orange line```. Primeramente, desarrollamos un modelo de 4 clases, sin embargo, no logró un buen rendimiento para todas las clases, ya que incluía, además del prisma rojo y verde, la línea naranja y la línea azul, que finalmente, debido a nuestros componentes, se podían inferir mediante el RPLIDAR C1. Posteriormente, se decidió omitir las clases relacionadas con las líneas de la pista, las cuales no eran necesarias para la detección de los prismas. Luego, se optó por un modelo de 2 clases, el cual fue capaz de detectar los prismas rojo y verde. Seguidamente, se optó por un conjunto de datos de 3 clases, ya que añadimos una clase adicional, el prisma magenta, para poder realizar la detección del estacionamiento. Después, se optó por dos modelos, uno con dos clases (**GR**), para poder detectar los obstáculos de la pista, y otro de una sola clase (**M**) para la detección del estacionamiento después de haber recorrido toda la pista. Finalmente, debido a ciertas complicaciones por la optimización de los modelos para el NPU Hailo 8, se optó por tres modelos de 1 clase (**G**, **M**, **R**), donde cada uno de estos modelos fue capaz de detectar los prismas de un color específico, acorde a lo requerido en la pista.

Ahora, vamos a explicar los pasos necesarios para continuar con el montaje del modelo de detección de objetos, donde se utilizará como ejemplo el modelo de 2 clases (**GR**). Sin embargo, los pasos son los mismos para los demás modelos, donde solo se debe cambiar la ruta de las imágenes y el número de clases.

Cabe destacar que, así como variamos el número de clases, también variamos el número de imágenes por clase, desde un dataset de alrededor de 350 imágenes antes de realizar el *data augmentation*, hasta un dataset de alrededor de 1300 imágenes antes de realizar el *data augmentation*, donde cada una fue anotada por algún integrante del equipo de forma manual para entrenar el modelo de la forma más precisa posible.

Después de haber anotado las imágenes con la plataforma Label Studio, se exportaron las anotaciones en formato YOLO y se guardaron en la carpeta [```dataset/gr/labeled/to_process```](dataset/gr/labeled/to_process). Posteriormente, se ejecutó el script [```augment.py```](augment.py) para generar alrededor de 10 imágenes por cada imagen del conjunto de datos, utilizando la biblioteca OpenCV. Este script aplica distintas transformaciones a las imágenes, como rotación, escalado, traslación y cambio de brillo y contraste, para aumentar la variabilidad del conjunto de datos y mejorar el rendimiento del modelo. Las imágenes generadas se guardaron en la carpeta [```dataset/gr/augmented```](dataset/gr/augmented). Finalmente, ejecutamos el script [```after_labeling.py```](after_labeling.py) para mover las imágenes de la carpeta [```dataset/gr/labeled/to_process```](dataset/gr/labeled/to_process) a la carpeta [```dataset/gr/labeled/processed```](dataset/gr/labeled/processed). 

Luego, se ejecutó el script [```split.py```](split.py) para dividir el conjunto de datos en un conjunto de entrenamiento [```dataset/gr/organized/train```](dataset/gr/organized/train), un conjunto de validación [```dataset/gr/organized/val```](dataset/gr/organized/val) y un conjunto de testing [```dataset/gr/organized/test```](dataset/gr/organized/test), con una distribución del 70%, 20% y 10%, respectivamente. Este script utiliza la biblioteca ```os``` para crear las carpetas necesarias y mover las imágenes a las carpetas correspondientes. Además, este script eliminará las imágenes de la carpeta [```dataset/gr/augmented```](dataset/gr/augmented), mas no modificará o eliminará las carpetas [```dataset/gr/labeledto_process```](dataset/gr/labeled/to_process) y [```dataset/gr/labeled/processed```](dataset/gr/labeled/processed).

*NOTA: Se puede observar, que en cada una de las rutas, se encuentra la carpeta ```to_process```, la cual es una carpeta temporal, que se utiliza para guardar las imágenes que se están procesando. Una vez que se han procesado las imágenes, los archivos dentro de las mismas se mueven a una carpeta ```processed``` correspondiente, la cual se encuentra en la misma ruta. De esta forma, se evita que las imágenes procesadas se mezclen con las imágenes por procesar, así como permite a futuro seguir entrenando el mismo modelo, sin necesidad de volver a procesar las mismas imágenes. Así mismo, se puede observar que tanto para ```augmented``` y ```organized```, no existe la carpeta ```to_process```, ya que, después de ser procesadas estas imágenes, son eliminadas debido al gran número de estas al momento de realizar el ```data augmentation```.*

<h1 id="entrenamiento-del-modelo">Entrenamiento del Modelo</h1>

<p align="center">
   <img src="https://i.postimg.cc/B6kkr5ZP/Figure-2.png" alt="Imagen con distintas inferencias realizadas (modelo GMR)" width="800">
   <br>
   <i>Imagen con distintas inferencias realizadas (modelo GMR)</i>
</p>

Primeramente, dependiendo del modelo y la forma en la que se vaya a entrenar el mismo, se debe modificar un archivo ```.yaml```, los cuales se encuentran dentro de la carpeta ````yolo/data````, donde se debe modificar la ruta de las imágenes y las etiquetas a las rutas correspondientes. En este caso, se debe modificar el archivo [```gr.yaml```](yolo/data/colab/gr.yaml) para el modelo de 2 clases y el archivo [```m.yaml```](data/colab/m.yaml) para el modelo de 1 clase, cuya carpeta padre variará entre ```colab``` y ```local``` dependiendo del entorno.

*NOTA: Al momento de clonar este repositorio, se suministran archivos plantilla para los ```.yaml```, los cuales terminan en ```.yaml.example```. A los cuales posterior a su modificación, se les debe cambiar la extensión a ```.yaml```.*

Existen dos maneras de entrenar el modelo dependiendo del equipo disponible en el momento:

1. **Entrenamiento de forma local**: Para ello, se debe contar con una GPU dedicada para el entrenamiento.   
   1. En este caso, debemos ejecutar el script [```train.py```](train.py) para entrenar el modelo YOLOv11. Este script utiliza la biblioteca ```ultralytics``` para realizar el entrenamiento del modelo y guardar los pesos en la carpeta [```v11/runs/gr```](v11/runs/gr).
2. **Entrenamiento de forma remota**: Para ello, se puede utilizar Google Colab [[10](#google-colab)], donde se puede utilizar una GPU de forma gratuita o de paga, dependiendo del tiempo requerido para el entrenamiento y la velocidad en la que se quiere completar dicho entrenamiento.
   1. En este caso, debemos ejecutar primero el script [```zip_to_train.py```](zip_to_train.py), el cual se encargará de crear un archivo comprimido con el conjunto de datos, el cual se guardará en la carpeta [```v11/zip```](v11/zip).
   2. Luego, tenemos dos opciones:
      1. Podemos descomprimir este archivo de forma local y subir dicha carpeta al Google Drive, considerando que Google Drive no tiene funciones para comprimir/descomprimir de forma nativa (al momento de realizar esta guía), en la carpeta ```Colab Files```. 
      2. Otra opción es subir el archivo comprimido a la carpeta ```Colab Files``` de Google Drive, y resubimos el Jupyter Notebook correspondiente, en este caso [```v11/notebooks/colab/gr_train.ipynb```](v11/notebooks/colab/gr_train.ipynb), ya que este contiene una sección que tiene la lógica para descomprimir el archivo comprimido. Ejecutamos la sección correspondiente a la conexión con Google Drive y ejecutamos la sección correspondiente a la descompresión del archivo comprimido.
   3. Seleccionamos el entorno de ejecución acorde a nuestra disponibilidad. Puedes utilizar de forma gratuita una GPU Tesla T4 de NVIDIA por alrededor de 5 h diarias, o comprar 100 créditos (que cuestan $10 al momento de redactar esta guía) de la plataforma para poder usarlo por más tiempo y/o utilizar mejores GPUs. En nuestro caso, empleamos una GPU Tesla L4 de NVIDIA, la cual consumió alrededor de 6 créditos por entrenar un modelo completo.
   4. Ejecutamos las secciones del Jupyter Notebook [```v11/notebooks/colab/gr_train.ipynb```](v11/notebooks/colab/gr_train.ipynb), omitiendo la sección antes mencionada relacionada con la descompresión del archivo comprimido. Este Jupyter Notebook utiliza la biblioteca ```ultralytics``` para realizar el entrenamiento del modelo y guarda los pesos en la carpeta [```v11/runs/gr```](v11/runs/gr).
   5. Una vez finalizado el entrenamiento, se puede descargar el archivo comprimido con los pesos del modelo desde Google Drive y descomprimirlo en la carpeta [```v11/runs/gr```](v11/runs/gr) de forma local.
3. **Inferencia**: Ejecutamos el script [```test.py```](test.py) para realizar la inferencia del modelo entrenado y evaluar el rendimiento del modelo con imágenes que no ha visualizado con anterioridad. Este script genera imágenes con las inferencias realizadas por el modelo, donde se muestran los cuadros delimitadores y las etiquetas de los objetos detectados.
4. **ONNX**: Ejecutamos el script [```export.py```](export.py), y pasamos como formato del modelo ```onnx```, el cual es un formato abierto empleado para representar modelos de Machine Learning de forma interoperable entre distintos frameworks, herramientas, entre otros [[13](#onnx)].
5. **Limpieza**: Finalmente, ejecutamos el script [```after_training.py```](after_training.py) para eliminar la carpeta [```dataset/gr/organized/val```](dataset/gr/organized/val), ya que esta no serán necesaria para los próximos pasos. Además, moverá el contenido de la carpeta [```dataset/gr/organized/train/images```](dataset/gr/organized/train/images) al subdirectorio en [```hailo/suite/train```](hailo/suite/train), para posteriormente ser eliminada la primera. Así mismo, para que el modelo pueda ser convertido a un formato compatible con el Hailo 8, moverá los pesos de formato ```ONNX``` con mejor resultado correspondiente al modelo. 
<!--  
5. **Limpieza**: Finalmente, ejecutamos el script [```after_training_with_calib_set.py```](after_training_with_calib_set.py) para crear un set de calibración en la carpeta [```hailo/suite/calib```](hailo/suite/calib), para eliminar la carpeta [```dataset/gr/organized/train```](dataset/gr/organized/train) y [```dataset/gr/organized/val```](dataset/gr/organized/val), ya que estas no serán necesarias para los próximos pasos, así como moverá los pesos de formato ```ONNX``` con mejor resultado correspondiente al modelo. 
-->

*TIP: En el caso de emplear Google Colab y que se desconecte la sesión del entorno de ejecución durante el entrenamiento del modelo, se puede retomar el mismo, al modificar la ruta del modelo o el nombre del modelo a emplear en la función ```train_model``` del Notebook, por la ruta donde se guardó los mejores pesos del entrenamiento, en nuestro caso: ```gr_to_train/yolo/v11/runs/m/weights/best.pt```.*

<p align="center">
   <img src="https://mediasysdubai.com/wp-content/uploads/2023/12/L4_Front.png" alt="Vista frontal de la GPU Tesla L4 de NVIDIA" width="400">
    <br>
    <i>Vista frontal de la GPU Tesla L4 de NVIDIA</i>
</p>

*NOTA: Durante esta sección se menciona la versión 11 de YOLO, pero, de la misma forma que se menciona el dataset **GR** a fines didáctivos, se puede utilizar cualquier versión de YOLO, así como cualquier dataset, ya que el proceso es el mismo. Sin embargo, se recomienda utilizar la versión 11 de YOLO, ya que es la más reciente y cuenta con mejoras significativas en comparación con versiones anteriores.*

<h1 id="instalacion-de-hailo-ai-hat">Instalación de Hailo AI HAT+</h1>

<p align="center">
   <img src="https://www.raspberrypi.com/documentation/accessories/images/ai-hat-plus-installation-02.png?hash=facb3c8fa8c3ae9595100a428e21560f" alt="Instalación de Hailo AI HAT+" width="300">
   <br>
   <i>Instalación de Hailo AI HAT+</i>
</p>

Para la instalación, empleamos las dos guías de la documentación oficial de Raspberry Pi, donde se explica cómo instalar el Hailo AI HAT+ y cómo instalar el software necesario para su funcionamiento [[5](#getting-started-raspberry-pi)][[6](#ai-hat-plus-raspberry-pi)].

1. Verificamos que la Raspberry Pi 5 esté actualizada, sino la actualizamos con el siguiente comando: `sudo apt update && sudo apt full-upgrade`
2. Revisamos la versión actual del firmware instalado en la Raspberry Pi con el siguiente comando: `sudo rpi-eeprom-update`
   1. Si dicho comando imprime una fecha anterior al 6 de diciembre de 2023, entonces debemos actualizar el firmware de la Raspberry Pi 5. Para ello, ejecutamos el siguiente comando: `sudo raspi-config`
   2. En el menú de configuración, seleccionamos la opción ```Advanced Options``` y luego ```Bootloader Version```. Elegimos la opción ```Latest``` y salimos del menú de configuración.
3. Ejecutamos el siguiente comando para actualizar el firmware: `sudo rpi-eeprom-update -a`
4. Reiniciamos la Raspberry Pi 5 con el siguiente comando: `sudo reboot`
5. Desconectamos la Raspberry Pi 5 de la corriente y desconectamos todos los dispositivos conectados a ella.
6. Instalamos los espaciadores de la Raspberry Pi 5 utilizando los cuatro tornillos proporcionados. Presionamos firmemente el conector GPIO apilado sobre los pines GPIO de la Raspberry Pi. Desconectamos el cable plano del AI HAT+ y conectamos el otro extremo al puerto PCIe de la Raspberry Pi. Levantamos el soporte del cable plano desde ambos lados, luego insertamos el cable con los puntos de contacto de cobre hacia adentro, hacia los puertos USB. Con el cable plano completamente insertado en el puerto PCIe, empujamos el soporte del cable hacia abajo desde ambos lados para asegurar el cable plano firmemente en su lugar.
7. Colocamos el AI HAT+ sobre los espaciadores y utilizamos los cuatro tornillos restantes para asegurarla en su lugar.
8. Conectamos el cable plano al AI HAT+ y lo aseguramos en su lugar. Para ello, levantamos el soporte del cable plano desde ambos lados, luego insertamos el cable con los puntos de contacto de cobre hacia arriba. Con el cable plano completamente insertado en el puerto PCIe, empujamos el soporte del cable hacia abajo desde ambos lados para asegurar el cable plano firmemente en su lugar.
9. Conectamos la Raspberry Pi 5 a la corriente y encendemos el dispositivo.
10. Para habilitar velocidades PCIe Gen 3.0 [[7](#computers-raspberry-pi)], ejecutamos el siguiente comando: `sudo raspi-config`
    1. En el menú de configuración, seleccionamos la opción ```Advanced Options``` y luego ```PCIe Speed```. Elegimos la opción ```Yes``` para habilitar el modo PCIe Gen 3.0.
    2. Reiniciamos la Raspberry Pi 5.
11. Instalamos las dependencias requeridas para usar el NPU. Ejecutamos el siguiente comando desde una ventana de terminal: `sudo apt install hailo-all`. Cabe destacar que, debido a que la última actualización (4.21.0) es muy reciente, recomendamos instalar la versión anterior que es con la que hemos podido trabajar y comprobar su correcto funcionamiento, para lo cual, en vez del anterior comando, sería: ```sudo apt install hailo-all=4.20.0```. Esto instalará las siguientes dependencias:
    - Controlador de dispositivo del kernel Hailo y firmware
    - Software de middleware HailoRT
    - Bibliotecas de post-procesamiento central Tappas de Hailo
    - Etapas de software de demostración de post-procesamiento rpicam-apps Hailo
12. Finalmente, reiniciamos la Raspberry Pi de nuevo para que estos ajustes tengan efecto.
13. Para verificar que el NPU está correctamente instalado y funcionando, ejecutamos el siguiente comando: `hailortcli fw-control identify`. Si el NPU está correctamente instalado, deberíamos ver un mensaje similar al siguiente:

```
Executing on device: 0001:01:00.0
Identifying board
Control Protocol Version: 2
Firmware Version: 4.20.0 (release,app,extended context switch buffer)
Logger Version: 0
Board Name: Hailo-8
Device Architecture: HAILO8
Serial Number: <N/A>
Part Number: <N/A>
Product Name: <N/A>
```

<h1 id="conversion-del-modelo">Conversión del Modelo</h1>

Para la conversión del modelo a un formato compatible con el Hailo 8, requerimos de Docker (mas no es imprescindible), para crear un contenedor con todos los paquetes necesarios para su correcto funcionamiento.

<p align="center">
   <img src="https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/97_Docker_logo_logos-1024.png" alt="Logo de Docker" width="200">
   <br>
   <i>Logo de Docker</i>
</p>

<h2 id="que-es-docker">Docker</h2>

Docker es una plataforma open-source (o de código abierto), con el cual se puede empaquetar una aplicación así como todas las dependencias que esta requiere, en una unidad denominada *contenedor* [[12](#what-is-docker)]. Estas son ligeras en peso, lo cual permite su portabilidad. Así mismo, los contenedores están aislados de la infraestructura donde está siendo ejecutados, y por ende la imagen del contenedor puede ser ejecutada como un contenedor en cualquier sistema operativo donde esté instalado Docker [[12](#what-is-docker)]. 

Si su sistema operativo es Windows, Docker Desktop se puede instalar con facilidad desde la Microsoft Store.

<h3 id="que-es-dockerfile">Dockerfile</h3>

Docker emplea archivos, denominados *Dockerfile*, los cuales usan DSL (Domain Specific Language) para describir todas las instrucciones necesarias para crear una imagen de forma rápida [[12](#que-es-dockerfile)].

<h3 id="que-es-docker-image">Docker Image</h3>

Es un archivo compuesto de múltiples capas, empleado para ejecutar un contenedor Docker [[12](#que-es-docker-image")]. Es un paquete de software ejecutable que contiene todo lo necesario para correr la aplicación. Esta imagen informa cómo un contenedor debe inicializarse, determinando qué software debe ejecutarse y de qué forma.

<h3 id="que-es-docker-container">Docker Container</h3>

Un contenedor Docker es una instancia *runtime* de una imagen Docker [[12](#que-es-docker-container")]. Contiene todo el kit requerido para una aplicación, y permite ser ejecutada de forma aislada.

<h2 id="como-convertir-el-modelo-a-un-formato-compatible-al-hailo-8l">Cómo Convertir el Modelo a un Formato Compatible al Hailo 8</h2>

Al momento de la instalación del AI HAT+, ejecutamos el comando `hailortcli fw-control identify`, donde pudimos notar la siguiente línea:
```
Firmware Version: 4.20.0 (release,app,extended context switch buffer)
```

Como podemos observar, en nuestro caso, la versión del firmware es 4.20.0, por lo que debemos asegurarnos de que el Dataflow Compiler, sea compatible con esta versión. Por ejemplo, debido a un cambio en el Dataflow Compiler para la versión 3.31.0, donde se emplean mecanismos distintos para la detección del error de forma predeterminada, las versiones viejas (previas a la 4.21.0) del HailoRT no serán capaces de ejecutar archivos HEF compilados por la nueva versión del DataFlow Compiler [[14](#2025-04-hailo")]. Recomendamos revisar la [```Tabla de Compatibilidad```](https://hailo.ai/developer-zone/documentation/hailo-sw-suite-2025-04/?sp_referrer=suite/versions_compatibility.html), para así poder tener conocimiento de las versiones de los paquetes que debemos instalar para que todos sean compatibles entre sí.

Primeramente, visitamos la página oficial de Hailo, en el cual debemos crearnos una cuenta, iniciar sesión y luego nos dirigimos al apartado de desarrolladores. Dentro de esta sección, seleccionamos el apartado de descargas de software, y descargamos los siguientes paquetes necesarios [[9](#custom-dataset-medium)]:

- HailoRT, para la arquitectura donde está siendo ejecutado el Docker (en nuestro caso, ```amd64```). Versión recomendada: 4.20.0. 
- Paquete de Python (whl) de HailoRT, para la arquitectura donde está siendo ejecutado el Docker (en nuestro caso, x86_64), y la versión de Python del contenedor (de no ser modificado, debe ser la versión 3.10). Versión recomendada: 4.20.0.
- Hailo Dataflow Compiler, para la arquitectura donde está siendo ejecutado el Docker (en nuestro caso, ```x86_64```). Versión recomendada: 3.30.0.

*NOTA: En el caso de emplear una GPU NVIDIA para la optimización del formato ```.har```, también debemos instalar el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)*

*NOTA: En el caso de no conseguir uno de los paquetes, en el portal para descargar software de Hailo, se tienen dos formas para buscar los paquetes: ```Latest releases``` (o últimas versiones), y ```Archive``` (o archivados); el primero de ellos es el predeterminado. De no conseguir el respectivo paquete en ```Latest releases```, este probablemente esté en ```Archive```*

Posteriormente, cambiamos de nuevo el directorio actual: 
- Si contamos con GPU, al directorio [```hailo/suite/dockerfiles/gpu```](hailo/suite/dockerfiles/gpu).
- En el caso de no contar con GPU, al directorio [```hailo/suite/dockerfiles/no-gpu```](hailo/suite/dockerfiles/no-gpu).

En ambos casos, debe existir este archivo [```Dockerfile```](hailo/suite/dockerfiles/gpu) o este [```Dockerfile```](hailo/suite/dockerfiles/no-gpu), dependiendo de la carpeta en la que nos encontramos.

Para crear la imagen de Docker, ejecutamos el siguiente comando: ```docker build -t hailo_compiler:v0 .```

Esperamos a que se instalen todas las dependencias necesarias y la imagen del contenedor Docker esté lista.

Posteriormente, inicializamos el contenedor Docker:

- En el caso de contar con GPU:
```
docker run -it --name compile_onnx_file --gpus all --ipc=host -v {path}:/home/hailo/shared hailo_compiler:v0
```
- En el caso de no contar con GPU:
```
docker run -it --name compile_onnx_file --ipc=host -v {path}:/home/hailo/shared hailo_compiler:v0
```

*NOTA: Sustituimos ```path``` por la ruta absoluta de la carpeta [```hailo/suite```](hailo/suite).*

Dentro del contenedor, nos movemos al directorio [```/home/hailo/shared/libs```](hailo/suite). En el mismo terminal, creamos un entorno virtual para Python:
```
python -m venv .venv
source .venv/bin/activate
```

Ahora instalamos los paquetes anteriormente descargados, que actualmente se encuentran en la carpeta [```hailo/suite/libs```](hailo/suite/libs). Para la versión que descargamos, ejecutamos el siguiente comando:
```
dpkg -i hailort_4.20.0_amd64.deb
pip install  hailort-4.20.0-cp310-cp310-linux_x86_64.whl
pip install hailo_dataflow_compiler-3.30.0-py3-none-linux_x86_64.whl
```

Realizamos un clone del siguiente repositorio de GitHub que contiene todo lo necesario para la conversión del modelo de formato ```ONNX``` a ```HEF```: ```git clone https://github.com/hailo-ai/hailo_model_zoo.git```. Sin embargo, en nuestro caso, como requerimos de la versión v2.14, el comando sería el siguiente: ```git clone -b v2.14 https://github.com/hailo-ai/hailo_model_zoo.git```. Ahora nos movemos del directorio actual al correspondiente del repositorio ```hailo-model-zoo```:

Instalamos todas las dependencias requeridas: ```pip install -e .```

*NOTA: En el caso de obtener un error similar a:*
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
tensorflow 2.12.0 requires numpy<1.24,>=1.22, but you have numpy 2.2.6 which is incompatible.
hailo-dataflow-compiler 3.30.0 requires numpy==1.23.3, but you have numpy 2.2.6 which is incompatible.
```
*Debemos modificar el archivo ```setup.py``` que se encuentra dentro del repositorio, y en la línea 44, dentro de la función ```main```, sustituimos ```"numpy"``` por ```"numpy==1.23.3"```, así como en la línea 46, sustituimos ```"scipy"``` por ```"scipy==1.9.3"```. Reintentamos el comando: ```pip install -e .```*

Evaluamos si los paquetes se han instalado correctamente con el siguiente comando: ```hailomz --version```

Ahora modificamos el archivo de configuración del modelo, en el campo ```classes```, estableciendo el número de clases con el que se ha entrenado el mismo (para el modelo **GR** serían 2):
```
sudo nano hailo_model_zoo/cfg/postprocess_config/yolov11n_nms_config.json
```

Establecemos la variable de entorno ```USER``` como Hailo:
```
export USER=hailo
```

Ahora, para convertir el modelo a un formato compatible con el Hailo 8, ejecutamos los siguientes comandos:
- Primero, parseamos el modelo:
```
hailomz parse --ckpt ~hailo/shared/v11/gr/best.onnx --hw-arch hailo8 yolov11n
mv yolov11n.har gr_parsed.har
```
- Segundo, optimizamos el modelo:
```
hailomz optimize --har gr_parsed.har --classes 2 --calib-path ~hailo/shared/train --hw-arch hailo8 yolov11n
mv yolov11n.har gr_optimized.har
```
- Finalmente, compilamos el modelo:
```
hailomz compile --har gr_optimized.har --hw-arch hailo8 yolov11n
mv yolov11n.hef gr_compiled.hef
```
<!--
Ahora, para convertir el modelo a un formato compatible con el Hailo 8, ejecutamos los siguientes comandos:
- Primero, parseamos el modelo:
```
hailo parser onnx --net-name yolov11n --hw-arch hailo8l --har-path ~hailo/shared/v11/gr/best_parsed.har ~hailo/shared/v11/gr/best.onnx
```
- Optimizamos el modelo:
```
hailo optimize --hw-arch hailo8l --calib-set-path ~hailo/shared/calib/calib.npy --output-har-path ~hailo/shared/v11/gr/best_optimized.har ~hailo/shared/v11/gr/best_parsed.har
```
- Finalmente, compilamos el modelo:
```
hailo compiler --hw-arch hailo8l --output-dir ~hailo/shared/v11/gr --output-har-path ~hailo/shared/v11/gr/best_compiled.har ~hailo/shared/v11/gr/best_optimized.har
mv ./yolov11n.hef ./gr_compiled.hef
```
-->

Esperamos a que se complete el anterior paso, y ya tendríamos nuestro modelo personalizado y compatible con el Hailo 8.

Para mover todos los archivos generados en el directorio [```hailo/suite/libs/hailo_model_zoo```](hailo/suite/libs/hailo_model_zoo) a la carpeta con los pesos del modelo correspondiente, ejecutamos el script [```after_hailo_compilation.py```](after_hailo_compilation.py).

Por último, para salir del contenedor Docker, ejecutamos el siguiente comando: ```exit```.

<h1 id="recursos-externos">Recursos Externos</h1>

1. *What is machine learning?*. (22 de septiembre de 2021). IBM. <a id="machine-learning-ibm">https://www.ibm.com/think/topics/machine-learning</a>
2. Murel, J., Kavlakoglu, E. *What is object detection?*. (3 de enero de 2024) IBM. <a id="object-detection-ibm">https://www.ibm.com/topics/object-detection</a>
3. Schneider, J., Smalley, I. *What is neural processing unit (NPU)?*. (27 de septiembre de 2024). IBM. <a id="npu-ibm">https://www.ibm.com/topics/neural-processing-unit</a>
4. *Label Studio*. (2025). Label Studio. <a id="label-studio">https://labelstud.io/</a>
5. *AI Kit and AI HAT+ software*. (2025). Raspberry Pi. <a id="getting-started-raspberry-pi">https://www.raspberrypi.com/documentation/computers/ai.html#getting-started</a>
6. *AI Hat+*. (2025). Raspberry Pi. <a id="ai-hat-plus-raspberry-pi">https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html#ai-hat-plus</a>
7. *Raspberry Pi*. (2025). Raspberry Pi. <a id="computers-raspberry-pi">https://www.raspberrypi.com/documentation/computers/raspberry-pi.html</a>
8. Hailo AI. (2025). *Hailo Application Code Examples*. GitHub. <a id="hailo-ai-examples-github">https://github.com/hailo-ai/Hailo-Application-Code-Examples</a>
9. d'Oleron, L. (23 de abril de 2025). *Custom dataset with Hailo AI Hat, Yolo, Raspberry PI 5, and Docker*. Medium. <a id="custom-dataset-medium">https://pub.towardsai.net/custom-dataset-with-hailo-ai-hat-yolo-raspberry-pi-5-and-docker-0d88ef5eb70f</a>
10. *Google Colab*. (2025). Google Colab. <a id="google-colab">https://colab.research.google.com/</a>
11. *Models*. (2025). Ultralytics. <a id="models-ultralytics">https://docs.ultralytics.com/models/</a>
12. *What is Docker?*. (22 de abril de 2025). Geeks for Geeks. <a id="what-is-docker">https://www.geeksforgeeks.org/introduction-to-docker/</a>
13. *ONNX*. (2025). ONNX. <a id="onnx">https://onnx.ai/</a>
14. *2025-04 | Hailo*. (2025). Hailo. <a id="2025-04-hailo">https://hailo.ai/developer-zone/documentation/hailo-sw-suite-2025-04/?sp_referrer=suite/suite_changelog.html</a>
15. *Try to complie YOLOv11 with DFC 3.30 got ValueError: failed to initialize intent(inout) array – expected elsize=8 but got 4*. (19 de enero de 2025). Hailo Community. <a id="try-to-compile-yolo-hailo">https://community.hailo.ai/t/try-to-complie-yolov11-with-dfc-3-30-got-valueerror-failed-to-initialize-intent-inout-array-expected-elsize-8-but-got-4/9024/3</a>