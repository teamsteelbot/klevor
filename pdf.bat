@echo Activating virtual environment...
call ./.venv/Scripts/activate

@echo Generating PDF...
python -m pdf

@echo PDF generation complete.
pause