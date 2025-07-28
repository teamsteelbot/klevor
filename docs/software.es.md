# Software {:#software}

Aquí se encuentran todos los programas que utilizamos como Team Steel Bot para poder desarrollar a Klevor.

## Programación {:#programming}

### Label Studio {:#label-studio}

<div class="hcenter">
    <img src="/assets/images/logo/label-studio.png" alt="Logo de Label Studio" 
class="logo--3rd-party">
    <i>Logo de Label Studio</i>
</div>

[Label Studio](https://labelstud.io/) es un programa open-source (de código abierto) el cual nos permite preparar las fotos para poder entrenar una Inteligencia Artificial para la detección de objetos. Este programa no se limita a esta funcionalidad, ya que además permite asignar etiquetas a una gran variedad de tipos, como texto, audio, imágenes, vídeos, series de tiempo, multi-dominio, entre otros.

En el caso de Klevor, este programa se utilizó para [remarcar](programming/guides/object-detection.es.md#model-creation) dónde están los bloques en las fotos de entrenamiento para que así, después de dejar el modelo entrenando un rato (ya sea de manera local o en la nube), este pueda reconocer los bloques por sí solo.

### Google Colab {:#google-colab}

<div class="hcenter">
    <img src="/assets/images/logo/google-colab.png" alt="Logo de Google Colab" 
class="logo--3rd-party">
    <i>Logo de Google Colab</i>
</div>

Como se mencionó anteriormente, un modelo de Inteligencia Artificial debe ser entrenado, ya sea de manera local o en la nube, pues Google Colab cumple exactamente está función. [Google Colab](https://colab.research.google.com/) es un servicio que te permite ejecutar código en Python en tu propio navegador web, además de brindar acceso gratuito a GPU y TPU que puedan ser utilizadas en línea, así como también la posibilidad de utilizar Google Drive para almacenar los archivos generados por el entrenamiento del modelo.

En el caso de Klevor, utilizamos esta plataforma para poder [entrenar el modelo YOLO](programming/guides/object-detection.es.md#model-training) que se mencionó anteriormente, mediante el uso de una GPU Nvidia A100, la cual es una de las más potentes del mercado, lo que nos permitió entrenar el modelo en un tiempo relativamente corto por un costo muy bajo.

### Visual Studio Code {:#visual-studio-code}

<div class="hcenter">
    <img src="/assets/images/logo/visual-studio-code.png" alt="Logo de Visual Studio Code" class="logo--3rd-party">
    <i>Logo de Visual Studio Code</i>
</div>

[Visual Studio Code](https://code.visualstudio.com/) es un programa de desarrollo de software con terminal integrado, soporte nativo de Git, soporte a casi todos los lenguajes de programación, un sin número de extensiones y totalmente personalizable.

En el caso de Klevor, nosotros utilizamos Visual Studio Code principalmente en la Raspberry Pi 5, como en los computadores del equipo menos potentes, ya que este programa es más ligero que otros programas de desarrollo, como PyCharm, y permite trabajar con múltiples lenguajes de programación, lo que lo hace ideal para el desarrollo de Klevor.

### PyCharm {:#pycharm}

<div class="hcenter">
    <img src="/assets/images/logo/pycharm.png" alt="Logo de PyCharm" 
class="logo--3rd-party">
    <i>Logo de PyCharm</i>
</div>

[PyCharm](https://www.jetbrains.com/pycharm/) es otro programa de desarrollo de software; sin embargo, este presenta muchas más funcionalidades que Visual Studio Code, con el detalle que este programa necesita de una licencia, mientras que una Visual Studio Code no necesita de una licencia. Esto es debido a que PyCharm es un programa de desarrollo integrado (IDE) para Python, lo que significa que está diseñado específicamente para trabajar con este lenguaje de programación, mientras que Visual Studio Code es un editor de código fuente más general, por lo tanto, PyCharm ofrece características más avanzadas y específicas para Python, como la depuración avanzada, la refactorización de código, la integración con bases de datos, entre otras.

En nuestro caso, empleamos PyCharm para verificar y depurar con más profundida el código de Klevor, ya que este programa cuenta con herramientas avanzadas de depuración y análisis de código, lo que nos permitió identificar y corregir errores en el código de manera más eficiente.

### Thonny {:#thonny}

<div class="hcenter">
    <img src="/assets/images/logo/thonny.png" alt="Logo de Thonny" 
class="logo--3rd-party">
    <i>Logo de Thonny</i>
</div>

[Thonny](https://thonny.org/) es otro programa de desarrollo integrado, utilizado principalmente para poder ejecutar código directamente en la Raspberry Pi Pico 2 W, tanto para probar, como para utilizarlo en los Desafíos. Cabe destacar que, a diferencia de las anteriores soluciones, Thonny es un IDE diseñado específicamente para principiantes en Python, lo que lo hace más fácil de usar y entender para aquellos que están empezando a aprender el lenguaje. Además, Thonny tiene una interfaz más simple y menos abrumadora que PyCharm o Visual Studio Code, así como integra funcionalidades específicas para trabajar con microcontroladores, en nuestro caso, la Raspberry Pi Pico 2 W.

## Diseño {:#design}

### Canva {:#canva}

<div class="hcenter">
    <img src="/assets/images/logo/canva.png" alt="Logo de Canva" 
class="logo--3rd-party">
    <i>Logo de Canva</i>
</div>

[Canva](https://www.canva.com/) es una plataforma de diseño en línea, la cual te permite diseñar cualquier cosa en 2D, decidimos utilizar Canva principalmente para la elaboración de los diagramas de conexiones y diagramas de flujo, como una solución rápida y efectiva para la documentación, sin embargo, notamos que nuestros diagramas eran muy complejos y tomaban mucho tiempo de hacer, por lo que cambiamos a otras soluciones en línea.

### Mermaid {:#mermaid}

<div class="hcenter">
    <img src="/assets/images/logo/mermaid.png" alt="Logo de Mermaid" 
class="logo--3rd-party">
    <i>Logo de Mermaid</i>
</div>

Después de no lograr los resultados esperados con Canva, decidimos optar por [Mermaid](https://www.mermaidchart.com/), el cual es un programa open-source (de código abierto) que se especializa principalmente en la creación de diagramas con texto, con un sistema parecido a Markdown, con el objetivo de elaborar los diagramas de flujo.

### Draw.io {:#draw-io}

<div class="hcenter">
    <img src="/assets/images/logo/draw.io.png" alt="Logo de Draw.io" 
class="logo--3rd-party">
    <i>Logo de Draw.io</i>
</div>

[Draw.io](https://www.drawio.com/) es una página web que permite la creación de diagramas en línea, con la posibilidad de que varios usuarios lo puedan modificar al mismo tiempo, con una interfaz muy similar a la de Microsoft Visio, pero con la ventaja de que es completamente gratuita y open-source (de código abierto). Decidimos utilizar Draw.io para la creación de los diagramas de conexiones y esquemas eléctricos, ya que nos permitió crear diagramas más complejos y detallados, además de ser más fácil de usar que Canva.

### Fusion 360 {:#fusion-360}

<div class="hcenter">
    <img src="/assets/images/logo/fusion-360.png" alt="Logo de Fusion 360" 
class="logo--3rd-party">
    <i>Logo de Fusion 360</i>
</div>

[Fusion 360](https://www.autodesk.com/products/fusion-360/overview) es un programa de diseño 3D de Autodesk, con el cual pudimos diseñar las piezas en 3D y exportarlas al formato `.stl` para imprimir con mucha facilidad. Es muy versátil para dibujantes, ingenieros, fabricantes y para la creación de equipos, ya que tiene funciones de renderizado, diseño, pesaje de componentes, diseño de PCB, simulaciones, modelado de forma libre, etc.

Elegimos este programa porque es una solución "todo en uno" que combina el diseño, la fabricación, la ingeniería y el diseño de PCB, todo esto asistido por computadora, lo que hace todo mucho más cómodo.

## Planificación {:#planning}

### Jira {:#jira}

<div class="hcenter">
    <img src="/assets/images/logo/jira.png" alt="Logo de Jira" 
class="logo--3rd-party">
    <i>Logo de Jira</i>
</div>

[Jira](https://www.atlassian.com/software/jira) es una página web cuyo objetivo es la de organizar las tareas de un equipo de trabajo y asignarles una prioridad, básicamente es una página de organización de trabajo.

En nuestro caso, el uso de Jira nos permitió mantener el desarrollo de Klevor a un ritmo constante, ya que cada miembro del equipo tenía asignadas tareas específicas y un plazo para completarlas, lo que nos permitió avanzar de manera más eficiente y organizada.