# MkDocs {:#mkdocs}

<div class="center">
    <img src="../../assets/images/logo/mkdocs.png" 
alt="Logo de MkDocs" class="logo--3rd-party">
    <i>Logo de MkDocs</i>
</div>

En la presente sección se presenta una guía para instalar MkDocs y servir la documentación desarrollada con la misma librería, una herramienta de documentación estática que permite generar sitios web a partir de archivos Markdown.

## Instalación {:#installation}

Para instalar MkDocs, es necesario tener `Python` y `pip` instalados en tu sistema. Así mismo, requerimos de todas las dependencias del proyecto. Para simplificar el proceso de instalación, hemos creado un archivo `requirements.txt` que contiene todas las dependencias necesarias para el proyecto.

Puedes crear un entorno virtual de Python, instalar MkDocs y las dependencias del proyecto ejecutando el siguiente comando en la terminal:

- Si el sistema operativo es Windows:
```cmd
python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
```

- Si el sistema operativo es Linux o macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Servir la Documentación {:#serve-documentation}

Una vez que hayas instalado MkDocs y las dependencias del proyecto, puedes servir la documentación localmente ejecutando el siguiente comando en la terminal:

```bash
mkdocs serve
```

> [!IMPORTANT]
> En el caso de querer servir la documentación desde otra terminal, es necesario activar el entorno virtual de Python nuevamente, ya que MkDocs depende de las dependencias instaladas en el entorno virtual de Python. Esto se puede realizar con el siguiente comando:
> - Si el sistema operativo es Windows:
> ```cmd
> .venv\Scripts\activate
> ```
> - Si el sistema operativo es Linux o macOS:
> ```bash
> source .venv/bin/activate
> ```

Aunque si deseas simplificar el proceso, puedes ejecutar directamente el archivo `serve.bat` en Windows o `serve.sh` en Linux o macOS, que se encargará de activar el entorno virtual y servir la documentación automáticamente.

## Despliegue {:#deployment}


Para desplegar la documentación en GitHub Pages, puedes utilizar el siguiente comando:

```bash
mkdocs gh-deploy
```

> [!NOTE]
> Este comando creará una rama `gh-pages` en tu repositorio de GitHub y desplegará la documentación en esa rama. Asegúrate de que tu repositorio esté configurado para utilizar GitHub Pages desde la rama `gh-pages`.

> [!IMPORTANT]
> Este comando solamente servirá si el repositorio al que quieres crear la rama no es el repositorio oficial del Team Steel Bot, es decir, un fork del mismo, ya que los usuarios externos al proyecto no tienen los permisos necesarios para realizar cualquier tipo de modificación en el repositorio antes mencionado.

Sin embargo, para simplificar el proceso de despliegue, puedes ejecutar directamente el archivo `deploy.bat` en Windows o `deploy.sh` en Linux o macOS, que se encargará de desplegar la documentación automáticamente. En nuestro caso, este `.bat` o `.sh` se encargará de desplegar la documentación a dicha rama tanto para el repositorio remoto oficial público como para nuestro repositorio de desarrollo interno.