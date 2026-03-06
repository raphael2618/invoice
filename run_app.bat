@echo off
echo ========================================
echo   DEMARRAGE FACTURE AI - SESSION 2026
echo ========================================
echo 1. Verification de l'environnement...
pip install -r requirements.txt
echo 2. Verification de la base de donnees...
python manage.py migrate
echo 3. Lancement du serveur Django...
start http://127.0.0.1:8000/
python manage.py runserver
pause