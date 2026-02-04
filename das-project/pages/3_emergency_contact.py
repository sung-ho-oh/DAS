"""
비상연락망 관리
- 직원별 비상연락처 CRUD
- 성명으로 SORT, 사번 입력 시 자동조회
"""
import streamlit as st
import pandas as pd
from components.common_ui import page_header, page_footer, show_success, show_error, show_info
from services import db

page_header("비상연락망", "📞")

# ── 검색 ──
col1, col2, col3 = st.columns([2, 2, 6])
with col1:
    search_emp_no = st.text_input("사번 검색", placeholder="E1001")
with col2:
    search_name = st.text_input("성명 검색", placeholder="홍길동")

# ── 연락망 조회 ──
try:
    # 전체 직원 + 비상연락망 조인
    client = db.get_client()
    query = (
        client.table("employees")
        .select("*, contact:emergency_contacts(*)")
        .eq("is_active", True)
        .order("name")
    )

    # 검색 조건 추가
    if search_emp_no:
        query = query.ilike("employee_no", f"%{search_emp_no}%")
    if search_name:
        query = query.ilike("name", f"%{search_name}%")

    response = query.execute()
    employees = response.data

    if employees:
        display_data = []
        for emp in employees:
            contact = emp.get("contact")
            if contact and isinstance(contact, list) and len(contact) > 0:
                contact = contact[0]

            display_data.append({
                "사번": emp["employee_no"],
                "성명": emp["name"],
                "소속": emp["department"],
                "직위": emp["position"],
                "공장": emp["factory"],
                "자택전화": contact.get("phone_home", "-") if contact else "-",
                "핸드폰": contact.get("phone_mobile", "-") if contact else "-",
                "비고": contact.get("note", "") if contact else "",
                "employee_id": emp["id"],
                "contact_id": contact.get("id") if contact else None,
            })

        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df.drop(columns=["employee_id", "contact_id"]), use_container_width=True, height=400)
        st.caption(f"총 {len(employees)}명 조회됨")

    else:
        show_info("조회 결과가 없습니다.")

except Exception as e:
    show_error(f"데이터 조회 실패: {e}")

# ── 연락처 등록/수정 ──
st.markdown("---")
st.subheader("📝 연락처 등록/수정")

with st.form("contact_form"):
    col1, col2 = st.columns(2)

    with col1:
        emp_no = st.text_input("사번", placeholder="E1001")
        phone_home = st.text_input("자택전화", placeholder="055-123-4567")

    with col2:
        phone_mobile = st.text_input("핸드폰", placeholder="010-1234-5678")
        note = st.text_area("비고", height=80)

    submitted = st.form_submit_button("✅ 저장", type="primary")

    if submitted:
        try:
            # 직원 조회
            emps = db.select_where("employees", "employee_no", emp_no)

            if not emps:
                show_error("입력한 사번의 직원을 찾을 수 없습니다.")
            else:
                emp_id = emps[0]["id"]

                # 기존 연락처 확인
                existing_contacts = db.select_where("emergency_contacts", "employee_id", emp_id)

                contact_data = {
                    "employee_id": emp_id,
                    "phone_home": phone_home,
                    "phone_mobile": phone_mobile,
                    "note": note,
                }

                if existing_contacts:
                    # 수정
                    db.update("emergency_contacts", existing_contacts[0]["id"], contact_data)
                    show_success("연락처가 수정되었습니다.")
                else:
                    # 신규 등록
                    db.insert("emergency_contacts", contact_data)
                    show_success("연락처가 등록되었습니다.")

                st.rerun()

        except Exception as e:
            show_error(f"저장 실패: {e}")

page_footer()
