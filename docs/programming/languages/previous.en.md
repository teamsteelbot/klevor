# Previous Programming Languages

## MicroPython

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/micro-python.png" alt="MicroPython's Logo" 
width="200">
	<br>
	<i>MicroPython's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/micro-python.png" alt="MicroPython's Logo" 
class="logo--3rd-party">
    <i>MicroPython's Logo</i>
</div>
mkdocs-only-end -->

MicroPython was created by **Damien George**, an australian software engineer. Damien started to work in MicroPython in 2013. The first public version was launched in 2014.

MicroPython is a Python implementation on microcontrollers, besides it being written in C, it replicated all of Python functions in microcontrollers like the ESP32 or ESP8266.

The main purpose of MicroPython is to provide a complete Python 3 implementation optimized to be used in microcontrollers. Before MicroPython, these devices were usually restricted to low-level languages like C or Assembly.

We used MicroPython for a bit in the Raspberry Pi Pico 2 WH, to allow a better communication between the Raspberry Pi 5 and the Raspberry Pi Pico 2 Wh [[1](#micro-python-docs)], however, we later decided to use CircuitPython due to compatibility issues with the GY-BNO085 library from Adafruit, which is developed specifically for CircuitPython, we switched to avoid having to re-write the entire library and avoid these compatibility issues.

## CircuitPython

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
width="200">
	<br>
	<i>CircuitPython's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
class="logo--3rd-party">
    <i>CircuitPython's Logo</i>
</div>
mkdocs-only-end -->

CircuitPython is a MicroPython fork, it was mainly develop by **Adafruit Industries**, a corporation specialized in open-source code and electronics. There's not a clear main developer, like Python or MicroPython does, so the work is mostly attributed to **Limor Fried (Ladyada)**, Adafruit's founder, and her team of programmers.

CircuitPython was launched in 2017. Its main purpose was to have a Python version for microcontrollers that was even more oriented into the education and also, it was beginner-friendly. CircuitPython was specifically designed for learning, quick experimenting and the ease of use for users that don't have or have very little experience with microcontrollers and electronics.

Since the code needs to be stored inside a disk unit that is accessible by USB, it's really easy to edit and update the code without having to use external tools to edit the code, unlike MicroPython, which is built for more general purposes, CircuitPython focuses in providing a direct and robust support for a wide variety of sensors, actuators, and external components, more specifically, the devices sold by Adafruit and its partners. This is made possible by a large amount of libraries and pre-written drivers.

In the same way as MicroPython, CircuitPython is an implementation for Python in microcontrollers, and it's optimized to be used on devices with limited resources, like the Raspberry Pi Pico 2 WH [[2](#circuit-python-docs)].

# References

1. Qué es MicroPython, el lenguaje de programación que ya puedes usar en tu Arduino.* (2022). GenBeta. <a id="micro-python-docs" href="https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador">https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador</a>

2. *CircuitPython*. (2025). CircuitPython. <a id="circuit-python-docs" href="https://docs.circuitpython.org/en/latest/README.html">https://docs.circuitpython.org/en/latest/README.html</a>