@echo off
cd /d "%~dp0"
REM =====================================================
REM Setup Script - Cai dat ung dung MauBieu7202
REM Ho tro cai dat OFFLINE (khong can Internet)
REM Version: 2.0 - Updated for KPI Dashboard
REM =====================================================

title MauBieu7202 - Setup

echo.
echo =====================================================
echo MauBieu7202 - Cai dat lan dau
echo Ho tro cai dat OFFLINE (bao gom KPI Dashboard)
echo =====================================================
echo.
echo Script nay se:
echo   1. Kiem tra Python
echo   2. Cai dat dependencies (bao gom dbfread cho KPI)
echo   3. Thiet lap database
echo   4. Thu thap static files
echo.
echo REQUIREMENTS MOI:
echo   - dbfread ^>= 2.0.7 (cho KPI Dashboard)
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
    echo Vui long cai Python 3.11+ tu: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo Python da duoc cai dat:
python --version
echo.

REM =====================================================
REM Step 2: Install Dependencies (OFFLINE)
REM =====================================================
echo [2/4] Cai dat dependencies...
echo.

REM Determine packages folder (support both 'packages' and 'offline_packages')
set PACKAGES_FOLDER=
if exist "packages" set PACKAGES_FOLDER=packages
if exist "offline_packages" set PACKAGES_FOLDER=offline_packages

if "%PACKAGES_FOLDER%"=="" (
    echo.
    echo LOI: Khong tim thay thu muc packages hoac offline_packages
    echo.
    echo HUONG DAN:
    echo   - Neu co Internet: Chay download_offline_packages.bat
    echo   - Hoac copy thu muc 'packages' hoac 'offline_packages' vao day
    echo.
    pause
    exit /b 1
)

echo Dang cai dat tu thu muc %PACKAGES_FOLDER% (OFFLINE)...
echo.

REM Upgrade pip first (from offline cache)
echo Nang cap pip...
python -m pip install --upgrade pip --no-index --find-links=%PACKAGES_FOLDER% 2>nul

REM Install all dependencies
echo Cai dat dependencies tu requirements.txt...
pip install --no-index --find-links=%PACKAGES_FOLDER% -r requirements.txt
if errorlevel 1 (
    echo.
    echo LOI: Khong the cai dat mot so dependencies
    echo.
    echo KIEM TRA:
    echo   1. Thu muc %PACKAGES_FOLDER% co day du cac file .whl
    echo   2. File requirements.txt co dung khong
    echo.
    echo PACKAGES CAN THIET MOI:
    echo   - dbfread ^>= 2.0.7 (cho KPI Dashboard)
    echo.
    echo CACH SUA:
    echo   1. Tren may co Internet, chay: download_offline_packages.bat
    echo   2. Copy lai thu muc offline_packages sang may nay
    echo.
    pause
    exit /b 1
)

echo.
echo Kiem tra dbfread da duoc cai dat...
python -c "import dbfread; print('✓ dbfread version:', dbfread.__version__)" 2>nul
if errorlevel 1 (
    echo.
    echo CANH BAO: dbfread chua duoc cai dat!
    echo Module nay can thiet cho KPI Dashboard.
    echo.
    set /p INSTALL_DBFREAD="Ban co muon thu cai dat dbfread tu Internet? [Y/n]: "
    if /i "!INSTALL_DBFREAD!"=="y" (
        echo Dang cai dat dbfread tu Internet...
        pip install dbfread>=2.0.7
    )
)

echo.
echo Dependencies da duoc cai dat thanh cong
echo.

REM =====================================================
REM Step 3: Setup Database
REM =====================================================
echo [3/4] Thiet lap database...
echo.

echo Dang tao migrations moi...
python manage.py makemigrations
if errorlevel 1 (
    echo.
    echo CANH BAO: Makemigrations gap van de
    echo Tiep tuc voi migrations hien co...
)

echo.
echo Dang ap dung migrations...
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
echo TINH NANG MOI - KPI DASHBOARD:
echo   - URL: http://10.135.7.108:8888/kpi-dashboard/
echo   - Tinh KPI tu dong cho Giao dich vien
echo   - Ho tro file: Thẻ, SMS, E-Mobile Banking
echo   - Yeu cau: dbfread (da duoc cai dat)
echo.
echo LUU Y:
echo   - Ung dung co the chay OFFLINE hoan toan
echo   - Tat ca CSS, icons, thu vien da duoc tich hop san
echo   - KPI Dashboard ho tro xu ly file DBF (dBase/FoxPro)
echo.
pause

set /p START_NOW="Khoi dong server ngay bay gio? [Y/n]: "
if /i "%START_NOW%"=="n" goto :end

echo.
echo Dang khoi dong server...
call run.bat

:end
