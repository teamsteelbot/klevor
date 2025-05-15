<h1 id="index">Índice</h1>

1. **[Introducción](#introduccion)**  
2. **[Estructura de archivos](#estructura-de-archivos)**
3. **[Componentes](#componentes)**
   1. [Raspberry Pi 5](#componentes-raspberry-pi-5)
   2. [Raspberry Pi Camera Module 3 Wide](#componentes-raspberry-pi-camera-module-3-wide)
   3. [Raspberry Pi AI HAT+ (26 TOPS)](#componentes-raspberry-pi-ai-hat-26-tops)
   4. [Raspberry Pi Pico 2 WH](#componentes-raspberry-pi-pico-2-wh) 
   5. [RPLIDAR C1](#componentes-rplidar-c1) 
   6. [Shargeek Storm 2](#componentes-shargeek-storm-2) 
   7. [INJORA 180 Motor 48T](#componentes-injora-180-motor-48t)
   8. [INJORA MB100 20A mini ESC](#componentes-injora-mb100-20a-mini-esc) 
   9. [URGENEX 7.4V Battery](#componentes-urgenex-74v-battery) 
   10. [INJORA 7KG 2065 Micro Servo](#componentes-injora-7kg-2065-micro-servo) 
4. **[Modelos 3D](models/README.md)**
5. **[Diagramas y esquemas](schemes/README.md)**
   1. [Diagrama de conexiones](#schemes/connection-diagram.jpg)
   2. [ Esquema de decisiones](#schemes/flowchart.jpg)
6. **[Código](src/README.md)**
7. **[Fotos del equipo](t-photos/README.md)**
8. **[Fotos de Klevor](v-photos/README.md)**
9. **[Vídeos](video/README.md)**
10. **[Recursos Externos](#recursos-externos)**

<h1 id="introduccion">Introducción</h1>

Este es el repositorio del Team Steelbot, compitiendo en la World Robot Olympiad 2025, en la categoría Futuros Ingenieros. Representando al Colegio Salto Ángel en Maracaibo, Estado Zulia, Venezuela. 

Actualmente, este equipo está conformado por 3 miembros:

- Ramón Álvarez, 19 años. [ralvarezdev](https://github.com/ralvarezdev).
- Otto Piñero, 16 años. [Ottorafaelpg](https://github.com/Ottorafaelpg).
- Sebastián Álvarez, 15 años. [salvarezdev](https://github.com/salvarezdev).

<h1 id="estructura-de-archivos">Estructura de archivos</h1>

- `models` contiene todos los archivos en 3D que se utilizaron para poder construir a nuestro robot (Klevor)

- `schemes` contiene todos los esquemas y diagramas de todas las conexiones de nuestro robot (Klevor)

- `src` contiene todo el código el cual fue utilizado para poder controlar este robot de manera autónoma.

- `t-photos` contiene las fotos del equipo

- `v-photos` contiene las fotos de Klevor

- `video` contiene los vídeos de Klevor en la pista, tanto en el Desafío Abierto como en el Desafío con Obstáculos.

<h1 id="componentes">Componentes</h1>

A continuación, está la descripción de todos los componentes principales de Klevor (mencionados en el índice).

<h2 id="componentes-raspberry-pi-5">Raspberry Pi 5 (16GB RAM)</h2>

[![Raspberry Pi 5](https://i.postimg.cc/wxDfLJkj/8713-a-1-removebg-preview.png)](https://postimg.cc/dDtjKhXb)

Equipada con un procesador ARM Cortex-A76 de 64 bits a 2.4 Ghz [[1](#raspberry-pi-5-16gb-8gb-4gb-2gb-tiendatec)]. La Raspberry Pi 5 es nuestro controlador principal de elección, decidimos usar a la Raspberry Pi 5 debido a múltiples factores, entre ellos:

- **Compatibilidad**: Existen muchos componentes de Klevor (como la Camera Module 3) que a su vez pertenecen al ecosistema Raspberry, lo que hace que implementarlos a la Raspberry Pi 5 no requiera tanto esfuerzo.

- **Potencia**: La Raspberry Pi 5 es uno de los controladores más potentes actualmente, gracias a esto, funciones demandantes como lo es el procesamiento de imágenes en tiempo real, son fácilmente realizables por una Raspberry Pi 5.

- **Portabilidad**: La Raspberry Pi 5 destaca entre los controladores, ya que no es una computadora bastante pesada, apenas llegando a los 60g, hace que incorporarlo a Klevor sea una opción prácticamente segura.

<h2 id="componentes-raspberry-pi-camera-module-3-wide">Raspberry Pi Camera Module 3 Wide</h2>

[![Raspberry Pi Camera Module 3](https://i.postimg.cc/fTf0cWFd/raspberry-pi-camera-module-3-raspberry-pi-sc0872-43251879182531-700x-removebg-preview.png)](https://postimg.cc/D8mZFh7f)

La Raspberry Pi Camera Module 3 Wide es nuestra elección de preferencia, como los demás componentes Raspberry, esta se destaca por ser bastante ligera y portátil, ya que, pues es una cámara bastante pequeña, midiendo apenas 25 mm × 24 mm × 12.4 mm y pesando 4 gramos, sin perder absolutamente ni una pizca de eficiencia, porque puede grabar a 1536 × 864p120, ahora bien, decidimos utilizar la versión Wide por su campo de visión horizontal de 102 grados [[2](#raspberry-pi-camera-module-3-geek-factory)], porque nos permite tener un rango de visión óptimo para poder detectar todos los obstáculos de la pista.

<h2 id="componentes-raspberry-pi-ai-hat-26-tops">Raspberry Pi AI HAT+ (26 TOPS)</h2>

[![Raspberry Pi AI HAT](https://i.postimg.cc/6399NRt6/raspberry-pi-ai-hat-raspberry-pi-71328528531841-removebg-preview.png)](https://postimg.cc/HJhGwrrF)

Si bien la Raspberry Pi 5 es capaz de procesar imágenes en tiempo real, tuvimos en cuenta que necesitaba un poco más de poder, por lo cual decidimos incorporar la AI HAT+ a la Raspberry Pi 5 para poder alcanzar el nivel de procesamiento necesario. 

El Raspberry Pi AI HAT+ tiene dos versiones, una de 13 Trillones de Operaciones por Segundo (TOPS) y otra de 26 TOPS [[3](#kit-ai-ai-hat-plus-raspberry-pi-kubii)]. Como se menciona en el índice, Klevor posee un Raspberry Pi AI HAT+ de 26 TOPS, gracias a este procesador de imágenes, Klevor puede analizar hasta 30 imágenes por segundo con una resolución de 640 px × 640 px.

<h2 id="componentes-raspberry-pi-pico-2-wh">Raspberry Pi Pico 2 WH</h2>

[![Raspberry Pi Pico 2 WH](https://i.postimg.cc/JzvDmp2r/raspberry-pi-pico-2-w-raspberry-pi-sc1634-1146616007-removebg-preview.png)](https://postimg.cc/LJk633Sw)

Construido sobre el chip RP235x [[4](#raspberry-pi-pico-2-2w-2h-2wh-kubii)], la Raspberry Pi Pico 2 es el microcontrolador de motores por excelencia de Klevor, además de ser un microcontrolador ligero y pequeño, este chip permite una fácil integración con el resto de los componentes Raspberry.

Además de ofrecer una frecuencia de procesamiento de 150 Mhz, superior a varios microcontroladores de similar tamaño, como, por ejemplo, el Arduino Nano el cual cuenta con una frecuencia de procesamiento de 20 Mhz.

<h2 id="componentes-rplidar-c1">RPLiDAR C1</h2>

[![RPLiDAR C1](https://i.postimg.cc/02wVPSzs/slamtec-rplidar-c1-360-laser-scanner-12m-removebg-preview.png)](https://postimg.cc/crdRcr79)

El RPLiDAR C1 es un escáner de rango láser de 360 grados, el cual puede detectar superficies que están hasta 12 metros de distancia, su punto ciego es de tan solo 5 centímetros alrededor del mismo [[5](#rplidar-c1-robot-shop)], todos estos factores hacen que el RPLiDAR C1 sea una gran opción para poder guíar a Klevor por la pista.

Este RPLiDAR C1 permite a Klevor poder identificar que tan cerca o que tan lejos está de las paredes de la pista, además de poder identificar la ubicación de los obstáculos mucho antes que la cámara y poder ajustarse a tiempo.

<h2 id="componentes-shargeek-storm-2">Shargeek Storm 2</h2>

[![Shargeek Storm 2](https://i.postimg.cc/fTcgYXDv/shargeek-100-power-bank-removebg-preview.png)](https://postimg.cc/0bNfsz66)

El Shargeek Storm 2 es un Power Bank, con múltiples características interesantes [[6](#shargeek-storm-2-amazon)] como:

- 25600 mAh de almacenamiento.
- Salida ajustable de hasta 100 W.
- Pantalla integrada IPS.
- Carga de 0% a 100% en tan solo 1 hora y media.

Todos estos factores hacen que sea una opción perfecta para alimentar un controlador potente como lo es la Raspberry Pi 5.

El único factor negativo de este Power Bank que hace que no suene tan perfecto son sus especifícaciones, puesto que son:


| **Medida** | **Valor** |
|------------|-----------|
| Largo      | 150.8 mm  |
| Alto       | 58.9 mm   |
| Ancho      | 45.9 mm   |
| Peso       | 579 g     |

Estos factores hacen que sea un componente un tanto difícil de incorporar a Klevor; sin embargo, hay maneras de navegar a través de estos problemas, con un manejo óptimo de peso y medidas.

<h2 id="componentes-injora-180-motor-48t">INJORA 180 Motor 48T</h2>

[![INJORA 180 Motor 48T](https://i.postimg.cc/fyTjX3K8/IMG-4570-1800x1800-removebg-preview.png)](https://postimg.cc/ZB2dz5XN)

El INJORA 180 Motor 48T es un motor diseñado para carros controlados por radio, ya que estos carros suelen tener un peso y medidas similares a las de Klevor, decidimos que este motor sería una buena incorporación. Debido a su tamaño compacto, bajo voltaje (necesitando apenas 7.4v), y bajo peso [[7](#injora-180-48t-amazon)].

<h2 id="componentes-injora-mb100-20a-mini-esc">INJORA MB100 20A mini ESC</h2>

[![INJORA MB100 mini ESC](https://i.postimg.cc/4yq7dnF7/DSC07300-1-1800x1800-3a89d5de-363f-4693-9ab8-815393072006-removebg-preview.png)](https://postimg.cc/y3hYp6Ks)

El INJORA MB100 20A mini ESC es un controlador de velocidad [[8](#injora-mb100-r80-amazon)], normalmente este se usa en conjunto con el INJORA 180 Motor 48T, este permite la conexión entre el INJORA 180 Motor 48T y la Raspberry Pi Pico 2.

<h2 id="componentes-urgenex-74v-battery">URGENEX 7.4V Battery</h2>

[![URGENEX 7.4V Battery](https://i.postimg.cc/25ybNPwX/71r3-PDycx-LL-AC-SL1500-1-removebg-preview.png)](https://postimg.cc/Z9kKrsXr)

La URGENEX 7.4 V Battery es nuestra segunda batería la cual cumple la única función de alimentar al INJORA 180 Motor 48T, además de esto es una batería recargable lo que lo convierte en una opción sólida para poder alimentar el motor principal.

Si bien cualquier batería de 7.4 V funcionaría perfectamente para poder utilizar al INJORA 180 Motor 48T, decidimos utilizar a la URGENEX 7.4v Battery por su capacidad de 3000 mAh [[9](#urgenex-3000-mah-amazon)], la cual nos permite asegurarnos un tiempo prologado de práctica.

<h2 id="componentes-injora-7kg-2065-micro-servo">INJORA 7Kg 2065 Micro Servo</h2>

[![INJORA Micro Servo](https://i.postimg.cc/Qt5MXsWS/61d-MNIVpk-YL-AC-SX300-SY300-QL70-FMwebp-removebg-preview.png)](https://postimg.cc/HcYm2qz7)

El INJORA 7KG 2065 Micro Servo es el motor encargado de controlar la dirección de Klevor, decidimos utilizar este modelo debido a su reducido tamaño y peso, además de una precisión más que suficiente para poder manejar a Klevor.

<h1 id="recursos-externos">Recursos Externos</h1>

1. *RASPBERRY PI 5 16GB, 8GB, 4GB, 2GB – MODELO B*. (2025). tiendatec. <a i="raspberry-pi-5-16gb-8gb-4gb-2gb-tiendatec">https://www.tiendatec.es/raspberry-pi/gama-raspberry-pi/2149-raspberry-pi-5-16gb-8gb-4gb-2gb-modelo-b.html</a>

2. *Raspberry Pi camera module 3 (standard | wide | NOIR)*. (2025). GeekFactory. <a i="raspberry-pi-camera-module-3-geek-factory">https://www.geekfactory.mx/producto/raspberry-pi-camera-module-3/</a>
   
3. *Kit AI, AI HAT+ Raspberry Pi*. (2025). Kubii. <a i="kit-ai-ai-hat-plus-raspberry-pi-kubii">https://www.kubii.com/es/tarjetas-integradas/4343-kit-ai-ai-hat-raspberry-pi-3272496319608.html</a>

4. *Raspberry Pi Pico 2, 2W, 2H, 2WH*. (2025). Kubii. <a i="raspberry-pi-pico-2-2w-2h-2wh-kubii">https://www.kubii.com/es/microcontroladores/4377-raspberry-pi-pico-2-2w-2h-2wh-3272496319394.html</a>

5. *Escáner Láser DTOF 360° SLAMTEC RPLIDAR C1*. (2025). RobotShop. <a i="rplidar-c1-robot-shop">https://www.robotshop.com/es/products/escaner-laser-dtof-360-slamtec-rplidar-c1?qd=3ec3808f4c3dd74dab521269d23d2fb2</a>

6. *Shargeek Storm 2, banco de energía para portátil de 100 W, cargador portátil de 25600 mAh, primer banco de energía transparente del mundo con pantalla IPS, Samsung Galaxy, MacBook y más*. (2025). Amazon. <a i="shargeek-storm-2-amazon">https://www.amazon.es/Shargeek-port%C3%A1til-cargador-transparente-pantalla/dp/B09NY8GN76</a>

7. *INJORA Motor Cepillado 180 48T con Piñón de Acero Inoxidable, Conector JST-PH2.0 para Upgrade 1/18 RC Crawler Redcat Ascent-18*. (2025). Amazon. <a i="injora-180-48t-amazon">https://www.amazon.es/INJORA-Cepillado-Inoxidable-JST-PH2-0-Ascent-18/dp/B0D97YNMLG?ref_=ast_sto_dp</a>

8. *INJORA MB100-R80 20A Brushed Mini ESC con Motor 180 de 48T para Actualización TRX4M 1/18 RC Crawler*. (2025). Amazon. <a i="injora-mb100-r80-amazon">https://www.amazon.es/INJORA-MB100-Brushed-Actualizaci%C3%B3n-Crawler/dp/B0CXT74XV6?ref_=ast_sto_dp</a>

9. *URGENEX 3000mAh 7.4 V Li-ion Battery with Dean-Style T Plug 2S Rechargeable RC Battery Fit for WLtoys 4WD High Speed RC Cars and Most 1/10, 1/12, 1/16 Scale RC Cars Trucks with 7.4V Battery Charger*. (2025). Amazon. <a i="urgenex-3000-mah-amazon">https://www.amazon.com/URGENEX-Bater%C3%ADa-enchufe-recargable-velocidad/dp/B0CYNVSN7W?ref_=ast_sto_dp</a>

10. *INJORA 7KG 2065 Digital Servo Waterproof High Voltage Sub-Micro Shift Servo for TRX4 TRX6 SCX10 III 1/10 RC Crawler Car,1PCS*. (2025). Amazon. <a i="injora-7kg-2065-amazon">https://www.amazon.com/digital-impermeable-voltaje-Sub-Micro-Crawler/dp/B0BLBMVYCW?ref_=ast_sto_dp</a>