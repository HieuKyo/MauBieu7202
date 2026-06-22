@echo off
cd /d "%~dp0"
REM =====================================================
REM Run Script - Khoi dong ung dung MauBieu7202
REM Mang noi bo Agribank: 10.135.7.108:8888
REM =====================================================

title MauBieu7202 - Server

echo.
echo =====================================================
echo MauBieu7202 - Khoi dong Server
echo Mang noi bo Agribank
echo =====================================================
echo.

REM =====================================================
REM Step 1: Check Python
REM =====================================================
echo [1/2] Kiem tra Python...
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
REM Step 2: Check Dependencies
REM =====================================================
echo [2/2] Kiem tra dependencies...
python -c "import waitress" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Waitress chua duoc cai dat. Dang cai dat tu packages...
    if exist "offline_packages" (
        pip install --no-index --find-links=offline_packages -r requirements.txt
    ) else (
        echo LOI: Khong tim thay thu muc offline_packages
        echo Vui long chay setup.bat truoc
        pause
        exit /b 1
    )
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
echo Truy cap ung dung tai:
echo   - Mang noi bo: http://10.135.7.108:8888
echo   - Local:       http://localhost:8888
echo.
echo Admin panel:
echo   - Mang noi bo: http://10.135.7.108:8888/admin
echo   - Local:       http://localhost:8888/admin
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
