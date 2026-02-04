"""
당직근무일지 (1공장/2공장)
- 1공장/2공장 탭 구성
- 근무인원현황, 공사현황, 문제점/조치사항, 특이사항
- 승인 프로세스: 저장 → 승인요청 → 승인/부결
"""
import streamlit as st
import json
from datetime import date, datetime
from components.common_ui import page_header, page_footer, show_success, show_error, show_info
from services import log_service, db
from config import FACTORIES

page_header("당직근무일지", "📝")

# ── 공장 탭 ──
tab1, tab2 = st.tabs(["🏭 창원1공장", "🏭 창원2공장"])

for tab, factory in zip([tab1, tab2], FACTORIES):
    with tab:
        st.subheader(f"{factory} 당직근무일지")

        # ── 일자 선택 ──
        col1, col2 = st.columns([3, 7])
        with col1:
            log_date = st.date_input("당직일자", value=date.today(), key=f"log_date_{factory}")
        with col2:
            duty_type = st.selectbox("근무", ["주간", "야간"], key=f"duty_type_{factory}")

        # 기존 일지 조회
        try:
            existing_log = log_service.get_log_by_date(log_date.isoformat(), factory, duty_type)
        except:
            existing_log = None

        # ── 일지 입력 폼 ──
        with st.form(f"log_form_{factory}"):
            # 근무인원현황 (간략화)
            st.markdown("**근무인원현황**")
            col1, col2 = st.columns(2)
            with col1:
                special_workers = st.number_input("특근 인원", min_value=0, value=0, key=f"special_{factory}")
            with col2:
                night_workers = st.number_input("야근 인원", min_value=0, value=0, key=f"night_{factory}")

            # 공사현황 (간략화)
            st.markdown("**공사현황**")
            col1, col2, col3 = st.columns(3)
            with col1:
                construction_count = st.number_input("업체 수", min_value=0, value=0, key=f"const_count_{factory}")
            with col2:
                construction_workers = st.number_input("공사 인원", min_value=0, value=0, key=f"const_workers_{factory}")
            with col3:
                fire_work = st.checkbox("화기작업 있음", key=f"fire_{factory}")

            # 문제점/조치사항
            issues = st.text_area(
                "문제점 / 조치사항",
                value=existing_log.get("issues", "") if existing_log else "",
                height=100,
                key=f"issues_{factory}"
            )

            # 특이사항
            special_notes = st.text_area(
                "특이사항",
                value=existing_log.get("special_notes", "") if existing_log else "",
                height=100,
                key=f"special_{factory}_notes"
            )

            # 버튼
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                save_btn = st.form_submit_button("💾 저장", type="primary")
            with col2:
                if existing_log and existing_log.get("approval_status") == "작성중":
                    request_btn = st.form_submit_button("📤 승인요청")
                else:
                    request_btn = False
            with col3:
                if existing_log and existing_log.get("approval_status") == "승인요청":
                    approve_btn = st.form_submit_button("✅ 승인")
                else:
                    approve_btn = False
            with col4:
                if existing_log and existing_log.get("approval_status") == "승인요청":
                    reject_btn = st.form_submit_button("❌ 부결")
                else:
                    reject_btn = False

            # 저장 처리
            if save_btn:
                try:
                    log_data = {
                        "log_date": log_date.isoformat(),
                        "factory": factory,
                        "duty_type": duty_type,
                        "workforce_status": json.dumps({
                            "special_workers": special_workers,
                            "night_workers": night_workers,
                        }),
                        "construction_status": json.dumps({
                            "count": construction_count,
                            "workers": construction_workers,
                            "fire_work": fire_work,
                        }),
                        "issues": issues,
                        "special_notes": special_notes,
                    }

                    log_service.save_log(log_data)
                    show_success("일지가 저장되었습니다.")
                    st.rerun()

                except Exception as e:
                    show_error(f"저장 실패: {e}")

            # 승인요청 처리
            if request_btn and existing_log:
                try:
                    log_service.request_approval(existing_log["id"])
                    show_success("승인 요청되었습니다.")
                    st.rerun()
                except Exception as e:
                    show_error(f"승인요청 실패: {e}")

            # 승인 처리
            if approve_btn and existing_log:
                try:
                    log_service.approve_log(existing_log["id"])
                    show_success("승인되었습니다.")
                    st.rerun()
                except Exception as e:
                    show_error(f"승인 실패: {e}")

            # 부결 처리
            if reject_btn and existing_log:
                try:
                    reason = st.text_input("부결 사유", key=f"reject_reason_{factory}")
                    if reason:
                        log_service.reject_log(existing_log["id"], reason)
                        show_success("부결 처리되었습니다.")
                        st.rerun()
                    else:
                        show_error("부결 사유를 입력하세요.")
                except Exception as e:
                    show_error(f"부결 실패: {e}")

        # 현재 상태 표시
        if existing_log:
            st.divider()
            col1, col2, col3 = st.columns(3)
            with col1:
                status = existing_log.get("approval_status", "작성중")
                st.metric("승인 상태", status)
            with col2:
                if existing_log.get("approved_at"):
                    st.metric("승인 일시", existing_log["approved_at"][:16])
            with col3:
                if existing_log.get("rejection_reason"):
                    st.error(f"부결 사유: {existing_log['rejection_reason']}")

page_footer()
