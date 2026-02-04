"""
당직일정 변경등록 / 변경자 LIST
- 변경 전/후 당직자 + 변경사유 입력
- 변경자 LIST: 당직구분별 SORT
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.common_ui import page_header, page_footer
from services import change_service, assignment_service, db
from config import CHANGE_REASONS

page_header("당직일정 변경", "🔄")

# ── 탭 구성 ──
tab1, tab2 = st.tabs(["📝 변경 등록", "📋 변경 이력 조회"])

# ── 탭1: 변경 등록 ──
with tab1:
    st.subheader("📝 당직 변경 등록")

    # 월 선택
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox(
            "연도",
            range(datetime.now().year - 1, datetime.now().year + 2),
            index=1,
            key="change_year",
        )
    with col2:
        selected_month = st.selectbox(
            "월",
            range(1, 13),
            index=datetime.now().month - 1,
            key="change_month",
        )

    # 해당 월의 발령 조회
    assignments = assignment_service.get_assignments_by_month(selected_year, selected_month)

    if not assignments:
        st.warning(f"{selected_year}년 {selected_month}월 발령이 없습니다. 먼저 발령을 생성해주세요.")
    else:
        st.markdown("---")

        # 변경 대상 발령 선택 (최적화: JOIN된 데이터 사용)
        assignment_options = {}
        for asmt in assignments:
            main_duty = asmt.get("main_duty")
            sub_duty = asmt.get("sub_duty")

            main_name = f"{main_duty['name']}({main_duty['employee_no']})" if main_duty else "-"
            sub_name = f"{sub_duty['name']}({sub_duty['employee_no']})" if sub_duty else "-"

            label = f"{asmt['duty_date']} ({asmt['day_of_week']}) - 총:{main_name} / 부:{sub_name}"
            assignment_options[label] = asmt

        selected_assignment_label = st.selectbox(
            "변경할 발령 선택",
            options=list(assignment_options.keys()),
        )

        selected_assignment = assignment_options[selected_assignment_label]

        # 변경 정보 입력
        col1, col2, col3 = st.columns(3)

        with col1:
            duty_role = st.radio("변경 대상", ["총당직", "부당직"])

        with col2:
            change_reason = st.selectbox("변경 사유", CHANGE_REASONS)

        with col3:
            change_date = st.date_input("변경일", value=datetime.now())

        # 원본 직원 정보 표시
        if duty_role == "총당직":
            original_employee_id = selected_assignment["main_duty_id"]
            original_employee = db.select_by_id("employees", original_employee_id)
        else:
            original_employee_id = selected_assignment["sub_duty_id"]
            original_employee = db.select_by_id("employees", original_employee_id)

        st.info(f"**변경 전 당직자**: {original_employee['name']} ({original_employee['employee_no']})")

        # 변경 후 직원 선택
        eligible_employees = assignment_service.get_eligible_employees(
            duty_role, selected_assignment["day_category"]
        )

        employee_options = {
            f"{emp['name']} ({emp['employee_no']}) - {emp['position']}": emp["id"]
            for emp in eligible_employees
        }

        selected_new_employee_label = st.selectbox(
            "변경 후 당직자",
            options=list(employee_options.keys()),
        )

        new_employee_id = employee_options[selected_new_employee_label]

        # 변경 등록 버튼
        if st.button("✅ 변경 등록", type="primary", use_container_width=True):
            if new_employee_id == original_employee_id:
                st.error("동일한 직원으로는 변경할 수 없습니다.")
            else:
                change_service.create_change({
                    "assignment_id": selected_assignment["id"],
                    "original_employee_id": original_employee_id,
                    "new_employee_id": new_employee_id,
                    "duty_role": duty_role,
                    "change_reason": change_reason,
                    "change_date": str(change_date),
                })

                st.success("✅ 변경이 등록되었습니다!")
                st.cache_data.clear()
                st.rerun()

# ── 탭2: 변경 이력 조회 ──
with tab2:
    st.subheader("📋 월별 변경 이력")

    # 월 선택
    col1, col2 = st.columns(2)
    with col1:
        history_year = st.selectbox(
            "연도",
            range(datetime.now().year - 1, datetime.now().year + 2),
            index=1,
            key="history_year",
        )
    with col2:
        history_month = st.selectbox(
            "월",
            range(1, 13),
            index=datetime.now().month - 1,
            key="history_month",
        )

    # 변경 이력 조회
    changes = change_service.get_changes_by_month(history_year, history_month)

    if not changes:
        st.info(f"{history_year}년 {history_month}월 변경 이력이 없습니다.")
    else:
        # 데이터프레임 생성
        df_data = []
        for change in changes:
            original_emp = change["original_employee"]
            new_emp = change["new_employee"]
            asmt = change["assignment"]

            df_data.append({
                "변경일": change["change_date"],
                "당직일": asmt["duty_date"],
                "요일": asmt["day_of_week"],
                "구분": change["duty_role"],
                "변경 전": f"{original_emp['name']} ({original_emp['employee_no']})",
                "변경 후": f"{new_emp['name']} ({new_emp['employee_no']})",
                "사유": change["change_reason"],
            })

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"총 {len(changes)}건")

page_footer()
