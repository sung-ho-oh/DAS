"""
DAS - 당직 업무 자동화 시스템
메인 엔트리포인트 (사이드바 네비게이션)

실행: streamlit run app.py
"""
import streamlit as st
from config import APP_TITLE, APP_VERSION

# ── 페이지 설정 ──
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 사이드바 ──
with st.sidebar:
    st.title("🏭 DAS")
    st.caption(f"v{APP_VERSION}")
    st.divider()
    st.markdown("""
    **메뉴 안내**
    - 📋 당직 예정자 LIST
    - 🔄 당직일정 변경
    - 📞 비상연락망
    - 💰 당직비 지급
    - 📝 당직근무일지
    - ⚙️ 관리자
    """)

# ── 메인 페이지 ──
st.title(APP_TITLE)
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 등록 직원", "- 명", help="DB 연결 후 표시")
    st.metric("📋 이번달 당직", "- 건", help="DB 연결 후 표시")

with col2:
    st.metric("🔄 이번달 변경", "- 건", help="DB 연결 후 표시")
    st.metric("📝 미승인 일지", "- 건", help="DB 연결 후 표시")

with col3:
    st.metric("💰 이번달 당직비", "- 원", help="DB 연결 후 표시")
    st.metric("📞 연락망 등록", "- 명", help="DB 연결 후 표시")

st.markdown("---")
st.info("👈 왼쪽 사이드바에서 메뉴를 선택하세요.")

# ── 시스템 상태 ──
with st.expander("🔧 시스템 상태"):
    st.markdown(f"""
    - **버전**: {APP_VERSION}
    - **환경**: Development (독립형 테스트)
    - **DB**: Supabase 연결 대기
    - **n8n**: Phase 6에서 연동 예정
    """)
