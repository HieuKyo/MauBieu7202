@echo off
REM =====================================================
REM First-Time Setup Script for WordGen Application
REM =====================================================
REM
REM This script sets up everything needed to run the
REM application for the first time on Windows.
REM
REM =====================================================

title WordGen - First Time Setup

echo.
echo =====================================================
echo WordGen Application - First Time Setup
echo =====================================================
echo.
echo This script will:
echo   1. Check Python installation
echo   2. Create virtual environment (optional)
echo   3. Install all dependencies
echo   4. Download Bootstrap CSS/JS files
echo   5. Collect static files
echo   6. Setup database
echo.
pause

REM Check Python
echo.
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Ask about virtual environment
echo [2/6] Virtual Environment Setup
echo.
set /p USE_VENV="Create a virtual environment? (Recommended) [Y/n]: "
if /i "%USE_VENV%"=="n" goto :skip_venv

if exist "venv" (
    echo Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo WARNING: Failed to create virtual environment
        echo Continuing with system Python...
    ) else (
        echo Virtual environment created successfully
    )
)

if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

:skip_venv
echo.

REM Install dependencies
echo [3/6] Installing dependencies from requirements.txt...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully
echo.

REM Download Bootstrap files
echo [4/6] Downloading Bootstrap CSS/JS files...
echo.
set /p DOWNLOAD="Do you have internet connection to download Bootstrap? [Y/n]: "
if /i "%DOWNLOAD%"=="n" goto :skip_download

echo Downloading Bootstrap files...
call download_bootstrap_files.bat
if errorlevel 1 (
    echo.
    echo WARNING: Failed to download Bootstrap files
    echo You can download them manually later
    echo See STATIC_FILES_SETUP.md for instructions
    echo.
    pause
)

:skip_download
echo.

REM Collect static files
echo [5/6] Collecting static files...
echo.
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo WARNING: collectstatic failed
    echo This is OK for now, will try again after database setup
)
echo.

REM Setup database
echo [6/6] Setting up database...
echo.
echo Running migrations...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo ERROR: Database migration failed
    pause
    exit /b 1
)
echo.

REM Create superuser
echo.
echo =====================================================
echo Creating Admin User
echo =====================================================
echo.
set /p CREATE_ADMIN="Create an admin user now? [Y/n]: "
if /i "%CREATE_ADMIN%"=="n" goto :skip_admin

echo.
echo Please enter admin credentials:
python manage.py createsuperuser
if errorlevel 1 (
    echo WARNING: Failed to create superuser
    echo You can create it later with: python manage.py createsuperuser
)

:skip_admin
echo.

REM Retry collectstatic after database is ready
echo Collecting static files (retry)...
python manage.py collectstatic --noinput
echo.

REM Success
echo =====================================================
echo Setup Complete!
echo =====================================================
echo.
echo Your WordGen application is ready to use!
echo.
echo To start the server:
echo   1. Run: start_server.bat
echo   2. Open browser: http://localhost:8000
echo.
echo To access admin panel:
echo   - URL: http://localhost:8000/admin
echo   - Use the admin credentials you just created
echo.
echo For help and documentation:
echo   - WINDOWS_SETUP.md: Windows setup guide
echo   - STATIC_FILES_SETUP.md: Static files guide
echo   - README.md: General documentation
echo.
pause

echo.
set /p START_NOW="Start the server now? [Y/n]: "
if /i "%START_NOW%"=="n" goto :end

echo.
echo Starting server...
start_server.bat

:end
