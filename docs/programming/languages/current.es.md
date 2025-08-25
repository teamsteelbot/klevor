# Lenguajes de Programación Actuales

Muchos robots autónomos, si no es que todos, necesitan de un lenguaje de programación para poder llevar a cabo tareas complejas. En el caso de Klevor, utilizamos un lenguaje principal: Python, y una implementación para la Raspberry Pi Pico 2 WH: CircuitPython.

## Python

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/python.png" alt="Logo de Python" 
width="200">
	<br>
	<i>Logo de Python</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/python.png" alt="Logo de Python" 
class="logo--3rd-party">
    <i>Logo de Python</i>
</div>
mkdocs-only-end -->

Python fue creado por **Guido van Rossum**, un programador holandés que comenzó a trabajar en Python a finales de la década de 1980. La primera versión pública de Python (versión 0.9.0) fue lanzada en febrero de 1991.

Además de esto, Guido mantuvo la autoridad final sobre el desarrollo de Python hasta que se retiró de ese rol en 2018.

Guido concibió Python con varios propósitos clave en mente, influenciado por su experiencia con otros lenguajes como **ABC** y **Modula-3**, principalmente, se enfocaba en crear un lenguaje que fuese tan fácil de entender como el pseudocódigo, para que fuese más accesible para principiantes y además fuese más fácil de mantener para los equipos. Además de esto, Guido diseñó Python de manera que, este fuese un lenguaje bastante versátil, que no estuviese restringido a una sóla rama, sino que pueda ser utilizado en una gran variedad, como:

- Scripting y automatización de tareas.

- Análisis de datos y ciencia de datos.

- Inteligencia Artificial y Machine Learning.

- Desarrollo de software de escritorio.

Python es un lenguaje de programación de alto nivel, este lenguaje cumple muchísimas funciones en general y es uno de los más versátiles. Klevor utiliza Python como lenguaje de programación para tareas como la detección de los obstáculos y el estacionamiento, escaneo 2D de los datos del RPLidar C1 y el control de los dos motores [[1](#python-docs)]. Debido a su sencillez y facilidad de uso, permite a los desarrolladores centrarse en la lógica del programa en lugar de preocuparse por la sintaxis compleja de otros lenguajes.

Python es un lenguaje interpretado, lo que significa que el código se ejecuta línea por línea. Además, Python cuenta con una amplia gama de bibliotecas y módulos que permiten realizar tareas específicas sin necesidad de escribir código desde cero, lo que acelera el proceso de desarrollo.

Cabe destacar que, a pesar de su sencillez, Python es un lenguaje potente y versátil, con soporte a clases, abstracción, herencia, polimorfismo, funciones, módulos, multiprocesamiento, multihilo, programación asíncrona, function overloading, decoradores, y mucho más.

La ventaja principal de Python es la versatilidad, pues no necesitamos administrar cada tarea en un lenguaje de programación distinto, sino que podemos utilizar Python para todo, desde la detección de obstáculos hasta el control de los motores, lo que simplifica el proceso de desarrollo y reduce la complejidad del código.

## Go {:#go}

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/go.png" alt="Logo de Go" 
width="200">
	<br>
	<i>Logo de Go</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/go.png" alt="Logo de Go" 
class="logo--3rd-party">
    <i>Logo de Go</i>
</div>
mkdocs-only-end -->

Go, también conocido como Golang es lenguaje de programación compilado y tipado, diseñado por Robert Griesemer, Rob Pike y Ken Thompson en Google en 2009. La meta principal era crear un lenguaje que solucionara los problemas de otros lenguajes modernos en una era de procesadores de múltiples núcleos, sistemas a gran escala y redes.

Características claves:

- Simplicidad y Legibilidad: La sintaxis de Go es intencionalmente mínima y fácil de aprender. Además de, evitar características complejas presentes en lenguajes como C++ o Java (como la herencia de clases o los genéricos complejos), lo que promueve un código limpio, legible y fácil de mantener. La naturaleza obstinada del lenguaje (por ejemplo, las reglas del formato específicas impuestas por gofmt) garantiza la consistencia del código entre diferentes equipos.

- Concurrencia: Esta es una de las características más potentes y definitorias de Go. Tiene primitivas incorporadas para la concurrencia:

	1. Goroutines: Hilos ligeros y económicos gestionados por el tiempo de ejecución de Go, no por el sistema operativo. Puedes tener miles o incluso millones de ellos ejecutándose al mismo tiempo.

	2. Canales (Channels): Una forma para que las goroutines se comuniquen y sincronicen. La filosofía es "No te comuniques compartiendo memoria; comparte memoria comunicándote". Esto previene problemas comunes de concurrencia.

- Compilación Rápida: Go se compila increíblemente rápido. Esto proporciona una experiencia de desarrollo similar a la de los lenguajes interpretados, donde puedes hacer cambios y ver los resultados casi al instante.

Además de esto, el diseño de Go lo hace especialmente práctico para actividades como:

- Servicios Web y APIs: Su buen manejo de redes y soporte de la concurrencia lo hace una buena opción para construir servidores web y microservicios de alto rendimiento.

- Herramienta de Línea de Comandos: Su rápida compilación y binarios estáticos lo hacen ideal para crear aplicaciones de línea de comandos poderosas que puedan ser distribuidas con facilidad.

- Computación en la Nube: Muchas herramientas de infraestructura en la nube, incluyendo Docker y Kubernetes, están escritos en Go.

En esencia, Go es un lenguaje que prioriza eficiencia, escalabilidad, y facilidad de uso, lo que lo convierte en una opción muy popular para desarrolladores que construyen los sistemas de backend que impulsan la web y nube modernas.

## TinyGo {:#tinygo}

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/tinygo.png" alt="Logo de TinyGo" 
width="200">
	<br>
	<i>Logo de TinyGo</i>
</p>

<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/tinygo.png" alt="Logo de TinyGo" 
class="logo--3rd-party">
    <i>Logo de TinyGo</i>
</div>
mkdocs-only-end -->

TinyGo es una implementación de Go para microcontroladores, como por ejemplo, la Raspberry Pi Pico 2 W H, TinyGo es bastante similar a Go, sin embargo, a diferencia de Go, la cual tiene una infraestructura de compilado exclusiva, está construida sobre la infraestructura de compilado LLVM (Low Level Virtual Machine). Gracias a esta infraestructura TinyGo puede implementar algunas caractesrísticas como: 

- Binarios drásticamente más pequeños: Un programa "¡Hello, World!" en Go estándar puede ocupar varios megabytes, mientras que el mismo programa compilado con TinyGo puede ocupar tan solo unos pocos kilobytes. Esta es la característica más importante para dispositivos con recursos limitados y memoria flash limitada.

- Generación de código eficiente: las optimizaciones avanzadas de LLVM pueden producir un código de máquina altamente eficiente, que a menudo supera a C y C++ en pruebas comparativas específicas.

# Referencias

1. *El tutorial de Python*. (2025). Python Software Foundation. <a id="python-docs" href="https://docs.python.org/es/3/tutorial/">https://docs.python.org/es/3/tutorial/</a>

2. *El tutorial de Go*. (2025). Google. <a id="go-docs" href="https://go.dev/">https://go.dev/</a>