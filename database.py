import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "safety_inspection.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        inspector TEXT NOT NULL,
        facility TEXT NOT NULL,
        location TEXT NOT NULL,
        category TEXT NOT NULL,
        item_name TEXT NOT NULL,
        status TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        description TEXT,
        corrective_action TEXT,
        action_status TEXT NOT NULL,
        action_deadline TEXT,
        action_assignee TEXT,
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()

    # Check if empty, insert sample records
    cursor.execute("SELECT COUNT(*) FROM inspections")
    count = cursor.fetchone()[0]
    if count == 0:
        _insert_sample_data(cursor)
        conn.commit()
    conn.close()

def _insert_sample_data(cursor):
    sample_records = [
        # (date, inspector, facility, location, category, item_name, status, risk_level, description, corrective_action, action_status, action_deadline, action_assignee)
        ("2026-10-25", "김안전", "제1제조공장", "프레스 가공실", "기계방호", "프레스 비상정지장치(양수조작버튼)", "양호", "낮음", "정상 작동 확인 및 감응속도 양호", "", "완료", "", "정기점검"),
        ("2026-10-26", "이보건", "제1제조공장", "도장 라인", "유해물질", "국소배기장치 후드 풍속 측정", "주의", "보통", "배기 후드 주변 분진 누적으로 제어풍속 기준치 소폭 하회", "필터 교체 및 덕트 청소 실시 예정", "조치중", "2026-11-05", "설비팀 박반장"),
        ("2026-10-27", "김안전", "제1제조공장", "화학물질 저장고", "유해물질", "MSDS(물질안전보건자료) 비치 및 경고표지", "불량", "높음", "신규 입고 용제(세척제) 경고표지 미부착 상태 보관", "경고표지 즉시 부착 및 작업자 교육 요청", "미조치", "2026-11-02", "물류팀 최주임"),
        ("2026-10-28", "박환경", "물류센터", "입출고 도크", "추락/전도", "도크 안전난간 및 스토퍼 상태", "불량", "치명적", "3번 도크 하역장 안전난간 용접부 파손으로 흔들림 심함", "출입 통제 테이프 설치 및 긴급 용접 보강 발주", "조치중", "2026-11-03", "시설관리팀 강기사"),
        ("2026-10-29", "김안전", "제2제조공장", "전기제어실", "전기안전", "분전반 배선 상태 및 절연저항", "양호", "낮음", "배선 정리 양호, 먼지 유입 방지 패킹 양호", "", "완료", "", "전기안전관리자"),
        ("2026-10-29", "이보건", "제1제조공장", "가공 2라인", "개인보호구", "보안경 및 귀마개 착용 상태", "주의", "보통", "신규 입사자 2명 귀마개 미착용 작업 적발", "현장 구두 지도 및 보호구 지급대장 확인", "완료", "2026-10-29", "가공2팀 조장"),
        ("2026-10-30", "김안전", "제2제조공장", "용접 작업장", "화재/소방", "소화기 비치 및 점검표", "불량", "높음", "용접 구역 이동식 소화기 압력 게이지 저하(노란색 구간)", "신품 분말소화기 교체 배치", "완료", "2026-10-30", "안전팀 김대리"),
        ("2026-10-31", "최기술", "물류센터", "지게차 충전소", "화재/소방", "배터리 충전구역 환기 및 방폭형 설비", "양호", "낮음", "수소 환기팬 정상 가동 및 가스누출경보기 양호", "", "완료", "", "물류안전담당"),
        ("2026-10-31", "박환경", "제1제조공장", "주통로", "통로/환경", "통로 유효폭 확보 및 바닥 기름때", "불량", "보통", "통로 중앙에 완제품 팔레트 적재로 지게차-보행자 동선 간섭", "적치물 지정 구역으로 전량 이동 조치 지시", "미조치", "2026-11-02", "생산관리팀"),
        ("2026-11-01", "김안전", "제2제조공장", "조립 라인", "기계방호", "컨베이어 비상정지 풀코드 스위치", "양호", "낮음", "라인 전체 풀코드 당김 테스트 정상 정지 확인", "", "완료", "", "안전팀"),
        ("2026-11-01", "이보건", "제1제조공장", "폐수처리장", "밀폐공간", "가스측정기 비치 및 환기팬 상태", "주의", "높음", "복합가스측정기 교정주기 도래(검교정 의뢰 필요)", "전문기관 검교정 접수 완료(대체기 운용 중)", "조치중", "2026-11-08", "환경팀"),
        ("2026-11-01", "최기술", "제1제조공장", "옥외 가스저장소", "화재/소방", "LPG 가스 누출경보 감지기 작동", "양호", "낮음", "감지센서 이상 없음, 긴급차단밸브 연동 시험 양호", "", "완료", "", "설비팀"),
    ]

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for r in sample_records:
        cursor.execute("""
        INSERT INTO inspections (
            date, inspector, facility, location, category, item_name, 
            status, risk_level, description, corrective_action, action_status, 
            action_deadline, action_assignee, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*r, now_str))

def get_all_inspections():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM inspections ORDER BY date DESC, id DESC", conn)
    conn.close()
    return df

def add_inspection(date, inspector, facility, location, category, item_name, status, risk_level, description, corrective_action, action_status, action_deadline, action_assignee):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO inspections (
        date, inspector, facility, location, category, item_name, 
        status, risk_level, description, corrective_action, action_status, 
        action_deadline, action_assignee, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, inspector, facility, location, category, item_name, status, risk_level, description, corrective_action, action_status, action_deadline, action_assignee, now_str))
    conn.commit()
    conn.close()

def update_action_status(inspection_id, new_status, new_action=""):
    conn = get_connection()
    cursor = conn.cursor()
    if new_action:
        cursor.execute("UPDATE inspections SET action_status = ?, corrective_action = ? WHERE id = ?", (new_status, new_action, inspection_id))
    else:
        cursor.execute("UPDATE inspections SET action_status = ? WHERE id = ?", (new_status, inspection_id))
    conn.commit()
    conn.close()

def delete_inspection(inspection_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inspections WHERE id = ?", (inspection_id,))
    conn.commit()
    conn.close()
