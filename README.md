# Klevor

> [!IMPORTANT]
> If you want to access this content in English, click [**here**](README-en.md)

<p align="center">
    <img src="assets/images/logo/teamsteelbot.png" alt="Logo del Equipo" width="400">
    <br>
    <i>Logo del Equipo</i>
</p>

Bienvenidos al repositorio de Klevor, el robot del Team Steel Bot, que compite en la World Robot Olympiad 2025 en la categoría Futuros Ingenieros. Aquí encontrarás toda la información sobre el robot, incluyendo su código, modelos 3D, esquemas y documentación.

## ¿Cómo acceder a la documentación?

Actualmente, toda la documentación oficial se encuentra tanto en [GitHub Pages](https://klevor.ralvarez.dev), como en el repositorio de [GitHub](https://github.com/teamsteelbot/klevor), recomendamos visualizarla en GitHub Pages, ya que esta documentación fue desarrollada para encajar mejor en este formato. Esta documentación está organizada en varias secciones, cada una de las cuales contiene información específica sobre el robot y su desarrollo.

<p align="center">
	<img src="assets/images/qr/page-url--dark.svg" alt="Código QR de la URL de la página web" width="200">
	<br>
	<i>Código QR de la URL de la página web</i>
</p>

<p align="center">
	<img src="assets/videos/documentation-preview.gif" alt="Preview de la documentación en GitHub Pages" width="500">
	<br>
	<i>Preview de la documentación en GitHub Pages</i>
</p>

## Estructura de la documentación

Esta documentación es bastante extensa, por lo que decidimos dividir los contenidos de esta documentación en múltiples archivos para facilitar la lectura, los cuales están ubicados en la carpeta `docs`; cabe recalcar que, si un archivo termina en `.es.md` está escrito en español, y si termina en `.en.md` está escrito en inglés.

Ahora bien, la estructura de los archivos es la siguiente:

- En la carpeta `assets` se encuentran las imágenes y videos que utilizamos para este `README`.

- En la carpeta `devices` se encuentra todo el código utilizado por Klevor, dividido en dos carpetas, una para la Raspberry Pi 5, y la otra para la Raspberry Pi Pico 2 W.

- En la carpeta `docs`, como ya se ha mencionado, se encuentra todo lo documentado sobre Klevor, dividido en 3 secciones, la electrónica, la mecánica, la programación, además de estas secciones, también contamos con algunos archivos que detallan, por ejemplo, el software utilizado, los "gadgets" o herramientas que utilizamos, cómo nos pueden contactar, y demás, **estos archivos están listados al final del índice**.

- En la carpeta `models` se encuentran todos los modelos de las piezas 3d que fueron impresas para Klevor, esta carpeta está dividida para los planos de las piezas, y el archivo para imprimirlas, además de, estar organizadas por cada prototipo.

- En la carpeta `schemes` están los diagramas de flujo, y los diagramas de conexiones, además de esto, se incluyeron unos diagramas que explican cómo funciona el sistema de comunicación entre los componentes de Klevor y como se procesan en la Raspberry Pi.

- En la carpeta `t-photos` están las fotos del equipo.

- En la carpeta `v-photos` están las fotos de Klevor.

## Índice 

1. **[Sobre Nosotros](docs/about.es.md)**
2. **Electrónica**
	1. Componentes
		1. [Componentes Previos](docs/electronic/components/previous.es.md)
		2. [Componentes Actuales](docs/electronic/components/current.es.md)
		3. [Componentes Futuros](docs/electronic/components/future.es.md)
	2. Diagramas
		1. [Diagramas de Conexiones](docs/electronic/diagrams/wiring.es.md)
3. **Mecánica**
	1. Piezas
		1. Piezas Comunes
			1. [Piezas Comunes Previas](docs/mechanical/parts/common/previous.es.md)
			2. [Piezas Comunes Actuales](docs/mechanical/parts/common/current.es.md)
		2. [Piezas del Prototipo 1](docs/mechanical/parts/prototype1.es.md)
		3. [Piezas del Prototipo 2](docs/mechanical/parts/prototype2.es.md)
		4. [Piezas del Prototipo 3](docs/mechanical/parts/prototype3.es.md)
		5. [Piezas del Prototipo 4](docs/mechanical/parts/prototype4.es.md)
	2. Prototipos
		1. [Prototipo 1](docs/mechanical/prototypes/prototype1.es.md)
		2. [Prototipo 2](docs/mechanical/prototypes/prototype2.es.md)
		3. [Prototipo 3](docs/mechanical/prototypes/prototype3.es.md)
		4. [Prototipo 4](docs/mechanical/prototypes/prototype4.es.md)
4. **Programación**
	1. Lenguajes de Programación
		1. [Lenguajes de Programación Previos](docs/programming/languages/previous.es.md)
		2. [Lenguajes de Programación Actuales](docs/programming/languages/current.es.md)
		3. [Lenguajes de Programación Futuros](docs/programming/languages/future.es.md)
	2. Librerías
		1. Legado:
		   1. [Librerías de CircuitPython](docs/programming/libraries/legacy/circuit-python.es.md)
		2. [Librerías de Python](docs/programming/libraries/python.es.md)
	3. Diagramas
		1. [Diagramas de Flujo](docs/programming/diagrams/flowcharts.es.md)
	4. [Glosario de Términos](docs/programming/glossary.es.md)
	5. Guías
		1. Legado 
			1. [Guía de MicroPython](docs/programming/guides/legacy/micro-python.es.md)
			2. [Guía de CircuitPython](docs/programming/guides/legacy/circuit-python.es.md)
			3. [Guía de la Raspberry Pi Pico 2 W](docs/programming/guides/legacy/raspberry-pi-pico-2w.es.md)
		2. [Guía de MkDocs](docs/programming/guides/mkdocs.es.md)
		3. [Guía de TinyGo](docs/programming/guides/tinygo.es.md)
		4. [Guía de la Raspberry Pi 5](docs/programming/guides/raspberry-pi-5.es.md)
		5. [Guía de la Raspberry Pi Pico 2 W](docs/programming/guides/raspberry-pi-pico-2w.es.md)
		6. [Guía de Detección de Objetos](docs/programming/guides/object-detection.es.md)
5. **[GitHub](docs/github.es.md)**
6. **[Vídeos](docs/videos.es.md)**
7. **[Software](docs/software.es.md)**
8. **[Gadgets](docs/gadgets.es.md)**
9. **[Patrocinadores](docs/sponsors.es.md)**
10. **[Contacto](docs/contact.es.md)**