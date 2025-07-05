# Klevor

<div class="center">
    <img src="assets/images/logo/teamsteelbot.svg" alt="Logo del Equipo" 
class="logo--team">
    <i>Logo del Equipo</i>
</div>

Bienvenidos a la documentación de Klevor, un robot autónomo diseñado para
participar en el Desafío Abierto y el Desafío Cerrado de la competencia de
robótica de la World Robot Olympiad 2025, en la categoría Futuros Ingenieros.
Esta documentación contiene toda la información necesaria para entender su
funcionamiento, los dispositivos utilizados, el código implementado, los
componentes y más. Esperamos que la misma sea útil tanto para los jueces
como para cualquier persona interesada en aprender sobre este proyecto.

<div class="center">
    <img src="assets/images/logo/wro.webp" alt="Logo de la World Robot Olympiad" 
class="logo--3rd-party">
    <i>Logo de la World Robot Olympiad</i>
</div>

A continuación se presenta un índice con los enlaces a las diferentes secciones de la
documentación. Cada sección contiene información detallada sobre los aspectos
técnicos y prácticos del robot, incluyendo la mecánica, el código, los dispositivos
utilizados, los componentes, los esquemas y diagramas, las fotos del equipo y los vídeos
de Klevor en acción. Además, se incluyen recursos externos para ampliar la información
y facilitar la comprensión de los conceptos presentados.

## Índice

1. **[Nosotros](about.md)**
2. **Electrónica**
    1. Componentes
        1. Actuales
            1. [Raspberry Pi 5](electronic/components/current.md#raspberry-pi-5)
            2. [Raspberry Pi Camera Module 3 Wide](electronic/components/current.md#raspberry-pi-camera-module-3-wide)
            3. [Raspberry Pi AI HAT+ (26 TOPS)](electronic/components/current.md#raspberry-pi-ai-hat-26-tops)
            4. [Raspberry Pi Pico 2 WH](electronic/components/current.md#raspberry-pi-pico-2-wh)
            5. [RPLIDAR C1](electronic/components/current.md#rplidar-c1)
            6. [Shargeek Storm 2](electronic/components/current.md#shargeek-storm-2)
            7. [INJORA 180 Motor 48T](electronic/components/current.md#injora-180-motor-48t)
            8. [INJORA MB100 20A mini ESC](electronic/components/current.md#injora-mb100-20a-mini-esc)
            9. [URGENEX 7.4V Battery](electronic/components/current.md#urgenex-7-4v-battery)
            10. [INJORA 7KG 2065 Micro Servo](electronic/components/current.md#injora-7kg-2065-micro-servo)
            11. [9-Axis IMU Gyroscope GY-BNO085](electronic/components/current.md#gyroscope-gy-bno085)
        2. Viejos
            1. [HiLetgo Time-of-Flight Sensor VL53L0X](#sensor-tof-hiletgo)
    2. Diagramas
        1. [Diagramas de Conexiones](electronic/diagrams/wiring.md#wiring-diagrams)
            1. [Prototipo 1](electronic/diagrams/wiring.md#prototype1)
            2. [Prototipo 2](electronic/diagrams/wiring.md#prototype2)
            3. [Prototipo 3](electronic/diagrams/wiring.md#prototype3)
3. **Mecánica**
4. **Programación**
    1. [Lenguajes de Programación](programming/languages.md#programming-languages)
        1. [Python](programming/languages.md#python)
        2. [MicroPython](programming/languages.md#micro-python)
        3. [CircuitPython](programming/languages.md#circuit-python)
    2. [Librerías](programming/libraries.md#libraries)
        1. [PyTorch](programming/libraries.md#pytorch)
        2. [Ultralytics YOLO](programming/libraries.md#ultralytics-yolo)
        3. [OpenCV](programming/libraries.md#opencv)
        4. [NumPy](programming/libraries.md#numpy)
        5. [PiCamera2](programming/libraries.md#picamera-2)
        6. [Hailo Platform](programming/libraries.md#hailo-platform)
    3. Diagramas
        1. [Diagramas de Flujo](programming/diagrams/flowcharts.md#flowcharts)
            1. [Desafío sin Obstáculos](programming/diagrams/flowcharts.md#without-obstacles-challenge.md)
            2. [Desafío con Obstáculos](programming/diagrams/flowcharts.md#obstacles-challenge.md)
5. **[GitHub](github.md)**
    1. [Repositorio](github.md#repository)
    2. [Estructura del Repositorio](github.md#repository-structure)
6. **[Vídeos](videos.md)**
    1. [Desafío sin Obstáculos](videos.md#without-obstacles-challenge)
        1. [Parte 1](videos.md#without-obstacles-challenge-part-1)
5. **[Descripción de la Mecánica](v-photos/prototype1/README.md)**
6. **[Código](devices/README.md)**
    1. **[Dispositivos](/devices)**
        1. [Raspberry Pi 5](devices/raspberry-pi-5/README.md)
        2. [Raspberry Pi Pico 2 WH](devices/raspberry-pi-pico-2w/README.md)
            1. [CircuitPython](devices/raspberry-pi-pico-2w/src/circuit-python/README.md)
            2. [MicroPython](devices/raspberry-pi-pico-2w/src/micro-python/README.md)