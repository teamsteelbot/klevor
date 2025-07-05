# Klevor

Bienvenidos a la documentación de Klevor, un robot autónomo diseñado para
participar en el Desafío Abierto y el Desafío Cerrado de la competencia de
robótica de la World Robot Olympiad 2025, en la categoría Futuros Ingenieros.
Esta documentación contiene toda la información necesaria para entender su 
funcionamiento, los dispositivos utilizados, el código implementado, los 
componentes y más. Esperamos que la misma sea útil tanto para los jueces
como para cualquier persona interesada en aprender sobre este proyecto.

A continuación se presenta un índice con los enlaces a las diferentes secciones de la
documentación. Cada sección contiene información detallada sobre los aspectos
técnicos y prácticos del robot, incluyendo la mecánica, el código, los dispositivos
utilizados, los componentes, los esquemas y diagramas, las fotos del equipo y los vídeos
de Klevor en acción. Además, se incluyen recursos externos para ampliar la información
y facilitar la comprensión de los conceptos presentados.

## Índice

1. **[Nosotros](about.md)**
2. **[Electrónica]**
   1. [Componentes]
      1. [Actuales](components/current.md#components-list)
         1. [Raspberry Pi 5](components/current.md#raspberry-pi-5)
         2. [Raspberry Pi Camera Module 3 Wide](components/current.md#raspberry-pi-camera-module-3-wide)
         3. [Raspberry Pi AI HAT+ (26 TOPS)](components/current.md#raspberry-pi-ai-hat-26-tops)
         4. [Raspberry Pi Pico 2 WH](components/current.md#raspberry-pi-pico-2-wh)
         5. [RPLIDAR C1](components/current.md#rplidar-c1)
         6. [Shargeek Storm 2](components/current.md#shargeek-storm-2)
         7. [INJORA 180 Motor 48T](components/current.md#injora-180-motor-48t)
         8. [INJORA MB100 20A mini ESC](components/current.md#injora-mb100-20a-mini-esc)
         9. [URGENEX 7.4V Battery](components/current.md#urgenex-7-4v-battery)
         10. [INJORA 7KG 2065 Micro Servo](components/current.md#injora-7kg-2065-micro-servo)
         11. [9-Axis IMU Gyroscope GY-BNO085](components/current.md#gyroscope-gy-bno085)
      2. [Viejos](components/old.md#components-list)
         1. [HiLetgo Time-of-Flight Sensor VL53L0X](#sensor-tof-hiletgo)
3. **[Descripción de la Mecánica](v-photos/prototype1/README.md)**
4. **[Código](devices/README.md)**
   1. **[Dispositivos](/devices)**
      1. [Raspberry Pi 5](devices/raspberry-pi-5/README.md)
      2. [Raspberry Pi Pico 2 WH](devices/raspberry-pi-pico-2w/README.md)
         1. [CircuitPython](devices/raspberry-pi-pico-2w/src/circuit-python/README.md)
         2. [MicroPython](devices/raspberry-pi-pico-2w/src/micro-python/README.md)
   2. **[Lenguajes de Programación](programming/languages.md#programming-languages)**
      1. [Python](programming/languages.md#python)
      2. [MicroPython](programming/languages.md#micro-python)
      3. [CircuitPython](programming/languages.md#circuit-python)
   3. **[Librerías](programming/libraries.md#libraries)**
      1. [PyTorch](programming/libraries.md#pytorch)
      2. [Ultralytics YOLO](programming/libraries.md#ultralytics-yolo)
      3. [OpenCV](programming/libraries.md#opencv)
      4. [NumPy](programming/libraries.md#numpy)
      5. [PiCamera2](programming/libraries.md#picamera-2)
      6. [Hailo Platform](programming/libraries.md#hailo-platform)
5. **[Esquemas y Diagramas](schemes/README.md)**
   1. [Esquemas de Conexiones](schemes/prototype3/wiring-diagram.png)
   2. [Diagrama de Flujo](schemes/prototype3/open-challenge-flowchart.png)
6. **[Fotos del equipo](t-photos/README.md)**
7. **[Vídeos](video/README.md)**
8. **[Recursos Externos](#recursos-externos)**

> [!IMPORTANT]
> Este listado contiene todo el contenido respectivo al desarrollo de
Klevor; sin embargo, no todo está presente en este README.md, asegúrese de hacer
clic para poder ser redireccionado si es necesario.



<h1 id="estructura-de-archivos">Estructura de archivos</h1>

- `devices` contiene todo el código el cual fue utilizado para poder controlar este robot de manera autónoma, además de su correspondiente explicación.

- `models` contiene todos los archivos en 3D que se utilizaron para poder
  construir a nuestro robot (Klevor).

- `schemes` contiene todos los esquemas y diagramas de todas las conexiones de nuestro robot (Klevor).

- `t-photos` contiene las fotos del equipo.

- `v-photos` contiene las fotos de Klevor.

- `video` contiene los vídeos de Klevor en la pista, tanto en el Desafío Abierto como en el Desafío con Obstáculos (Desafío Cerrado).