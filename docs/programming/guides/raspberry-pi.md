# Raspberry Pi {:#raspberry-pi}

## Instalación de Raspberry Pi OS {:#raspberry-pi-os-installation}

Raspberry Pi OS es el sistema operativo oficial para las Raspberry Pi, basado en Debian Linux, y es ampliamente utilizado para proyectos de programación y robótica debido a su facilidad de uso y amplia comunidad de soporte [[1](#raspberry-pi-os)]. A continuación, se detallan los pasos para instalarlo en una Raspberry Pi:

1. Descargar la imagen de Raspberry Pi OS desde el sitio oficial: [Raspberry Pi OS](https://www.raspberrypi.com/software/).
2. Grabar la imagen en una tarjeta microSD utilizando un software como Balena Etcher o Raspberry Pi Imager.
3. Insertar la tarjeta microSD en la Raspberry Pi y encenderla.
4. Configurar la Raspberry Pi siguiendo las instrucciones en pantalla, incluyendo la conexión a una red wifi y la creación de un usuario.
5. Actualizar el sistema operativo ejecutando los siguientes comandos en la terminal:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

<div class="center">
    <img src="../../assets/images/app/raspberry-pi-imager.png" alt="Raspberry Pi Imager" class="app--image">
    <i>Raspberry Pi Imager</i>
</div>

> [!IMPORTANT]
> Por experiencia propia, recomendamos la configuración de la aplicación oficial de Raspberry Pi para conexión remota, Raspberry Pi Connect, que permite acceder a la Raspberry Pi desde cualquier lugar y sin necesidad de estar conectado a la misma red wifi [[2](#raspberry-pi-connect)]. En nuestro caso, en reiteradas ocasiones nos permitió de forma remota, a través del modo Remote Shell, eliminar procesos que han producido un crash o han limitado la repuesta de la Raspberry Pi.

## Instalación de la Cámara {:#camera-installation}

1. Conectar la cámara a la Raspberry Pi utilizando el conector CSI.
2. Probar el correcto funcionamiento de la cámara ejecutando el siguiente comando en la terminal:
   ```bash
   libcamera-hello
   ```
3. Si la cámara funciona correctamente, se mostrará una vista previa de la cámara en la pantalla por unos segundos.

> [!IMPORTANT]
> En caso de estar interesado en adquirir algún tipo de Raspberry Pi Camera, se debe comprar un cable aparte dependiendo del proveedor, ya que normalmente estas vienen con el cable para la Raspberry Pi 4, el cual no es el mismo.

# Referencias Bibliográficas

1. *Raspberry Pi OS*. (2025). Raspberry Pi. <a id="raspberry-pi-os" href="https://www.raspberrypi.com/software/">https://www.raspberrypi.com/software/</a>

2. *Raspberry Pi Connect*. (2025). Raspberry Pi. <a id="raspberry-pi-connect" href="https://www.raspberrypi.com/documentation/remote-access/raspberry-pi-connect.html">https://www.raspberrypi.com/documentation/remote-access/raspberry-pi-connect.html</a>