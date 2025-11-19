@echo off
REM =====================================================
REM Run Script - Khoi dong ung dung MauBieu7202
REM =====================================================

title MauBieu7202 - Server

echo.
echo =====================================================
echo MauBieu7202 - Khoi dong Server
echo =====================================================
echo.

REM =====================================================
REM Step 1: Check Python
REM =====================================================
echo [1/3] Kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo LOI: Python chua duoc cai dat hoac chua them vao PATH
    echo Vui long chay setup.bat truoc
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM =====================================================
REM Step 2: Activate Virtual Environment
REM =====================================================
echo [2/3] Kich hoat virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment da duoc kich hoat
) else (
    echo.
    echo CANH BAO: Khong tim thay virtual environment
    echo Dang chay voi system Python...
    echo.
    echo Neu gap loi, vui long chay setup.bat truoc
)
echo.

REM =====================================================
REM Step 3: Check Dependencies
REM =====================================================
echo [3/3] Kiem tra dependencies...
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Waitress chua duoc cai dat. Dang cai dat...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo LOI: Khong the cai dat dependencies
        echo Vui long chay setup.bat truoc
        pause
        exit /b 1
    )
)
echo Dependencies OK
echo.

REM =====================================================
REM Start Server
REM =====================================================
echo =====================================================
echo Dang khoi dong server...
echo =====================================================
echo.
echo Server se chay tai: http://localhost:8000
echo Admin panel: http://localhost:8000/admin
echo.
echo Nhan Ctrl+C de dung server
echo.
echo =====================================================
echo.

REM Run the waitress server
python run_waitress.py

REM If server stopped
echo.
echo =====================================================
echo Server da dung
echo =====================================================
pause
