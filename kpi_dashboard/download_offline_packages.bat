@echo off
REM Script download packages cho offline deployment - Windows

echo ========================================
echo   KPI Dashboard - Offline Downloader
echo ========================================
echo.

python download_offline_packages.py

if errorlevel 1 (
    echo.
    echo [ERROR] Download that bai!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Hoan thanh!
pause
