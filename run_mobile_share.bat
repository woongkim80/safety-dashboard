@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   스마트폰/외부 접속을 위한 보안 터널을 시작합니다.
echo ========================================================
echo.
echo [주의] 먼저 다른 창에서 'run.bat'이 실행 중이어야 합니다!
echo.

where cloudflared >nul 2>&1
if not errorlevel 1 (
    echo [Cloudflare Tunnel 감지] 무료 HTTPS 터널을 생성합니다...
    cloudflared tunnel --url http://localhost:8501
    pause
    exit /b 0
)

where ngrok >nul 2>&1
if not errorlevel 1 (
    echo [ngrok 감지] ngrok을 이용해 포트 8501로 연결합니다...
    echo (접속 주소: Forwarding 옆의 https://... 주소를 사용하세요)
    echo (주의: 주소 뒤에 /app 등을 붙이지 마세요)
    echo.
    ngrok http 8501
    pause
    exit /b 0
)

if exist "C:\laragon\bin\ngrok\ngrok.exe" (
    echo [Laragon ngrok 감지] ngrok을 이용해 포트 8501로 연결합니다...
    C:\laragon\bin\ngrok\ngrok.exe http 8501
    pause
    exit /b 0
)

echo [오류] 외부 접속 도구(ngrok 또는 cloudflared)를 찾을 수 없습니다.
echo ngrok(https://ngrok.com) 또는 cloudflared를 설치해 주세요.
echo.
pause
