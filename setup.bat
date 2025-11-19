@echo off
REM =====================================================
REM Setup Script - Cai dat ung dung MauBieu7202
REM Khong can Virtual Environment
REM =====================================================

title MauBieu7202 - Setup

echo.
echo =====================================================
echo MauBieu7202 - Cai dat lan dau
echo =====================================================
echo.
echo Script nay se:
echo   1. Kiem tra Python
echo   2. Cai dat dependencies
echo   3. Thiet lap database
echo   4. Thu thap static files
echo.
pause

REM =====================================================
REM Step 1: Check Python
REM =====================================================
echo.
echo [1/4] Kiem tra Python...
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
REM Step 2: Install Dependencies
REM =====================================================
echo [2/4] Cai dat dependencies...
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
REM Step 3: Setup Database
REM =====================================================
echo [3/4] Thiet lap database...
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
REM Step 4: Collect Static Files
REM =====================================================
echo [4/4] Thu thap static files...
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
echo   2. Truy cap: http://10.135.7.108:8888
echo.
echo De truy cap trang admin:
echo   - URL: http://10.135.7.108:8888/admin
echo   - Su dung tai khoan admin da tao
echo.
echo LUU Y:
echo   - Ung dung co the chay OFFLINE hoan toan
echo   - Tat ca CSS, icons da duoc tich hop san
echo.
pause

set /p START_NOW="Khoi dong server ngay bay gio? [Y/n]: "
if /i "%START_NOW%"=="n" goto :end

echo.
echo Dang khoi dong server...
call run.bat

:end
