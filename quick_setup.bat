@echo off
REM =====================================================
REM Quick Setup - Minimal steps to get running
REM =====================================================

title WordGen - Quick Setup

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setting up database...
python manage.py migrate

echo.
echo Creating placeholder static files...
if not exist "templates_app\static\vendor\bootstrap\css" mkdir templates_app\static\vendor\bootstrap\css
if not exist "templates_app\static\vendor\bootstrap\js" mkdir templates_app\static\vendor\bootstrap\js
if not exist "templates_app\static\vendor\bootstrap-icons\css" mkdir templates_app\static\vendor\bootstrap-icons\css
if not exist "templates_app\static\vendor\bootstrap-icons\fonts" mkdir templates_app\static\vendor\bootstrap-icons\fonts

echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo =====================================================
echo Quick Setup Complete!
echo =====================================================
echo.
echo NEXT STEPS:
echo 1. Download Bootstrap (optional but recommended):
echo    download_bootstrap_files.bat
echo.
echo 2. Start the server:
echo    start_server.bat
echo.
echo 3. Create admin user:
echo    python manage.py createsuperuser
echo.
pause
