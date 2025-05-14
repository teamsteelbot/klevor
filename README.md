# Índice
- ## 1.[ Introducción](#introducción)  
- ## 2.[ Componentes](#componentes)
    - [ Raspberry Pi 5](#raspberry-pi-5)
    - [ Raspberry Pi Camera Module 3 Wide](#raspberry-pi-camera-module-3-wide)
    - [ Raspberry Pi AI HAT+ (26 TOPS)](#raspberry-pi-ai-hat-26-tops)
    - [ Raspberry Pi Pico 2 WH](#raspberry-pi-pico-2-wh)
    - [ RPLIDAR C1](#rplidar-c1)
    - [ Shargeek Storm 2](#shargeek-storm-2)
    - [ INJORA 180 Motor 48T](#injora-180-motor-48t)
    - [ INJORA MB100 20A mini ESC](#injora-mb100-20a-mini-esc)
    - [ URGENEX 7.4V Battery](#urgenex-74v-battery)
    - [ INJORA 7KG 2065 Micro Servo](#injora-7kg-2065-micro-servo)
- ## 3.[ Diagramas y esquemas](#schemes/README.md)
    - ### 3.1 [ Diagrama de conexiones](#schemes/connection-diagram.jpg)
    - ### 3.2 [ Esquema de decisiones](#schemes/flowchart.jpg)
- ## 4.[ Código](#src)
- ## 5. [ Fotos del equipo](#t-photos)
- ## 6. [ Fotos de Klevor](#v-photos)
- ## 7. [ Vídeos](#video)

# Introducción

Este es el repositorio del Team Steelbot, compitiendo en la World Robot Olympiad 2025, en la categoría Futuros Ingenieros. Representando al Colegio Salto Ángel en Maracaibo, Estado Zulia. Actualmente este equipo está conformado por 3 miembros:

Ramón Álvarez, 19 años

Otto Piñero, 16 años

Sebastián Álvarez, 15 años


`models` contiene todos los archivos en 3D que se utilizaron para poder construir a nuestro robot (Klevor)

`schemes` contiene todos los esquemas y diagramas de todas las conexiones de nuestro robot (Klevor)

`src` contiene todo el código el cual fue utilizado para poder controlar este robot de manera autónoma.

`t-photos` contiene 2 fotos del equipo

`v-photos` contiene 6 fotos de Klevor (Una por cada cara)

`video` contiene 2 vídeos de Klevor en la pista, tanto en el Desafío Abierto como en el Desafío Cerrado.

# Componentes

A continuación, está la descripción de todos los componentes principales de Klevor (mencionados en el índice), además de incluirse una lista con algunos componentes recomendados.

## Raspberry Pi 5 (16GB RAM)

[![Raspberry Pi 5](https://i.postimg.cc/wxDfLJkj/8713-a-1-removebg-preview.png)](https://postimg.cc/dDtjKhXb)

Equipada con un procesador ARM Cortex-A76 de 64 bits a 2.4Ghz. La Raspberry Pi 5 es nuestro controlador principal de elección, decidimos usar a la Raspberry Pi 5 debido a múltiples factores, entre ellos:

- Compatibilidad: Existen muchos componentes de Klevor (como el Camera Module 3) que a su vez pertenecen al ecosistema Raspberry, lo que hace que implementarlos a la Raspberry Pi 5 no requiera tanto esfuerzo.

- Potencia: La Raspberry Pi 5 es uno de los controladores más potentes actualmente, gracias a esto, funciones demandantes como lo es el procesamiento de imágenes en tiempo real, son fácilmente realizables por una Raspberry Pi 5.

- Portabilidad: La Raspberry Pi 5 destaca entre los controladores ya que no es una computadora bastante pesada, apenas llegando a los 60g, hace que incorporarlo a Klevor sea una opción prácticamente segura.

- Fuente: https://www.tiendatec.es/raspberry-pi/gama-raspberry-pi/2149-raspberry-pi-5-16gb-8gb-4gb-2gb-modelo-b.html

## Raspberry Pi Camera Module 3 Wide

[![Raspberry Pi Camera Module 3 Wide](https://i.postimg.cc/LXr7mxTv/RPI-CAM3-W-c-800x800-1-removebg-preview.png)](https://postimg.cc/N9kb47Zr)

La Raspberry Pi Camera Module 3 Wide es nuestra elección de preferencia, como los demás componentes Raspberry, ésta se destaca por ser bastante ligera y pórtatil ya que, pues es una cámara bastante pequeña, midiendo apenas 25mm × 24mm × 12.4 mm y pesando 4 gramos, sin perder absolutamente ni una pizca de eficiencia, ya que puede grabar a 480p120, ahora bien, deicidimos utilizar la versión Wide por su campo de visión horizontal de 102 grados, ya que nos permite tener un rango de visión óptimo para poder detectar todos los obstáculos de la pista.

- Fuente: https://www.geekfactory.mx/producto/raspberry-pi-camera-module-3/

## Raspberry Pi AI HAT+ (26 TOPS)

[![Raspberry Pi AI HAT+](https://i.postimg.cc/6399NRt6/raspberry-pi-ai-hat-raspberry-pi-71328528531841-removebg-preview.png)](https://postimg.cc/HJhGwrrF)

Si bien la Raspberry Pi 5 es capaz de procesar imágenes en tiempo real, tuvimos en cuenta que necesitaba un poco más de poder, por lo cual decidimos incorporar el AI HAT+ a la Raspberry Pi 5 para poder alcanzar el nivel de procesamiento necesario. 

El Raspberry Pi AI HAT+ tiene dos versiones, una de 13 Trillones de Operaciones por Segundo (TOPS) y otra de 26 TOPS, como se menciona en el índice, Klevor posee un Raspberry Pi AI HAT+ de 26 TOPS, gracias a este procesador de imágenes, Klevor puede analizar hasta 30 imágenes por segundo con una resolución de 640x640

Fuente: https://www.kubii.com/es/tarjetas-integradas/4343-kit-ai-ai-hat-raspberry-pi-3272496319608.html

## Raspberry Pi Pico 2 WH

[![Raspberry Pi Pico 2 WH](https://i.postimg.cc/JzvDmp2r/raspberry-pi-pico-2-w-raspberry-pi-sc1634-1146616007-removebg-preview.png)](https://postimg.cc/LJk633Sw)

Construido sobre el chip RP235x, la Raspberry Pi Pico 2 es el microcontrolador de motores por excelencia de Klevor, además de ser un microcontrolador ligero y pequeño, este chip permite una fácil integración con el resto de los componentes Raspberry.

Además de ofrecer una frecuencia de procesamiento de 150Mhz, superior a varios microcontroladores de similar tamaño, como, por ejemplo el Arduino Nano el cual cuenta con una frecuencia de procesamiento de 20Mhz.

- Fuente: https://www.kubii.com/es/microcontroladores/4377-raspberry-pi-pico-2-2w-2h-2wh-3272496319394.html

## RPLiDAR C1

[![RPLiDAR C1](https://i.postimg.cc/02wVPSzs/slamtec-rplidar-c1-360-laser-scanner-12m-removebg-preview.png)](https://postimg.cc/crdRcr79)

El RPLiDAR C1 es un escáner de rango láser de 360 grados, el cual puede detectar superficies que están hasta 12 metros de distancia, su punto ciego es de tan sólo 5 centímetros alrededor del mismo, todos estos factores hacen que el RPLiDAR C1 sea una gran opción para poder guíar a Klevor por la pista.

Este RPLiDAR C1 permite a Klevor poder identificar que tan cerca o que tan lejos está de las paredes de la pista, además de poder identificar la ubicación de los obstaculos mucho antes que la cámara y poder ajustarse a tiempo.

- Fuente: https://www.robotshop.com/es/products/escaner-laser-dtof-360-slamtec-rplidar-c1?qd=3ec3808f4c3dd74dab521269d23d2fb2

## Shargeek Storm 2

[![Shargeek Storm 2](https://i.postimg.cc/fTcgYXDv/shargeek-100-power-bank-removebg-preview.png)](https://postimg.cc/0bNfsz66)

El Shargeek Storm 2 es un Power Bank, con múltiples características interesantes como:

- 25600mAh de almacenamiento
- Salida ajustable de hasta 100W
- Pantalla integrada IPS
- Carga de 0% a 100% en tan sólo 1 hora y media.

Todos estos factores hacen que sea una opción perfecta para alimentar un controlador potente como lo es la Raspberry Pi 5.

El único factor negativo de este Power Bank que hace que no suene tan perfecto son sus especifícaciones, puesto que son:


| **Especificaciones**                          ||
|-----------------------------------------|--------------|
| Largo                          | 150.8mm            |
| Alto                            | 58.9mm            |
| Ancho            | 45.9mm            |
| Peso                          | 579g            |

Estos factores hacen que sea un componente un tanto díficil de incorporar a Klevor, sin embargo hay maneras de navegar a través de estos problemas, con un manejo óptimo de peso y medidas

- Fuente: https://www.amazon.es/Shargeek-port%C3%A1til-cargador-transparente-pantalla/dp/B09NY8GN76

## INJORA 180 Motor 48T

[![INJORA 180 Motor 48T](https://i.postimg.cc/fyTjX3K8/IMG-4570-1800x1800-removebg-preview.png)](https://postimg.cc/ZB2dz5XN)

EL INJORA 180 Motor 48T es un motor diseñado para carros controlados por radio, ya que estos carros suelen tener un peso y medidas similares a las de Klevor, decidimos que este motor sería una buena incorporación. Debido a su tamaño compacto, bajo voltaje (necesitando apenas 7.4v), y bajo peso, 

- Fuente: https://www.amazon.es/INJORA-Cepillado-Inoxidable-JST-PH2-0-Ascent-18/dp/B0D97YNMLG?ref_=ast_sto_dp

## INJORA MB100 20A mini ESC

[![INJORA MB100 mini ESC](https://i.postimg.cc/4yq7dnF7/DSC07300-1-1800x1800-3a89d5de-363f-4693-9ab8-815393072006-removebg-preview.png)](https://postimg.cc/y3hYp6Ks)

El INJORA MB100 20A mini ESC es un controlador de velocidad, normalmente éste se usa en conjunto con el INJORA 180 Motor 48T, éste permite la conexión entre el INJORA 180 Motor 48T y la Raspberry Pi Pico 2.

- Fuente: https://www.amazon.es/INJORA-MB100-Brushed-Actualizaci%C3%B3n-Crawler/dp/B0CXT74XV6?ref_=ast_sto_dp


## URGENEX 7.4V Battery

[![URGENEX 7.4V Battery](https://i.postimg.cc/25ybNPwX/71r3-PDycx-LL-AC-SL1500-1-removebg-preview.png)](https://postimg.cc/Z9kKrsXr)

La URGENEX 7.4V Battery es nuestra segunda batería la cual cumple la única función de alimentar al INJORA 180 Motor 48T, además de esto es una batería recargable lo que lo convierte en una opción sólida para poder alimentar el motor principal.

Si bien cualquier batería de 7.4v funcionaría perfectamente para poder utilizar al INJORA 180 Motor 48T, decidimos utilizar a la URGENEX 7.4v Battery por su capacidad de 3000mAh, la cual nos permite asegurarnos un tiempo prologado de práctica.

- Fuente: https://www.amazon.com/URGENEX-Bater%C3%ADa-enchufe-recargable-velocidad/dp/B0CYNVSN7W?ref_=ast_sto_dp

## INJORA 7Kg 2065 Micro Servo

[![INJORA Micro Servo](https://i.postimg.cc/Qt5MXsWS/61d-MNIVpk-YL-AC-SX300-SY300-QL70-FMwebp-removebg-preview.png)](https://postimg.cc/HcYm2qz7)

El INJORA 7KG 2065 Micro Servo es el motor encargado de controlar la dirección de Klevor, decidimos utilizar este modelo debido a su reducido tamaño y peso, además de una precisión más que suficiente para poder manejar a Klevor.

- Fuente: https://www.amazon.com/digital-impermeable-voltaje-Sub-Micro-Crawler/dp/B0BLBMVYCW?ref_=ast_sto_dp