@echo Activating virtual environment...
call ./.venv/Scripts/activate

@echo Deploying MkDocs site to main origin...
mkdocs gh-deploy --remote-name main

@echo Deployment complete.
pause