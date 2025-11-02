@echo off
REM =====================================================
REM Fix Static Files - Khắc phục lỗi CSS không hiển thị
REM =====================================================

title Fix Static Files

echo.
echo =====================================================
echo Fix Static Files - Khac phuc loi CSS
echo =====================================================
echo.

echo Loi gap phai:
echo   - CSS khong hien thi
echo   - Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
echo.

echo Cac buoc sua loi:
echo   1. Cap nhat dependencies (them WhiteNoise)
echo   2. Tai Bootstrap files
echo   3. Chay collectstatic
echo   4. Khoi dong lai server
echo.
pause

REM Step 1: Install/Update dependencies
echo.
echo [1/4] Cap nhat dependencies...
echo.
pip install --upgrade -r requirements.txt
if errorlevel 1 (
    echo ERROR: Khong the cap nhat dependencies
    echo Thu chay lai voi: pip install --upgrade -r requirements.txt
    pause
    exit /b 1
)
echo.

REM Step 2: Download Bootstrap (if needed)
echo [2/4] Kiem tra Bootstrap files...
echo.
if not exist "templates_app\static\vendor\bootstrap\css\bootstrap.min.css" (
    echo Bootstrap files chua co, dang tai xuong...
    call download_bootstrap_files.bat
) else (
    echo Bootstrap files da co
)
echo.

REM Step 3: Run collectstatic
echo [3/4] Chay collectstatic...
echo.
echo Xoa staticfiles cu...
if exist "staticfiles" (
    rmdir /s /q staticfiles
    echo Da xoa staticfiles cu
)

echo.
echo Collect static files moi...
python manage.py collectstatic --noinput
if errorlevel 1 (
    echo.
    echo ERROR: Collectstatic that bai
    echo.
    echo Hay thu:
    echo   1. Kiem tra Django da cai: python -c "import django"
    echo   2. Chay migrate: python manage.py migrate
    echo   3. Chay lai script nay
    echo.
    pause
    exit /b 1
)
echo.

REM Step 4: Verify
echo [4/4] Xac nhan...
echo.
if exist "staticfiles\vendor\bootstrap\css\bootstrap.min.css" (
    echo [OK] Bootstrap CSS da duoc collect thanh cong!
) else (
    echo [CANH BAO] Khong tim thay Bootstrap CSS sau khi collect
)

if exist "staticfiles\css\agribank-theme.css" (
    echo [OK] Agribank theme CSS da duoc collect thanh cong!
) else (
    echo [CANH BAO] Khong tim thay Agribank theme CSS
)

if exist "staticfiles\images\agribank_logo.png" (
    echo [OK] Logo da duoc collect thanh cong!
) else (
    echo [CANH BAO] Khong tim thay logo
)

echo.
echo =====================================================
echo Fix hoan thanh!
echo =====================================================
echo.
echo QUAN TRONG:
echo   1. KHOI DONG LAI SERVER
echo   2. Chay: start_server.bat
echo   3. Xoa cache trinh duyet (Ctrl+F5)
echo.
echo Neu van con loi:
echo   - Kiem tra terminal khi chay server
echo   - Dam bao khong co loi khi collectstatic
echo   - Xem log chi tiet
echo.
pause

set /p RESTART="Khoi dong lai server bay gio? [Y/n]: "
if /i "%RESTART%"=="n" goto :end

echo.
echo Dang khoi dong server...
start_server.bat

:end
