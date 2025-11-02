@echo off
REM =====================================================
REM Download Bootstrap and Bootstrap Icons Files
REM =====================================================
REM
REM This batch file downloads Bootstrap CSS/JS and
REM Bootstrap Icons for offline use.
REM
REM Requirements:
REM   - Internet connection
REM   - curl (included in Windows 10+)
REM
REM =====================================================

title Download Bootstrap Files

echo.
echo =====================================================
echo Downloading Bootstrap Files
echo =====================================================
echo.

REM Create directory structure
echo [1/5] Creating directories...
if not exist "templates_app\static\vendor\bootstrap\css" mkdir templates_app\static\vendor\bootstrap\css
if not exist "templates_app\static\vendor\bootstrap\js" mkdir templates_app\static\vendor\bootstrap\js
if not exist "templates_app\static\vendor\bootstrap-icons\css" mkdir templates_app\static\vendor\bootstrap-icons\css
if not exist "templates_app\static\vendor\bootstrap-icons\fonts" mkdir templates_app\static\vendor\bootstrap-icons\fonts
echo Done.
echo.

REM Download Bootstrap CSS
echo [2/5] Downloading Bootstrap CSS (v5.3.0)...
curl -L -o templates_app\static\vendor\bootstrap\css\bootstrap.min.css ^
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css
if errorlevel 1 (
    echo ERROR: Failed to download Bootstrap CSS
    goto :error
)
echo Done.
echo.

REM Download Bootstrap JS
echo [3/5] Downloading Bootstrap JS Bundle (v5.3.0)...
curl -L -o templates_app\static\vendor\bootstrap\js\bootstrap.bundle.min.js ^
  https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js
if errorlevel 1 (
    echo ERROR: Failed to download Bootstrap JS
    goto :error
)
echo Done.
echo.

REM Download Bootstrap Icons CSS
echo [4/5] Downloading Bootstrap Icons CSS (v1.11.0)...
curl -L -o templates_app\static\vendor\bootstrap-icons\css\bootstrap-icons.min.css ^
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.min.css
if errorlevel 1 (
    echo ERROR: Failed to download Bootstrap Icons CSS
    goto :error
)
echo Done.
echo.

REM Download Bootstrap Icons Fonts
echo [5/5] Downloading Bootstrap Icons Fonts...
curl -L -o templates_app\static\vendor\bootstrap-icons\fonts\bootstrap-icons.woff ^
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff
if errorlevel 1 (
    echo WARNING: Failed to download Bootstrap Icons WOFF font
)

curl -L -o templates_app\static\vendor\bootstrap-icons\fonts\bootstrap-icons.woff2 ^
  https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/fonts/bootstrap-icons.woff2
if errorlevel 1 (
    echo WARNING: Failed to download Bootstrap Icons WOFF2 font
)
echo Done.
echo.

REM Show file sizes
echo =====================================================
echo Download Complete!
echo =====================================================
echo.
echo File sizes:
dir /s templates_app\static\vendor\bootstrap\css\*.css
dir /s templates_app\static\vendor\bootstrap\js\*.js
dir /s templates_app\static\vendor\bootstrap-icons\css\*.css
dir /s templates_app\static\vendor\bootstrap-icons\fonts\*.woff*
echo.

echo =====================================================
echo Next Steps:
echo =====================================================
echo 1. Run: python manage.py collectstatic
echo 2. Restart your server: start_server.bat
echo.

goto :end

:error
echo.
echo =====================================================
echo Download Failed!
echo =====================================================
echo.
echo Possible reasons:
echo - No internet connection
echo - Firewall blocking curl
echo - CDN is not accessible
echo.
echo Manual download:
echo 1. Visit: https://getbootstrap.com/docs/5.3/getting-started/download/
echo 2. Download Bootstrap v5.3.0
echo 3. Extract to: templates_app\static\vendor\bootstrap\
echo.
echo 4. Visit: https://icons.getbootstrap.com/
echo 5. Download Bootstrap Icons v1.11.0
echo 6. Extract to: templates_app\static\vendor\bootstrap-icons\
echo.
pause
exit /b 1

:end
pause
