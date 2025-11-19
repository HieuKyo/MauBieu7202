@echo off
REM =====================================================
REM Setup Script - Cai dat ung dung MauBieu7202
REM =====================================================

title MauBieu7202 - Setup

echo.
echo =====================================================
echo MauBieu7202 - Cai dat lan dau
echo =====================================================
echo.
echo Script nay se:
echo   1. Kiem tra Python
echo   2. Tao virtual environment
echo   3. Cai dat dependencies
echo   4. Thiet lap database
echo   5. Thu thap static files
echo.
pause

REM =====================================================
REM Step 1: Check Python
REM =====================================================
echo.
echo [1/5] Kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo LOI: Python chua duoc cai dat hoac chua them vao PATH
    echo Vui long cai Python 3.7+ tu: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo Python da duoc cai dat:
python --version
echo.

REM =====================================================
REM Step 2: Create Virtual Environment
REM =====================================================
echo [2/5] Tao virtual environment...
echo.

if exist "venv" (
    echo Virtual environment da ton tai
    echo Dang kich hoat...
) else (
    echo Dang tao virtual environment moi...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo LOI: Khong the tao virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment da duoc tao thanh cong
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment da duoc kich hoat
) else (
    echo LOI: Khong tim thay venv\Scripts\activate.bat
    pause
    exit /b 1
)
echo.

REM =====================================================
REM Step 3: Install Dependencies
REM =====================================================
echo [3/5] Cai dat dependencies...
echo.

pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo LOI: Khong the cai dat dependencies
    echo Vui long kiem tra ket noi mang va thu lai
    pause
    exit /b 1
)
echo.
echo Dependencies da duoc cai dat thanh cong
echo.

REM =====================================================
REM Step 4: Setup Database
REM =====================================================
echo [4/5] Thiet lap database...
echo.

echo Dang chay migrations...
python manage.py migrate
if errorlevel 1 (
    echo.
    echo LOI: Migration that bai
    pause
    exit /b 1
)
echo Database da duoc thiet lap thanh cong
echo.

REM =====================================================
REM Step 5: Collect Static Files
REM =====================================================
echo [5/5] Thu thap static files...
echo.

python manage.py collectstatic --noinput
if errorlevel 1 (
    echo.
    echo CANH BAO: Collectstatic that bai
    echo Ban co the chay lai sau: python manage.py collectstatic --noinput
)
echo.

REM =====================================================
REM Create Admin User (Optional)
REM =====================================================
echo =====================================================
echo Tao tai khoan Admin (tuy chon)
echo =====================================================
echo.
set /p CREATE_ADMIN="Ban co muon tao tai khoan admin? [Y/n]: "
if /i "%CREATE_ADMIN%"=="n" goto :skip_admin

echo.
echo Vui long nhap thong tin admin:
python manage.py createsuperuser
if errorlevel 1 (
    echo.
    echo CANH BAO: Khong the tao admin
    echo Ban co the tao sau bang: python manage.py createsuperuser
)

:skip_admin
echo.

REM =====================================================
REM Complete
REM =====================================================
echo =====================================================
echo Cai dat hoan tat!
echo =====================================================
echo.
echo De khoi dong ung dung:
echo   1. Chay: run.bat
echo   2. Mo trinh duyet: http://localhost:8000
echo.
echo De truy cap trang admin:
echo   - URL: http://localhost:8000/admin
echo   - Su dung tai khoan admin da tao
echo.
pause

set /p START_NOW="Khoi dong server ngay bay gio? [Y/n]: "
if /i "%START_NOW%"=="n" goto :end

echo.
echo Dang khoi dong server...
call run.bat

:end
