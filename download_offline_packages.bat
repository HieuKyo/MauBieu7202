@echo off
cd /d "%~dp0"
REM ====================================================================
REM Script: Download Offline Packages for LAN Installation
REM ====================================================================
REM Mục đích: Download tất cả Python packages để cài đặt offline
REM Sử dụng: Chạy script này trên máy có internet, sau đó copy
REM          thư mục packages sang máy LAN
REM ====================================================================

echo.
echo ====================================================================
echo  DOWNLOAD OFFLINE PACKAGES FOR LAN INSTALLATION
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

REM Tạo thư mục packages
if not exist "packages" (
    echo [INFO] Tao thu muc packages...
    mkdir packages
)

echo [INFO] Bat dau download packages...
echo.

REM Download tất cả packages từ requirements.txt
pip download -r requirements.txt -d packages

if errorlevel 1 (
    echo.
    echo [ERROR] Download that bai!
    echo Vui long kiem tra ket noi internet va thu lai.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo  DOWNLOAD THANH CONG!
echo ====================================================================
echo.
echo Thu muc: packages
echo So luong packages:
dir /b packages | find /c /v ""
echo.
echo HUONG DAN CAI DAT TREN MAY LAN:
echo 1. Copy thu muc "packages" sang may LAN
echo 2. Chay script: install_offline.bat
echo.
echo ====================================================================

pause
