@echo off
REM ====================================================================
REM Script: Install Python Packages from Offline Cache (LAN)
REM ====================================================================
REM Mục đích: Cài đặt tất cả dependencies từ offline_packages
REM          (không cần internet, cho môi trường LAN)
REM ====================================================================

echo.
echo ====================================================================
echo  CAI DAT OFFLINE PACKAGES - MAUBIEU7202
echo ====================================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong duoc cai dat hoac khong co trong PATH!
    echo.
    echo HUONG DAN:
    echo 1. Tai Python 3.8 hoac cao hon tu: https://www.python.org/downloads/
    echo 2. Trong qua trinh cai dat, CHON "Add Python to PATH"
    echo 3. Khoi dong lai Command Prompt va chay script nay lai
    echo.
    pause
    exit /b 1
)

echo [INFO] Phat hien Python version:
python --version
echo.

REM Kiểm tra thư mục offline_packages
if not exist "offline_packages" (
    echo [ERROR] Khong tim thay thu muc "offline_packages"!
    echo.
    echo HUONG DAN:
    echo 1. Tren may co internet, chay: download_offline_packages.bat
    echo 2. Copy thu muc "offline_packages" sang may nay
    echo 3. Chay lai script nay
    echo.
    pause
    exit /b 1
)

REM Kiểm tra virtual environment
if not exist "venv" (
    echo [INFO] Tao virtual environment...
    python -m venv venv

    if errorlevel 1 (
        echo [ERROR] Tao virtual environment that bai!
        pause
        exit /b 1
    )
    echo [OK] Da tao virtual environment
)

echo [INFO] Kich hoat virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Khong the kich hoat virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment da kich hoat
echo.

REM Nâng cấp pip (từ offline cache nếu có)
echo [INFO] Nang cap pip...
python -m pip install --upgrade pip --no-index --find-links=offline_packages
echo.

REM Cài đặt packages từ offline cache
echo [INFO] Cai dat packages tu offline cache...
echo.
pip install --no-index --find-links=offline_packages -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Cai dat that bai!
    echo Vui long kiem tra thu muc offline_packages co day du packages.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo  CAI DAT THANH CONG!
echo ====================================================================
echo.
echo BUOC TIEP THEO:
echo 1. Cau hinh database:
echo    - Mo file .env va cap nhat thong tin database
echo.
echo 2. Chay migrations:
echo    python manage.py migrate
echo.
echo 3. Tao superuser:
echo    python manage.py createsuperuser
echo.
echo 4. Khoi dong server:
echo    python manage.py runserver 0.0.0.0:8000
echo.
echo ====================================================================

pause
