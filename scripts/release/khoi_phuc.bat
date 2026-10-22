@echo off
REM Quay ve ban truoc lan cap nhat gan nhat (chay tren may LAN)
chcp 65001 >nul
cd /d "%~dp0"
title MauBieu7202 - Khoi phuc ban truoc
set PYTHONIOENCODING=utf-8
python --version >nul 2>&1
if errorlevel 1 (
    echo LOI: Khong tim thay Python.
    pause
    exit /b 1
)
python apply_update.py --restore
pause
