@echo off
start microsoft-edge:http://localhost:8000/
cd C:\priceapp
python manage.py runserver --insecure
cmd /k