@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   📱 ngrok 스마트폰/외부 기기 접속 터널 실행기
echo ========================================================
echo.
echo [⚠️ 404 에러 방지 핵심 체크사항]
echo 1. 반드시 'run.bat'을 먼저 실행하여 대시보드가 켜져 있어야 합니다.
echo 2. Laragon의 기본 'Share'를 누르면 80번 포트로 연결되어 [404 에러]가 납니다!
echo    Streamlit은 [8501 포트]를 사용하므로 이 배치파일로 실행해야 합니다.
echo 3. 생성된 ngrok 주소 접속 시 주소 끝에 /app이나 파일명을 붙이지 말고,
echo    예: https://xxxx.ngrok-free.app 그대로 접속해 주세요.
echo ========================================================
echo.

:: ngrok 설치 확인
where ngrok >nul 2>&1
if errorlevel 1 (
    if exist "C:\laragon\bin\ngrok\ngrok.exe" (
        set "NGROK_BIN=C:\laragon\bin\ngrok\ngrok.exe"
    ) else (
        echo [오류] 시스템에 ngrok이 설치되어 있지 않습니다.
        echo https://ngrok.com 에서 다운로드하거나 PATH를 확인해 주세요.
        pause
        exit /b 1
    )
) else (
    set "NGROK_BIN=ngrok"
)

echo Streamlit 포트(8501)로 ngrok 터널을 개방합니다...
echo 터널이 연결되면 'Forwarding' 옆의 https://... 주소를 스마트폰에 입력하세요.
echo (종료하려면 Ctrl+C 또는 창을 닫으세요)
echo.
"%NGROK_BIN%" http 8501
pause

