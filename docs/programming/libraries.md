# Librerías {#libraries}

## PyTorch {#pytorch}

<div class="center">
    <img src="../assets/images/pytorch.png" alt="PyTorch" class="logo--3rd-party">
    <i>Logo de PyTorch</i>
</div>

PyTorch es una librería de software de código abierto diseñada en el Aprendizaje
Automático (Machine Learning), y, en particular para el Aprendizaje Profundo (
Deep Learning). PyTorch se ha convertido en uno de los frameworks más populares
para el desarrollo de las IA [[1](#pytorch-docs)].

Al igual que muchas de las librerías ya mencionadas, PyTorch es bastante útil
cuando se trata de desarrollar un programa que involucre Visión por
Computadoras, o el Aprendizaje por Refuerzo. Ya que, facilitan el desarrollo de
modelos de Inteligencia Artificial.

## Ultralytics YOLO {#ultralytics-yolo}

<div class="center">
    <img src="../assets/images/ultralytics.png" alt="Ultralytics" class="logo--3rd-party">
    <i>Logo de Ultralytics</i>
</div>

La librería Ultralytics YOLO está construida sobre PyTorch y se 
caracteriza por su modularidad y su enfoque en la eficiencia y la facilidad 
de uso. Todo gira en torno a la clase YOLO, que encapsula todas las 
funcionalidades clave. En su núcleo se basa en los modelos You Only 
Look Once (YOLO) originales, que, a diferencia de los algoritmos de dos etapas 
(primero proponen regiones y luego la clasifica) los modelos YOLO se 
caracterizan por su detección de objetos de una pasada en la red neuronal, 
dándole una gran velocidad de detección.

### Clase YOLO

Es la interfaz principal para interactuar con los modelos.
Permite cargar modelos preentrenados, construir nuevos modelos desde cero,
entrenar, validar, realizar inferencias, exportar y rastrear objetos. Además de
la clase, la librería contiene múltiples modos para poder organizar todas sus
funciones (como `train`, `val`, `predict` o `export`).

### Detección de Objetos

La tarea central de YOLO. Identifica la ubicación de
objetos en una imagen/video mediante cajas delimitadoras (bounding boxes) y
asigna una clase a cada objeto. Los modelos están disponibles en diferentes
tamaños (Nano `n`, Small `s`, Medium `m`, Large `l`, XLarge `x`) para escalar
según las necesidades de rendimiento y precisión. Si bien la librería contiene
múltiples usos, en el caso de Klevor utilizamos la Detección de Objetos para
poder detectar e identificar los obstáculos [[2](#ultralytics-yolo-docs)].

## OpenCV {#opencv}

<div class="center">
    <img src="../assets/images/opencv.png" alt="OpenCV" class="logo--3rd-party">
    <i>Logo de OpenCV</i>
</div>

Open Source Computer Vision Library (OpenCV) es una de las librerías de software
más populares y potentes del mundo para la visión por computadora y el
aprendizaje automático (Machine Learning). Fue desarrollada inicialmente por
Intel y ahora es mantenida por una comunidad global activa. En su esencia,
OpenCV es una colección masiva de algoritmos y funciones que te permiten
procesar imágenes y videos, extraer información de ellos y hacer que las
computadoras "vean" y "entiendan" el mundo visual de una manera similar a como
lo hacen los humanos.

Su propósito principal es proporcionar una infraestructura común para
aplicaciones de visión por computadora y acelerar el uso de la percepción
automática en productos comerciales, investigación y
desarrollo [[3](#opencv-docs)].

## NumPy {#numpy}

<div class="center">
    <img src="../assets/images/numpy.png" alt="Numpy" class="logo--3rd-party">
    <i>Logo de NumPy</i>
</div>

La librería NumPy o Numerical Python es una librería la cual contiene muchísimas
funciones utilizadas ampliamente en el ecosistema de Python, gracias a esta
librería, otras más populares y más flexibles como TensorFlow y PyTorch pudieron
ser construidas. Esta librería se basa en la computación numérica y científica
en Python.

El propósito general es permitir operaciones numéricas rápidas y eficientes en
grandes cantidades de datos [[4](#numpy-docs)]. Estos cálculos tan
extensos, se utilizan para el procesamiento de imágenes de Klevor, aunque
también tiene usos como el análisis de datos.

## PiCamera 2 {#picamera-2}

<div class="center">
    <img src="../assets/images/raspberry-pi.png" alt="Picamera 2" class="logo--3rd-party">
    <i>Logo de Raspberry Pi</i>
</div>

La librería PiCamera 2 es la sucesora de la `picamera` original, desarrollada
por Raspberry Pi Foundation [[5](#the-picamera2-library)]. Esta librería
permite la conexión entre la RPi Camera Module 3 y el Modelo de Detección de
Obstáculos. Entre sus múltiples funciones se encuentran:

- Obtener streams de video para procesamiento en tiempo real (por ejemplo, con
  OpenCV o NumPy).
- Controlar diversos parámetros de la cámara (exposición, ganancia, balance de
  blancos, modos de enfoque, etc.).

Además de, obviamente, permitir la toma de imágenes y videos

## Hailo Platform {#hailo-platform}

<div class="center">
    <img src="../assets/images/hailo.png" alt="Hailo Platform" class="logo--3rd-party">
    <i>Logo de Hailo Platform</i>
</div>

Hailo Platform es un ecosistema tanto de hardware y software desarrollado por la
empresa Hailo, este ecosistema está diseñado para llevar un modelo de Deep
Learning desde su entrenamiento hasta su aplicación en tiempo real en
periféricos [[6](#hailo-ai-software-suite)].

Además de esto, la Hailo Platform también incluye múltiples librerías, el
objetivo principal de estas librerías (como HailoRT o PyHailoRT) es la de
acelerar el proceso de desarrollo de extremo a extremo, tanto en la compilación
y optimización hasta su uso en tiempo real.

# Referencias Bibliográficas

1. *PyTorch Documentation*. (2025). PyTorch
    Contributors. <a id="pytorch-docs" href="https://docs.pytorch.org/docs/stable/index.html">https://docs.pytorch.org/docs/stable/index.html</a>

2. *Ultralytics Docs*. (2025). Ultralytics
    Inc. <a id="ultralytics-yolo-docs" href="https://docs.ultralytics.com/#where-to-start">https://docs.ultralytics.com/#where-to-start</a>

3. *OpenCV Documentation*. (2025).
    OpenCV. <a id="opencv-docs" href="https://docs.opencv.org/4.11.0/d1/dfb/intro.html">https://docs.opencv.org/4.11.0/d1/dfb/intro.html</a>

4. *NumPy Documentation*. (2024). NumPy
    Developers. <a id="numpy-docs" href="https://numpy.org/doc/stable/user/index.html">https://numpy.org/doc/stable/user/index.html</a>

5. *The PiCamera 2 Library*. (2025). Raspberry Pi
    Ltd. <a id="the-picamera2-library" href="https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf">https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf</a>

6. *Hailo AI Software Suite*. (2025). Hailo Technologies
    Ltd. <a id="hailo-ai-software-suite" href="https://hailo.ai/products/hailo-software/hailo-ai-software-suite/#sw-overview">https://hailo.ai/products/hailo-software/hailo-ai-software-suite/#sw-overview</a>
