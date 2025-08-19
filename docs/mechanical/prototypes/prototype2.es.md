# Prototipo 2

Este es un segundo prototipo de Klevor, donde se le hicieron correcciones esenciales y se agregaron nuevos componentes que explicaremos detalladamente.

<!-- github-only-start -->
<table>
	<tbody>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-front-view.png"
alt="Vista delantera del prototipo 2" width="600">
					<br>
					<i>Vista delantera del prototipo 2</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-back-view.png"
alt="Vista trasera del prototipo 2" width="600">
					<br>
					<i>Vista trasera del prototipo 2</i>
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-right-view.png"
alt="Vista derecha del prototipo 2" width="600">
					<br>
					<i>Vista derecha del prototipo 2</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-left-view.png"
alt="Vista izquierda del prototipo 2" width="600">
					<br>
					<i>Vista izquierda del prototipo 2</i>
				</p>
			</td>
		</tr>
		<tr>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-top-view.png"
alt="Vista superior del prototipo 2" width="600">
					<br>
					<i>Vista superior del prototipo 2</i>
				</p>
			</td>
			<td>
				<p align="center">
					<img src="../../assets/images/github/v-photos/prototype2/prototype2-bottom-view.png"
alt="Vista inferior del prototipo 2" width="600">
					<br>
					<i>Vista inferior del prototipo 2</i>
				</p>
			</td>
		</tr>
	</tbody>
</table>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="vehicle-views-container">
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype2/prototype2-front-view.png"
alt="Vista delantera" class="vehicle-view-image">
        <i>Vista delantera</i>
    </div>
    <div class="hcenter"> 
        <img src="/assets/images/github/v-photos/prototype2/prototype2-back-view.png" 
alt="Vista Trasera" class="vehicle-view-image">
        <i>Vista trasera</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype2/prototype2-right-view.png" 
alt="Vista derecha" class="vehicle-view-image">
        <i>Vista derecha</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype2/prototype2-left-view.png" 
alt="Vista izquierda" class="vehicle-view-image">
        <i>Vista izquierda</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype2/prototype2-top-view.png"
alt="Vista superior" class="vehicle-view-image">
        <i>Vista superior</i>
    </div>
    <div class="hcenter">
        <img src="/assets/images/github/v-photos/prototype2/prototype2-bottom-view.png"
alt="Vista inferior" class="vehicle-view-image">
        <i>Vista inferior</i>
    </div>
</div>
mkdocs-only-end -->

## Primera Capa

En esta primera capa, al igual que en nuestro primer prototipo, tenemos nuestro sistema motriz, al cual no se le hicieron modificaciones. Este funciona como el sistema mecánico de un automóvil, un mecanismo 4x4 de dos diferenciales (sistema de engranajes cubiertos por una carcasa) conectados entre sí por un eje transmisor. Nosotros conectamos nuestro motor ([INJORA 48T](../../electronic/components/current.es.md#injora-180-motor-48t)) a un piñón que tiene el eje transmisor, esto hace que los diferenciales giren en un mismo sentido y que por consecuencia, Klevor se mueva.

Una parte fundamental para nuestro robot es su sistema de cruce. Es basado en un mecanismo Ackermann, que consiste en que las dos ruedas están conectadas por una dirección o "sistema de trapecio", esto lo que hace es que, mediante una fuerza que haga el cruce (en este caso nuestro servomotor [INJORA 7 kg 2065](../../electronic/components/current.es.md#injora-7-kg-2065-micro-servo))la dirección se mueva y eso hace girar ambas ruedas al mismo lado, debido a la geometría y forma de trapecio que tiene la dirección, las ruedas no giran con el mismo ángulo, sino que, la rueda interna respecto al cruce gira más que la rueda externa.

Las ruedas para funcionar están conectadas a un muñón de dirección, luego a un "palier" o "semieje" que pasa por dentro del muñón y se junta con la rueda para que esta gire, el palier gira mientras está junto al diferencial.

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/mechanical/ackermann-steering-system.png"
alt="Sistema Ackermann"
width="600">
	<br>
	<i>Sistema Ackermann</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/mechanical/ackermann-steering-system.png" 
alt="Sistema Ackermann" class="mechanical-image">
	<i>Sistema Ackermann</i>
</div>
mkdocs-only-end -->

En este diagrama se ve un ejemplo más claro de cómo funciona este sistema. Describiremos a continuación el significado de cada término:

- **ICR** (Centro Instantáneo de Rotación): Es el punto alrededor del cual el eje delantero está girando.

- **R**: Es el radio del giro del vehículo, medido desde el ICR hasta el centro del eje trasero.

- **L**: Es la distancia entre el eje delantero y el eje trasero de Klevor, o la distancia de nuestro eje transmisor.

- **B**: Es la distancia entre los muñones de dirección (La pieza en la que va la rueda y se conecta a la dirección).

- **a(i)**: Es el ángulo de giro de nuestra rueda interior respecto a la curva.

- **a(o)**: Es el ángulo de nuestra rueda exterior respecto al giro.

Esto ilustra más la geometría de la dirección que permite que las ruedas delanteras giren en ángulos diferentes y a su vez en la misma dirección, consiguiendo así un giro eficiente.

De componentes tiene un giroscopio ([BNO08X](../../electronic/components/current.es.md#9-axis-imu-gyroscope-gy-bno085)) que ayuda al robot a orientarse y así contar el número de vueltas que da, tiene una batería ([URGENEX 7.4 V](../../electronic/components/current.es.md#batería-urgenex-74-v)) que alimenta al [INJORA MB100 20 A mini ESC](../../electronic/components/current.es.md#injora-mb100-20a-mini-esc) que es un regulador de velocidad y a su vez también alimenta el motor [INJORA 48T](../../electronic/components/current.es.md#injora-180-motor-48t) y el servomotor [INJORA 7 kg 2065](../../electronic/components/current.es.md#injora-7-kg-2065-micro-servo).

### ¿Por qué diseñamos así nuestro chasis?

Este chasis es una modificación de la primera capa del primer prototipo de Klevor. Decidimos modificarla por el peso, reduciendo el espacio por componentes que ya no están, esta primera capa también está diseñada con esa forma debido a las piezas de kits que no son modificables, como lo son los diferenciales, los muñones de dirección y el eje transmisor. Así hicimos un espacio a medida para cada componente. Esta también es la razón por la que diseñamos toda la parte de conexión de las ruedas (Ruedas, Semiejes y cajas de diferenciales).

## Segunda Capa

Esta es la capa donde más cambios se hicieron, anteriormente aquí teníamos los sensores ToF (Time of Flight), pero fueron reemplazados por el [RPLidar C1](../../electronic/components/current.es.md#rplidar-c1) un sensor que mediante un láser infrarrojo nos permite detectar distancias de hasta 12 metros en los 360 grados, cosa que corrige el mal funcionamiento de los anteriores sensores, que daban lecturas erróneas y tenían un rango de detección muchísimo más corto. Decidimos colocarlo al revés para que evitar que tenga lecturas erróneas debido a que su láser pasaría por encima de la pared de la pista.

En esta parte superior también está el microcontrolador ([Raspberry Pi Pico 2 WH](../../electronic/components/current.es.md#raspberry-pi-pico-2-wh)) y el microprocesador ([Raspberry Pi 5](../../electronic/components/current.es.md#raspberry-pi-5)), además de la alimentación de los mismos, que es un power bank marca Harvic de 10000 mAh y 22.5 W, este se conecta a la [Raspberry Pi 5](../../electronic/components/current.es.md#raspberry-pi-5-16gb-ram) y a su vez, envía parte del voltaje al RPLIDAR; la Raspberry Pi Pico 2 WH y la [Raspberry Camera Module 3 Wide](../../electronic/components/current.es.md#raspberry-pi-camera-module-3-wide), que es la cámara que nos ayudará a detectar los colores de los bloques en el desafío cerrado.

### ¿Por qué diseñamos así la parte superior?

La parte superior cambió drásticamente en cuanto a diseño, los cambios que hicimos fueron:

- **Crear un espacio en la parte frontal**: Esto lo hicimos para colocar el RPLiDAR con el mayor ángulo de visión posible.

- **Recortar bordes**: Para reducir peso y espacio innecesario.

- **Orificios**: Con el fin de poder conectar cables con la parte de abajo, esto nos da más facilidad a la hora de ensamblar a Klevor.

- **Soporte Raspberry Pi Camera 3**: Luego de probar qué ángulo de colocación era el mejor para la cámara decidimos hacer un soporte completamente fijo. Aunque pensamos cambiarlo más adelante.

Decidimos eliminar también la tercera capa que tenía el primer prototipo, ya que pudimos resumir todos los componentes en una única superficie.

## Lista de Materiales

| Componente                                                                                     | Unidad | Costo por Unidad ($) | Total ($)           |
|------------------------------------------------------------------------------------------------|--------|----------------------|---------------------|
| [Raspberry Pi 5](https://www.canakit.com/raspberry-pi-5-16gb.html)                             | 1      | 120.00               | 120.00              |
| [Raspberry Pi AI HAT+](https://www.canakit.com/raspberry-pi-ai-hat-with-case.html)             | 1      | 139.95               | 139.95              |
| [Micro SD 512GB](https://www.amazon.com/dp/B0C1Q79X3P)                                         | 1      | 54.99                | 54.99               |
| [RPLiDAR C1](https://www.amazon.com/dp/B0CNXLJJ61)                                             | 1      | 75.90                | 75.90               |
| [Raspberry Pi Pico 2WH](https://www.amazon.com/dp/B0F4W9J5CC)                                  | 1      | 14.99                | 14.99               |
| [Raspberry Pi Pico 2WH Breakout Board](https://www.amazon.com/dp/B0BFB53Y2N)                   | 1      | 11.95                | 11.95               |
| [Raspberry Pi Camera Module 3 Wide](https://www.canakit.com/raspberry-pi-camera-module-3.html) | 1      | 37.95                | 37.95               |
| [Case para la Raspberry Pi Camera Module 3](https://www.amazon.com/dp/B09TNG4V55)              | 1      | 5.99                 | 5.99                |
| [Cable para la cámara de la Raspberry Pi 5 de 50cm](https://www.amazon.com/dp/B0D3YWTNF8)      | 1      | 9.79                 | 9.79                |
| [URGENEX 3000mAh Battery](https://www.amazon.com/dp/B0CYNVSN7W)                                | 1      | 26.99                | 26.99               |
| [Giroscopio BNO085](https://www.amazon.com/dp/B0CDGZMLPP)                                      | 1      | 18.59                | 18.59               |
| [INJORA 7Kg 2065 Servo](https://www.amazon.com/dp/B0BLBMVYCW)                                  | 1      | 17.98                | 17.98               |
| [INJORA MB100 20A Brushed Mini ESC](https://www.amazon.com/dp/B0CXT74XV6)                      | 1      | 32.99                | 32.99               |
| [INJORA 180 48T Motor PRO](https://www.amazon.com/es/dp/B0BZ7D63YW/)                           | 1      | 13.98                | 13.98               |
| [Harvic Power Bank PB-607](https://nebulixcolombia.com/products/power-bank-harvic)             | 1      | 17.50 [[1](#note1)]  | 17.50 [[1](#note1)] |
| [Aluminium Alloy Front & Rear Steering Knuckle Hub Base](https://www.amazon.com/dp/B09XW246FQ) | 1      | 17.99                | 17.99               |
| [RC Car Metal Differential Kit 1/18](https://www.amazon.com/dp/B08GHC4D5M)                     | 1      | 21.98                | 21.98               |
| [10PCS Toy Car Wheels 35mm](https://www.amazon.com/dp/B0DQ96VJGL)                              | 1      | 7.99                 | 7.99                |
| [20 rodamientos de bolas MR128-2RS](https://www.amazon.com/dp/B09P1QV29K)                      | 1      | 9.29                 | 9.29                |

**Total para los Componentes: $656.79**

1. El producto está listado con un valor de $70.000,00 COP lo cual es equivalente alrededor de 17,50 dólares estadounidenses a fecha del 21 de julio de 2025.<a id="note1" ></a>