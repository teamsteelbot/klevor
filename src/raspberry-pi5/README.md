<h1 id="indice">Índice</h1>

1. [Configuración Básica de la Raspberry Pi](#configuracion-basica-de-la-raspberry-pi)
   1. [Instalación de Raspberry Pi OS](#instalacion-de-raspberry-pi-os) 
   2. [Instalación de la cámara](#instalacion-de-la-camara)
2. [Multiprocesamiento](#multiprocesamiento)
3. [YOLO](yolo/README.md)
4. [Recursos Externos](#recursos-externos)

<h1 id="configuracion-basica-de-la-raspberry-pi">Configuración Básica de la Raspberry Pi</h1>

<h1 id="instalacion-de-raspberry-pi-os">Instalación de Raspberry Pi OS</h1>

1. Descargar la imagen de Raspberry Pi OS desde el sitio oficial: [Raspberry Pi OS](https://www.raspberrypi.com/software/).
2. Grabar la imagen en una tarjeta microSD utilizando un software como Balena Etcher o Raspberry Pi Imager.
3. Insertar la tarjeta microSD en la Raspberry Pi y encenderla.
4. Configurar la Raspberry Pi siguiendo las instrucciones en pantalla, incluyendo la conexión a una red Wi-Fi y la creación de un usuario.
5. Actualizar el sistema operativo ejecutando los siguientes comandos en la terminal:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```
   
<p align="center">
    <img src="https://www.raspberrypi.com/documentation/computers/images/imager/welcome.png?hash=a351c2ba01f30809c2921de09be67683" alt="Raspberry Pi OS" width="600">
    <br>
    <i>Raspberry Pi OS</i>
</p>

*TIP: Por experiencia propia, recomendamos la configuración de la aplicación oficial de Raspberry Pi para conexión remota, Raspberry Pi Connect, que permite acceder a la Raspberry Pi desde cualquier lugar y sin necesidad de estar conectado a la misma red Wi-Fi [[3](#raspberry-pi-connect)]. En nuestro caso, en reiteradas ocasiones nos permitió de forma remota, a través del modo Remote Shell, eliminar procesos que han producido un crash o han limitado la repuesta de la Raspberry Pi.* 

<h1 id="instalacion-de-la-camara">Instalación de la cámara</h1>

1. Conectar la cámara a la Raspberry Pi utilizando el conector CSI.
2. Probar el correcto funcionamiento de la cámara ejecutando el siguiente comando en la terminal:
   ```bash
   libcamera-hello
   ```
3. Si la cámara funciona correctamente, se mostrará una vista previa de la cámara en la pantalla por unos segundos.

*NOTA: En caso de estar interesado en adquirir algún tipo de Raspberry Pi Camera, se debe comprar un cable aparte dependiendo del proveedor, ya que normalmente estas vienen con el cable para la Raspberry Pi 4, el cual no es el mismo.*

<h1 id="multiprocesamiento">Multiprocesamiento</h1>

<h1 id="recursos-externos">Recursos Externos</h1>

1. *Raspberry Pi OS*. (2025). Raspberry Pi. <a id="raspberry-pi-os">https://www.raspberrypi.com/software/</a>
2. *Getting Started*. (2025). Raspberry Pi. <a id="getting-started">https://www.raspberrypi.com/documentation/getting-started/</a>
3. *Raspberry Pi Connect*. (2025). Raspberry Pi. <a id="raspberry-pi-connect">https://www.raspberrypi.com/documentation/remote-access/raspberry-pi-connect.html</a>
4. Python Software Foundation. (2025). *Multiprocessing*. Python documentation. <a id="multiprocessing">https://docs.python.org/3/library/multiprocessing.html</a>
5. Brownlee, J. (28 de julio de 2022). *Use an Event in the Multiprocessing Pool*. SuperFastPython*. <a id="multiprocessing-pool">https://superfastpython.com/multiprocessing-pool/</a>
6. *Camera*. (2025). Raspberry Pi. <a id="camera">https://www.raspberrypi.com/documentation/computers/camera.html</a>
7. Brownlee, J. (21 de noviembre de 2022). *What is a Multiprocessing Manager*. SuperFastPython. <a id="multiprocessing-manager">https://superfastpython.com/multiprocessing-manager/</a>