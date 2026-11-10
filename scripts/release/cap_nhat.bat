@echo off
REM Cap nhat MauBieu7202 len ban moi trong goi nay (chay tren may LAN)
chcp 65001 >nul
cd /d "%~dp0"
title MauBieu7202 - Cap nhat
set PYTHONIOENCODING=utf-8
python --version >nul 2>&1
if errorlevel 1 (
    echo LOI: Khong tim thay Python. Vui long chay setup.bat truoc.
    pause
    exit /b 1
)
python apply_update.py
pause
