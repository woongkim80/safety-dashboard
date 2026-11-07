@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   📱 ngrok 스마트폰/외부 기기 접속 터널 실행기
echo ========================================================
echo.

:: 1. 8501 포트(Streamlit) 활성화 여부 확인 및 자동 실행
netstat -ano | findstr ":8501" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo [안내] Streamlit 대시보드가 아직 실행되지 않았습니다.
    echo [안내] 새 창에서 대시보드(run.bat)를 자동으로 시작합니다...
    start "🛡️ 안전 대시보드 서버 (포트 8501)" cmd /c "run.bat"
    echo 서버가 준비될 때까지 5초간 대기합니다...
    timeout /t 5 /nobreak >nul
) else (
    echo [확인] 8501 포트에서 Streamlit 대시보드가 정상 동작 중입니다.
)

:: 2. ngrok 실행 파일 탐색
set "NGROK_BIN="
where ngrok >nul 2>&1
if not errorlevel 1 (
    set "NGROK_BIN=ngrok"
) else (
    if exist "C:\laragon\bin\ngrok\ngrok.exe" (
        set "NGROK_BIN=C:\laragon\bin\ngrok\ngrok.exe"
    )
)

if "%NGROK_BIN%"=="" (
    echo.
    echo [오류] 시스템에서 ngrok 실행 파일을 찾을 수 없습니다.
    echo https://ngrok.com 에서 ngrok을 다운로드하거나 경로를 확인해 주세요.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo [⚠️ 404 에러 방지 핵심 안내]
echo 1. 아래 화면의 'Forwarding' 옆 https://...ngrok-free.app 주소 확인
echo 2. 접속할 때 주소 뒤에 /app 등을 붙이지 말고 주소 그대로 접속하세요!
echo ========================================================
echo.
echo ngrok 8501 포트 터널을 개방합니다...
echo.

"%NGROK_BIN%" http 8501
pause
