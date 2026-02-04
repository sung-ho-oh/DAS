"""
당직 예정자 LIST / 발령 관리
- 월별 당직 발령 예정자 조회/입력/수정/삭제
- 총당직 + 부당직 명단 병기 표시
- 휴무일 행 별도 색상 구분
- LAST 사번 기반 순번 자동배정
"""
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from components.common_ui import page_header, page_footer, show_success, show_error, show_info
from components.duty_rules_help import show_duty_rules
from services import assignment_service

page_header("당직 예정자 LIST", "📋")

# ── 월 선택 ──
col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    year = st.selectbox("연도", range(2024, 2027), index=1)  # 2025 기본값
with col2:
    month = st.selectbox("월", range(1, 13), index=datetime.now().month - 1)

# ── 발령 조회 ──
try:
    assignments = assignment_service.get_assignments_by_month(year, month)

    if assignments:
        # DataFrame 변환 및 표시 형식 정리
        df = pd.DataFrame(assignments)

        # 직원 정보 조인 (간단한 표시용)
        display_data = []
        for asmt in assignments:
            main_name = asmt.get("main_duty", {}).get("name", "-") if isinstance(asmt.get("main_duty"), dict) else "-"
            sub_name = asmt.get("sub_duty", {}).get("name", "-") if isinstance(asmt.get("sub_duty"), dict) else "-"

            display_data.append({
                "일자": asmt["duty_date"],
                "요일": asmt["day_of_week"],
                "구분": asmt["day_category"],
                "근무": asmt["duty_type"],
                "총당직": main_name,
                "부당직": sub_name,
                "상태": asmt["status"],
                "id": asmt["id"],
            })

        display_df = pd.DataFrame(display_data)

        # 휴무일 행 스타일링
        def highlight_holiday(row):
            if row["구분"] == "휴무일":
                return ["background-color: #FFF3E0"] * len(row)
            return [""] * len(row)

        styled_df = display_df.drop(columns=["id"]).style.apply(highlight_holiday, axis=1)

        st.dataframe(styled_df, use_container_width=True, height=400)
        st.caption(f"총 {len(assignments)}건 조회됨")

    else:
        show_info(f"{year}년 {month}월 발령 데이터가 없습니다.")

except Exception as e:
    show_error(f"데이터 조회 실패: {e}")

# ── 발령 등록 ──
st.markdown("---")
st.subheader("📝 새 발령 등록")

with st.form("new_assignment_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        duty_date = st.date_input("당직일자", value=date(year, month, 1))
        day_of_week = ["월", "화", "수", "목", "금", "토", "일"][duty_date.weekday()]
        st.text_input("요일", value=day_of_week, disabled=True)

    with col2:
        is_holiday = duty_date.weekday() >= 5
        day_category = st.selectbox("구분", ["휴무일", "평일"], index=0 if is_holiday else 1)
        duty_type = st.selectbox("근무", ["주간", "야간"])

    with col3:
        status = st.selectbox("상태", ["예정", "확정", "변경", "완료"])

    st.markdown("**당직자 지정**")
    col1, col2, col3 = st.columns([3, 3, 4])

    with col1:
        main_emp_no = st.text_input("총당직 사번")
    with col2:
        sub_emp_no = st.text_input("부당직 사번")
    with col3:
        if st.form_submit_button("🤖 자동배정", help="LAST 사번 기반 자동 배정"):
            try:
                main_auto = assignment_service.auto_assign_next("총당직", day_category)
                sub_auto = assignment_service.auto_assign_next("부당직", day_category)

                if main_auto and sub_auto:
                    st.session_state["auto_main"] = main_auto["employee_no"]
                    st.session_state["auto_sub"] = sub_auto["employee_no"]
                    st.rerun()
            except Exception as e:
                show_error(f"자동배정 실패: {e}")

    # 자동배정 결과 표시
    if "auto_main" in st.session_state:
        st.info(f"자동배정 결과: 총당직 {st.session_state.get('auto_main')} / 부당직 {st.session_state.get('auto_sub')}")

    submitted = st.form_submit_button("✅ 등록", type="primary")

    if submitted:
        try:
            # 자동배정 결과 사용
            if main_emp_no == "" and "auto_main" in st.session_state:
                main_emp_no = st.session_state.get("auto_main")
            if sub_emp_no == "" and "auto_sub" in st.session_state:
                sub_emp_no = st.session_state.get("auto_sub")

            # 직원 조회하여 UUID 가져오기
            from services import db
            main_emps = db.select_where("employees", "employee_no", main_emp_no)
            sub_emps = db.select_where("employees", "employee_no", sub_emp_no)

            if not main_emps or not sub_emps:
                show_error("입력한 사번의 직원을 찾을 수 없습니다.")
            else:
                new_assignment = {
                    "duty_date": duty_date.isoformat(),
                    "day_of_week": day_of_week,
                    "duty_type": duty_type,
                    "day_category": day_category,
                    "main_duty_id": main_emps[0]["id"],
                    "sub_duty_id": sub_emps[0]["id"],
                    "status": status,
                }

                result = assignment_service.create_assignment(new_assignment)
                show_success("발령이 등록되었습니다.")

                # 자동배정 세션 클리어
                if "auto_main" in st.session_state:
                    del st.session_state["auto_main"]
                if "auto_sub" in st.session_state:
                    del st.session_state["auto_sub"]

                st.rerun()

        except Exception as e:
            show_error(f"등록 실패: {e}")

# ── 도움말 ──
show_duty_rules()

page_footer()
