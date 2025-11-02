@echo off
REM =====================================================
REM WordGen Django Application - Waitress Server Launcher
REM =====================================================
REM
REM This batch file starts the Django application using
REM Waitress WSGI server on Windows.
REM
REM Prerequisites:
REM   - Python 3.7 or higher installed
REM   - Virtual environment activated (recommended)
REM   - Dependencies installed (pip install -r requirements.txt)
REM
REM =====================================================

title WordGen Server - Waitress

echo.
echo =====================================================
echo WordGen Django Application Server
echo =====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [2/3] Activating virtual environment...
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo [2/3] No virtual environment found (venv folder)
    echo Running with system Python...
    echo.
    echo RECOMMENDATION: Create a virtual environment:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
)
echo.

REM Check if waitress is installed
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Waitress is not installed
    echo.
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [3/3] Starting Waitress server...
echo.
echo =====================================================
echo Server is starting...
echo =====================================================
echo.

REM Run the waitress server
python run_waitress.py

REM If server stopped, show message
echo.
echo =====================================================
echo Server has stopped
echo =====================================================
pause
