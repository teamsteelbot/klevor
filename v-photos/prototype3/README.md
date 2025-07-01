<h1 id="index">Índice</h1>

1. **[Introducción](#introduccion)**
2. **[Actualizaciones](#introduccion)**
3. **[Capas](#capas)**
    1. **[Capa Inferior](#capa-inferior)**
    1. **[Capa Superior](#capa-superior)**

 <h1 id="introduccion">Introducción</h1> 
En esta carpeta explicaremos minuciosamente ¿cómo? y por qué hicimos un tercer prototipo de Klevor, detallando los componentes agregados y los que fueron removidos.


<h1 id="Actualizaciones">Actualizaciones</h1>

-  Implementación de la [SHARGEEK STORM 2](../../README.md/#componentes-shargeek-storm-2)
- Rediseño de la capa inferior
- Rediseño de la capa superior

<h2 id="capa-inferior">Capa Inferior</h2>

A este primer nivel del robot únicamente se le hicieron modificaciones en cuanto a pesaje. Lo que significa que su sistema motriz continúa exactamente igual al del prototipo anterior ([prototype2](../prototype2/README.md)). 

Redujimos significativamente el tamaño de esta capa, ajustándola a los componentes. Esto nos permitió reducir 10 gramos su peso, un avance crucial. Gracias a esto, ahora Klevor cumple con el peso reglamentario, ya que en pruebas anteriores excedió los 1510g. 

<h2 id="capa-supeior">Capa Superior</h2>

Esta fué la capa que tuvo más cambios, adjuntaremos una vista superior de esta y la que estaba previamente a modo de comparación, para que se note más la diferencia.

Se puede apreciar con claridad el drástico cambio que tuvo la parte superior de Klevor, donde reemplazamos la capa anterior por un soporte nuevo, hecho específicamente para que se acople la Shargeek Storm 2, sobre esta misma base, y encima de este powerbank, se colocó estratégicamente la [Raspberry Pi 5](../../README.md/#componentes-raspberry-pi-5).

Adicionalmente, aprovechamos la estructura y ubicación del [RPLidar C1](../../README.md/#componentes-rplidar-c1) para usarlo de soporte sin interferir en su función, al este estar colocado al revés, nos permite colocar en la parte superior la [Raspberry Pi Pico 2](../../README.md/#componentes-raspberry-pi-pico-2-wh), y en la parte posterior de este la [Raspberry Cam Module 3 Wide](../../README.md/#componentes-raspberry-pi-camera-module-3-wide). 

Esto ayudó enormemente a solucionar nuestro problema con el peso, ya que esta modificación nos ahorró el soporte impreso de todos los componentes antes mencionados. En total, pudimos pasar de tener una capa de 42g a una de tan solo 18g, lo que se traduce en un Klevor que cumple con el peso reglamentario, alcanzando un peso total de __g.