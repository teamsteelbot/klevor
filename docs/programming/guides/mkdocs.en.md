# MkDocs Guide

<!-- github-only-start -->
<p align="center">
	<img src="../../assets/images/logo/mkdocs.png" alt="MkDocs' Logo" 
width="200">
	<br>
	<i>MkDocs' Logo</i>
</p>
<!-- github-only-end -->

<!-- mkdocs-only-start
<div class="hcenter">
    <img src="/assets/images/logo/mkdocs.png" alt="MkDocs' Logo" 
class="logo--3rd-party">
    <i>MkDocs' Logo</i>
</div>
mkdocs-only-end -->

In this section we present a guide to install Mkdocs and serving documentation made with the library, a static documentation tool that allows to generate websites from Markdown files.

## Installation

To install MkDocs, you need to have `Python` and `pip` installed in your system. Also, it is needed to install all of the libraries' dependencies. To simplify the installation process, we created a `requirements.txt` which contains all of the project's dependencies

You can create a Python virtual environment, install MkDocs and the project's dependencies by executing this command in the terminal:

- If the operating system is Windows:

```cmd
python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
```
- If the operating system is Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Serve Documentation

Once you have installed MkDocs and the project's dependencies, you can serve the documentation locally by executing the following command in the terminal:

```bash
mkdocs serve
```

> [!IMPORTANT]
> If you want to serve the documentation from another terminal, it's necessary to activate Python's virtual environment again, because MkDocs depends on the dependencies installed on the virtual environment. You can do this with this command:
> - If the operating system is Windows:
> ```cmd
> .env\Scripts\activate
> ```
> 
> - If the operating system is Linux or macOS:
> ```bash
> source .venv/bin/activate
> ```

However, if you want to simplify the process, simply execute the `serve.bat` file in Windows or `serve.sh` in Linux or macOS, which will activate the virtual environment and serve the documentation automatically.

## Deployment

To deploy the documentation in GitHub Pages, use the following command:

```bash
mkdocs gh-deploy
```

> [!NOTE]
> This command will create a branch named `gh-pages` in your GitHub repository and will deploy the documentation on that branch. Make sure your repository is configured to use GitHub Pages from the `gh-pages` branch.

> [!IMPORTANT]
> This command will only work if the repository you want to create the branch on, is **not** Team Steel Bot's official repository, basically, it must be a fork of this repository to be able to deploy GitHub Pages, this is because, users external to the project don't have the permissions necessary to do any kind of modification to the aforementioned repository.

However, to simplify the deployment process, you can execute the `deploy.bat` file in Windows or `deploy.sh` in Linux or macOS, which will deploy the documentation automatically. In this project, this `.bat`or `.sh` will deploy the documentation to said branch both to the official public remote repository and also our internal developping repository.