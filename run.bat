@echo off
chcp 65001 > nul
echo ===================================================
echo   안전점검 및 실시간 대시보드를 실행합니다...
echo ===================================================
cd /d "%~dp0"
.\.venv\Scripts\streamlit.exe run app.py
pause
