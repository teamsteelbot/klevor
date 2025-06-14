<h1 id="index">Índice</h1>

1. **[Introducción](#introduccion)**
2. **[Capas](#capas)**
    1. **[Primera Capa](#primera-capa)**
    1. **[Segunda Capa](#segunda-capa)**

 <h1 id="introduccion">Introducción</h1> 
Este es un segundo prototipo de Klevor, donde se le hicieron correcciones esenciales y se agregaron nuevos componentes que explicaremos detalladamente.


<h1 id="capas">Capas</h1>

<h2 id="primera-capa">Primera Capa</h2>

En esta primera capa, al igual que en nuestro primer prototipo, tenemos nuestro sistema motriz, al cual no se le hicieron modificaciones. Este funciona como el sistema mecánico de un automovil, un mecanismo 4x4 de dos diferenciales (sistema de engranajes cubiertos por una carcasa) conectados entre si por un eje transmisor. Nosotros conectamos nuestro motor ([INJORA 48T](../../README.md/#componentes-injora-180-motor-48t)) a un piñón que tiene el eje transmisor, esto hace que los diferenciales giren en un mismo sentido y que por consecuencia, Klevor se mueva.

Una parte fundamental para nuestro robot es su sistema de cruce. Es basado en un mecanismo Ackermann, que consiste en que las dos ruedas están conectadas por una dirección o "sistema de trapecio", esto lo que hace es que, mediante una fuerza que haga el cruce (en este caso nuestro servomotor [INJORA 7kg 2065](../../README.md/#componentes-injora-7kg-2065-micro-servo)) esta dirección se mueva y eso hace girar ambas ruedas en el mismo sentido debido a la geometría y forma de trapecio que tiene la dirección.