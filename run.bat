@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ===================================================
echo   🛡️ 현장 안전점검 및 실시간 대시보드 실행기
echo ===================================================
echo.

:: 가상환경(.venv) 확인 및 자동 설치
if not exist ".\.venv\Scripts\activate.bat" (
    echo [안내] 가상환경(.venv)이 존재하지 않습니다.
    echo [안내] 최초 1회 가상환경 생성 및 필수 라이브러리를 설치합니다...
    echo.
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [오류] Python이 설치되어 있지 않거나 시스템 PATH에 등록되지 않았습니다.
        echo https://www.python.org 에서 Python을 설치해 주세요.
        pause
        exit /b 1
    )
    python -m venv .venv
    call ".\.venv\Scripts\activate.bat"
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [오류] 패키지 설치에 실패했습니다.
        pause
        exit /b 1
    )
    echo [완료] 필수 라이브러리 설치가 완료되었습니다!
    echo.
) else (
    call ".\.venv\Scripts\activate.bat"
)

echo 대시보드 서버를 시작합니다...
echo 잠시 후 기본 웹 브라우저(Chrome/Edge)가 자동으로 열립니다!
echo.
echo 로컬 접속 주소: http://localhost:8501
echo (서버를 종료하려면 이 창에서 Ctrl+C를 누르거나 창을 닫으세요)
echo ===================================================
echo.

python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo [오류 발생] 대시보드가 예기치 않게 종료되었습니다.
    pause
)
