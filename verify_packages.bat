@echo off
REM ====================================================================
REM Script: Verify Downloaded Packages
REM ====================================================================
REM Mục đích: Kiểm tra thư mục packages có đầy đủ dependencies chưa
REM ====================================================================

title Verify Packages - MauBieu7202

echo.
echo ====================================================================
echo  KIEM TRA PACKAGES OFFLINE
echo ====================================================================
echo.

REM Determine packages folder
set PACKAGES_FOLDER=
if exist "packages" set PACKAGES_FOLDER=packages
if exist "offline_packages" set PACKAGES_FOLDER=offline_packages

if "%PACKAGES_FOLDER%"=="" (
    echo [ERROR] Khong tim thay thu muc packages hoac offline_packages!
    echo.
    echo Vui long chay: download_packages.bat hoac download_offline_packages.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Kiem tra thu muc: %PACKAGES_FOLDER%
echo.

REM Count files
for /f %%A in ('dir /b %PACKAGES_FOLDER% 2^>nul ^| find /c /v ""') do set FILE_COUNT=%%A

if "%FILE_COUNT%"=="0" (
    echo [ERROR] Thu muc %PACKAGES_FOLDER% trong hoac khong co file nao!
    echo.
    pause
    exit /b 1
)

echo [OK] Tong so files: %FILE_COUNT%
echo.

REM Check critical packages
echo [INFO] Kiem tra cac packages quan trong:
echo.

set ALL_OK=1

REM Check Django
dir /b %PACKAGES_FOLDER% | findstr /i "Django" >nul 2>&1
if errorlevel 1 (
    echo   [X] Django - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] Django
)

REM Check pandas
dir /b %PACKAGES_FOLDER% | findstr /i "pandas" >nul 2>&1
if errorlevel 1 (
    echo   [X] pandas - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] pandas
)

REM Check openpyxl
dir /b %PACKAGES_FOLDER% | findstr /i "openpyxl" >nul 2>&1
if errorlevel 1 (
    echo   [X] openpyxl - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] openpyxl
)

REM Check dbfread (NEW!)
dir /b %PACKAGES_FOLDER% | findstr /i "dbfread" >nul 2>&1
if errorlevel 1 (
    echo   [X] dbfread - KHONG TIM THAY (CAN THIET CHO KPI!)
    set ALL_OK=0
) else (
    echo   [✓] dbfread (cho KPI Dashboard)
)

REM Check python-docx
dir /b %PACKAGES_FOLDER% | findstr /i "docx" >nul 2>&1
if errorlevel 1 (
    echo   [X] python-docx - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] python-docx
)

REM Check Pillow
dir /b %PACKAGES_FOLDER% | findstr /i "Pillow" >nul 2>&1
if errorlevel 1 (
    echo   [X] Pillow - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] Pillow
)

REM Check waitress
dir /b %PACKAGES_FOLDER% | findstr /i "waitress" >nul 2>&1
if errorlevel 1 (
    echo   [X] waitress - KHONG TIM THAY
    set ALL_OK=0
) else (
    echo   [✓] waitress
)

echo.
echo ====================================================================

if "%ALL_OK%"=="1" (
    echo [SUCCESS] Tat ca packages quan trong da san sang!
    echo Ban co the chay setup.bat de cai dat OFFLINE.
) else (
    echo [WARNING] Mot so packages quan trong bi thieu!
    echo.
    echo CACH SUA:
    echo   1. Tren may co Internet, chay: download_packages.bat
    echo   2. Hoac: pip download -r requirements.txt -d %PACKAGES_FOLDER%
    echo   3. Copy lai thu muc %PACKAGES_FOLDER% sang may LAN
)

echo.
echo ====================================================================

pause
