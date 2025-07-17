# Raspberry Pi Pico 2W {:#raspberry-pi-pico-2w}

## Configuración {:#configuration}

<div class="center">
    <img src="../../assets/images/components/raspberry-pi-pico-2-w.png" alt="Raspberry Pi Pico 2W" 
class="component-image">
    <i>Raspberry Pi Pico 2W</i>
</div>

Para poder configurar la Raspberry Pi Pico 2 W y poder utilizarla sin problemas, recomendamos seguir una serie de pasos:

1. Instala la última versión de [CircuitPython](../guides/circuit-python.md).
2. Copiar tanto `code.py` como el contenido de las carpetas `config` y `lib` mediante una conexión por USB:
    1. Para ello, conecta la Raspberry Pi Pico 2 W a tu computadora mediante un cable USB.
    2. Copia el archivo `code.py` y la carpeta `lib` en la raíz de la unidad de almacenamiento de la Raspberry Pi Pico 2 W.
    3. Copiar el archivo `boot.py` de la carpeta `config` en la raíz de la unidad de almacenamiento de la Raspberry Pi Pico 2 W.
    4. Modificar las variables de entorno en el archivo `settings.toml.example` de la carpeta `config` según tus necesidades, y luego renombrar el archivo a `settings.toml`. Cuando hayas terminado, copia el archivo `settings.toml` en la raíz de la unidad de almacenamiento de la Raspberry Pi Pico 2 W.
    5. Reinicia la Raspberry Pi Pico 2 W para que los cambios surtan efecto.
3. En caso de que se necesite cambiar algunos aspectos partes del código, se recomienda utilizar [Thonny](https://thonny.org/) como editor de código, gracias a su enfoque en microcontroladores con MicroPython o CircuitPython instalados, además de facilitar el uso de librerías externas.