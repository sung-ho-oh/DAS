"""
직원 선택 컴포넌트
- 사번으로 검색 → 소속/성명/직위 자동 표시
"""
import streamlit as st
from services import db


def employee_selector(key: str = "emp_select", label: str = "직원 선택"):
    """
    직원 선택 위젯
    - 사번 입력 시 직원 정보 자동 조회
    - 반환: 선택된 직원 dict 또는 None
    """
    emp_no = st.text_input(f"{label} (사번)", key=f"{key}_input")

    if emp_no:
        try:
            employees = db.select_where("employees", "employee_no", emp_no)
            if employees:
                emp = employees[0]
                st.caption(f"✅ {emp['name']} | {emp['department']} | {emp['position']}")
                return emp
            else:
                st.caption("❌ 해당 사번의 직원을 찾을 수 없습니다.")
                return None
        except Exception as e:
            st.caption(f"⚠️ DB 조회 오류: {e}")
            return None
    return None
