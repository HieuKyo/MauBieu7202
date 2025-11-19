@echo off
REM =====================================================
REM Quick Setup - Minimal steps to get running
REM =====================================================

title WordGen - Quick Setup

echo Installing dependencies (including WhiteNoise for static files)...

REM Check if packages folder exists for offline installation
if exist "packages" (
    echo Found local packages folder - installing offline...
    pip install --no-index --find-links=packages -r requirements.txt
) else (
    pip install -r requirements.txt
)

echo.
echo Setting up database...
python manage.py migrate

echo.
echo Collecting static files...
echo This will copy CSS, JS, images to staticfiles folder...
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
