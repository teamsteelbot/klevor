# Inicio {:#home}

<div class="hcenter">
    <img src="/assets/images/logo/teamsteelbot.png" alt="Logo del Equipo" 
class="logo--team">
    <i>Logo del Equipo</i>
</div>

Bienvenidos a la documentación de Klevor, un robot autónomo diseñado para participar en el Desafío Abierto y el Desafío Cerrado de la competencia de robótica de la World Robot Olympiad 2025, en la categoría Futuros Ingenieros. Esta documentación contiene toda la información necesaria para entender su funcionamiento, los dispositivos utilizados, el código implementado, los componentes y más. Esperamos que la misma sea útil tanto para los jueces como para cualquier persona interesada en aprender sobre este proyecto.

<div class="image-horizontal-container">
    <div class="hcenter">
        <img src="/assets/images/logo/wro.webp" alt="Logo de la World Robot Olympiad" 
    class="logo--education">
        <i>Logo de la World Robot Olympiad</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/logo/mincyt.png" alt="Logo del MINCYT" 
    class="logo--education">
        <i>Logo del MINCYT</i>
    </div>
</div>

!!! important 
	Si deseas visualizar esta documentación de una forma más tradicional, puedes descargarla en formato PDF: [Descargar](downloads/teamsteelbot.pdf).

A continuación se presenta un índice con los enlaces a las diferentes secciones de la documentación. Cada sección contiene información detallada sobre los aspectos técnicos y prácticos del robot, incluyendo la mecánica, el código, los dispositivos utilizados, los componentes, los esquemas y diagramas, las fotos del equipo y los vídeos de Klevor en acción. Además, se incluyen recursos externos para ampliar la información y facilitar la comprensión de los conceptos presentados.

<div class="hcenter">
    <img src="/assets/images/github/t-photos/salto-angel-regional-competition-photo.jpg" alt="Team Steel Bot en la competencia regional del Salto Ángel" 
class="picture--team">
    <i>Team Steel Bot en la competencia regional del Salto Ángel</i>
</div>

## Índice {:#index}

1. **[Nosotros](about.es.md)**
2. **Electrónica**
	1. Componentes
		1. [Previos](electronic/components/previous.es.md)
			1. [HiLetgo Time-of-Flight Sensor VL53L0X](electronic/components/previous.es.md#sensor-tof-hiletgo)
		2. [Actuales](electronic/components/current.es.md)
			1. [Raspberry Pi 5](electronic/components/current.es.md#raspberry-pi-5)
			2. [Raspberry Pi Camera Module 3 Wide](electronic/components/current.es.md#raspberry-pi-camera-module-3-wide)
			3. [Raspberry Pi AI HAT+ (26 TOPS)](electronic/components/current.es.md#raspberry-pi-ai-hat-26-tops)
			4. [Raspberry Pi Pico 2 WH](electronic/components/current.es.md#raspberry-pi-pico-2-wh)
			5. [RPLIDAR C1](electronic/components/current.es.md#rplidar-c1)
			6. [Shargeek Storm 2](electronic/components/current.es.md#shargeek-storm-2)
			7. [INJORA 180 Motor 48T](electronic/components/current.es.md#injora-180-motor-48t)
			8. [INJORA MB100 20A mini ESC](electronic/components/current.es.md#injora-mb100-20a-mini-esc)
			9. [URGENEX 7.4V Battery](electronic/components/current.es.md#urgenex-7-4v-battery)
			10. [INJORA 7KG 2065 Micro Servo](electronic/components/current.es.md#injora-7kg-2065-micro-servo)
			11. [9-Axis IMU Gyroscope GY-BNO085](electronic/components/current.es.md#gyroscope-gy-bno085)
		3. [Futuros](electronic/components/future.es.md)
			1. [Motor 540](electronic/components/future.es.md#motor-540)
			2. [ESC para Motores 540/550 2-3s 60 A](electronic/components/future.es.md#esc-for-540-550-motors-2-3s-60-a)
			3. [UGREEN Nexode Power Bank 12000mAh 100W PD PPS](electronic/components/future.es.md#ugreen-nexode-power-bank-12000mah-100w-pd-pps)
			4. [USB-C QC PD3.0 Trigger 5V/9V/12V/15V/20V 5A](electronic/components/future.es.md#usb-c-qc-pd3-0-trigger-5v-9v-12v-15v-20v-5a)
	2. Diagramas
		1. [Diagramas de Conexiones](electronic/diagrams/wiring.es.md)
			1. [Versión 1](electronic/diagrams/wiring.es.md#version1)
			2. [Versión 2](electronic/diagrams/wiring.es.md#version2)
			3. [Versión 3](electronic/diagrams/wiring.es.md#version3)
3. **Mecánica**
	1. Piezas
		1. Piezas Comunes
			1. [Previas](mechanical/parts/common/previous.es.md)
			2. [Actuales](mechanical/parts/common/current.es.md)
		2. [Piezas del Prototipo 1](mechanical/parts/prototype1.es.md)
		3. [Piezas del Prototipo 2](mechanical/parts/prototype2.es.md)
		4. [Piezas del Prototipo 3](mechanical/parts/prototype3.es.md)
	2. Prototipos
		1. [Prototipo 1](mechanical/prototypes/prototype1.es.md)
			1. [Primera Capa](mechanical/prototypes/prototype1.es.md#first-layer)
			2. [Segunda Capa](mechanical/prototypes/prototype1.es.md#second-layer)
			3. [Tercera Capa](mechanical/prototypes/prototype1.es.md#third-layer)
			4. [Lista de Materiales](mechanical/prototypes/prototype1.es.md#materials-list)
		2. [Prototipo 2](mechanical/prototypes/prototype2.es.md)
			1. [Primera Capa](mechanical/prototypes/prototype2.es.md#first-layer)
			2. [Segunda Capa](mechanical/prototypes/prototype2.es.md#second-layer)
			3. [Lista de Materiales](mechanical/prototypes/prototype2.es.md#materials-list)
		3. [Prototipo 3](mechanical/prototypes/prototype3.es.md)
			1. [Actualizaciones](mechanical/prototypes/prototype3.es.md#updates)
			2. [Primera Capa](mechanical/prototypes/prototype3.es.md#first-layer)
			3. [Segunda Capa](mechanical/prototypes/prototype3.es.md#second-layer)
			4. [Lista de Materiales](mechanical/prototypes/prototype3.es.md#materials-list)
		4. [Prototipo 4](mechanical/prototypes/prototype4.es.md)
			1. [Lista de Materiales](mechanical/prototypes/prototype4.es.md#materials-list)
4. **Programación**
	1. [Lenguajes de Programación](programming/languages.es.md)
		1. [Python](programming/languages.es.md#python)
		2. [MicroPython](programming/languages.es.md#micro-python)
		3. [CircuitPython](programming/languages.es.md#circuit-python)
	2. Librerías
		1. [Python](programming/libraries/python.es.md)
			1. [PyTorch](programming/libraries/python.es.md#pytorch)
			2. [Ultralytics YOLO](programming/libraries/python.es.md#ultralytics-yolo)
			3. [OpenCV](programming/libraries/python.es.md#opencv)
			4. [NumPy](programming/libraries/python.es.md#numpy)
			5. [PiCamera2](programming/libraries/python.es.md#picamera-2)
			6. [Hailo Platform](programming/libraries/python.es.md#hailo-platform)
			7. [MkDocs](programming/libraries/python.es.md#mkdocs)
			8. [WeasyPrint](programming/libraries/python.es.md#weasyprint)
		2. [CircuitPython](programming/libraries/circuit-python.es.md)
			1. [Adafruit Motor](programming/libraries/circuit-python.es.md#adafruit-motor)
			2. [Adafruit BNO08X](programming/libraries/circuit-python.es.md#adafruit-bno08x)
	3. Diagramas
		1. [Diagramas de Flujo](programming/diagrams/flowcharts.es.md)
			1. [Desafío sin Obstáculos](programming/diagrams/flowcharts.es.md#without-obstacles-challenge)
				1. [Versión 1](programming/diagrams/flowcharts.es.md#without-obstacles-challenge-version1)
				2. [Versión 2](programming/diagrams/flowcharts.es.md#without-obstacles-challenge-version2)
			2. [Desafío con Obstáculos](programming/diagrams/flowcharts.es.md#obstacles-challenge)
				1. [Versión 1](programming/diagrams/flowcharts.es.md#obstacles-challenge-version1)
	4. [Glosario de Términos](programming/glossary.es.md)
		1. [Machine Learning](programming/glossary.es.md#machine-learning)
		2. [Detección de Objetos](programming/glossary.es.md#object-detection)
			1. [Funcionamiento de la Detección de Objetos](programming/glossary.es.md#how-object-detection-works)
		3. [You Only Look Once (YOLO)](programming/glossary.es.md#yolo)
		4. [Neural Processing Unit (NPU)](programming/glossary.es.md#npu)
		5. [Docker](programming/glossary.es.md#docker)
			1. [Dockerfile](programming/glossary.es.md#dockerfile)
			2. [Docker Image](programming/glossary.es.md#docker-image)
			3. [Docker Container](programming/glossary.es.md#docker-container)
		6. [Multiprocesamiento](programming/glossary.es.md#multiprocessing)
	5. Guías
		1. [Guía de MkDocs](programming/guides/mkdocs.es.md)
			1. [Instalación](programming/guides/mkdocs.es.md#installation)
			2. [Servir la Documentación](programming/guides/mkdocs.es.md#serve-documentation)
		2. [Guía de CircuitPython](programming/guides/circuit-python.es.md)
			1. [Instalación](programming/guides/circuit-python.es.md#installation)
		3. [Guía de MicroPython](programming/guides/micro-python.es.md)
			1. [Instalación](programming/guides/micro-python.es.md#installation)
		4. [Guía de Raspberry Pi 5](programming/guides/raspberry-pi-5.es.md)
			1. [Instalación de Raspberry Pi OS](programming/guides/raspberry-pi-5.es.md#raspberry-pi-os-installation)
			2. [Instalación de la Cámara](programming/guides/raspberry-pi-5.es.md#camera-installation)
			3. [Instalación de Raspberry Pi AI HAT+](programming/guides/raspberry-pi-5.es.md#raspberry-pi-ai-hat-plus-installation)
			4. [Configuración de la Raspberry Pi](programming/guides/raspberry-pi-5.es.md#raspberry-pi-configuration)
		5. [Guía de Raspberry Pi Pico 2 W](programming/guides/raspberry-pi-pico-2w.es.md)
			1. [Configuración](programming/guides/raspberry-pi-pico-2w.es.md#configuration)
		6. [Guía de Detección de Objetos](programming/guides/object-detection.es.md)
			1. [Creación del Modelo](programming/guides/object-detection.es.md#model-creation)
			2. [Entrenamiento del Modelo](programming/guides/object-detection.es.md#model-training)
			3. [Conversión del Modelo](programming/guides/object-detection.es.md#model-conversion)
			4. [Prueba del Funcionamiento del Modelo](programming/guides/object-detection.es.md#model-testing)
	6. Referencia del Código
		1. Raspberry Pi 5
			1. [Args](programming/code/raspberry-pi-5/args.es.md)
			2. [Camera](programming/code/raspberry-pi-5/camera.es.md)
			3. [Common](programming/code/raspberry-pi-5/common.es.md)
			4. [Files](programming/code/raspberry-pi-5/files.es.md)
			5. [Hailo](programming/code/raspberry-pi-5/hailo.es.md)
			6. [Log](programming/code/raspberry-pi-5/log.es.md)
			7. [Model](programming/code/raspberry-pi-5/model.es.md)
			8. [OpenCV](programming/code/raspberry-pi-5/opencv.es.md)
			9. [Pilot](programming/code/raspberry-pi-5/pilot.es.md)
			10. [Plot](programming/code/raspberry-pi-5/plot.es.md)
			11. [RPLiDAR](programming/code/raspberry-pi-5/rplidar.es.md)
			12. [Serial Communication](programming/code/raspberry-pi-5/serial-communication.es.md)
			13. [Server](programming/code/raspberry-pi-5/server.es.md)
			14. [Spawner](programming/code/raspberry-pi-5/spawner.es.md)
			15. [Utils](programming/code/raspberry-pi-5/utils.es.md)
			16. [YOLO](programming/code/raspberry-pi-5/yolo.es.md)
		2. Raspberry Pi Pico 2W
			1. [Lib](programming/code/raspberry-pi-pico-2w/lib.es.md)
			2. [Code](programming/code/raspberry-pi-pico-2w/code.es.md)
5. **[GitHub](github.es.md)**
	1. [Repositorio](github.es.md#repository)
	2. [Estructura del Repositorio](github.es.md#repository-structure)
6. **[Vídeos](videos.es.md)**
	1. [Desafío sin Obstáculos](videos.es.md#without-obstacles-challenge)
		1. [Parte 1](videos.es.md#without-obstacles-challenge-part1)
7. **[Software](software.es.md)**
	1. [Programación](software.es.md#programming)
		1. [Label Studio](software.es.md#label-studio)
		2. [Google Colab](software.es.md#google-colab)
		3. [Visual Studio Code](software.es.md#visual-studio-code)
		4. [PyCharm](software.es.md#pycharm)
		5. [Thonny](software.es.md#thonny)
	2. [Diseño](software.es.md#design)
		1. [Canva](software.es.md#canva)
		2. [Mermaid](software.es.md#mermaid)
		3. [Draw.io](software.es.md#draw-io)
		4. [Fusion 360](software.es.md#fusion-360)
	3. [Planificación](software.es.md#planning)
		1. [Jira](software.es.md#jira)
8. [Gadgets](gadgets.es.md)
	1. [Multímetro Digital con Puerto USB-C 4-30 V 0-12 A](gadgets.es.md#usb-c-tester)
9. **[Patrocinadores](sponsors.es.md)**
	1. [Viajes Giorgio](sponsors.es.md#viajes-giorgio)
	2. [Nathaly's Star](sponsors.es.md#nathalys-star)
	3. [Steel C.A.](sponsors.es.md#steel-ca)
10. **[Contacto](contact.es.md)**

## Patrocinadores {:#sponsors}

<div class="hcenter">
    <a href="sponsors.html#viajes-giorgio">
        <img src="/assets/images/sponsors/viajes-giorgio.png" alt="Logo de Viajes Giorgio" 
class="logo--sponsor">
    </a>
    <i>Logo de Viajes Giorgio</i>
</div>

<div class="hcenter">
    <a href="sponsors.html#nathalys-star">
        <img src="/assets/images/sponsors/nathalys-star.png" alt="Logo de Nathaly's Star" 
class="logo--sponsor">
    </a>
    <i>Logo de Nathaly's Star</i>
</div>

<div class="hcenter">
    <a href="sponsors.html#steel-ca">
        <img src="/assets/images/sponsors/steel-ca.jpg" alt="Logo de Steel C.A." 
class="logo--sponsor">
    </a>
    <i>Logo de Steel C.A.</i>
</div>