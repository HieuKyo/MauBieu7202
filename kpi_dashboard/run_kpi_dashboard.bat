@echo off
REM Script chạy KPI Dashboard trên Windows

echo ========================================
echo    KPI Dashboard - Agribank
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long cai dat Python tu https://www.python.org/
    pause
    exit /b 1
)

REM Kiểm tra Streamlit
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Dang cai dat Streamlit...
    pip install streamlit
)

echo [INFO] Khoi dong ung dung...
echo.

REM Lấy IP LAN
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set LAN_IP=%%a
    goto :ip_found
)
:ip_found
set LAN_IP=%LAN_IP:~1%

echo Dia chi truy cap:
echo    - Local:   http://localhost:8501
if defined LAN_IP (
    echo    - LAN:     http://%LAN_IP%:8501
    echo.
    echo Cac may khac trong mang LAN co the truy cap qua:
    echo    http://%LAN_IP%:8501
)
echo.
echo Nhan Ctrl+C de dung ung dung
echo.
echo ==========================================
echo.

streamlit run app.py

pause
