@echo Activating virtual environment...
call ./.venv/Scripts/activate

@echo Generating QR codes...
python -m qr

@echo QR codes generation complete.
pause