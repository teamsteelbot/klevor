# Previous Programming Languages

## MicroPython

<div class="hcenter">
    <img src= "/assets/images/logo/micro-python.png" alt="MicroPython" class="logo--3rd-party">
    <i>MicroPython's Logo</i>
</div>

MicroPython was created by **Damien George**, an australian software engineer. Damien started to work in MicroPython in 2013. The first public version was launched in 2014.

MicroPython is a Python implementation on microcontrollers, besides it being written in C, it replicated all of Python functions in microcontrollers like the ESP32 or ESP8266.

The main purpose of MicroPython is to provide a complete Python 3 implementation optimized to be used in microcontrollers. Before MicroPython, these devices were usually restricted to low-level languages like C or Assembly.

We used MicroPython for a bit in the Raspberry Pi Pico 2 WH, to allow a better communication between the Raspberry Pi 5 and the Raspberry Pi Pico 2 Wh [[1](#micro-python-docs)], however, we later decided to use CircuitPython due to compatibility issues with the GY-BNO085 library from Adafruit, which is developed specifically for CircuitPython, we switched to avoid having to re-write the entire library and avoid these compatibility issues.

# References

1. Qué es MicroPython, el lenguaje de programación que ya puedes usar en tu Arduino.* (2022). GenBeta. <a id="micro-python-docs" href="https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador">https://www.genbeta.com/desarrollo/que-micropython-lenguaje-programacion-que-puedes-usar-tu-arduino-probar-tu-navegador</a>