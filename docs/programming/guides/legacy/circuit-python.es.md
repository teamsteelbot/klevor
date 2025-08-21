# Guía de CircuitPython

## Instalación de CircuitPython

<!-- github-only-start -->
<p align="center">
	<img src="../../../assets/images/logo/circuit-python.png" alt="Logo de CircuitPython" 
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

El proceso para instalar CircuitPython es prácticamente el mismo método que se usa para poder instalar MicroPython, en resumidas cuentas lo que hay que hacer es:

1. Descargar la última versión de CircuitPython para Raspberry Pi Pico desde el sitio oficial: [CircuitPython](https://circuitpython.org/board/raspberry_pi_pico2_w/).
2. Presionar el botón BOOTSEL en la Raspberry Pi Pico 2 WH y conectarla a la computadora mediante un cable USB (mantener presionado el botón hasta que se reconozca la Pico como un dispositivo de almacenamiento).
3. Copiar el archivo `.uf2` descargado en la unidad de almacenamiento de la Raspberry Pi Pico. Automáticamente, la Raspberry Pi Pico se reiniciará.
4. Desconectar la Raspberry Pi Pico y volver a conectarla sin presionar el botón BOOTSEL

Después del reinicio, tu Raspberry Pi Pico debería aparecer ahora como una nueva unidad de disco llamada "CIRCUITPY" además de tener unos archivos como `code.py` [[1](#circuit-python-docs)]. Esto significa que la instalación fue exitosa y CircuitPython está listo para usar.

# Referencias

1. *CircuitPython*. (2025). CircuitPython. <a id="circuit-python-docs" href="https://docs.circuitpython.org/en/latest/README.html">https://docs.circuitpython.org/en/latest/README.html</a>