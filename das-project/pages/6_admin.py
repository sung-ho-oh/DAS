"""
관리자 페이지
- 발령기준/근무시간 관리
- 테스트 데이터 초기화
- 시스템 상태 확인
"""
import streamlit as st
from components.common_ui import page_header, page_footer, show_success, show_error, show_warning
from components.duty_rules_help import show_duty_rules
from services import db
from config import APP_VERSION, DUTY_RULES, WORK_HOURS

page_header("관리자", "⚙️")

# ── 시스템 정보 ──
st.subheader("📊 시스템 정보")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("버전", APP_VERSION)

with col2:
    try:
        emp_count = db.count("employees")
        st.metric("등록 직원", f"{emp_count}명")
    except:
        st.metric("등록 직원", "연결 실패")

with col3:
    try:
        asmt_count = db.count("duty_assignments")
        st.metric("총 당직 발령", f"{asmt_count}건")
    except:
        st.metric("총 당직 발령", "연결 실패")

# ── 발령 기준 ──
st.markdown("---")
st.subheader("📋 발령 기준")
show_duty_rules()

# ── 테스트 데이터 관리 ──
st.markdown("---")
st.subheader("🧪 테스트 데이터 관리")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**테스트 데이터 생성**")
    st.info("""
    테스트 데이터를 생성하려면 터미널에서 다음 명령을 실행하세요:

    ```bash
    python data/seed_data.py
    ```

    또는 dry-run 모드로 미리보기:

    ```bash
    python data/seed_data.py --dry-run
    ```
    """)

with col2:
    st.markdown("**데이터 초기화**")
    st.warning("⚠️ 주의: 이 작업은 모든 데이터를 삭제합니다.")

    if st.button("🗑️ 전체 데이터 삭제", type="secondary"):
        if st.checkbox("정말로 삭제하시겠습니까?"):
            try:
                # 테이블 순서대로 삭제 (FK 제약 고려)
                tables = [
                    "duty_payments",
                    "duty_logs",
                    "duty_changes",
                    "duty_assignments",
                    "emergency_contacts",
                    "employees",
                ]

                for table in tables:
                    try:
                        client = db.get_client()
                        client.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                        st.success(f"✅ {table} 삭제 완료")
                    except Exception as e:
                        st.error(f"❌ {table} 삭제 실패: {e}")

                show_success("전체 데이터가 삭제되었습니다.")
                st.rerun()

            except Exception as e:
                show_error(f"삭제 실패: {e}")

# ── DB 연결 테스트 ──
st.markdown("---")
st.subheader("🔌 DB 연결 테스트")

if st.button("연결 테스트"):
    try:
        client = db.get_client()
        result = client.table("employees").select("*").limit(1).execute()
        show_success("✅ Supabase 연결 성공!")
        st.json({"status": "connected", "sample_count": len(result.data)})
    except Exception as e:
        show_error(f"❌ Supabase 연결 실패: {e}")
        st.error("`.env` 파일에 SUPABASE_URL과 SUPABASE_KEY가 올바르게 설정되어 있는지 확인하세요.")

# ── 통계 ──
st.markdown("---")
st.subheader("📈 데이터 통계")

try:
    stats = {
        "직원": db.count("employees"),
        "당직 발령": db.count("duty_assignments"),
        "당직 변경": db.count("duty_changes"),
        "당직근무일지": db.count("duty_logs"),
        "비상연락망": db.count("emergency_contacts"),
        "당직비 기록": db.count("duty_payments"),
    }

    col1, col2, col3 = st.columns(3)
    items = list(stats.items())

    for i, (label, count) in enumerate(items):
        with [col1, col2, col3][i % 3]:
            st.metric(label, f"{count}건")

except Exception as e:
    show_error(f"통계 조회 실패: {e}")

page_footer()
