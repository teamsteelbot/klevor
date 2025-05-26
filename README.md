<h1 id="index">Índice</h1>

1. **[Introducción](#introduccion)**  
2. **[Estructura de archivos](#estructura-de-archivos)**
3. **[Componentes](#componentes)**
   1. [Raspberry Pi 5](#componentes-raspberry-pi-5)
   2. [Raspberry Pi Camera Module 3 Wide](#componentes-raspberry-pi-camera-module-3-wide)
   3. [Raspberry Pi AI HAT+ (26 TOPS)](#componentes-raspberry-pi-ai-hat-26-tops)
   4. [Raspberry Pi Pico 2 WH](#componentes-raspberry-pi-pico-2-wh) 
   5. [RPLIDAR C1](#componentes-rplidar-c1) 
   6. [Shargeek Storm 2](#componentes-shargeek-storm-2) 
   7. [INJORA 180 Motor 48T](#componentes-injora-180-motor-48t)
   8. [INJORA MB100 20A mini ESC](#componentes-injora-mb100-20a-mini-esc) 
   9. [URGENEX 7.4V Battery](#componentes-urgenex-74v-battery) 
   10. [INJORA 7KG 2065 Micro Servo](#componentes-injora-7kg-2065-micro-servo) 
   11. [HiLetgo Time-of-Flight Sensor VL53L0X](#sensor-tof-hiletgo)
   12. [9-Axis IMU Gyroscope GY-BNO085](#gyroscope-gy-bno085)
4. **[Lenguajes de Programación](#lenguajes-de-programacion)**
   1. [Python](#python)
   2. [MicroPython](#micropython)
   3. [CircuitPython](#circuitpython)
4. **[Librerías](#librerias)**
   1. [Ultralytics YOLO](#ultralytics-yolo)
   2. [OpenCV](#opencv)
   3. [Numpy](#numpy)
   4. [Pytorch](#pytorch)
   5. [PiCamera2](#picamera2)
   6. [Hailo Platform](#hailo-platform)
5. **[Modelos 3D](models/README.md)**
6. **[Diagramas y esquemas](schemes/README.md)**
   1. [Diagrama de conexiones](#schemes/connection-diagram.jpg)
   2. [Esquema de decisiones](#schemes/flowchart.jpg)
7. **[Código](src/README.md)**
   1. [Raspberry Pi 5](src/raspberry-pi5/README.md)
      1. [YOLO](src/raspberry-pi5/yolo/README.md)
   2. [Raspberry Pi Pico 2 WH](src/raspberry-pi-pico2/README.md)
8. **[Fotos del equipo](t-photos/README.md)**
9. **[Fotos de Klevor](v-photos/README.md)**
10. **[Vídeos](video/README.md)**
11. **[Recursos Externos](#recursos-externos)**

<h1 id="introduccion">Introducción</h1>

Este es el repositorio del Team Steelbot, compitiendo en la World Robot Olympiad 2025, en la categoría Futuros Ingenieros. Representando al Colegio Salto Ángel en Maracaibo, Estado Zulia, Venezuela. 

Actualmente, este equipo está conformado por 3 miembros:

- Ramón Álvarez, 19 años. [ralvarezdev](https://github.com/ralvarezdev).
- Otto Piñero, 16 años. [Ottorafaelpg](https://github.com/Ottorafaelpg).
- Sebastián Álvarez, 15 años. [salvarezdev](https://github.com/salvarezdev).

<h1 id="estructura-de-archivos">Estructura de archivos</h1>

- `models` contiene todos los archivos en 3D que se utilizaron para poder construir a nuestro robot (Klevor).

- `schemes` contiene todos los esquemas y diagramas de todas las conexiones de nuestro robot (Klevor).

- `src` contiene todo el código el cual fue utilizado para poder controlar este robot de manera autónoma.

- `t-photos` contiene las fotos del equipo.

- `v-photos` contiene las fotos de Klevor.

- `video` contiene los vídeos de Klevor en la pista, tanto en el Desafío Abierto como en el Desafío con Obstáculos (Desafío Cerrado).

<h1 id="componentes">Componentes</h1>

A continuación, está la descripción de todos los componentes principales de Klevor (mencionados en el índice).

<h2 id="componentes-raspberry-pi-5">Raspberry Pi 5 (16GB RAM)</h2>

<p align="center">
  <img src="https://i.postimg.cc/wxDfLJkj/8713-a-1-removebg-preview.png" alt="Raspberry Pi 5" width="400">
</p>

Equipada con un procesador ARM Cortex-A76 de 64 bits a 2.4 Ghz. [[1](#raspberry-pi-5-16gb-8gb-4gb-2gb-tiendatec)][[2](#raspberry-pi-16gb-ram)][[3](#raspberry-pi-5-datasheet)] La Raspberry Pi 5 es nuestro controlador principal de elección, decidimos usar a la Raspberry Pi 5 debido a múltiples factores, entre ellos:

- **Compatibilidad**: Existen muchos componentes de Klevor (como el Camera Module 3 Wide) que a su vez pertenecen al ecosistema Raspberry, lo que hace que implementarlos a la Raspberry Pi 5 no requiera tanto esfuerzo.

- **Potencia**: La Raspberry Pi 5 es uno de los controladores más potentes actualmente, gracias a esto, funciones demandantes como lo es el procesamiento de imágenes en tiempo real, son fácilmente realizables por una Raspberry Pi 5.

- **Portabilidad**: La Raspberry Pi 5 destaca entre los controladores, ya que no es una computadora bastante pesada, apenas llegando a los 60g, hace que incorporarlo a Klevor sea una opción prácticamente segura.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 85 mm     |
| Alto       | 58.9 mm   |
| Ancho      | 56 mm     |
| Peso       | 46 g      |

<h2 id="componentes-raspberry-pi-camera-module-3-wide">Raspberry Pi Camera Module 3 Wide</h2>

<p align="center">
  <img src="https://i.postimg.cc/fTf0cWFd/raspberry-pi-camera-module-3-raspberry-pi-sc0872-43251879182531-700x-removebg-preview.png" alt="Raspberry Pi Camera Module 3 Wide" width="200">
</p>

La Raspberry Pi Camera Module 3 Wide es nuestra elección de preferencia, como los demás componentes Raspberry, esta se destaca por ser bastante ligera y portátil, ya que, pues es una cámara bastante pequeña, midiendo apenas 25 mm × 24 mm × 12.4 mm y pesando 4 gramos, sin perder absolutamente ni una pizca de eficiencia, porque puede grabar a 1536 x 864p120, ahora bien, decidimos utilizar la versión Wide por su campo de visión horizontal de 102 grados, [[4](#raspberry-pi-camera-module-3-geek-factory)][[5](#raspberry-pi-camera-documentation)] porque nos permite tener un rango de visión óptimo para poder detectar todos los obstáculos de la pista.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 24 mm     |
| Alto       | 25 mm     |
| Ancho      | 12.4 mm   |
| Peso       | 4 g       |

<h2 id="componentes-raspberry-pi-ai-hat-26-tops">Raspberry Pi AI HAT+ (26 TOPS)</h2>

<p align="center">
  <img src="https://i.postimg.cc/6399NRt6/raspberry-pi-ai-hat-raspberry-pi-71328528531841-removebg-preview.png" alt="Raspberry Pi AI HAT+ 26 TOPS" width="400">
</p>

Si bien la Raspberry Pi 5 es capaz de procesar imágenes en tiempo real, tuvimos en cuenta que necesitaba un poco más de poder, por lo cual decidimos incorporar el AI HAT+ a la Raspberry Pi 5 para poder alcanzar el nivel de procesamiento necesario. 

El Raspberry Pi AI HAT+ tiene dos versiones, una de 13 Trillones de Operaciones por Segundo (TOPS) y otra de 26 TOPS. [[6](#kit-ai-ai-hat-plus-raspberry-pi-kubii)][[7](#raspberry-pi-ai-hat-documentation)] Como se menciona en el índice, Klevor posee un Raspberry Pi AI HAT+ de 26 TOPS, gracias a este procesador de imágenes, Klevor puede analizar hasta 30 imágenes por segundo con una resolución de 640 px × 640 px.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 65 mm     |
| Alto       | 5.5 mm    |
| Ancho      | 56 mm     |
| Peso       | 9.07 g    |

<h2 id="componentes-raspberry-pi-pico-2-wh">Raspberry Pi Pico 2 WH</h2>

<p align="center">
  <img src="https://i.postimg.cc/JzvDmp2r/raspberry-pi-pico-2-w-raspberry-pi-sc1634-1146616007-removebg-preview.png" alt="Raspberry Pi Pico 2 WH" width="300">
</p>

Construido sobre el chip RP235x, [[8](#raspberry-pi-pico-2-2w-2h-2wh-kubii)][[9](#raspberry-pi-pico-2-wh-datasheet)] la Raspberry Pi Pico 2 es el microcontrolador de motores por excelencia de Klevor, además de ser un microcontrolador ligero y pequeño, este chip permite una fácil integración con el resto de los componentes Raspberry.

Además de ofrecer una frecuencia de procesamiento de 150 Mhz, superior a varios microcontroladores de similar tamaño, como, por ejemplo, el Arduino Nano el cual cuenta con una frecuencia de procesamiento de 20 Mhz.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 51 mm     |
| Alto       | 12 mm     |
| Ancho      | 21 mm     |
| Peso       | 6 g       |

<h2 id="componentes-rplidar-c1">RPLiDAR C1</h2>

<p align="center">
  <img src="https://i.postimg.cc/02wVPSzs/slamtec-rplidar-c1-360-laser-scanner-12m-removebg-preview.png" alt="RPLiDAR C1" width="250">
</p>

El RPLiDAR C1 es un escáner de rango láser de 360 grados, el cual puede detectar superficies que están hasta 12 metros de distancia, su punto ciego es de tan solo 5 centímetros alrededor del mismo [[10](#rplidar-c1-robot-shop)][[11](#rplidar-c1-datasheet)], todos estos factores hacen que el RPLiDAR C1 sea una gran opción para poder guíar a Klevor por la pista.

Este RPLiDAR C1 permite a Klevor poder identificar que tan cerca o que tan lejos está de las paredes de la pista, además de poder identificar la ubicación de los obstáculos mucho antes que la cámara y poder ajustarse a tiempo.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 55.6 mm   |
| Alto       | 41.3 mm   |
| Ancho      | 55.6 mm   |
| Peso       | 110 g     |

Especificaciones técnicas:

| **Especificación**     | **Valor**                                                                           |
|------------------------|-------------------------------------------------------------------------------------|
| Rango de distancia     | Blanco: 0,05-12 m (70 % de reflectividad); Negro: 0,05-6 m (10 % de reflectividad)  |
| Frecuencia de muestreo | 5 kHz                                                                               |
| Resolución angular     | 0,72°                                                                               |
| Ángulo de inclinación  | 0°-1,5°                                                                             |

<h2 id="componentes-shargeek-storm-2">Shargeek Storm 2</h2>

<p align="center">
  <img src="https://i.postimg.cc/fTcgYXDv/shargeek-100-power-bank-removebg-preview.png" alt="Shargeek Storm 2" width="400">
</p>

El Shargeek Storm 2 es un Power Bank, con múltiples características interesantes [[12](#shargeek-storm-2-amazon)][[13](#shargeek-storm-2-100w-power-bank)]como:

- 25600 mAh de almacenamiento.
- Salida ajustable de hasta 100 W.
- Pantalla integrada IPS.
- Carga de 0% a 100% en tan solo 1 hora y media.

Todos estos factores hacen que sea una opción perfecta para alimentar un controlador potente como lo es la Raspberry Pi 5.

Sin embargo, sus características físicas, hacen que sea un componente un tanto difícil de incorporar a Klevor; sin embargo, hay maneras de navegar a través de estos problemas, con un manejo óptimo de peso y medidas.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 150.8 mm  |
| Alto       | 58.9 mm   |
| Ancho      | 45.9 mm   |
| Peso       | 579 g     |

<h2 id="componentes-injora-180-motor-48t">INJORA 180 Motor 48T</h2>

<p align="center">
  <img src="https://i.postimg.cc/fyTjX3K8/IMG-4570-1800x1800-removebg-preview.png" alt="INJORA 180 Motor 48T" width="250">
</p>

El INJORA 180 Motor 48T es un motor diseñado para carros controlados por radio, ya que estos carros suelen tener un peso y medidas similares a las de Klevor, decidimos que este motor sería una buena incorporación. Debido a su tamaño compacto, bajo voltaje (necesitando apenas 7.4V), y bajo peso. [[14](#injora-180-48t-amazon)].

A pesar de todas estas ventajas, un motor DC con Encoder podría ser mejor para tener una mayor cantidad de datos a la hora de trabajar en la programación, ya que este tipo de motores son capaces de controlar completamente sus vueltas, algo que en una competencia como la categoría Futuros Ingenieros es increíblemente ventajoso.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 42.7 mm   |
| Alto       | 10 mm     |
| Ancho      | 15 mm     |
| Peso       | 38 g      |

Especificaciones mecánicas:

| **Especificación** | **Valor** |
|--------------------|-----------|
| Velocidad sin carga| 20500rpm  |
| Corriente sin carga| 0.48A     |

<h2 id="componentes-injora-mb100-20a-mini-esc">INJORA MB100 20A mini ESC</h2>

<p align="center">
  <img src="https://i.postimg.cc/4yq7dnF7/DSC07300-1-1800x1800-3a89d5de-363f-4693-9ab8-815393072006-removebg-preview.png" alt="INJORA MB100 20A Mini ESC" width="250">
</p>

El INJORA MB100 20A mini ESC es un controlador de velocidad [[15](#injora-mb100-r80-amazon)], normalmente este se usa en conjunto con el INJORA 180 Motor 48T, este permite la conexión entre el INJORA 180 Motor 48T y la Raspberry Pi Pico 2.

Gracias a este dispositivo, podemos asegurar una conexión segura y efectiva entre el motor y la Pico 2, sin necesitar componentes más grandes (como un puente H L298N) para cumplir la misma función. Además que, este mini controlador de velocidad es capaz de soportar el alto amperaje que pueda consumir el motor INJORA 180.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 37 mm     |
| Alto       | 22 mm     |
| Ancho      | 10 mm     |
| Peso       | 15 g      |

Especificaciones mecánicas:

| **Especificación**        | **Valor**                                    |
|---------------------------|----------------------------------------------|
| Tipo de motor compatible: | Motor Escobillado (030/050/130/**180**/370)  |
| Salida BEC                | 6V/3A (Modo Lineal)                          |

<h2 id="componentes-urgenex-74v-battery">URGENEX 7.4V Battery</h2>

<p align="center">
  <img src="https://i.postimg.cc/25ybNPwX/71r3-PDycx-LL-AC-SL1500-1-removebg-preview.png" alt="URGENEX 7.4V Battery" width="250">
</p>

La URGENEX 7.4 V Battery es nuestra segunda batería la cual cumple la única función de alimentar al INJORA 180 Motor 48T, además de esto es una batería recargable lo que lo convierte en una opción sólida para poder alimentar el motor principal.

Si bien cualquier batería de 7.4 V funcionaría perfectamente para poder utilizar al INJORA 180 Motor 48T, decidimos utilizar a la URGENEX 7.4v Battery por su alta calidad, ya que, el motor INJORA 180, en casos extremos puede llegar a consumir 100A, lo que podría causarle problemas a la Shargeek Storm 2, por lo cual decidimos irnos por la ruta más segura y utilizar al motor con su batería propia.

Además de esto, esta batería ofrece una alta capacidad comparada con el resto del mercado, pues que esta alcanza los 3000mAh [[16](#urgenex-3000-mah-amazon)].

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 37 mm     |
| Alto       | 70 mm     |
| Ancho      | 19 mm     |
| Peso       | 103 g     |

<h2 id="componentes-injora-7kg-2065-micro-servo">INJORA 7Kg 2065 Micro Servo</h2>

<p align="center">
  <img src="https://i.postimg.cc/Qt5MXsWS/61d-MNIVpk-YL-AC-SX300-SY300-QL70-FMwebp-removebg-preview.png" alt="INJORA Micro Servo" width="200">
</p>

El INJORA 7KG 2065 Micro Servo es el motor encargado de controlar la dirección de Klevor, decidimos utilizar este modelo debido a su reducido tamaño y peso, además de una precisión más que suficiente para poder manejar a Klevor [[17](#injora-7kg-2065-amazon)].

No sólo estos aspectos definieron la elección, el INJORA 7KG 2065 ofrece también una gran precisión a pesar de su reducido tamaño, algo esencialmente vital en esta competencia.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 23 mm     |
| Alto       | 25.8 mm   |
| Ancho      | 13 mm     |
| Peso       | 20 g      |

<h2 id="sensor-tof-hiletgo">HiLetgo Time-of-Flight Sensor VL53L0X</h2>

<p align="center">
  <img src="https://i.postimg.cc/tJKzWrmG/61-Y5-Qt-Pu-NGL-SX466-removebg-preview.png" alt="sensor-tof-hiletgo" width="200">
</p>

El sensor VL53L0X en sí mismo es un pequeño sensor de distancia muy popular que utiliza la tecnología Time-of-Flight (ToF) para medir la distancia a un objeto. El sensor VL53L0X emite un pulso de luz láser infrarroja invisible y mide el tiempo que tarda en regresar al sensor. 

Estos sensores son una buena alternativa a los sensores ultrasónicos como el HC-SR04, además de ser más pequeños y confiables[[18](#sensor-tof)].

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 25 mm     |
| Alto       | 1 mm      |
| Ancho      | 10.7 mm   |
| Peso       | 0.8 g     |

<h2 id="gyroscope-gy-bno085">9-Axis IMU Gyroscope GY-BNO085</h2>

<p align="center">
  <img src="https://i.postimg.cc/Y9WJnxvg/gyroscope-removebg-preview.png"
  alt="gyroscope-gy-bno085" width="200">
</p>

El GY-BNO085 es un sensor de orientación inercial (IMU) de 9 Grados de Libertad (9DOF), ampliamente utilizado en aplicaciones que requieren un seguimiento de movimiento preciso. En el caso de Klevor, optamos por utilizar este sensor para poder lograr una mayor autonomía del robot en los cruces, ya que este sensor le permite alinearse casi perfectamente y poder ajustarse.

| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 25.75 mm  |
| Alto       | 15.5 mm   |
| Ancho      | 1.8 mm    |
| Peso       | 3 g       |

<h1 id="lenguajes-de-programacion">Lenguajes de Programación</h1>

Muchos robots autónomos necesitan de un lenguaje de programación para poder llevar a cabo tareas complejas, en el caso de Klevor, utilizamos un lenguaje principal: Python, y una implementación en microcontroladores como la Raspberry Pi Pico 2 WH, MicroPython.

<h2 id="python">Python</h2>

<p align="center">
  <img src= "https://i.postimg.cc/9MGx4R3B/5848152fcef1014c0b5e4967.webp" alt="Python" width="100">
</p>

Python es un lenguaje de programación de alto nivel, este lenguaje es cumple muchísimas funciones en general y es uno de los más vérsatiles en general. Klevor utiliza Python como lenguaje de programación para tareas como la detección de los obstáculos y el estacionamiento, escaneo 2D de los datos del RPLidar C1 y el control de los dos motores. 

La ventaja principal de Python es la versatilidad, pues no necesitamos administrar cada tarea en su lenguaje de programación distinto. [[18](#lenguaje-python)]

<h2 id="micropython">MicroPython</h2>

<p align="center">
  <img src= "https://i.postimg.cc/GmjdDQY4/image-1.png" alt="MicroPython" width="100">
</p>

MicroPython es una implementación de Python en microcontroladores, a pesar de estar escrito en en el lenguaje de programación C, éste replica todas las funciones de Python en microcontroladores como la ESP32 y ESP8266.

En el caso de Klevor, utilizamos MicroPython en la Raspberry Pi Pico 2 WH, para permitir una comunicación más eficiente entre la Raspberry Pi 5 y la Raspberry Pi Pico 2 WH. [[19](#lenguaje-micropython)]

<h2 id="circuitpython">CircuitPython</h2>

<p align="center">
    <img src="https://i.postimg.cc/G2GdpCfL/Adafruit-blinka-angles-left-svg.png" alt="CircuitPython" width="200">
</p>

CircuitPython es una ramificación de MicroPython diseñada para ser compatibles con microcontroladores pequeños y baratos. [[21](#circuit-python)]

Debido a unos problemas de compatibilidad con la librería del giroscopio GY-BNO085 de Adafruit, ya que ésta estaba diseñada para ser utilizada con CircuitPython, decidimos utilizar CircuitPython en la Raspberry Pi Pico para evitar estos problemas de compatibilidad y no tener que modificar la librería casi en su totalidad.

<h1 id="librerias">Librerías</h1> 

<h2 id="ultralytics-yolo">Ultralytics YOLO</h2>


La librería Ultralytics YOLO está construida sobre PyTorch y se caracteriza por su modularidad y su enfoque en la eficiencia y la facilidad de uso. Todo gira en torno a la clase YOLO, que encapsula todas las funcionalidades clave. En su núcleo se basa en los modelos YOLO (You Only Look Once) originales, que, a diferencia de los algoritmos de dos etapas (primero proponen regiones y luego la clasifica) los modelos YOLO se caracterizan por su detección de objetos de una pasada en la red neuronal, dándole una gran velocidad de detección.

Clase YOLO: Es la interfaz principal para interactuar con los modelos. Permite cargar modelos pre-entrenados, construir nuevos modelos desde cero, entrenar, validar, realizar inferencias, exportar y rastrear objetos. Además de la clase,la librería contiene múltiples modos para  poder organizar todas sus funciones (como `train`, `val`, `predict` o `export`)

Detección de Objetos: La tarea central de YOLO. Identifica la ubicación de objetos en una imagen/video mediante cajas delimitadoras (bounding boxes) y asigna una clase a cada objeto. Los modelos están disponibles en diferentes tamaños (Nano `n`, Small `s`, Medium `m`, Large `l`, XLarge `x`) para escalar según las necesidades de rendimiento y precisión. Si bien la librería contiene múltiples usos, en el caso de Klevor utilizamos la Detección de Objetos para poder detectar e identificar los obstáculos.

<h2 id="opencv">OpenCV</h2>

OpenCV (Open Source Computer Vision Library) es una de las librerías de software más populares y potentes del mundo para la visión por computadora y el aprendizaje automático (Machine Learning). Fue desarrollada inicialmente por Intel y ahora es mantenida por una comunidad global activa. En su esencia, OpenCV es una colección masiva de algoritmos y funciones que te permiten procesar imágenes y videos, extraer información de ellos y hacer que las computadoras "vean" y "entiendan" el mundo visual de una manera similar a como lo hacen los humanos.

Su propósito principal es proporcionar una infraestructura común para aplicaciones de visión por computadora y acelerar el uso de la percepción automática en productos comerciales, investigación y desarrollo.

<h2 id="numpy">NumPy</h2>

La librería NumPy o Numerical Python es una librería la cual contiene muchísimas funciones utilizadas ampliamente en el ecosistema de Python, gracias a esta librería, otras más populares y más flexibles como TensorFlow y PyTorch pudieron ser construidas. Esta librería se basa en la computación numérica y científica en Python.

El propósito general es permitir operaciones numéricas rápidas y eficientes en grandes cantidades de datos. Estos cálculos tan extensos, se utilizan para el procesamiento de imágenes de Klevor, aunque también tiene usos como el análisis de datos.

<h2 id="pytorch">Pytorch</h2>

PyTorch es un framework

<h2 id="picamera2">PiCamera 2</h2>

<h2 id="hailo-platform">Hailo Platform</h2>

# Recursos Externos

1. *RASPBERRY PI 5 16GB, 8GB, 4GB, 2GB – MODELO B*. (2025). tiendatec. <a id="raspberry-pi-5-16gb-8gb-4gb-2gb-tiendatec">https://www.tiendatec.es/raspberry-pi/gama-raspberry-pi/2149-raspberry-pi-5-16gb-8gb-4gb-2gb-modelo-b.html</a>

2. *Raspberry Pi 5 16GB RAM*. (2025). RaspberryPiCL. 
<a id="raspberry-pi-16gb-ram">https://raspberrypi.cl/producto/raspberry-pi-5-16gb-ram/</a>

3. *Raspberry Pi 5 Datasheet*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-5-datasheet">https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-product-brief.pdf</a>

4. *Raspberry Pi camera module 3 (standard | wide | NOIR)*. (2025). GeekFactory. <a id="raspberry-pi-camera-module-3-geek-factory">https://www.geekfactory.mx/producto/raspberry-pi-camera-module-3/</a>

5. *Raspberry Pi Camera Documentation*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-camera-documentation">https://www.raspberrypi.com/documentation/accessories/camera.html</a>

6. *Kit AI, AI HAT+ Raspberry Pi*. (2025). Kubii. <a id="kit-ai-ai-hat-plus-raspberry-pi-kubii">https://www.kubii.com/es/tarjetas-integradas/4343-kit-ai-ai-hat-raspberry-pi-3272496319608.html</a>

7. *Raspberry Pi AI HAT+ Documentation*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-ai-hat-documentation">https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html</a>

8. *Raspberry Pi Pico 2, 2W, 2H, 2WH*. (2025). Kubii. <a id="raspberry-pi-pico-2-2w-2h-2wh-kubii">https://www.kubii.com/es/microcontroladores/4377-raspberry-pi-pico-2-2w-2h-2wh-3272496319394.html</a>

9. *Raspberry Pi Pico 2 WH Datasheet*. (2025). Raspberry Pi Ltd. <a id="raspberry-pi-pico-2-wh-datasheet">https://datasheets.raspberrypi.com/pico/pico-2-product-brief.pdf</a>

10. *Escáner Láser DTOF 360° SLAMTEC RPLIDAR C1*. (2025). RobotShop. <a id="rplidar-c1-robot-shop">https://www.robotshop.com/es/products/escaner-laser-dtof-360-slamtec-rplidar-c1?qd=3ec3808f4c3dd74dab521269d23d2fb2</a>

11. *RPLidar C1 360 ToF LiDAR Datasheet*. (2025). RobotShop. <a id="rplidar-c1-datasheet">https://cdn.robotshop.com/media/R/Rpk/RB-Rpk-35/pdf/rp-lidar-360-tof-lidar-datasheet.pdf</a>

12. *Shargeek Storm 2, banco de energía para portátil de 100 W, cargador portátil de 25600 mAh, primer banco de energía transparente del mundo con pantalla IPS, Samsung Galaxy, MacBook y más*. (2025). Amazon. <a id="shargeek-storm-2-amazon">https://www.amazon.es/Shargeek-port%C3%A1til-cargador-transparente-pantalla/dp/B09NY8GN76</a>

13. *Shargeek Storm 2, 100W Portable Power Bank*. (2025). Sharge Technology (Shenzhen) Co., Ltd. <a id="shargeek-storm-2-100w-power-bank">https://docs.google.com/gview?embedded=true&url=manuals.plus/m/74637553dc00ed21580afe764bb86b7b118410fa97478a675e0edc76f8214d87_optim.pdf</a>

14. *INJORA Motor Cepillado 180 48T con Piñón de Acero Inoxidable, Conector JST-PH2.0 para Upgrade 1/18 RC Crawler Redcat Ascent-18*. (2025). Amazon. <a id="injora-180-48t-amazon">https://www.amazon.es/INJORA-Cepillado-Inoxidable-JST-PH2-0-Ascent-18/dp/B0D97YNMLG?ref_=ast_sto_dp</a>

15. *INJORA MB100-R80 20A Brushed Mini ESC con Motor 180 de 48T para Actualización TRX4M 1/18 RC Crawler*. (2025). Amazon. <a id="injora-mb100-r80-amazon">https://www.amazon.es/INJORA-MB100-Brushed-Actualizaci%C3%B3n-Crawler/dp/B0CXT74XV6?ref_=ast_sto_dp</a>

16. *URGENEX 3000mAh 7.4 V Li-ion Battery with Dean-Style T Plug 2S Rechargeable RC Battery Fit for WLtoys 4WD High Speed RC Cars and Most 1/10, 1/12, 1/16 Scale RC Cars Trucks with 7.4V Battery Charger*. (2025). Amazon. <a id="urgenex-3000-mah-amazon">https://www.amazon.com/URGENEX-Bater%C3%ADa-enchufe-recargable-velocidad/dp/B0CYNVSN7W?ref_=ast_sto_dp</a>

17. *INJORA 7KG 2065 Digital Servo Waterproof High Voltage Sub-Micro Shift Servo for TRX4 TRX6 SCX10 III 1/10 RC Crawler Car,1PCS*. (2025). Amazon. <a id="injora-7kg-2065-amazon">https://www.amazon.com/digital-impermeable-voltaje-Sub-Micro-Crawler/dp/B0BLBMVYCW?ref_=ast_sto_dp</a>

18. *VL53L0X*. (2025). STMicroElectronics. <a id="sensor-tof">https://www.st.com/en/imaging-and-photonics-solutions/vl53l0x.html</a>

19. *El tutorial de Python*. (2025). Python Software Fundation. <a id="lenguaje-python">https://docs.python.org/es/3/tutorial/</a>

20. *Qué es MicroPython, el lenguaje de programación que ya puedes usar en tu Arduino.* (2022). GenBeta. <a id="lenguaje-micropython">https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador</a>

21. *CircuitPython*. (2025). CircuitPython. <a id="circuitpython">https://docs.circuitpython.org/en/latest/README.html</a>
