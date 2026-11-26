@echo off
REM Tao goi cap nhat cho may LAN tu cac commit moi (chay tren may dev)
REM   tao_ban_cap_nhat.bat         -> hien menu: 1 = ban moi nhat, 2 = tao lai ban da phat hanh
REM   tao_ban_cap_nhat.bat --full  -> toan bo code
REM   tao_ban_cap_nhat.bat --lai 2026.11.26  -> tao LAI goi cua ban da phat hanh (bi mat / ghi nham USB)
chcp 65001 >nul
cd /d "%~dp0"
title MauBieu7202 - Tao goi cap nhat
set PYTHONIOENCODING=utf-8
python scripts\release\build_update.py %*
pause
