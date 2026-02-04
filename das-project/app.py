"""
DAS - 당직 업무 자동화 시스템
메인 엔트리포인트 (사이드바 네비게이션)

실행: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
import calendar
from config import APP_TITLE, APP_VERSION
from services import db

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

# ── 통계 데이터 가져오기 ──
@st.cache_data(ttl=60)  # 1분 캐시
def get_dashboard_stats():
    """대시보드 통계 조회"""
    try:
        # 현재 연월
        now = datetime.now()
        current_month = f"{now.year}-{now.month:02d}"
        # 해당 월의 마지막 날 계산
        last_day = calendar.monthrange(now.year, now.month)[1]
        month_start = f"{current_month}-01"
        month_end = f"{current_month}-{last_day:02d}"

        # 통계 조회
        total_employees = db.count("employees", "is_active", True)
        total_assignments_this_month = len(db.select_between(
            "duty_assignments", "duty_date",
            month_start, month_end
        ))
        # 변경 건수는 change_date 범위 조회
        changes_this_month = db.select_between(
            "duty_changes", "change_date",
            month_start, month_end
        )
        total_changes_this_month = len(changes_this_month)
        pending_logs = db.count("duty_logs", "approval_status", "승인요청")
        total_contacts = db.count("emergency_contacts")

        # 당직비는 payment_month로 조회
        payments = db.select_where("duty_payments", "payment_month", current_month)
        total_payment = sum(p.get("amount", 0) for p in payments) if payments else 0

        return {
            "employees": total_employees,
            "assignments": total_assignments_this_month,
            "changes": total_changes_this_month,
            "pending_logs": pending_logs,
            "payment": total_payment,
            "contacts": total_contacts,
            "db_connected": True,
        }
    except Exception as e:
        return {
            "employees": 0,
            "assignments": 0,
            "changes": 0,
            "pending_logs": 0,
            "payment": 0,
            "contacts": 0,
            "db_connected": False,
            "error": str(e)
        }

# ── 메인 페이지 ──
st.title(APP_TITLE)
st.markdown("---")

# 통계 조회
stats = get_dashboard_stats()

if not stats["db_connected"]:
    st.error("⚠️ Supabase 연결 실패. .env 파일 설정을 확인하세요.")
    st.code(stats.get("error", "알 수 없는 오류"))

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 등록 직원", f"{stats['employees']:,} 명")
    st.metric("📋 이번달 당직", f"{stats['assignments']:,} 건")

with col2:
    st.metric("🔄 이번달 변경", f"{stats['changes']:,} 건")
    st.metric("📝 미승인 일지", f"{stats['pending_logs']:,} 건")

with col3:
    st.metric("💰 이번달 당직비", f"{stats['payment']:,} 원")
    st.metric("📞 연락망 등록", f"{stats['contacts']:,} 명")

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
