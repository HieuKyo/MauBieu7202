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
echo Ung dung se mo tai: http://localhost:8501
echo Nhan Ctrl+C de dung ung dung
echo.

streamlit run app.py

pause
