---
name: run-tunnel
description: Start a secure tunnel (Cloudflare Tunnel or ngrok) to share the safety dashboard with mobile devices.
---

# Run Tunnel Skill (모바일/외부 공유 스킬)

스마트폰, 태블릿 등 외부 기기에서 로컬 실행 중인 Streamlit 대시보드(`http://localhost:8501`)에 무료로 안전하게 접속할 수 있도록 HTTPS 터널을 생성합니다.

---

## 1. Cloudflare Tunnel (강력 권장 - 시간 제한 없음, 완전 무료)

Cloudflare Tunnel(`cloudflared`)은 별도의 회원가입이나 인증 토큰 없이 즉시 퍼블릭 URL을 만들어 줍니다:

```powershell
# 1회성 간이 터널 실행
cloudflared tunnel --url http://localhost:8501
```

실행 후 터미널에 출력되는 `https://*.trycloudflare.com` 주소를 스마트폰 브라우저나 QR코드 생성기를 통해 접속합니다.

---

## 2. ngrok 사용법

ngrok 토큰이 등록되어 있는 경우:

```powershell
# run_ngrok.bat 실행 또는 터미널에서 8501 포트 지정
ngrok http 8501
```
출력되는 `Forwarding https://*.ngrok-free.app` 주소 원본 그대로 접속합니다.
(주의: 80번 포트를 지정하거나 주소 뒤에 `/app`을 붙이면 404 에러가 발생합니다.)

