@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ===================================================
echo   🛡️ 현장 안전점검 및 실시간 대시보드 실행
echo ===================================================
echo.

:: 가상환경(.venv) 및 의존성 존재 여부 확인
if not exist ".\.venv\Scripts\streamlit.exe" (
    echo [안내] 가상환경 또는 필수 패키지가 설치되지 않았습니다.
    echo [안내] 최초 1회 가상환경 생성 및 라이브러리 설치를 진행합니다...
    echo.
    
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [오류] Python이 설치되어 있지 않거나 시스템 PATH에 등록되지 않았습니다.
        echo https://www.python.org 에서 Python 3.11 이상을 설치해 주세요.
        echo (설치 시 'Add python.exe to PATH' 옵션을 반드시 선택하세요)
        pause
        exit /b 1
    )
    
    echo 1. 가상환경(.venv) 생성 중...
    python -m venv .venv
    
    echo 2. 필수 라이브러리 설치 중 (Streamlit, Pandas, Plotly 등)...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo [오류] 패키지 설치 중 오류가 발생했습니다.
        pause
        exit /b 1
    )
    echo [완료] 환경 설정이 성공적으로 끝났습니다!
    echo.
)

echo 대시보드 웹 앱을 시작합니다... (포트: 8501)
echo 접속 주소: http://localhost:8501
echo.
.\.venv\Scripts\streamlit.exe run app.py
pause
