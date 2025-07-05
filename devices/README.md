<h1 id="indice">Índice</h1>

1. **[¿Cómo funciona Klevor durante el Desafío Abierto?](#open-challenge-explanation)**
2. **[Raspberry Pi 5](raspberry-pi-5/README.md)**
3. **[Raspberry Pi Pico 2 WH](raspberry-pi-pico-2w/README.md)**
    1. [CircuitPython](raspberry-pi-pico-2w/src/circuit-python/README.md)
    2. [MicroPython](raspberry-pi-pico-2w/src/micro-python/README.md)

<h2 id="open-challenge-explanation">¿Cómo funciona Klevor durante el Desafío
Abierto?</h2>

Durante el Desafío Abierto, Klevor prioriza cumplir una serie de pasos antes de
dar una vuelta, esto está mejor definido en
el [Diagrama de Flujo](../schemes/flowcharts/open-challenge-flowchart.png).

<p align="center">
    <img src="../schemes/prototype2/open-challenge-flowchart.png" alt="Diagrama de Flujo" width=500>
</p>
<p align="center">
    <i>Diagrama de Flujo del Desafío Abierto</i>
</p>

Como se puede apreciar, Klevor siempre intenta cumplir una serie de pasos:

- Al iniciar la ronda, Klevor avanza hasta que detecte que la pared esté a 60cm
  de distancia o menos al frente, para poder empezar a girar asi que, empieza a
  comparar con el [RPLiDAR C1](../../../../README.md/#componentes-rplidar-c1)
  con los ángulos que están a su izquierda y su derecha (por ejemplo un promedio
  de los ángulos de 175° a 185° para saber la distancia por la cual está
  separado por la pared a la izquierda) para saber hacia dónde girar.
- Mientras está girando, empieza a leer los datos del giroscopio, cuando detecte
  que su orientación ha cambiado al menos 90° con respecto a como inició a
  girar, empieza a avanzar hacia adelante, sumándole 1 a su contador de giros,
  en caso contrario, es decir, que no ha girado 90°, simplemente sigue girando.
- Tras completar los 12 giros, Klevor simplemente avanza hasta que detecte que
  la distancia al frente sea de alrededor de 1.25m, tras esto simplemente para.