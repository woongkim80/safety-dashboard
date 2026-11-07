import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import database as db
import ai_inspector

# 1. 페이지 설정
st.set_page_config(
    page_title="현장 안전점검 & 사업자별 통합 관리 대시보드",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터베이스 초기화
db.init_db()

# 커스텀 CSS (모바일 가독성 및 UI 뱃지 스타일)
st.markdown("""
<style>
    .main-title {
        font-size: 1.85rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    .badge-comp {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# 2. 데이터 불러오기
df = db.get_all_inspections()
company_list = db.get_companies()

# 3. 사이드바 - 다차원 필터링 및 사업자 관리
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/safety-shield.png", width=52)
    st.title("안전통합 필터")
    
    # 사업자 / 협력사 필터
    selected_company = st.selectbox("🏢 사업자 / 협력사 선택", ["전체"] + company_list)

    # 사업장 구분 필터
    facility_list = ["전체"] + sorted(df["facility"].dropna().unique().tolist())
    selected_facility = st.selectbox("🏭 사업장 구분", facility_list)
    
    # 안전 분야 필터
    category_list = ["전체"] + sorted(df["category"].dropna().unique().tolist())
    selected_category = st.selectbox("🔍 안전 점검 분야", category_list)

    # 점검 결과 필터
    status_list = ["전체", "양호", "주의", "불량"]
    selected_status = st.selectbox("📌 점검 판정 결과", status_list)

    # 조치 상태 필터
    action_list = ["전체", "미조치", "조치중", "완료"]
    selected_action = st.selectbox("⚙️ 시정조치 상태", action_list)

    st.divider()
    storage_info = db.get_storage_status()
    st.caption(f"💾 데이터베이스: **{storage_info['label']}**")
    if storage_info["is_gsheets"]:
        st.caption("☁️ 구글 시트 실시간 동기화 작동 중")
    else:
        st.caption("ℹ️ '구글 시트 연동' 탭에서 영구 보존 설정 가능")

    st.divider()
    st.subheader("🤖 Gemini AI 설정")
    gemini_api_key = st.text_input("Gemini API Key (선택)", type="password", help="키가 없을 경우 내장 안전규칙 데모 모드로 작동합니다.")
    st.caption("권장 모델: `gemini-1.5-flash`")

# 필터 적용
filtered_df = df.copy()
if selected_company != "전체":
    filtered_df = filtered_df[filtered_df["company"] == selected_company]
if selected_facility != "전체":
    filtered_df = filtered_df[filtered_df["facility"] == selected_facility]
if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]
if selected_status != "전체":
    filtered_df = filtered_df[filtered_df["status"] == selected_status]
if selected_action != "전체":
    filtered_df = filtered_df[filtered_df["action_status"] == selected_action]

# 상단 헤더
st.markdown('<div class="main-title">🛡️ 현장 안전점검 & 사업자별 통합 관리 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">원청·협력사별 점검 등록, 수정, 삭제 및 드론 AI 판독 실시간 대시보드</div>', unsafe_allow_html=True)

# 4. 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 종합 현황 대시보드", 
    "🛸 드론 사진 & 서류 AI 판독",
    "✍️ 안전점검 신규 등록", 
    "📝 점검 기록 수정 · 삭제",
    "🛠️ 부적합 조치 관리", 
    "📖 사업자별 안전가이드",
    "☁️ 구글 스프레드시트 연동"
])

# ==========================================
# TAB 1: 종합 현황 대시보드
# ==========================================
with tab1:
    total_count = len(filtered_df)
    pass_count = len(filtered_df[filtered_df["status"] == "양호"])
    warn_count = len(filtered_df[filtered_df["status"] == "주의"])
    fail_count = len(filtered_df[filtered_df["status"] == "불량"])
    
    pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
    unresolved_count = len(filtered_df[(filtered_df["status"].isin(["주의", "불량"])) & (filtered_df["action_status"] != "완료")])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 점검 건수", f"{total_count}건", delta=f"{len(df)}건 중 필터링")
    with col2:
        st.metric("✅ 안전 적합률", f"{pass_rate:.1f}%", delta=f"{pass_count}건 양호")
    with col3:
        st.metric("⚠️ 주의(개선권고)", f"{warn_count}건", delta_color="inverse", delta=f"{warn_count}건")
    with col4:
        st.metric("🚨 긴급 부적합(미조치)", f"{unresolved_count}건", delta_color="inverse", delta=f"불량 총 {fail_count}건")

    critical_items = filtered_df[(filtered_df["status"] == "불량") & (filtered_df["action_status"] != "완료")]
    if not critical_items.empty:
        st.error(f"🚨 **[긴급 조치 요구]** 현재 즉각 시정이 필요한 불량 항목이 **{len(critical_items)}건** 있습니다. 아래 현황을 확인하고 조치해 주세요!")

    st.markdown("---")

    # 차트 행 1: 사업자별 비교 차트 & 안전 분야 비중
    c1, c2 = st.columns([6, 4])
    with c1:
        st.subheader("🏢 사업자(원청/협력사)별 점검 결과 분포")
        if not filtered_df.empty:
            comp_summary = filtered_df.groupby(["company", "status"]).size().reset_index(name="count")
            fig_comp = px.bar(
                comp_summary, 
                x="company", 
                y="count", 
                color="status",
                color_discrete_map={"양호": "#22C55E", "주의": "#F59E0B", "불량": "#EF4444"},
                barmode="stack",
                text="count",
                labels={"company": "사업자/협력사명", "count": "점검 건수", "status": "상태"}
            )
            fig_comp.update_layout(xaxis_tickangle=-15, height=340, margin=dict(l=20, r=20, t=30, b=40))
            st.plotly_chart(fig_comp, use_container_width=True)
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
            fig_cat.update_layout(height=340, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 차트 행 2: 구역별 결함 현황 & 위험도 등급
    c3, c4 = st.columns([6, 4])
    with c3:
        st.subheader("📍 구역별 점검 현황")
        if not filtered_df.empty:
            loc_summary = filtered_df.groupby(["location", "status"]).size().reset_index(name="count")
            fig_loc = px.bar(
                loc_summary, 
                x="location", 
                y="count", 
                color="status",
                color_discrete_map={"양호": "#22C55E", "주의": "#F59E0B", "불량": "#EF4444"},
                barmode="group",
                labels={"location": "점검 구역", "count": "점검 건수"}
            )
            fig_loc.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=40))
            st.plotly_chart(fig_loc, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    with c4:
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
            fig_risk.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=20, b=30))
            st.plotly_chart(fig_risk, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # 최근 점검 리스트 요약
    st.subheader("📋 최근 점검 기록 요약")
    preview_cols = ["date", "company", "facility", "location", "category", "item_name", "status", "risk_level", "action_status", "inspector"]
    st.dataframe(
        filtered_df[preview_cols].rename(columns={
            "date": "점검일자", "company": "사업자/협력사", "facility": "사업장", "location": "구역", "category": "분야",
            "item_name": "점검항목", "status": "결과", "risk_level": "위험도", "action_status": "조치상황", "inspector": "점검자"
        }),
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# TAB 2: 드론 사진 & 서류 AI 판독
# ==========================================
with tab2:
    st.subheader("🛸 드론 항공사진 및 안전 서류 AI 자동 판독")
    st.write("현장에서 촬영한 고해상도 드론 사진이나 안전 서류를 업로드하면, Gemini 1.5 Flash가 **산업안전보건기준**에 따라 위험 요소를 자동 검출합니다.")

    uploaded_file = st.file_uploader(
        "📷 드론 항공사진 또는 현장 점검 사진 업로드 (JPG, PNG)", 
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        col_img, col_info = st.columns([5, 5])
        with col_img:
            st.image(uploaded_file, caption=f"업로드된 이미지: {uploaded_file.name}", use_container_width=True)

        with col_info:
            st.info("💡 안전난간, 개구부 덮개, 작업자 턱끈 체결, 중장비 신호수 배치 여부를 정밀 분석합니다.")
            if st.button("🔍 Gemini AI 현장 안전 분석 실행", type="primary", use_container_width=True):
                with st.spinner("Gemini AI가 고해상도 이미지를 정밀 분석 중입니다..."):
                    img_bytes = uploaded_file.getvalue()
                    analysis = ai_inspector.analyze_image_with_gemini(
                        img_bytes, 
                        mime_type=uploaded_file.type, 
                        api_key=gemini_api_key
                    )

                if "error" in analysis:
                    st.error(analysis["error"])
                else:
                    st.success("✅ AI 안전 판독이 완료되었습니다!")
                    
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("🛡️ 안전 점수 (100점 만점)", f"{analysis.get('safety_score', 70)}점")
                    with m2:
                        grade = analysis.get("overall_risk_grade", "주의")
                        st.metric("🚨 종합 위험 등급", grade)

                    st.markdown(f"**📌 총평:** {analysis.get('summary_review', '')}")

                    ppe = analysis.get("ppe_compliance", {})
                    st.markdown("##### 🦺 필수 보호구 준수 상태")
                    p1, p2, p3 = st.columns(3)
                    p1.write(f"안전모 착용: {'✅ 양호' if ppe.get('helmet_detected') else '❌ 미흡'}")
                    p2.write(f"턱끈 체결: {'✅ 정상' if ppe.get('chinstrap_fastened') else '🚨 풀림/미체결'}")
                    p3.write(f"안전대(그네): {'✅ 착용' if ppe.get('safety_harness') else '⚠️ 미착용/해당없음'}")

                    st.markdown("##### ⚠️ 검출된 위해·위험 요인")
                    hazards = analysis.get("detected_hazards", [])
                    for idx, h in enumerate(hazards, 1):
                        with st.expander(f"위험 #{idx}: {h.get('hazard_type')} [{h.get('risk_level', '보통')}]", expanded=True):
                            st.write(f"**법적 기준:** `{h.get('legal_basis')}`")
                            st.write(f"**상세 상황:** {h.get('description')}")
                            st.write(f"**권고 조치:** {h.get('suggested_action')}")

                    st.markdown("---")
                    st.markdown("##### 📋 점검 일지 자동 등록 설정")
                    col_ai_comp, col_ai_btn = st.columns([6, 4])
                    with col_ai_comp:
                        target_ai_company = st.selectbox("해당 위험 담당 사업자(협력사)", company_list, key="ai_target_comp")
                    with col_ai_btn:
                        st.write("")
                        st.write("")
                        if st.button("💾 점검 일지에 자동 등록하기", type="primary", use_container_width=True):
                            primary_hazard = hazards[0] if hazards else {}
                            db.add_inspection(
                                company=target_ai_company,
                                date=str(date.today()),
                                inspector="드론 AI 자동점검",
                                facility="현장 드론 구역",
                                location=analysis.get("inspection_title", "드론 촬영 공구"),
                                category=primary_hazard.get("hazard_type", "기계방호/추락"),
                                item_name="드론 항공 판독 결함",
                                status="불량" if grade in ["위험", "치명적"] else ("주의" if grade == "주의" else "양호"),
                                risk_level=primary_hazard.get("risk_level", "높음"),
                                description=primary_hazard.get("description", analysis.get("summary_review")),
                                corrective_action=primary_hazard.get("suggested_action", ""),
                                action_status="미조치",
                                action_deadline=str(date.today() + pd.Timedelta(days=3)),
                                action_assignee="현장 안전관리자"
                            )
                            st.success(f"🎉 '{target_ai_company}'의 점검 일지에 자동 등록되었습니다! 대시보드에서 즉시 반영됩니다.")
                            st.rerun()

# ==========================================
# TAB 3: 안전점검 신규 등록 (Create)
# ==========================================
with tab3:
    st.subheader("✍️ 사업자별 새로운 안전점검 일지 등록")
    st.write("원청 또는 협력사별 현장 순회 점검 후 결과를 등록하세요.")

    with st.form("new_inspection_form", clear_on_submit=True):
        col_c1, col_c2 = st.columns([6, 4])
        with col_c1:
            input_company_select = st.selectbox("🏢 사업자 / 협력사 선택", company_list + ["+ 신규 사업자 직접 입력"])
            input_new_company = st.text_input("새 사업자명 (직접 입력 선택 시)", placeholder="예: (주)한라엔지니어링")
        with col_c2:
            input_date = st.date_input("점검 일자", value=date.today())
            input_inspector = st.text_input("점검자 성명", placeholder="예: 김안전 책임")

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            input_facility = st.selectbox("사업장 / 공장 구분", ["제1제조공장", "제2제조공장", "물류센터", "건설 1공구", "기타 현장"])
            input_location = st.text_input("점검 상세 구역", placeholder="예: 프레스 3라인, 도장실, 타워크레인 하부 등")
        with col_f2:
            input_category = st.selectbox("안전 분야", [
                "기계방호", "화재/소방", "전기안전", "유해물질", "추락/전도", 
                "개인보호구", "밀폐공간", "통로/환경", "드론점검", "기타"
            ])
            input_item = st.text_input("점검 세부 항목", placeholder="예: 비상정지 스위치, 안전난간 고정 상태")

        st.markdown("##### 📌 점검 판정 및 위험도 평가")
        col_eval1, col_eval2 = st.columns(2)
        with col_eval1:
            input_status = st.radio("점검 결과 판정", ["양호", "주의", "불량"], horizontal=True)
        with col_eval2:
            input_risk = st.select_slider("위험도 등급", options=["낮음", "보통", "높음", "치명적"], value="보통")

        input_desc = st.text_area("점검 상세 내용 및 현장 상태", placeholder="현장에서 확인된 정상 상태 또는 이상 부적합 사항을 기록해 주세요.")

        st.markdown("##### 🛠️ 시정 조치 사항 (주의 또는 불량 시 필수)")
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            input_action_status = st.selectbox("조치 진행 상태", ["완료", "조치중", "미조치"], index=0 if input_status=="양호" else 2)
        with col_act2:
            input_deadline = st.date_input("조치 예정 기한", value=date.today() + pd.Timedelta(days=7))
        with col_act3:
            input_assignee = st.text_input("조치 담당자/부서", placeholder="예: 공무팀 박과장")

        input_action = st.text_input("시정 조치 계획 및 결과 내용", placeholder="예: 신품 부품 발주 및 교체 완료 예정")

        submitted = st.form_submit_button("💾 안전점검 일지 등록하기", use_container_width=True, type="primary")

        if submitted:
            # 사업자명 결정
            actual_company = input_new_company.strip() if input_company_select == "+ 신규 사업자 직접 입력" and input_new_company.strip() else input_company_select
            
            if not actual_company or not input_inspector or not input_location or not input_item:
                st.error("사업자명, 점검자 성명, 점검 상세 구역, 점검 세부 항목은 필수 입력값입니다!")
            else:
                db.add_inspection(
                    actual_company,
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
                st.success(f"✅ [{actual_company}] '{input_location} - {input_item}' 점검 기록이 성공적으로 등록되었습니다!")
                st.rerun()

# ==========================================
# TAB 4: 점검 기록 수정 · 삭제 (Update & Delete)
# ==========================================
with tab4:
    st.subheader("📝 점검 기록 수정 및 삭제 관리 (CRUD)")
    st.write("등록된 점검 기록의 세부 내용을 수정하거나, 잘못 입력된 데이터를 안전하게 삭제할 수 있습니다.")

    if df.empty:
        st.info("등록된 점검 기록이 없습니다.")
    else:
        # 수정/삭제 대상 선택 옵션 리스트
        record_options = {
            f"[#{row['id']}] {row['date']} | {row['company']} | {row['location']} - {row['item_name']} ({row['status']})": row["id"]
            for _, row in df.iterrows()
        }

        selected_record_label = st.selectbox("수정 또는 삭제할 점검 기록을 선택하세요:", list(record_options.keys()))
        selected_rec_id = record_options[selected_record_label]
        target_rec = df[df["id"] == selected_rec_id].iloc[0]

        # 탭 안에서 [수정 폼]과 [삭제 섹션] 분리
        col_edit_main, col_del_main = st.columns([7, 3])

        with col_edit_main:
            st.markdown(f"#### ✏️ [ID #{selected_rec_id}] 점검 정보 수정")
            with st.form("edit_inspection_form"):
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    edit_company = st.text_input("사업자 / 협력사명", value=target_rec["company"] or "")
                    edit_inspector = st.text_input("점검자 성명", value=target_rec["inspector"] or "")
                    edit_facility = st.text_input("사업장 구분", value=target_rec["facility"] or "")
                    edit_location = st.text_input("점검 상세 구역", value=target_rec["location"] or "")
                with col_e2:
                    try:
                        parsed_date = datetime.strptime(target_rec["date"], "%Y-%m-%d").date()
                    except:
                        parsed_date = date.today()
                    edit_date = st.date_input("점검 일자", value=parsed_date)
                    edit_category = st.selectbox(
                        "안전 분야", 
                        ["기계방호", "화재/소방", "전기안전", "유해물질", "추락/전도", "개인보호구", "밀폐공간", "통로/환경", "드론점검", "기타"],
                        index=["기계방호", "화재/소방", "전기안전", "유해물질", "추락/전도", "개인보호구", "밀폐공간", "통로/환경", "드론점검", "기타"].index(target_rec["category"]) if target_rec["category"] in ["기계방호", "화재/소방", "전기안전", "유해물질", "추락/전도", "개인보호구", "밀폐공간", "통로/환경", "드론점검", "기타"] else 0
                    )
                    edit_item = st.text_input("점검 세부 항목", value=target_rec["item_name"] or "")

                col_eval_e1, col_eval_e2 = st.columns(2)
                with col_eval_e1:
                    status_idx = ["양호", "주의", "불량"].index(target_rec["status"]) if target_rec["status"] in ["양호", "주의", "불량"] else 0
                    edit_status = st.radio("점검 결과", ["양호", "주의", "불량"], index=status_idx, horizontal=True)
                with col_eval_e2:
                    risk_idx = ["낮음", "보통", "높음", "치명적"].index(target_rec["risk_level"]) if target_rec["risk_level"] in ["낮음", "보통", "높음", "치명적"] else 1
                    edit_risk = st.select_slider("위험도", options=["낮음", "보통", "높음", "치명적"], value=["낮음", "보통", "높음", "치명적"][risk_idx])

                edit_desc = st.text_area("점검 상세 내용", value=target_rec["description"] or "")

                st.markdown("##### 🛠️ 시정 조치 사항")
                col_ea1, col_ea2, col_ea3 = st.columns(3)
                with col_ea1:
                    act_idx = ["완료", "조치중", "미조치"].index(target_rec["action_status"]) if target_rec["action_status"] in ["완료", "조치중", "미조치"] else 0
                    edit_act_status = st.selectbox("조치 상태", ["완료", "조치중", "미조치"], index=act_idx)
                with col_ea2:
                    edit_deadline = st.text_input("조치 기한", value=target_rec["action_deadline"] or "")
                with col_ea3:
                    edit_assignee = st.text_input("조치 담당자", value=target_rec["action_assignee"] or "")

                edit_action = st.text_input("조치 내용 및 계획", value=target_rec["corrective_action"] or "")

                btn_update = st.form_submit_button("💾 수정사항 저장하기", type="primary", use_container_width=True)
                if btn_update:
                    db.update_inspection(
                        selected_rec_id,
                        edit_company.strip(),
                        str(edit_date),
                        edit_inspector.strip(),
                        edit_facility.strip(),
                        edit_location.strip(),
                        edit_category,
                        edit_item.strip(),
                        edit_status,
                        edit_risk,
                        edit_desc,
                        edit_action,
                        edit_act_status,
                        edit_deadline,
                        edit_assignee
                    )
                    st.success(f"ID #{selected_rec_id} 점검 기록이 성공적으로 수정되었습니다!")
                    st.rerun()

        with col_del_main:
            st.markdown(f"#### 🗑️ [ID #{selected_rec_id}] 삭제")
            st.warning("⚠️ 삭제된 데이터는 복구할 수 없습니다.")
            confirm_delete = st.checkbox("해당 점검 기록을 영구 삭제하는 것에 동의합니다.", key=f"del_confirm_{selected_rec_id}")
            if st.button("🗑️ 영구 삭제 실행", type="secondary", use_container_width=True, disabled=not confirm_delete):
                db.delete_inspection(selected_rec_id)
                st.success(f"ID #{selected_rec_id} 점검 기록이 완전히 삭제되었습니다.")
                st.rerun()

# ==========================================
# TAB 5: 부적합 조치 관리
# ==========================================
with tab5:
    st.subheader("🛠️ 사업자별 위해·위험 요인 시정조치 관리")
    st.write("개선 권고(주의) 또는 즉시 시정(불량) 판정을 받은 사업자별 조치 이행 현황을 추적합니다.")

    defect_df = filtered_df[filtered_df["status"].isin(["주의", "불량"])].copy()

    if defect_df.empty:
        st.success("🎉 현재 선택된 조건에 부적합(주의/불량) 항목이 없습니다!")
    else:
        st.markdown("#### ⚡ 신속 조치 상태 갱신")
        item_options = {
            f"[{row['id']}] {row['company']} | {row['location']} - {row['item_name']} (현재: {row['action_status']})": row["id"]
            for _, row in defect_df.iterrows()
        }
        
        selected_label = st.selectbox("조치 상태를 변경할 항목을 선택하세요:", list(item_options.keys()))
        selected_id = item_options[selected_label]
        target_row = defect_df[defect_df["id"] == selected_id].iloc[0]

        with st.expander("📌 선택된 항목 세부 정보 및 상태 변경", expanded=True):
            st.info(f"**담당 사업자:** {target_row['company']} | **점검 내용:** {target_row['description'] or '기록 없음'}")
            st.warning(f"**위험도:** {target_row['risk_level']} | **기존 조치계획:** {target_row['corrective_action'] or '없음'}")

            col_u1, col_u2 = st.columns([4, 6])
            with col_u1:
                new_act_status = st.selectbox("새로운 조치 상태", ["미조치", "조치중", "완료"], index=["미조치", "조치중", "완료"].index(target_row["action_status"]))
            with col_u2:
                new_action_text = st.text_input("조치 내용 보완 / 완료 보고", value=target_row["corrective_action"] or "")

            if st.button("상태 변경 저장하기", type="primary"):
                db.update_action_status(selected_id, new_act_status, new_action_text)
                st.success(f"ID #{selected_id} 항목의 조치 상태가 '{new_act_status}'(으)로 갱신되었습니다!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 부적합 및 시정조치 목록 전체")
        st.dataframe(
            defect_df[["id", "company", "date", "facility", "location", "category", "item_name", "status", "risk_level", "description", "corrective_action", "action_status", "action_deadline", "action_assignee"]],
            use_container_width=True,
            hide_index=True
        )

        csv_data = defect_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 부적합 조치 목록 다운로드 (CSV)",
            data=csv_data,
            file_name=f"safety_actions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# ==========================================
# TAB 6: 사업자별 안전가이드
# ==========================================
with tab6:
    st.subheader("📖 산업안전보건법상 도급인(원청) 및 수급인(협력사) 의무사항")
    st.markdown("""
    #### 🛡️ 중대재해처벌법 및 산안법 제63조 도급인의 안전조치 의무
    1. **안전보건협의체 구성 및 운영**: 원청과 협력업체 전원이 매월 1회 이상 정기 협의체 회의 실시
    2. **작업장 합동 안전보건점검**: 
       * 건설업 및 조선업: 2개월에 1회 이상 합동 점검
       * 기타 제조업: 분기 1회 이상 정기 합동 순회 점검
    3. **위험성평가 실시 및 협력업체 참여**: 유해·위험요인 파악 시 협력업체 근로자의 의견을 반드시 청취하고 개선대책 수립
    
    ---
    #### 🏢 수급인(협력사)의 필수 안전조치
    * 작업 시작 전 안전점검(TBM) 일지 매일 작성 및 근로자 공유
    * 신규 근로자 채용 시 안전보건교육(건설업 기초안전보건교육 포함) 이수 확인
    * 지급된 개인보호구(안전모, 안전화, 안전대) 전원 착용 상태 상시 감독
    """)

# ==========================================
# TAB 7: 구글 스프레드시트 연동 관리
# ==========================================
with tab7:
    st.subheader("☁️ 구글 스프레드시트(Google Sheets) 영구 데이터베이스 연동")
    st.write("클라우드 서버가 재부팅되어도 현장 점검 일지가 영구 보존되도록 Google Sheets와 실시간 동기화합니다.")

    cur_storage = db.get_storage_status()
    if cur_storage["is_gsheets"]:
        st.success(f"🎉 **{cur_storage['label']}**")
        st.info(f"**연동 시트 URL / 식별자:** `{cur_storage['detail']}`\n\n모든 신규 등록, 수정, 삭제 작업이 구글 시트에 실시간으로 영구 기록됩니다.")
    else:
        st.warning(f"⚠️ **{cur_storage['label']}**\n\n현재 로컬 파일(SQLite)에 저장 중입니다. Streamlit Cloud가 장기 미사용으로 재부팅될 때 데이터를 영구 보존하려면 아래 가이드에 따라 구글 시트를 연동해 주세요.")

    st.markdown("---")
    st.markdown("### 📋 1단계: 구글 시트 초기 템플릿(데이터) 준비")
    st.write("현재 등록되어 있는 점검 데이터를 구글 시트에 바로 붙여넣거나 가져올 수 있는 CSV 파일로 다운로드합니다.")
    
    current_csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 구글 시트용 초기 점검 데이터 다운로드 (CSV)",
        data=current_csv,
        file_name=f"safety_records_template_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown("### 🚀 2단계: 3분 완성 구글 시트 연동 방법")
    st.markdown("""
    1. **구글 스프레드시트 만들기**:
       * [Google Sheets (새 스프레드시트)](https://sheets.new)에 접속하여 새 시트를 생성합니다.
       * 메뉴에서 **[파일] ➔ [가져오기] ➔ [업로드]**를 선택하여 위에서 다운로드한 CSV 파일을 업로드합니다.
    2. **시트 공유 설정**:
       * 우측 상단 **[공유]** 버튼 클릭 ➔ 일반 액세스를 **'링크가 있는 모든 사용자' (뷰어 또는 편집자)**로 설정합니다.
       * **[링크 복사]**를 누릅니다.
    3. **Streamlit Cloud에 시트 주소 등록**:
       * Streamlit Cloud 대시보드([share.streamlit.io](https://share.streamlit.io))로 이동합니다.
       * 내 앱 우측 **점 3개(`⋮`) ➔ [Settings] ➔ [Secrets]** 메뉴로 들어갑니다.
       * 아래 템플릿을 복사하여 내 구글 시트 주소를 붙여넣고 **[Save]**를 클릭합니다:

    ```toml
    [connections.gsheets]
    spreadsheet = "https://docs.google.com/spreadsheets/d/여러분의_구글시트_ID/edit"
    ```
    4. **완료!** 저장이 완료되면 대시보드가 자동으로 새로고침되며 구글 시트와 실시간 연동됩니다.
    """)
