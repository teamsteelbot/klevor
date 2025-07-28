# Guía de WeasyPrint {:#weasyprint-guide}

Para la presente documentación, decidimos también permitir la visualización de la misma en formato PDF, para que puedas descargarla y consultarla sin conexión a Internet. Para ello, utilizamos una herramienta llamada WeasyPrint, la cual es capaz de convertir documentos HTML y CSS en archivos PDF.

## Instalación de WeasyPrint {:#installation}

Esta guía para instalar WeasyPrint está basada en la documentación oficial de WeasyPrint, la cual puedes encontrar en su sitio web: [WeasyPrint](https://doc.courtbouillon.org/weasyprint).

!!! important
	Cabe destacar que, para el momento que lees esta guía, el enfoque de la misma es para el sistema operativo de Windows, sin embargo, WeasyPrint también es compatible con otros sistemas operativos como Linux y macOS.

Primero, debemos asegurarnos de tener instalado Python en nuestro sistema. Puedes descargar la última versión de Python desde su sitio oficial: [Python](https://www.python.org/downloads/).

Una vez que tengas Python instalado, verifica tener instalado MSYS2, el cual es un entorno de desarrollo que proporciona herramientas y bibliotecas necesarias para compilar y ejecutar aplicaciones en Windows. Puedes descargarlo desde su sitio oficial: [MSYS2](https://www.msys2.org/).

Luego, abre una terminal de MSYS2 y ejecuta los siguientes comandos para instalar las dependencias necesarias:

```shell
pacman -S mingw-w64-ucrt-x86_64-gtk3
pacman -S mingw-w64-ucrt-x86_64-python-gobject
pacman -S mingw-w64-x86_64-pango
```

!!! note
	El primer comando instala GTK 3, que es necesario para la renderización de gráficos, el segundo comando instala las bindings de Python para GObject, que son necesarias para interactuar con GTK, y el tercer comando instala Pango, que es una biblioteca para el manejo de texto y tipografía.

Después de instalar las dependencias, puedes instalar WeasyPrint con el ejecutable oficial en [WeasyPrint Releases](https://github.com/Kozea/WeasyPrint/releases).

Si instalaste las dependencias del entorno virtual de Python a través del `requirements.txt`, ya estás listo para usar WeasyPrint. En el caso contrario, activa tu entorno virtual de Python y ejecuta el siguiente comando para instalar WeasyPrint:

```shell
pip install weasyprint
```

Listo, ahora tienes WeasyPrint instalado en tu sistema y puedes utilizarlo para generar documentos PDF a partir de archivos HTML y CSS.

Para verificar que WeasyPrint se ha instalado correctamente, puedes ejecutar el siguiente comando en la terminal:

```shell
python -m weasyprint --info
```

Esto debería mostrarte información sobre la versión de WeasyPrint instalada y las dependencias que se están utilizando. Si ves esta información, significa que WeasyPrint se ha instalado correctamente y está listo para usarse.