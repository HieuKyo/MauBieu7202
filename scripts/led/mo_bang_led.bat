@echo off
REM Chep file nay vao thu muc Startup cua PC noi bang LED (Win+R, go shell:startup).
REM Sua dia chi IP may chu MauBieu o dong duoi.
set BASE=http://192.168.1.10:8888/led

REM Doi may chu san sang, tranh Edge dung o trang loi khi PC khoi dong truoc.
:cho
curl -s -o NUL --max-time 5 %BASE%/
if errorlevel 1 (
    timeout /t 10 /nobreak >nul
    goto cho
)

start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk %BASE%/ --edge-kiosk-type=fullscreen --no-first-run

REM Moi phut hoi lich tat may. Huy trong 60 giay: Win+R, go shutdown /a
:theo_doi
for /f %%i in ('curl -s --max-time 10 %BASE%/tat-may/') do (
    if "%%i"=="TAT" shutdown /s /t 60 /c "Bang LED tat theo lich"
)
timeout /t 60 /nobreak >nul
goto theo_doi
