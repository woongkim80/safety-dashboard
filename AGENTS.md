# 🛡️ AGENTS.md: 현장 안전점검 및 드론 서류 검토 시스템 개발 명세서
> **Specs-Driven Development (스펙 주도 개발) 공식 에이전트 가이드**

---

## 1. 프로젝트 개요 및 목적
- **프로젝트 명**: 현장 안전점검 및 드론 서류·사진 검토 웹 대시보드
- **대상 사용자**: 비전공자 및 현장 안전관리자, 본사 안전보건팀
- **사용 환경**: 스마트폰, 태블릿, PC 어디서나 접속하여 점검 일지와 사진을 실시간 작성 및 검토할 수 있는 반응형 웹

---

## 2. 기술 스택 및 환경 제약 (Zero-Cost & Lightweight)
- **언어 및 프레임워크**: Python 3.11+, Streamlit (반응형 웹 UI)
- **데이터베이스**: SQLite (`safety_records.db` 단일 파일, 별도 서버 설치 금지)
- **AI 연동**: Google Gemini API (`gemini-1.5-flash` 멀티모달 분석)
- **외부 공유**: Cloudflare Tunnel (`cloudflared`) 또는 `ngrok`
- **코드 스타일**: 초보자가 읽기 쉬운 직관적인 구조, **100% 한국어 주석 필수**

---

## 3. 에이전트 작업 원칙 및 제약 사항
1. **외부 유료 라이브러리나 무거운 프레임워크 추가 금지**: React, Vue, Docker, Node.js 등을 배제하고 순수 Python 생태계 유지.
2. **단일 DB 파일 처리**: 모든 데이터 처리는 `sqlite3` 모듈을 사용해 `safety_records.db` 단일 파일로 처리.
3. **모바일 뷰포트 최적화**: 스마트폰 화면에서도 깨지지 않도록 Streamlit의 컬럼 레이아웃(`st.columns`)과 유연한 너비 적용.
4. **법적 기준 기반 AI 프롬프트**: 현장 점검 AI 분석 시 「산업안전보건기준에 관한 규칙」 및 「중대재해처벌법 지침」을 기준으로 피드백 제공.

---

## 4. 실제 작업 진행 방법 (Specs-Driven Development)

`AGENTS.md`가 준비되면 수강생은 복잡한 지시를 할 필요가 없습니다. Antigravity IDE 에이전트 채팅창에 다음과 같이 한 줄만 입력하면 됩니다:

> 💬 **"AGENTS.md 내용에 맞춰서, 안전점검 일지를 SQLite DB에 저장하고 모바일에서도 볼 수 있는 Streamlit 기본 앱(app.py)을 작성하고 실행해줘."**

에이전트가 알아서 `AGENTS.md`의 규칙(SQLite 사용, 한국어 주석, 모바일 반응형, Gemini API 연동)을 준수하며 코드를 생성하고 실행까지 도와줍니다.

---

## 5. 도메인 규칙 및 스킬 연동 체계
- **도메인 업무 규칙**: `.agents/rules/safety_rules.md`  
  (드론 사진 판독 시 안전난간 미설치, 개구부 덮개 미고정, 근로자 안전모 턱끈 미체결 등 6대 핵심 위험 우선 감지)
- **반복 실행 도구**: `.agents/skills/`  
  - `export_to_excel/SKILL.md`: 점검 이력 엑셀 자동 내보내기
  - `run_tunnel/SKILL.md`: 외부 스마트폰 접속용 터널링

