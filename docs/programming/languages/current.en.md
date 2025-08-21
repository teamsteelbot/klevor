# Current Programming Languages

A lot of autonomous robots, if not all, need a programming language to be able to process complex tasks. In Klevor, we used one main language: Python, and a Python implementation for the Raspberry Pi Pico 2 WH: CircuitPython.

## Python

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/python.png" alt="Python's Logo" 
width="200">
	<br>
	<i>Python's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/python.png" alt="Python's Logo" 
class="logo--3rd-party">
    <i>Python's Logo</i>
</div>
mkdocs-only-end -->


Python was created by **Guido van Rossum**, a dutch programmer that started to work on Python in the late 80's. The first public version (version 0.9.0) was launched in February 1991.

Also, Guido kept the final decision on Python's development until he retired in 2018.

Guido created Python with a lot of different purposes in mind, inspired by his experience on other languages like **ABC** and **Modula-3**, mainly, he focused in creating a language that as easy to understand as pseudocode, to make it accessible for beginners and easy to maintain for computers. Aside from this, Guido designed Python, in a way that it's a versatile language, and not stuck with a single niche use, some of its intended uses are:

- Scripting and task automation.

- Data analysis and data science.

- Artificial Intelligence and Machine Learning.

- Desktop software development.

Python is a high-level programming language, this language has a lot of general functions, and is one of the most versatile. Klevor uses Python as its main language for certain tasks like obstacle detection and parking, 2D scanning from the RPLiDAR C1 data and controlling the motors [[1](#python-docs)]. Due to its simplicity and ease of use, it allows programmers to focus entirely on the programs' logic instead of worrying about the complex sintaxis from other languages.

Python is an interpreted language, which means, that the code is run line by line. Also, Python has a lot of different libraries and modules that allow to execute specific tasks without the need of writing code by scratch, which accelerates the development process.

It is worth mentioning that, aside from its simplicity, Python is still a very powerful and versatile language, supporting classes, 
Cabe destacar que, a pesar de su sencillez, Python es un lenguaje potente y versátil, con soporte a clases, abstracción, herencia, polimorfismo, funciones, módulos, multiprocesamiento, multihilo, programación asíncrona, function overloading, decoradores, y mucho más.

Python's main advantage is, again, its versatility, since we don't need to run every task in a different programming language for each of them, since we can just use Python from everything, like object detection and controlling the motors, which simplifies the developing and reduces the code's complexity.

## CircuitPython

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
width="200">
	<br>
	<i>CircuitPython's Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/circuit-python.png" alt="CircuitPython's Logo" 
class="logo--3rd-party">
    <i>CircuitPython's Logo</i>
</div>
mkdocs-only-end -->

CircuitPython is a MicroPython fork, it was mainly develop by **Adafruit Industries**, a corporation specialized in open-source code and electronics. There's not a clear main developer, like Python or MicroPython does, so the work is mostly attributed to **Limor Fried (Ladyada)**, Adafruit's founder, and her team of programmers.

CircuitPython was launched in 2017. Its main purpose was to have a Python version for microcontrollers that was even more oriented into the education and also, it was beginner-friendly. CircuitPython was specifically designed for learning, quick experimenting and the ease of use for users that don't have or have very little experience with microcontrollers and electronics.

Since the code needs to be stored inside a disk unit that is accessible by USB, it's really easy to edit and update the code without having to use external tools to edit the code, unlike MicroPython, which is built for more general purposes, CircuitPython focuses in providing a direct and robust support for a wide variety of sensors, actuators, and external components, more specifically, the devices sold by Adafruit and its partners. This is made possible by a large amount of libraries and pre-written drivers.

In the same way as MicroPython, CircuitPython is an implementation for Python in microcontrollers, and it's optimized to be used on devices with limited resources, like the Raspberry Pi Pico 2 WH [[2](#circuit-python-docs)].

# References

1. *El tutorial de Python*. (2025). Python Software Foundation. <a id="python-docs" href="https://docs.python.org/es/3/tutorial/">https://docs.python.org/es/3/tutorial/</a>

2. *CircuitPython*. (2025). CircuitPython. <a id="circuit-python-docs" href="https://docs.circuitpython.org/en/latest/README.html">https://docs.circuitpython.org/en/latest/README.html</a>