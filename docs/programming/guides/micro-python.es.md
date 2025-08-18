# Guía de MicroPython

## Instalación de MicroPython

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

Por defecto, la Raspberry Pi Pico 2 WH viene con MicroPython preinstalado. Sin embargo, si deseas instalar una versión diferente o actualizarla, puedes seguir estos pasos [[1](#micro-python-docs)] | [[2](#raspberry-pi-micro-python-docs)]:

1. Descargar la última versión de MicroPython para Raspberry Pi Pico desde el sitio oficial: [MicroPython](https://micropython.org/download/rp2-pico-w/).
2. Presionar el botón BOOTSEL en la Raspberry Pi Pico 2 WH y conectarla a la computadora mediante un cable USB (mantener presionado el botón hasta que se reconozca la Pico como un dispositivo de almacenamiento).
3. Copiar el archivo `.uf2` descargado en la unidad de almacenamiento de la Raspberry Pi Pico. Automáticamente, la Raspberry Pi Pico se reiniciará.
4. Desconectar la Raspberry Pi Pico y volver a conectarla sin presionar el botón BOOTSEL.

# Referencias

1. *MicroPython*. (2025). MicroPython. <a id="micro-python-docs" href="https://micropython.org/">https://micropython.org/</a>

2. *MicroPython*. (2025). Raspberry Pi. <a id="raspberry-pi-micro-python-docs" href="https://www.raspberrypi.com/documentation/micropython/">https://www.raspberrypi.com/documentation/micropython/</a>