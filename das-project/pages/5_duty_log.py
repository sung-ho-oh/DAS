"""
당직근무일지 (1공장/2공장)
- 1공장/2공장 탭 구성
- 근무인원현황, 공사현황, 문제점/조치사항, 특이사항
- 승인 프로세스: 저장 → 승인요청 → 승인/부결
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import json
from components.common_ui import page_header, page_footer
from services import log_service, assignment_service, db
from config import FACTORIES, APPROVAL_STATUS

page_header("당직근무일지", "📝")

# ── 탭 구성 ──
tab1, tab2 = st.tabs(["📝 일지 작성", "📋 일지 조회 / 승인"])

# ── 탭1: 일지 작성 ──
with tab1:
    st.subheader("📝 당직근무일지 작성")

    # 일자, 공장, 주야 선택
    col1, col2, col3 = st.columns(3)

    with col1:
        log_date = st.date_input("일자", value=datetime.now())

    with col2:
        factory = st.selectbox("공장", FACTORIES)

    with col3:
        duty_type = st.selectbox("주야", ["주간", "야간"])

    # 기존 일지 로드
    existing_log = log_service.get_log_by_date(str(log_date), factory, duty_type)

    if existing_log and existing_log["approval_status"] == "승인":
        st.warning("⚠️ 이미 승인된 일지입니다. 수정할 수 없습니다.")
        st.json(existing_log)
    else:
        st.markdown("---")

        # 당직자 정보 (발령에서 자동 조회)
        st.subheader("👥 당직자 정보")

        # 해당 날짜의 발령 조회
        year = log_date.year
        month = log_date.month
        assignments = assignment_service.get_assignments_by_month(year, month)

        # 해당 날짜의 발령 찾기
        target_assignment = None
        for asmt in assignments:
            if asmt["duty_date"] == str(log_date):
                target_assignment = asmt
                break

        if target_assignment:
            main_duty = target_assignment.get("main_duty")
            sub_duty = target_assignment.get("sub_duty")

            col_a, col_b = st.columns(2)
            with col_a:
                st.info(f"**총당직**: {main_duty['name']} ({main_duty['employee_no']})" if main_duty else "**총당직**: 미배정")
            with col_b:
                st.info(f"**부당직**: {sub_duty['name']} ({sub_duty['employee_no']})" if sub_duty else "**부당직**: 미배정")

            main_duty_id = main_duty["id"] if main_duty else None
            sub_duty_id = sub_duty["id"] if sub_duty else None
        else:
            st.warning("해당 날짜에 당직 발령이 없습니다.")
            main_duty_id = None
            sub_duty_id = None

        st.markdown("---")

        # 근무인원현황
        st.subheader("👷 근무인원현황")
        st.caption("부서별 특근/야근 인원")

        workforce_status = existing_log.get("workforce_status", {}) if existing_log else {}

        col1, col2, col3 = st.columns(3)
        with col1:
            dept1 = st.text_input("부서1", value=list(workforce_status.keys())[0] if workforce_status else "", key="dept1")
            count1 = st.number_input("인원1", value=list(workforce_status.values())[0] if workforce_status else 0, min_value=0, key="count1")

        with col2:
            dept2 = st.text_input("부서2", value=list(workforce_status.keys())[1] if len(workforce_status) > 1 else "", key="dept2")
            count2 = st.number_input("인원2", value=list(workforce_status.values())[1] if len(workforce_status) > 1 else 0, min_value=0, key="count2")

        with col3:
            dept3 = st.text_input("부서3", value=list(workforce_status.keys())[2] if len(workforce_status) > 2 else "", key="dept3")
            count3 = st.number_input("인원3", value=list(workforce_status.values())[2] if len(workforce_status) > 2 else 0, min_value=0, key="count3")

        # JSONB 형식으로 변환
        workforce_data = {}
        if dept1:
            workforce_data[dept1] = count1
        if dept2:
            workforce_data[dept2] = count2
        if dept3:
            workforce_data[dept3] = count3

        st.markdown("---")

        # 공사현황
        st.subheader("🏗 공사현황")

        construction_status = existing_log.get("construction_status", {}) if existing_log else {}

        col1, col2, col3 = st.columns(3)
        with col1:
            company_count = st.number_input(
                "업체수",
                value=construction_status.get("company_count", 0) if construction_status else 0,
                min_value=0,
            )

        with col2:
            worker_count = st.number_input(
                "인원",
                value=construction_status.get("worker_count", 0) if construction_status else 0,
                min_value=0,
            )

        with col3:
            fire_work = st.checkbox(
                "화기작업",
                value=construction_status.get("fire_work", False) if construction_status else False,
            )

        construction_data = {
            "company_count": company_count,
            "worker_count": worker_count,
            "fire_work": fire_work,
        }

        st.markdown("---")

        # 문제점/조치사항
        issues = st.text_area(
            "❗ 문제점 / 조치사항",
            value=existing_log.get("issues", "") if existing_log else "",
            placeholder="문제점 및 조치사항을 입력하세요",
            height=100,
        )

        # 특이사항
        special_notes = st.text_area(
            "📌 특이사항",
            value=existing_log.get("special_notes", "") if existing_log else "",
            placeholder="특이사항을 입력하세요",
            height=100,
        )

        st.markdown("---")

        # 저장 버튼
        col_save, col_request = st.columns(2)

        with col_save:
            if st.button("💾 저장 (작성중)", type="secondary", use_container_width=True):
                if not main_duty_id or not sub_duty_id:
                    st.error("당직 발령이 없어 저장할 수 없습니다.")
                else:
                    try:
                        log_service.save_log({
                            "log_date": str(log_date),
                            "factory": factory,
                            "duty_type": duty_type,
                            "main_duty_id": main_duty_id,
                            "sub_duty_id": sub_duty_id,
                            "workforce_status": workforce_data,
                            "construction_status": construction_data,
                            "issues": issues,
                            "special_notes": special_notes,
                        })

                        st.success("✅ 저장되었습니다!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"저장 실패: {e}")

        with col_request:
            if st.button("📤 승인 요청", type="primary", use_container_width=True):
                if not main_duty_id or not sub_duty_id:
                    st.error("당직 발령이 없어 저장할 수 없습니다.")
                else:
                    try:
                        # 저장 + 승인 요청
                        saved_log = log_service.save_log({
                            "log_date": str(log_date),
                            "factory": factory,
                            "duty_type": duty_type,
                            "main_duty_id": main_duty_id,
                            "sub_duty_id": sub_duty_id,
                            "workforce_status": workforce_data,
                            "construction_status": construction_data,
                            "issues": issues,
                            "special_notes": special_notes,
                        })

                        log_service.request_approval(saved_log["id"])

                        st.success("✅ 승인 요청되었습니다!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"승인 요청 실패: {e}")

# ── 탭2: 일지 조회 / 승인 ──
with tab2:
    st.subheader("📋 월별 일지 조회")

    # 월 선택 및 필터
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        view_year = st.selectbox(
            "연도",
            range(datetime.now().year - 1, datetime.now().year + 2),
            index=1,
            key="view_year",
        )

    with col2:
        view_month = st.selectbox(
            "월",
            range(1, 13),
            index=datetime.now().month - 1,
            key="view_month",
        )

    with col3:
        view_factory = st.selectbox("공장", ["전체"] + FACTORIES, key="view_factory")

    with col4:
        view_status = st.selectbox("승인상태", ["전체"] + APPROVAL_STATUS, key="view_status")

    # 일지 조회
    logs = log_service.get_logs_by_month(
        view_year,
        view_month,
        None if view_factory == "전체" else view_factory
    )

    # 승인 상태 필터
    if view_status != "전체":
        logs = [log for log in logs if log["approval_status"] == view_status]

    if not logs:
        st.info(f"{view_year}년 {view_month}월 일지가 없습니다.")
    else:
        # 데이터프레임 표시
        df_data = []
        for log in logs:
            main_duty = log.get("main_duty")
            sub_duty = log.get("sub_duty")

            df_data.append({
                "일자": log["log_date"],
                "공장": log["factory"],
                "주야": log["duty_type"],
                "총당직": f"{main_duty['name']}" if main_duty else "-",
                "부당직": f"{sub_duty['name']}" if sub_duty else "-",
                "승인상태": log["approval_status"],
                "id": log["id"],
            })

        df = pd.DataFrame(df_data)

        # 승인 상태별 색상
        def highlight_status(row):
            if row["승인상태"] == "승인":
                return ["background-color: #E8F5E9"] * len(row)
            elif row["승인상태"] == "승인요청":
                return ["background-color: #FFF9C4"] * len(row)
            elif row["승인상태"] == "부결":
                return ["background-color: #FFEBEE"] * len(row)
            return [""] * len(row)

        display_df = df.drop(columns=["id"])
        styled_df = display_df.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        st.caption(f"총 {len(logs)}건")

        st.markdown("---")

        # 승인/부결 처리
        st.subheader("✅ 승인 / 부결 처리")

        # 일지 선택
        log_options = {
            f"{log['log_date']} - {log['factory']} ({log['duty_type']}) [{log['approval_status']}]": log
            for log in logs
        }

        selected_log_label = st.selectbox("일지 선택", options=list(log_options.keys()))
        selected_log = log_options[selected_log_label]

        st.json(selected_log)

        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button("✅ 승인", type="primary", use_container_width=True):
                try:
                    log_service.approve_log(selected_log["id"])
                    st.success("✅ 승인되었습니다!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"승인 실패: {e}")

        with col_reject:
            reject_reason = st.text_input("부결 사유", placeholder="부결 사유를 입력하세요")
            if st.button("❌ 부결", use_container_width=True):
                if not reject_reason:
                    st.error("부결 사유를 입력하세요.")
                else:
                    try:
                        log_service.reject_log(selected_log["id"], reject_reason)
                        st.success("❌ 부결되었습니다!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"부결 실패: {e}")

page_footer()
