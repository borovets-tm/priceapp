@echo off
start microsoft-edge:http://localhost:8000/
cd C:\priceapp
venv/Scripts/activate.ps1
python manage.py runserver
cmd /k