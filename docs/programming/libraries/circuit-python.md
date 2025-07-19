# Circuit Python {#circuit-python}

## Adafruit Motor {#adafruit-motor}

<div class="center">
	<img src="../../assets/images/logo/adafruit.png" alt="Logo de Adafruit" class="logo--3rd-party">
	<i>Logo de Adafruit</i>
</div>

La librería `adafruit_motor` tiene sus orígenes aproximadamente en 2017, hay versiones provenientes de Adafruit Industries previos a 2017 que cumplen con el mismo propósito que `adafruit_motor`, sin embargo, estas librerías se conocen por otros nombres, y son incompatibles con CircuitPython, esta librería le es atribuida a Scott Shawcroft como desarrollador principal, teniendo como propósito principal, la de facilitar el uso de motores y servomotores por microcontroladores por CircuitPython [[1](#adafruit-motor-documentation)].

Esta librería cumple el mismo propósito en Klevor, siendo utilizada por la [Raspberry Pi Pico 2WH](../../electronic/components/current.md#raspberry-pi-pico-2-wh) quien se comunica con el [ESC](../../electronic/components/current.md#injora-mb100-20a-mini-esc) para controlar el [motor](../../electronic/components/current.md#injora-180-motor-48t) y el [servomotor](../../electronic/components/current.md#injora-7kg-2065-micro-servo) y así poder manejar a Klevor.

## Adafruit BNO08X {#adafruit-bno08x}

La librería `adafruit_bno08x` también es desarrollada y mantenida por Adafruit Industries, su versión más antigua fue lanzada el 22 de spetiembre de 2020 (version 1.0.0), esta librería es mantenida por Adafruit Industries, siendo la persona encargada y a quien se le atribuye el trabajo de esta librería a Bryan Siepert [[2](#adafruit-bno08x-documentation)].

El propósito de esta librería es la de recibir los datos del sensor BNO08X y poder simplificar la forma en la que los usuarios manejan los datos, como por ejemplo, simplificar los cálculos de los cuaterniones (algo así como un vector 3D), para poder manejar su posición relativa.

En el caso de Klevor, utilizamos esta librería en conjunto con el [giroscopio](../../electronic/components/current.md#gyroscope-gy-bno085) para que, cuando Klevor esté en medio de un cruce, poder determinar con exactitud cuando ha girado 90° y así, saber que ya terminó de cruzar y que debe de avanzar recto.

# Referencias Biliográficas 

1. Shawcroft, S. (2025). *Adafruit motor Library*. <a id="adafruit-motor-documentation" href="https://docs.circuitpython.org/projects/motor/en/latest/">https://docs.circuitpython.org/projects/motor/en/latest/</a>

2. Siepert, B. (2025). *Adafruit BNO08X Library*. <a id="adafruit-bno08x-documentation" href="https://docs.circuitpython.org/projects/bno08x/en/latest/">https://docs.circuitpython.org/projects/bno08x/en/latest/</a>