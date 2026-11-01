@echo off
chcp 65001 > nul
echo ========================================================
echo   스마트폰/외부 접속을 위한 Cloudflare Tunnel을 시작합니다.
echo   (별도 회원가입 없이 완전 무료로 HTTPS 주소를 발급합니다)
echo ========================================================
echo.
echo 먼저 다른 창에서 Streamlit 앱이 실행 중이어야 합니다.
echo.
cloudflared tunnel --url http://localhost:8501
pause

