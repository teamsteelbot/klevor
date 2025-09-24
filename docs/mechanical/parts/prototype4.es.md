# Prototipo 4 {:#prototype4}

## Chasis {:#Chassis}

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/github/models/plans/prototype4/chassis-prototype4-plan.png" alt="Chasis" width="200" class="mechanical-image">
	<br>
	<i>Chasis</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
	<img src="../../assets/images/github/models/plans/prototype4/chassis-prototype4-plan.png" alt="Chasis" 
class="mechanical-image">
	<i>Chasis</i>
</div>
mkdocs-only-end -->

En este prototipo, decidimos hacer un solo chasis que sirva como base para todos los componentes. Este cambio fue posible porque a diferencia de los modelos anteriores, ya no necesitamos el sistema de reducción de RPM, un sistema que antes ocupaba bastante espacio.

El objetivo principal de este nuevo chasis era mejorar el funcionamiento del sistema motriz. Las nuevas ruedas que usamos son 30mm más grandes en diámetro, lo que representaba un problema, si solamente las colocábamos, el robot completo se elevaría. Esto sería un gran inconveniente para el RPLiDAR, ya que si su altura aumenta demasiado, podría no detectar los obstáculos que están en la pista, para evitar este problema, diseñamos el chasis con una base que tiene cuatro puntos elevados específicamente en las esquinas. De esta manera, las ruedas se colocan en estos puntos más altos, mientras que el resto de los componentes, incluido el RPLidar, se mantienen a una altura baja.

Además de resolver el problema de la altura, este diseño especial de la base tiene otro beneficio clave, permite que las ruedas tengan un mayor ángulo de giro. Con esta mejora, el robot tiene una ventaja con respecto a los prototipos anteriores, lo que le da una gran ventaja en la pista.

## Base del Servomotor

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/github/models/plans/prototype4/servo-base-plan.png" alt="Servo base" width="200" class="mechanical-image">
	<br>
	<i>Base del servomotor</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
	<img src="../../assets/images/github/models/plans/prototype4/servo-base-plan.png" alt="Servo base" 
class="mechanical-image">
	<i>Base del servomotor</i>
</div>
mkdocs-only-end -->

Esta pieza fue diseñada para colocarse directamente en el servomotor, y posteriormente ser fijado en el chasis, lo hicimos así porque necesitabamos que el servomotor estuviera en un nivel bajo, para que al hacer los cruces no chocara con el eje de transmisión, y tuviera el espacio suficiente como para poder aprovechar al máximo el nuevo ángulo de giro que tiene Klevor.
