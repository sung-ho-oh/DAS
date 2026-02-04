"""
당직 예정자 LIST / 발령 관리
- 월별 당직 발령 예정자 조회/입력/수정/삭제
- 총당직 + 부당직 명단 병기 표시
- 휴무일 행 별도 색상 구분
- LAST 사번 기반 순번 자동배정
"""
import streamlit as st
from components.common_ui import page_header, page_footer
from components.duty_rules_help import show_duty_rules

page_header("당직 예정자 LIST", "📋")

# TODO: Phase 2에서 구현
st.info("Phase 2에서 구현 예정입니다.")

# ── 도움말 ──
show_duty_rules()

page_footer()
