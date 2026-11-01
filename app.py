import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db

# 1. 페이지 설정
st.set_page_config(
    page_title="산업안전보건 통합점검 & 대시보드",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화
db.init_db()

# 커스텀 CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 18px 20px;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .badge-pass {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warn {
        background-color: #FEF9C3;
        color: #854D0E;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-fail {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 불러오기
df = db.get_all_inspections()

# 3. 사이드바 - 필터링 및 네비게이션
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/safety-shield.png", width=64)
    st.title("안전점검 필터")
    
    # 사업장 필터
    facility_list = ["전체"] + sorted(df["facility"].dropna().unique().tolist())
    selected_facility = st.selectbox("🏭 사업장 선택", facility_list)
    
    # 분야 필터
    category_list = ["전체"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("🔍 안전 분야", category_list)

    # 결과 필터
    status_list = ["전체", "양호", "주의", "불량"]
    selected_status = st.selectbox("📌 점검 결과", status_list)

    # 조치 상태 필터
    action_list = ["전체", "미조치", "조치중", "완료"]
    selected_action = st.selectbox("⚙️ 조치 진행상황", action_list)

    st.divider()
    st.caption("시스템: 산업안전보건법 및 중대재해 예방 모니터링 시스템")
    st.caption("버전: v1.0.0 (Python + Streamlit)")

# 필터 적용
filtered_df = df.copy()
if selected_facility != "전체":
    filtered_df = filtered_df[filtered_df["facility"] == selected_facility]
if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]
if selected_status != "전체":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]
if selected_action != "전체":
    filtered_df = filtered_df[filtered_df["action_status"] == selected_action]

# 상단 헤더
st.markdown('<div class="main-title">🛡️ 산업안전보건 통합점검 & 실시간 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">작업장 안전점검 현황, 위해·위험 요인 발굴 및 시정조치 이력 모니터링</div>', unsafe_allow_html=True)

# 4. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 종합 현황 대시보드", 
    "✍️ 안전점검 일지 등록", 
    "🛠️ 부적합 조치 관리", 
    "📖 안전 수칙 & 분석"
])

# ==========================================
# TAB 1: 종합 현황 대시보드
# ==========================================
with tab1:
    # KPI 요약 지표
    total_count = len(filtered_df)
    pass_count = len(filtered_df[filtered_df["status"] == "양호"])
    warn_count = len(filtered_df[filtered_df["status"] == "주의"])
    fail_count = len(filtered_df[filtered_df["status"] == "불량"])
    
    pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
    unresolved_count = len(filtered_df[(filtered_df["status"].isin(["주의", "불량"])) & (filtered_df["action_status"] != "완료")])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 총 점검 건수", f"{total_count}건", delta=f"{len(df)}건 중 필터링됨")
    with col2:
        st.metric("✅ 안전 적합률(양호)", f"{pass_rate:.1f}%", delta=f"{pass_count}건 양호")
    with col3:
        st.metric("⚠️ 주의/개선 권고", f"{warn_count}건", delta_color="inverse", delta=f"{warn_count}건")
    with col4:
        st.metric("🚨 긴급 부적합(미조치)", f"{unresolved_count}건", delta_color="inverse", delta=f"불량 총 {fail_count}건")

    # 긴급 부적합 경보 배너
    critical_items = filtered_df[(filtered_df["status"] == "불량") & (filtered_df["action_status"] != "완료")]
    if not critical_items.empty:
        st.error(f"🚨 **[긴급 조치 요구]** 현재 즉각 조치가 필요한 불량 항목이 **{len(critical_items)}건** 있습니다. 아래 현황을 확인하고 신속히 조치해 주세요!")

    st.markdown("---")

    # 대시보드 차트 행 1
    c1, c2 = st.columns([6, 4])
    
    with c1:
        st.subheader("🏢 구역별 점검 결과 분포")
        if not filtered_df.empty:
            loc_summary = filtered_df.groupby(["location", "status"]).size().reset_index(name="count")
            fig_loc = px.bar(
                loc_summary, 
                x="location", 
                y="count", 
                color="status",
                color_discrete_map={"양호": "#22C55E", "주의": "#F59E0B", "불량": "#EF4444"},
                barmode="stack",
                text="count",
                labels={"location": "점검 구역", "count": "점검 건수", "status": "상태"}
            )
            fig_loc.update_layout(xaxis_tickangle=-30, height=360, margin=dict(l=20, r=20, t=30, b=50))
            st.plotly_chart(fig_loc, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with c2:
        st.subheader("🔍 안전 분야별 점검 비중")
        if not filtered_df.empty:
            cat_summary = filtered_df["category"].value_counts().reset_index()
            cat_summary.columns = ["category", "count"]
            fig_cat = px.pie(
                cat_summary, 
                values="count", 
                names="category", 
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_cat.update_layout(height=360, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 대시보드 차트 행 2
    c3, c4 = st.columns([5, 5])
    with c3:
        st.subheader("⚡ 위험도(Risk Level) 분석")
        if not filtered_df.empty:
            risk_order = ["낮음", "보통", "높음", "치명적"]
            risk_summary = filtered_df["risk_level"].value_counts().reindex(risk_order, fill_value=0).reset_index()
            risk_summary.columns = ["risk_level", "count"]
            fig_risk = px.bar(
                risk_summary,
                x="risk_level",
                y="count",
                color="risk_level",
                color_discrete_map={"낮음": "#3B82F6", "보통": "#FBBF24", "높음": "#F97316", "치명적": "#DC2626"},
                text="count"
            )
            fig_risk.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=20, b=30))
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with c4:
        st.subheader("📅 일별 점검 추이")
        if not filtered_df.empty:
            date_summary = filtered_df.groupby("date").size().reset_index(name="count")
            fig_date = px.line(
                date_summary, 
                x="date", 
                y="count", 
                markers=True,
                labels={"date": "점검 일자", "count": "점검 건수"}
            )
            fig_date.update_traces(line_color="#2563EB", line_width=3)
            fig_date.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=30))
            st.plotly_chart(fig_date, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 최근 점검 리스트
    st.subheader("📋 최근 점검 기록 요약")
    preview_cols = ["date", "facility", "location", "category", "item_name", "status", "risk_level", "action_status", "inspector"]
    st.dataframe(
        filtered_df[preview_cols].rename(columns={
            "date": "점검일자", "facility": "사업장", "location": "구역", "category": "분야",
            "item_name": "점검항목", "status": "결과", "risk_level": "위험도", "action_status": "조치상황", "inspector": "점검자"
        }),
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# TAB 2: 안전점검 일지 등록
# ==========================================
with tab2:
    st.subheader("✍️ 새로운 안전점검 일지 작성")
    st.write("현장 순회 점검 후 결과를 즉시 등록하세요. 등록된 정보는 실시간으로 대시보드에 반영됩니다.")

    with st.form("inspection_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            input_date = st.date_input("점검 일자", value=date.today())
            input_inspector = st.text_input("점검자 성명", placeholder="예: 김안전 책임")
        with col_f2:
            input_facility = st.selectbox("사업장 / 공장 구분", ["제1제조공장", "제2제조공장", "물류센터", "연구소/본사", "기타 사업장"])
            input_location = st.text_input("점검 상세 구역", placeholder="예: 프레스 3라인, 도장실, 옥외 가스실 등")
        with col_f3:
            input_category = st.selectbox("안전 분야", [
                "기계방호", "화재/소방", "전기안전", "유해물질", "추락/전도", 
                "개인보호구", "밀폐공간", "통로/환경", "기타"
            ])
            input_item = st.text_input("점검 세부 항목", placeholder="예: 비상정지 스위치 작동 점검, 소화기 게이지 확인")

        st.markdown("##### 📌 점검 판정 및 위험도 평가")
        col_eval1, col_eval2 = st.columns(2)
        with col_eval1:
            input_status = st.radio("점검 결과 판정", ["양호", "주의", "불량"], horizontal=True)
        with col_eval2:
            input_risk = st.select_slider("위험도 등급", options=["낮음", "보통", "높음", "치명적"], value="보통")

        input_desc = st.text_area("점검 상세 내용 및 현장 상태", placeholder="현장에서 확인된 정상 상태 또는 이상 부적합 사항을 구체적으로 기록해 주세요.")

        st.markdown("##### 🛠️ 시정 조치 사항 (주의 또는 불량 시 필수)")
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            input_action_status = st.selectbox("조치 진행 상태", ["완료", "조치중", "미조치"], index=0 if input_status=="양호" else 2)
        with col_act2:
            input_deadline = st.date_input("조치 예정 기한", value=date.today() + pd.Timedelta(days=7))
        with col_act3:
            input_assignee = st.text_input("조치 담당자/부서", placeholder="예: 공무팀 박과장")

        input_action = st.text_input("시정 조치 계획 및 결과 내용", placeholder="예: 신품 부품 발주 및 11/5 교체 완료 예정")

        submitted = st.form_submit_button("💾 안전점검 일지 등록하기", use_container_width=True, type="primary")

        if submitted:
            if not input_inspector or not input_location or not input_item:
                st.error("점검자 성명, 점검 상세 구역, 점검 세부 항목은 필수 입력값입니다!")
            else:
                db.add_inspection(
                    str(input_date),
                    input_inspector,
                    input_facility,
                    input_location,
                    input_category,
                    input_item,
                    input_status,
                    input_risk,
                    input_desc,
                    input_action,
                    input_action_status,
                    str(input_deadline) if input_status != "양호" else "",
                    input_assignee if input_status != "양호" else ""
                )
                st.success(f"✅ '{input_location} - {input_item}' 점검 기록이 성공적으로 저장되었습니다!")
                st.rerun()

# ==========================================
# TAB 3: 부적합 조치 관리
# ==========================================
with tab3:
    st.subheader("🛠️ 위해·위험 요인 및 부적합 사항 조치 관리")
    st.write("개선 권고(주의) 또는 즉시 시정(불량) 판정을 받은 항목들의 조치 이행 현황을 추적합니다.")

    defect_df = df[df["status"].isin(["주의", "불량"])].copy()

    if defect_df.empty:
        st.success("🎉 현재 등록된 위해·위험 요인이나 부적합 항목이 없습니다! 현장이 매우 안전하게 관리되고 있습니다.")
    else:
        # 조치 상태 수정 폼
        st.markdown("#### ⚡ 신속 조치 상태 갱신")
        item_options = {
            f"[{row['id']}] {row['date']} | {row['location']} - {row['item_name']} (현재: {row['action_status']})": row["id"]
            for _, row in defect_df.iterrows()
        }
        
        selected_label = st.selectbox("조치 상태를 변경할 항목을 선택하세요:", list(item_options.keys()))
        selected_id = item_options[selected_label]
        target_row = defect_df[defect_df["id"] == selected_id].iloc[0]

        with st.expander("📌 선택된 항목 세부 정보 및 상태 변경", expanded=True):
            st.info(f"**점검 내용:** {target_row['description'] or '기록 없음'}")
            st.warning(f"**현재 위험도:** {target_row['risk_level']} | **기존 조치계획:** {target_row['corrective_action'] or '없음'}")

            col_u1, col_u2 = st.columns([4, 6])
            with col_u1:
                new_act_status = st.selectbox("새로운 조치 상태", ["미조치", "조치중", "완료"], index=["미조치", "조치중", "완료"].index(target_row["action_status"]))
            with col_u2:
                new_action_text = st.text_input("조치 내용 보완 / 완료 보고", value=target_row["corrective_action"] or "")

            if st.button("수정사항 저장하기", type="primary"):
                db.update_action_status(selected_id, new_act_status, new_action_text)
                st.success(f"ID #{selected_id} 항목의 조치 상태가 '{new_act_status}'(으)로 갱신되었습니다!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 부적합 및 시정조치 목록 전체")
        st.dataframe(
            defect_df[["id", "date", "facility", "location", "category", "item_name", "status", "risk_level", "description", "corrective_action", "action_status", "action_deadline", "action_assignee"]],
            use_container_width=True,
            hide_index=True
        )

        # 엑셀/CSV 다운로드 버튼
        csv_data = defect_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 부적합 조치 목록 다운로드 (CSV)",
            data=csv_data,
            file_name=f"safety_actions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ==========================================
# TAB 4: 안전 수칙 & 분석 가이드
# ==========================================
with tab4:
    st.subheader("📖 산업안전보건 핵심 관리 수칙 및 체크포인트")
    st.markdown("""
    #### 🛡️ 중대재해 예방 3대 핵심 안전수칙
    1. **추락 방지 조치**: 안전난간, 개구부 덮개 설치 및 안전대 지급·착용 확인
    2. **끼임 방지 조치**: 회전체 덮개·울 설치, 방호장치 해제 금지, 정비 시 LOTO(전원 차단 및 표지판 부착) 철저
    3. **보호구 착용 철저**: 안전모, 안전화, 보안경, 방진/방독마스크 필수 지급 및 실착용 점검
    
    ---
    #### 📋 정기 안전점검 주기 권장 가이드
    * **일일 점검**: 기계 설비 가동 전 점검, 비상정지장치 테스트, 작업 전 TBM(Tool Box Meeting) 10분
    * **주간 점검**: 화재·소방 시설(소화기, 유도등), 통로 및 적치물 상태, 유해화학물질 저장 상태
    * **월간 점검**: 국소배기장치 풍속, 크레인·호이스트 와이어로프, 절연저항 및 접지선 상태
    """)
