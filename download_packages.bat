@echo off
REM ====================================================================
REM Script: Download Packages for Offline Installation
REM ====================================================================
REM Mục đích: Download tất cả Python packages vào thư mục "packages"
REM           để cài đặt offline trên mạng LAN
REM ====================================================================

title Download Packages - MauBieu7202

echo.
echo ====================================================================
echo  DOWNLOAD PACKAGES CHO CAI DAT OFFLINE
echo  (Bao gom dbfread cho KPI Dashboard)
echo ====================================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong duoc cai dat hoac khong co trong PATH!
    echo Vui long cai dat Python 3.8 hoac cao hon.
    pause
    exit /b 1
)

echo [INFO] Phat hien Python version:
python --version
echo.

REM Kiểm tra Internet connection (optional)
echo [INFO] Kiem tra ket noi Internet...
ping -n 1 pypi.org >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Khong the ket noi pypi.org
    echo Dam bao may tinh co ket noi Internet de download packages.
    echo.
    set /p CONTINUE="Ban van muon tiep tuc? [Y/n]: "
    if /i "!CONTINUE!"=="n" exit /b 1
)

REM Tạo thư mục packages
if not exist "packages" (
    echo [INFO] Tao thu muc packages...
    mkdir packages
) else (
    echo [INFO] Thu muc packages da ton tai
)

echo.
echo [INFO] Bat dau download packages...
echo.
echo CAC PACKAGES QUAN TRONG:
echo   - Django 5.2.7
echo   - pandas, openpyxl (Excel processing)
echo   - dbfread ^>= 2.0.7 (KPI Dashboard - MOI!)
echo   - python-docx, Pillow
echo   - waitress (production server)
echo.

REM Download tất cả packages từ requirements.txt
pip download -r requirements.txt -d packages

if errorlevel 1 (
    echo.
    echo [ERROR] Download that bai!
    echo.
    echo KIEM TRA:
    echo   1. Ket noi Internet
    echo   2. File requirements.txt co ton tai
    echo   3. Proxy settings (neu co)
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo  DOWNLOAD THANH CONG!
echo ====================================================================
echo.

REM Đếm số lượng files
for /f %%A in ('dir /b packages ^| find /c /v ""') do set FILE_COUNT=%%A
echo Thu muc: packages\
echo So luong files: %FILE_COUNT%
echo.

REM Verify dbfread đã được download
dir /b packages | findstr /i "dbfread" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Khong tim thay dbfread trong packages!
    echo Package nay can thiet cho KPI Dashboard.
) else (
    echo [OK] dbfread da duoc download thanh cong!
)

echo.
echo CAC BUOC TIEP THEO:
echo 1. Copy thu muc "packages" sang may LAN (neu can)
echo 2. Tren may LAN, chay: setup.bat
echo 3. Script se tu dong cai dat tu thu muc packages
echo.
echo LUU Y:
echo   - Thu muc packages chua TAT CA dependencies
echo   - Khong can Internet khi chay setup.bat
echo.
echo ====================================================================

pause
