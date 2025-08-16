# Glosario de Términos {:#glossary}

## Machine Learning {:#machine-learning}

<div class="hcenter">
   <img src="/assets/images/logo/pytorch.png" alt="Logo de PyTorch" 
class="logo--3rd-party">
   <i>Logo de PyTorch</i>
</div>

El Machine Learning (ML) es una rama de la inteligencia artificial enfocada en imitar la manera en que los humanos piensan en una computadora, para realizar tareas de forma autónoma, y para mejorar el rendimiento y precisión a medida que se expone a un mayor conjunto de datos [[1](#machine-learning-ibm)].

Normalmente, se divide en 3 partes el sistema de aprendizaje de un algoritmo de Machine Learning:

1. **Proceso de decisión**: En general, los algoritmos de Machine Learning son empleados para predecir o clasificar, a través de unos datos de entrada, que pueden ser etiquetados o no etiquetados, los cuales producen un patrón estimado de dicho conjunto de datos.
2. **Función de error**: Una función de error que evalúa las predicciones del modelo. Este emplea conjuntos de datos, de los cuales ya se conoce su resultado, para poder comparar la precisión del modelo.
3. **Proceso de optimización del modelo**: Si el modelo puede encajar mejor al conjunto de los datos en el set de entrenamiento, los pesos son ajustados para reducir la diferencia entre las estimaciones y los resultados conocidos. Este proceso iterativo de evaluación y optimización, se repite de forma autónoma hasta actualizar los pesos a un umbral de aceptación.

## Detección de Objetos {:#object-detection}

Para la presente competencia, debido a la necesidad de poder reconocer distintos prismas de diferentes colores, específicamente en el Desafío con Obstáculos, se optó por utilizar un modelo de detección de objetos.

Dicha detección de objetos, es una tarea de visión por computadora que emplea redes neuronales para identificar y localizar objetos en imágenes o videos, al enmarcarlos con cuadros delimitadores y asignarles etiquetas.

A través de esta técnica, se pueden clasificar y localizar múltiples objetos dentro de una sola imagen. Además, se considera una parte de la inteligencia artificial, ya que permite a las máquinas interpretar y comprender el contenido visual de manera similar a los humanos.

### Funcionamiento de la Detección de Objetos {:#how-object-detection-works}

Primeramente, debemos comprender distintos conceptos relacionados con la detección de objetos, como el preprocesamiento de imágenes, la arquitectura del modelo y las métricas de evaluación para la detección de objetos. A continuación, se presentan estos conceptos:

#### Preprocesamiento de Imágenes {:#object-detection-preprocessing}

Para la visión por computadora, las imágenes se expresan como funciones continuas en un plano de coordenadas 2D representadas como f(x, y). Cuando se digitalizan, las imágenes pasan por dos procesos primarios llamados muestreo y cuantización, que, en resumen, convierten la función de imagen continua en una estructura de cuadrícula discreta de elementos que representan píxeles [[2](#object-detection-ibm)].

<div class="hcenter">
   <img src="/assets/images/app/object-detection.png" alt="Imagen con distintas anotaciones de manzanas" class="app--image">
   <i>Imagen con distintas anotaciones de manzanas</i>
</div>

Al ser anotada la imagen, el modelo de detección de objetos puede reconocer regiones con características similares a las definidas en el conjunto de datos de entrenamiento como el mismo objeto. Los modelos de detección de objetos no reconocen objetos per se, sino agregados de propiedades como tamaño, forma, color, etc., y clasifican regiones según patrones visuales inferidos a partir de datos de entrenamiento anotados manualmente [[2](#object-detection-ibm)].

#### Arquitectura del Modelo {:#object-detection-architecture}

Los modelos de detección de objetos siguen una estructura general que incluye un modelo de fondo, cuello y cabeza [[2](#object-detection-ibm)].

El modelo de fondo extrae características de una imagen de entrada. A menudo, el modelo de fondo se deriva de parte de un modelo de clasificación preentrenado. La extracción de características produce una miríada de mapas de características de diferentes resoluciones que el modelo de fondo pasa al cuello. Esta última parte de la estructura concatena los mapas de características para cada imagen. Luego, la arquitectura pasa los mapas de características en capas a la cabeza, que predice cuadros delimitadores y puntuaciones de clasificación para cada conjunto de características [[2](#object-detection-ibm)].

#### Funcionamiento de la Evaluación de Métricas {:#object-detection-metrics}

La evaluación de métricas es un paso crucial en el proceso de detección de objetos, ya que permite medir la precisión y efectividad del modelo. Existen varias métricas utilizadas para evaluar modelos de detección de objetos, entre las cuales se encuentran:

- **Precisión**: Mide la proporción de verdaderos positivos (TP) entre el total de predicciones positivas (TP + FP). Es decir, cuántas de las predicciones realizadas por el modelo son correctas.
- **Exhaustividad (Recall)**: Mide la proporción de verdaderos positivos (TP) entre el total de casos positivos reales (TP + FN). Es decir, cuántos de los objetos que realmente están presentes en la imagen fueron detectados por el modelo.
- **F1 Score**: Es la media armónica entre precisión y exhaustividad. Se utiliza para evaluar el rendimiento del modelo en situaciones donde hay un desbalance entre las clases.
- **Mean Average Precision (mAP)**: Es una métrica que combina precisión y exhaustividad en un solo valor. Se calcula promediando la precisión a diferentes niveles de exhaustividad. El mAP se utiliza comúnmente para evaluar modelos de detección de objetos, ya que proporciona una medida más completa del rendimiento del modelo.

## You Only Look Once (YOLO) {:#yolo}

<div class="hcenter">
   <img src="/assets/images/logo/ultralytics.png" 
alt="Logo de Ultralytics" class="logo--3rd-party">
   <i>Logo de Ultralytics</i>
</div>

YOLO, o "You Only Look Once" ("Solo Miras Una Vez"), consiste en una familia de modelos de una sola etapa que realizan detección de objetos en tiempo real, mantenida por Ultralytics [[3](#models-ultralytics)]. A diferencia de otros modelos de detección de objetos que utilizan un enfoque de dos etapas, YOLO divide la imagen en una cuadrícula y predice simultáneamente los cuadros delimitadores y las probabilidades de clase para cada celda de la cuadrícula. Esto permite que YOLO sea extremadamente rápido y eficiente [[2](#object-detection-ibm)].

Para Klevor, la detección de objetos se basa en el modelo YOLOv11; la última versión de YOLO hasta la fecha [[3](#models-ultralytics)].

## Neural Processing Unit (NPU) {:#npu}

Una unidad de procesamiento neuronal (NPU) es un microprocesador especializado y diseñado para imitar la función de procesamiento del cerebro humano. Están optimizados para tareas y aplicaciones de inteligencia artificial (IA), redes neuronales, aprendizaje profundo y aprendizaje automático [[4](#npu-ibm)].

<div class="hcenter">
   <img src="/assets/images/components/raspberry-pi-ai-hat-plus.png" 
alt="Raspberry Pi AI HAT+ 26 TOPS" class="component-image">
   <i>Raspberry Pi AI HAT+ 26 TOPS</i>
</div>

A diferencia de las unidades de procesamiento gráfico (GPU) y las unidades de procesamiento central (CPU), que son procesadores de propósito general, las NPU están diseñadas para acelerar tareas y cargas de trabajo de IA, como el cálculo de capas de redes neuronales compuestas por matemáticas escalares, vectoriales y tensoriales [[4](#npu-ibm)].

### Características Clave de las NPU {:#npu-characteristics}

Las NPU están diseñadas para realizar tareas que requieran una baja latencia y un alto rendimiento en paralelo, lo que las hace ideales para aplicaciones de inteligencia artificial. Estas tareas incluyen el procesamiento de algoritmos de aprendizaje profundo, reconocimiento de voz, procesamiento de lenguaje natural, procesamiento de fotos y videos, y detección de objetos [[4](#npu-ibm)].

Entre las características clave de las NPU se encuentran:

- **Procesamiento paralelo**: Las NPU están diseñadas para realizar cálculos en paralelo, lo que les permite procesar múltiples operaciones simultáneamente. Esto es especialmente útil para tareas de aprendizaje profundo, donde se requieren grandes cantidades de cálculos en matrices y tensores.

- **Baja precisión aritmética**: Las NPU a menudo admiten operaciones de 8 bits (o menos) para reducir la complejidad computacional y aumentar la eficiencia energética.

- **Memoria de alto ancho de banda**: Muchas NPU cuentan con memoria de alto ancho de banda en el chip para realizar eficientemente tareas de procesamiento de IA que requieren grandes conjuntos de datos.

- **Aceleración por hardware**: Los avances en el diseño de NPU han llevado a la incorporación de técnicas de aceleración por hardware, como arquitecturas de matriz sistólica o procesamiento tensorial mejorado para optimizar el rendimiento de las cargas de trabajo de IA.

## Docker {:#docker}

<div class="hcenter">
    <img src="/assets/images/logo/docker.png" alt="Logo de Docker" 
class="logo--3rd-party">
    <i>Logo de Docker</i>
</div>

Docker es una plataforma open-source (o de código abierto), con el cual se puede empaquetar una aplicación así como todas las dependencias que esta requiere, en una unidad denominada *contenedor* [[5](#what-is-docker)]. Estas son ligeras en peso, lo cual permite su portabilidad. Así mismo, los contenedores están aislados de la infraestructura donde está siendo ejecutados, y por ende la imagen del contenedor puede ser ejecutada como un contenedor en cualquier sistema operativo donde esté instalado Docker [[5](#what-is-docker)].

Si su sistema operativo es Windows, Docker Desktop se puede instalar con facilidad desde la Microsoft Store.

### Dockerfile {:#dockerfile}

Docker emplea archivos, denominados *Dockerfile*, los cuales usan DSL (Domain Specific Language) para describir todas las instrucciones necesarias para crear una imagen de forma rápida [[5](#what-is-docker)].

### Docker Image {:#docker-image}

Es un archivo compuesto de múltiples capas, empleado para ejecutar un contenedor Docker [[5](#what-is-docker)]. Es un paquete de software ejecutable que contiene todo lo necesario para correr la aplicación. Esta imagen informa cómo un contenedor debe inicializarse, determinando qué software debe ejecutarse y de qué forma.

### Docker Container {:#docker-container}

Un contenedor Docker es una instancia *runtime* de una imagen Docker [[5](#what-is-docker)]. Contiene todo el kit requerido para una aplicación, y permite ser ejecutada de forma aislada.

## Multiprocesamiento {:#multiprocessing}

El multiprocesamiento es la técnica que permite la utilización de dos o más unidades centrales de procesamiento (CPU) en un único sistema informático para ejecutar múltiples procesos de forma simultánea [[6](#what-is-multiprocessing)]. Esta técnica es especialmente útil en sistemas que requieren un alto rendimiento y eficiencia, ya que permite distribuir la carga de trabajo entre varias CPU, mejorando así el tiempo de respuesta y la capacidad de procesamiento.

# Referencias Bibliográficas

1. *What is machine learning?*. (22 de septiembre de 2021). IBM. <a id="machine-learning-ibm" href="https://www.ibm.com/think/topics/machine-learning">https://www.ibm.com/think/topics/machine-learning</a>

2. Murel, J., Kavlakoglu, E. *What is object detection?*. (3 de enero de 2024). IBM. <a id="object-detection-ibm" href="https://www.ibm.com/topics/object-detection">https://www.ibm.com/topics/object-detection</a>

3. *Models*. (2025). Ultralytics. <a id="models-ultralytics" href="https://docs.ultralytics.com/models/">https://docs.ultralytics.com/models/</a>

4. Schneider, J., Smalley, I. *What is neural processing unit (NPU)?*. (27 de septiembre de 2024). IBM. <a id="npu-ibm" href="https://www.ibm.com/topics/neural-processing-unit">https://www.ibm.com/topics/neural-processing-unit</a>

5. *What is Docker?*. (22 de abril de 2025). Geeks for Geeks. <a id="what-is-docker" href="https://www.geeksforgeeks.org/introduction-to-docker/">https://www.geeksforgeeks.org/introduction-to-docker/</a>

6. Yasar, K. (23 de junio de 2023). *What is multiprocessing?*. TechTarget. <a id="what-is-multiprocessing" href="https://www.techtarget.com/searchdatacenter/definition/multiprocessing">https://www.techtarget.com/searchdatacenter/definition/multiprocessing</a>