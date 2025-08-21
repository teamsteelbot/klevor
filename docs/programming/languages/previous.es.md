# Lenguajes de Programación Previos

## MicroPython

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/micro-python.png" alt="Logo de MicroPython" 
width="200">
	<br>
	<i>Logo de MicroPython</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/micro-python.png" alt="Logo de MicroPython" 
class="logo--3rd-party">
    <i>Logo de MicroPython</i>
</div>
mkdocs-only-end -->

MicroPython fue creado por **Damien George**, un ingeniero de software australiano. Damien comenzó a trabajar en MicroPython en 2013. La primera versión pública fue lanzada en 2014.

MicroPython es una implementación de Python en microcontroladores, a pesar de estar escrito en el lenguaje de programación C, este replica todas las funciones de Python en microcontroladores como la ESP32 y ESP8266.

El propósito principal de MicroPython fue proporcionar una implementación completa del lenguaje de programación Python 3, optimizada para ejecutarse en microcontroladores. Antes de MicroPython, la programación de estos dispositivos de recursos limitados se realizaba principalmente con lenguajes de bajo nivel como C o Assembly.

En el caso de Klevor, utilizamos MicroPython en la Raspberry Pi Pico 2 WH, para permitir una comunicación más eficiente entre la Raspberry Pi 5 y la Raspberry Pi Pico 2 WH [[1](#micro-python-docs)], sin embargo, posteriormente decidimos utilizar CircuitPython debido a problemas de compatibilidad con la librería del giroscopio GY-BNO085 de Adafruit, ya que esta estaba diseñada para ser utilizada con CircuitPython, lo que nos llevó a cambiar a CircuitPython para evitar estos problemas de compatibilidad y no tener que modificar la librería casi en su totalidad.

## CircuitPython

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/circuit-python.png" alt="Logo de CircuitPython" 
width="200">
	<br>
	<i>Logo de CircuitPython</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/circuit-python.png" alt="Logo de CircuitPython" 
class="logo--3rd-party">
    <i>Logo de CircuitPython</i>
</div>
mkdocs-only-end -->

CircuitPython es una bifurcación de MicroPython, y fue desarrollado principalmente por **Adafruit Industries**, una empresa líder en hardware de código abierto y educación electrónica. Si bien no hay un único creador individual como en Python o MicroPython, **Limor Fried (Ladyada)**, la fundadora de Adafruit, y su equipo han sido los principales impulsores y desarrolladores de CircuitPython.

CircuitPython fue lanzado en 2017. Nació de la necesidad de tener una versión de Python para microcontroladores que estuviera aún más orientada a la educación y la facilidad de uso para principiantes, CircuitPython fue diseñado con un enfoque muy específico en la educación, la experimentación rápida y la facilidad de uso para personas que se inician en la programación de microcontroladores y la electrónica.

Dado que el código reside en una unidad de disco accesible por USB, es muy fácil editar y actualizar el código sin necesidad de herramientas de desarrollo complejas, a diferencia de MicroPython, que es más genérico, CircuitPython se enfoca en proporcionar soporte directo y robusto para una amplia gama de sensores, actuadores y componentes externos, especialmente los vendidos por Adafruit y sus socios. Esto se logra a través de una extensa colección de librerías y controladores pre-escritos.

Al igual que MicroPython, CircuitPython es una implementación de Python en microcontroladores, pero está optimizada para ser utilizada en dispositivos con recursos limitados, como la Raspberry Pi Pico 2 WH [[2](#circuit-python-docs)].

# Referencias

1. Qué es MicroPython, el lenguaje de programación que ya puedes usar en tu Arduino.* (2022). GenBeta. <a id="micro-python-docs" href="https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador">https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador</a>

2. *CircuitPython*. (2025). CircuitPython. <a id="circuit-python-docs" href="https://docs.circuitpython.org/en/latest/README.html">https://docs.circuitpython.org/en/latest/README.html</a>