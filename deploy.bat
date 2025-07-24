@echo Activating virtual environment...
call ./.venv/Scripts/activate

@echo Update the PDF...
python -m pdf

@echo Deploying MkDocs site to remote...
mkdocs gh-deploy --remote-name dev

@echo Deployment complete.
pause