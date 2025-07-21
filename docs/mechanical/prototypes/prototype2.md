# Prototipo 2 {:#prototype2}

Este es un segundo prototipo de Klevor, donde se le hicieron correcciones esenciales y se agregaron nuevos componentes que explicaremos detalladamente.

<div class="vehicle-views-container">
    <div class="center">
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-front-view.png"
alt="Vista delantera" class="vehicle-view-image">
        <i>Vista delantera</i>
    </div>
    <div class="center"> 
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-back-view.png" 
alt="Vista Trasera" class="vehicle-view-image">
        <i>Vista trasera</i>
    </div>
    <div class="center">
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-right-view.png" 
alt="Vista derecha" class="vehicle-view-image">
        <i>Vista derecha</i>
    </div>
    <div class="center">
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-left-view.png" 
alt="Vista izquierda" class="vehicle-view-image">
        <i>Vista izquierda</i>
    </div>
    <div class="center">
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-top-view.png"
alt="Vista superior" class="vehicle-view-image">
        <i>Vista superior</i>
    </div>
    <div class="center">
        <img src="../../assets/images/github/v-photos/prototype2/prototype2-bottom-view.png"
alt="Vista inferior" class="vehicle-view-image">
        <i>Vista inferior</i>
    </div>
</div>

## Primera Capa {:#first-layer}

En esta primera capa, al igual que en nuestro primer prototipo, tenemos nuestro sistema motriz, al cual no se le hicieron modificaciones. Este funciona como el sistema mecánico de un automóvil, un mecanismo 4x4 de dos diferenciales (sistema de engranajes cubiertos por una carcasa) conectados entre sí por un eje transmisor. Nosotros conectamos nuestro motor ([INJORA 48T](../../electronic/components/current.md#injora-180-motor-48t)) a un piñón que tiene el eje transmisor, esto hace que los diferenciales giren en un mismo sentido y que por consecuencia, Klevor se mueva.

Una parte fundamental para nuestro robot es su sistema de cruce. Es basado en un mecanismo Ackermann, que consiste en que las dos ruedas están conectadas por una dirección o "sistema de trapecio", esto lo que hace es que, mediante una fuerza que haga el cruce (en este caso nuestro servomotor [INJORA 7 kg 2065](../../electronic/components/current.md#injora-7kg-2065-micro-servo))la dirección se mueva y eso hace girar ambas ruedas al mismo lado, debido a la geometría y forma de trapecio que tiene la dirección, las ruedas no giran con el mismo ángulo, sino que, la rueda interna respecto al cruce gira más que la rueda externa.

Las ruedas para funcionar están conectadas a un muñón de dirección, luego a un
"palier" o "semieje" que pasa por dentro del muñón y se junta con la rueda para que esta gire, el palier gira mientras está junto al diferencial.

<div class="center">
    <img src="../../assets/images/mechanical/ackermann-steering-system.png" 
alt="Sistema Ackermann" class="mechanical-image">
</div>

En este diagrama se ve un ejemplo más claro de cómo funciona este sistema. Describiremos a continuación el significado de cada término:

- **ICR** (Centro Instantáneo de Rotación): Es el punto alrededor del cual el eje delantero está girando.

- **R**: Es el radio del giro del vehículo, medido desde el ICR hasta el centro del eje trasero.

- **L**: Es la distancia entre el eje delantero y el eje trasero de Klevor, o la distancia de nuestro eje transmisor.

- **B**: Es la distancia entre los muñones de dirección (La pieza en la que va la rueda y se conecta a la dirección).

- **a(i)**: Es el ángulo de giro de nuestra rueda interior respecto a la curva.

- **a(o)**: Es el ángulo de nuestra rueda exterior respecto al giro.

Esto ilustra más la geometría de la dirección que permite que las ruedas delanteras giren en ángulos diferentes y a su vez en la misma dirección, consiguiendo así un giro eficiente.

Nuestro motor ([INJORA 48T](../../electronic/components/current.md#injora-180-motor-48t)) es el que se encarga de mover gran parte del sistema motriz, pero presentó una falla al no tener el suficiente torque para mover el robot. Por esto tomamos la decisión de hacer un sistema reductor de RPM, consta de un piñón que está en la boquilla del motor y que se conecta a 2 piñones más junto al engranaje principal del eje transmisor, reduciendo así la velocidad del motor, pero añadiendo más fuerza al mismo.

Seguiremos explicando esta primera capa de nuestro robot. De componentes tiene un giroscopio ([BNO08X](../../electronic/components/current.md#gyroscope-gy-bno085)) que ayuda al robot a orientarse y así contar el número de vueltas que da, tiene una batería ([URGENEX 7.4 V](../../electronic/components/current.md#urgenex-7-4v-battery)) que alimenta al [INJORA MB100 20 A mini ESC](../../electronic/components/current.md#injora-mb100-20a-mini-esc) que es un regulador de velocidad y a su vez también alimenta el motor INJORA 48T y el servomotor INJORA 7 kg 2065.

### ¿Por qué diseñamos así nuestro chasis? {:#why-design-chassis}

Este chasis es una modificación de la primera capa del primer prototipo de Klevor. Decidimos modificarla por el peso, reduciendo el espacio por componentes que ya no están, esta primera capa también está diseñada con esa forma debido a las piezas de kits que no son modificables, como lo son los diferenciales, los muñones de dirección y el eje transmisor. Así hicimos un espacio a medida para cada componente. Esta también es la razón por la que diseñamos toda la parte de conexión de las ruedas (Ruedas, Semiejes y cajas de diferenciales).

## Segunda Capa {:#second-layer}

Esta es la capa donde más cambios se hicieron, anteriormente aquí teníamos los sensores ToF (Time of Flight), pero fueron reemplazados por el [RPLidar C1](../../electronic/components/current.md#rplidar-c1) un sensor que mediante un láser infrarrojo nos permite detectar distancias de hasta 12 metros en los 360 grados, cosa que corrige el mal funcionamiento de los anteriores sensores, que daban lecturas erróneas y tenían un rango de detección muchísimo más corto. Decidimos colocarlo al revés para que evitar que tenga lecturas erróneas debido a que su láser pasaría por encima de la pared de la pista.

En esta parte superior también está el microcontrolador ([Raspberry Pi Pico 2 WH](../../electronic/components/current.md#raspberry-pi-pico-2-wh)) y el microprocesador ([Raspberry Pi 5](../../electronic/components/current.md#raspberry-pi-5)), además de la alimentación de los mismos, que es un power bank marca Harvic de 10000 mAh y 22.5 W, este se conecta a la Raspberry Pi 5 y a su vez, envía parte del voltaje al RPLIDAR; la Raspberry Pi Pico 2 WH y la [Raspberry Camera Module 3 Wide](../../electronic/components/current.md#raspberry-pi-camera-module-3-wide), que es la cámara que nos ayudará a detectar los colores de los bloques en el desafío cerrado.

### ¿Por qué diseñamos así la parte superior? {:#why-design-top}

La parte superior cambió drásticamente en cuanto a diseño, los cambios que hicimos fueron:

- **Crear un espacio en la parte frontal**: Esto lo hicimos para colocar el RPLIDAR con el mayor ángulo de visión posible.

- **Recortar bordes**: Para reducir peso y espacio innecesario.

- **Orificios**: Con el fin de poder conectar cables con la parte de abajo, esto nos da más facilidad a la hora de ensamblar a Klevor.

- **Soporte Raspberry Pi Camera 3**: Luego de probar qué ángulo de colocación era el mejor para la cámara decidimos hacer un soporte completamente fijo. Aunque pensamos cambiarlo más adelante.

Decidimos eliminar también la tercera capa que tenía el primer prototipo, ya que pudimos resumir todos los componentes en una única superficie.

## Lista de Materiales {:#materials-list}

| Componente                                             | Unidad | Costo por Unidad ($) | Total ($) |
|--------------------------------------------------------|--------|----------------------|-----------|
| Raspberry Pi 5                                         | 1      | 120.00               | 120.00    |
| Raspberry Pi AI HAT+                                   | 1      | 139.95               | 139.95    |
| Micro SD 512GB                                         | 1      | 29.99                | 29.99     |
| RPLiDAR C1                                             | 1      | 75.90                | 75.90     |
| Raspberry Pi Camera Module 3                           | 1      | 35.00                | 35.00     |
| Case para la Raspberry Pi Camera Module 3              | 1      | 5.99                 | 5.99      |
| Cable para la cámara de la Raspberry Pi 5 de 50cm      | 1      | 9.79                 | 9.79      |
| URGENEX 3000mAh Battery                                | 1      | 26.99                | 26.99     |
| Giroscopio BNO085                                      | 1      | 18.59                | 18.59     |
| INJORA 7Kg 2065 Servo                                  | 1      | 17.98                | 17.98     |
| INJORA MB100 20A Brushed Mini ESC                      | 1      | 32.99                | 32.99     |
| INJORA 180 48T Motor PRO                               | 1      | 13.99                | 13.99     |
| Raspberry Pi Pico 2WH                                  | 1      | 14.99                | 14.99     |
| Raspberry Pi Pico 2WH Breakout Board                   | 1      | 14.94                | 14.94     |
| Harvic Power Bank PB-607                               | 1      | 17.50                | 17.50     |
| Aluminium Alloy Front & Rear Steering Knuckle Hub Base | 1      | 18.38                | 18.38     |
| RC Car Metal Differential Kit 1/18                     | 1      | 23.28                | 23.28     |
| 10PCS Toy Car Wheels 35mm                              | 1      | 7.99                 | 7.99      |
| Metal Upgrade Drive Shaft Driving Gear                 | 1      | 26.99                | 26.99     |

**Total para los Componentes: $651.23**