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

Una vez que hayas instalado MkDocs y las dependencias del proyecto, puedes
servir la documentación localmente ejecutando el siguiente comando en la
terminal:

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