# 🛡️ 산업안전보건 통합점검 & 실시간 모니터링 대시보드

산업안전보건법 및 중대재해처벌법 대응을 위한 Python 기반 작업장 안전점검 관리 및 실시간 대시보드 웹 애플리케이션입니다.

---

## 🌟 주요 기능

1. **📊 종합 현황 대시보드 (Real-time Analytics)**
   - 안전 적합률, 주의/개선권고, 긴급 부적합(미조치) 등 핵심 KPI 요약
   - 사업자(원청/협력사)별 점검 결과 분포 및 구역별 결함 분석
   - 안전 분야별 점검 비중 (기계방호, 화재/소방, 전기안전, 유해물질 등)
   - 위험도(Risk Level: 낮음/보통/높음/치명적) 등급 분석
   - 최근 점검 기록 요약 및 실시간 필터링

2. **🛸 드론 사진 & 서류 AI 판독 (AI Inspector)**
   - 현장 항공 촬영 사진 또는 안전 서류 업로드
   - Google Gemini 1.5 Flash 기반 6대 위해·위험 요인 자동 판독
   - 원클릭 점검 일지 등록 지원

3. **✍️ 실시간 안전점검 일지 등록 (CRUD - Create)**
   - 원청 및 협력사별 현장 순회 점검 결과 등록
   - 4단계 위험도 평가 및 시정조치 기한/담당자 지정

4. **📝 점검 기록 수정 및 삭제 (CRUD - Update & Delete)**
   - 잘못 입력된 점검 기록의 세부 항목 수정 및 안전 삭제

5. **🛠️ 위해·위험 요인 시정조치 관리 (Action Items)**
   - 주의 및 불량 항목 집중 조치 상태 추적 (미조치 ➔ 조치중 ➔ 완료)
   - 조치 내역 CSV 다운로드 기능 제공

6. **📖 사업자별 안전가이드**
   - 산업안전보건법 및 중대재해처벌법상 도급인(원청)과 수급인(협력사) 의무사항 가이드

---

## 🛠️ 기술 스택
- **Language**: Python 3.11+
- **Web UI & Dashboard**: Streamlit
- **Data Visualization**: Plotly, Pandas
- **Database**: SQLite3 (`safety_records.db`, 단일 파일 기반)
- **External Tunnel**: ngrok / Cloudflare Tunnel

---

## 🚀 실행 방법

### 방법 1: 원클릭 자동 실행 (가장 추천 👍)
1. 폴더 안의 **`run.bat`** 파일을 더블 클릭합니다.
   - 가상환경(`.venv`)과 필수 패키지가 없을 경우 **자동으로 감지하여 설치**한 뒤 대시보드를 실행합니다.
2. 브라우저에서 `http://localhost:8501` 주소로 대시보드가 자동으로 열립니다.

### 방법 2: 수동 터미널 실행
```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\activate

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. Streamlit 대시보드 실행
streamlit run app.py
```

---

## 📱 스마트폰 / 외부 기기 접속 (ngrok 연동)

현장 안전관리자가 스마트폰이나 태블릿으로 점검표를 작성하려면:

1. **대시보드 먼저 실행**: `run.bat`을 실행하여 포트 8501에서 대시보드가 켜져 있어야 합니다.
2. **ngrok 터널 실행**: **`run_ngrok.bat`** 파일을 더블 클릭합니다.
3. 터미널 창에 표시되는 `Forwarding` 주소(예: `https://xxxx.ngrok-free.app`)를 스마트폰 브라우저에 입력하여 접속합니다.

---

## ❓ 자주 묻는 질문 및 오류 해결 (FAQ)

### Q. ngrok 접속 시 404 Not Found 에러가 발생합니다.
- **원인 1 (포트 번호 불일치)**: Laragon의 기본 'Share' 기능이나 `ngrok http 80`을 실행한 경우 발생합니다. Streamlit은 **8501 포트**를 사용하므로 반드시 `run_ngrok.bat` 또는 `ngrok http 8501` 명령어로 실행해야 합니다.
- **원인 2 (URL 경로 오입력)**: 주소 뒤에 `/app` 또는 `/app.py` 등을 덧붙이면 Streamlit이 404를 반환합니다. ngrok이 발급한 주소 원본(`https://xxxx.ngrok-free.app/`) 그대로 접속하세요.
- **원인 3 (프로그램 미실행)**: `run.bat`으로 대시보드를 켜지 않은 상태에서 ngrok에 접속하면 연결 오류가 발생합니다.

### Q. ngrok 실행 시 인증 에러(ERR_NGROK_4018)가 납니다.
- [ngrok 공식 홈페이지](https://ngrok.com) 회원가입 후 발급받은 본인 인증 토큰을 터미널에서 1회 등록해 주세요:
  ```bash
  ngrok config add-authtoken [내_인증_토큰]
  ```
