"""
당직일정 변경등록 / 변경자 LIST
- 변경 전/후 당직자 + 변경사유 입력
- 변경자 LIST: 당직구분별 SORT
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.common_ui import page_header, page_footer, show_success, show_error, show_info
from services import change_service, assignment_service, db
from config import CHANGE_REASONS

page_header("당직일정 변경", "🔄")

# ── 월 선택 ──
col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    year = st.selectbox("연도", range(2024, 2027), index=1, key="change_year")
with col2:
    month = st.selectbox("월", range(1, 13), index=datetime.now().month - 1, key="change_month")

# ── 변경 이력 조회 ──
try:
    changes = change_service.get_changes_by_month(year, month)

    if changes:
        display_data = []
        for change in changes:
            asmt = change.get("assignment", {})
            orig_emp = change.get("original", {})
            new_emp = change.get("new", {})

            display_data.append({
                "변경일": change["change_date"],
                "당직일": asmt.get("duty_date", "-") if asmt else "-",
                "구분": change["duty_role"],
                "변경 전": orig_emp.get("name", "-") if orig_emp else "-",
                "변경 후": new_emp.get("name", "-") if new_emp else "-",
                "사유": change["change_reason"],
            })

        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, use_container_width=True, height=400)
        st.caption(f"총 {len(changes)}건 조회됨")

    else:
        show_info(f"{year}년 {month}월 변경 이력이 없습니다.")

except Exception as e:
    show_error(f"데이터 조회 실패: {e}")

# ── 변경 등록 ──
st.markdown("---")
st.subheader("📝 변경 등록")

with st.form("new_change_form"):
    col1, col2 = st.columns(2)

    with col1:
        # 당직 발령 선택 (당월 발령만)
        try:
            assignments = assignment_service.get_assignments_by_month(year, month)
            if assignments:
                asmt_options = {}
                for asmt in assignments:
                    main_name = asmt.get("main_duty", {}).get("name", "-") if isinstance(asmt.get("main_duty"), dict) else "-"
                    sub_name = asmt.get("sub_duty", {}).get("name", "-") if isinstance(asmt.get("sub_duty"), dict) else "-"
                    label = f"{asmt['duty_date']} {asmt['duty_type']} (총:{main_name}, 부:{sub_name})"
                    asmt_options[label] = asmt

                selected_asmt_label = st.selectbox("변경할 당직 선택", list(asmt_options.keys()))
                selected_asmt = asmt_options[selected_asmt_label]
            else:
                st.warning("선택한 월에 당직 발령이 없습니다.")
                selected_asmt = None
        except Exception as e:
            st.error(f"발령 조회 실패: {e}")
            selected_asmt = None

        change_role = st.selectbox("변경 구분", ["총당직", "부당직"])

    with col2:
        change_reason = st.selectbox("변경 사유", CHANGE_REASONS)
        new_emp_no = st.text_input("변경 후 사번")

    submitted = st.form_submit_button("✅ 등록", type="primary")

    if submitted and selected_asmt:
        try:
            # 직원 조회
            new_emps = db.select_where("employees", "employee_no", new_emp_no)

            if not new_emps:
                show_error("입력한 사번의 직원을 찾을 수 없습니다.")
            else:
                # 변경 전 직원 ID 가져오기
                if change_role == "총당직":
                    original_emp_id = selected_asmt["main_duty_id"]
                else:
                    original_emp_id = selected_asmt["sub_duty_id"]

                new_change = {
                    "assignment_id": selected_asmt["id"],
                    "original_employee_id": original_emp_id,
                    "new_employee_id": new_emps[0]["id"],
                    "duty_role": change_role,
                    "change_reason": change_reason,
                    "change_date": selected_asmt["duty_date"],
                }

                result = change_service.create_change(new_change)
                show_success("변경이 등록되었습니다.")
                st.rerun()

        except Exception as e:
            show_error(f"등록 실패: {e}")

page_footer()
