@echo off
REM Tao goi cap nhat cho may LAN tu cac commit moi (chay tren may dev)
REM   tao_ban_cap_nhat.bat         -> chi cac file thay doi tu ban truoc
REM   tao_ban_cap_nhat.bat --full  -> toan bo code
chcp 65001 >nul
cd /d "%~dp0"
title MauBieu7202 - Tao goi cap nhat
set PYTHONIOENCODING=utf-8
python scripts\release\build_update.py %*
pause
