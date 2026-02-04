"""
비상연락망 관리
- 직원별 비상연락처 CRUD
- 성명으로 SORT, 사번 입력 시 자동조회
"""
import streamlit as st
import pandas as pd
from components.common_ui import page_header, page_footer
from services import db
from config import FACTORIES, FACTORY1_DEPARTMENTS, FACTORY2_DEPARTMENTS

page_header("비상연락망", "📞")

# ── 필터 ──
col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    filter_factory = st.selectbox("공장", ["전체"] + FACTORIES)

with col2:
    if filter_factory == "전체":
        departments = []
    elif filter_factory == "창원1공장":
        departments = FACTORY1_DEPARTMENTS
    else:
        departments = FACTORY2_DEPARTMENTS

    filter_department = st.selectbox("부서", ["전체"] + departments) if departments else st.selectbox("부서", ["전체"])

with col3:
    search_query = st.text_input("🔍 검색 (이름 또는 사번)", placeholder="홍길동 또는 E1001")

st.markdown("---")

# ── 연락망 조회 ──
@st.cache_data(ttl=30)
def load_contacts():
    """비상연락망 조회 (최적화: 한 번에 조회)"""
    # 모든 직원 조회
    employees = db.select_all("employees", order_by="name")

    # 모든 연락망 한 번에 조회
    all_contacts = db.select_all("emergency_contacts")

    # employee_id로 매핑 (O(1) 조회를 위해)
    contact_map = {c["employee_id"]: c for c in all_contacts}

    contacts_data = []
    for emp in employees:
        # 메모리에서 연락망 조회 (DB 호출 없음)
        contact_info = contact_map.get(emp["id"])

        contacts_data.append({
            "employee_id": emp["id"],
            "employee_no": emp["employee_no"],
            "name": emp["name"],
            "department": emp["department"],
            "position": emp["position"],
            "factory": emp["factory"],
            "phone_home": contact_info["phone_home"] if contact_info else "",
            "phone_mobile": contact_info["phone_mobile"] if contact_info else "",
            "note": contact_info.get("note", "") if contact_info else "",
            "contact_id": contact_info["id"] if contact_info else None,
        })

    return contacts_data


contacts = load_contacts()

# 필터링
filtered_contacts = contacts

if filter_factory != "전체":
    filtered_contacts = [c for c in filtered_contacts if c["factory"] == filter_factory]

if filter_department != "전체":
    filtered_contacts = [c for c in filtered_contacts if c["department"] == filter_department]

if search_query:
    search_query_lower = search_query.lower()
    filtered_contacts = [
        c for c in filtered_contacts
        if search_query_lower in c["name"].lower() or search_query_lower in c["employee_no"].lower()
    ]

# ── 연락망 목록 표시 ──
st.subheader(f"📞 비상연락망 ({len(filtered_contacts)}명)")

if not filtered_contacts:
    st.info("조건에 맞는 직원이 없습니다.")
else:
    df = pd.DataFrame(filtered_contacts)
    display_df = df[[
        "employee_no", "name", "department", "position",
        "phone_home", "phone_mobile", "note"
    ]].rename(columns={
        "employee_no": "사번",
        "name": "성명",
        "department": "부서",
        "position": "직위",
        "phone_home": "자택전화",
        "phone_mobile": "핸드폰",
        "note": "비고",
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

# ── 연락망 등록/수정 ──
st.subheader("✏️ 연락망 등록/수정")

with st.expander("📝 연락망 정보 입력"):
    # 직원 선택
    employee_options = {
        f"{c['name']} ({c['employee_no']}) - {c['department']}": c
        for c in contacts
    }

    selected_employee_label = st.selectbox(
        "직원 선택",
        options=list(employee_options.keys()),
    )

    selected_contact = employee_options[selected_employee_label]

    col1, col2 = st.columns(2)

    with col1:
        phone_home = st.text_input(
            "자택전화",
            value=selected_contact["phone_home"],
            placeholder="02-1234-5678",
        )

    with col2:
        phone_mobile = st.text_input(
            "핸드폰",
            value=selected_contact["phone_mobile"],
            placeholder="010-1234-5678",
        )

    note = st.text_area(
        "비고",
        value=selected_contact["note"],
        placeholder="추가 정보 입력",
    )

    # 저장 버튼
    if st.button("💾 저장", type="primary", use_container_width=True):
        contact_data = {
            "employee_id": selected_contact["employee_id"],
            "phone_home": phone_home,
            "phone_mobile": phone_mobile,
            "note": note,
        }

        if selected_contact["contact_id"]:
            # 기존 연락망 수정
            db.update("emergency_contacts", selected_contact["contact_id"], contact_data)
            st.success("✅ 연락망 정보가 수정되었습니다!")
        else:
            # 새 연락망 등록
            db.insert("emergency_contacts", contact_data)
            st.success("✅ 연락망 정보가 등록되었습니다!")

        st.cache_data.clear()
        st.rerun()

page_footer()
