"""
당직 예정자 LIST / 발령 관리
- 월별 당직 발령 예정자 조회/입력/수정/삭제
- 총당직 + 부당직 명단 병기 표시
- 휴무일 행 별도 색상 구분
- LAST 사번 기반 순번 자동배정
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from components.common_ui import page_header, page_footer
from components.duty_rules_help import show_duty_rules
from services import assignment_service, db

page_header("당직 예정자 LIST", "📋")

# ── 월 선택 ──
col1, col2, col3 = st.columns([2, 2, 6])

with col1:
    selected_year = st.selectbox(
        "연도",
        range(datetime.now().year - 1, datetime.now().year + 2),
        index=1,
    )

with col2:
    selected_month = st.selectbox(
        "월",
        range(1, 13),
        index=datetime.now().month - 1,
    )

with col3:
    st.write("")  # 공간 확보

# ── 월별 당직 발령 조회 ──
@st.cache_data(ttl=30)
def load_assignments(year: int, month: int):
    """월별 당직 발령 조회"""
    return assignment_service.get_assignments_by_month(year, month)


assignments = load_assignments(selected_year, selected_month)

st.markdown("---")

# ── 당직 발령 현황 ──
st.subheader(f"📋 {selected_year}년 {selected_month}월 당직 발령")

if not assignments:
    st.info(f"{selected_year}년 {selected_month}월 당직 발령이 없습니다.")
    st.info("💡 아래 '자동 발령 생성' 버튼으로 한 달치 발령을 자동 생성할 수 있습니다.")
else:
    # 데이터프레임으로 변환 (최적화: 이미 JOIN된 데이터 사용)
    df_data = []
    for asmt in assignments:
        # JOIN으로 이미 가져온 직원 정보 사용 (DB 호출 없음)
        main_duty = asmt.get("main_duty")
        sub_duty = asmt.get("sub_duty")

        df_data.append({
            "일자": asmt["duty_date"],
            "요일": asmt["day_of_week"],
            "구분": asmt["day_category"],
            "주야": asmt["duty_type"],
            "총당직": f"{main_duty['name']} ({main_duty['employee_no']})" if main_duty else "-",
            "부당직": f"{sub_duty['name']} ({sub_duty['employee_no']})" if sub_duty else "-",
            "상태": asmt["status"],
        })

    df = pd.DataFrame(df_data)

    # 휴무일 행 강조 (배경색)
    def highlight_holiday(row):
        if row["구분"] == "휴무일":
            return ["background-color: #FFF3E0"] * len(row)
        return [""] * len(row)

    styled_df = df.style.apply(highlight_holiday, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    st.caption(f"총 {len(assignments)}건")

st.markdown("---")

# ── 자동 발령 생성 ──
st.subheader("⚡ 자동 발령 생성")

col_a, col_b = st.columns([3, 7])

with col_a:
    if st.button("📅 한 달치 발령 자동 생성", type="primary", use_container_width=True):
        # 해당 월의 일수 계산
        num_days = calendar.monthrange(selected_year, selected_month)[1]

        with st.spinner("발령 생성 중..."):
            created_count = 0
            for day in range(1, num_days + 1):
                duty_date = f"{selected_year}-{selected_month:02d}-{day:02d}"
                weekday = calendar.weekday(selected_year, selected_month, day)
                day_name = ["월", "화", "수", "목", "금", "토", "일"][weekday]

                # 휴무일 판별 (토/일)
                day_category = "휴무일" if weekday >= 5 else "평일"

                # 총당직/부당직 자동 배정
                main_duty = assignment_service.auto_assign_next("총당직", day_category)
                sub_duty = assignment_service.auto_assign_next("부당직", day_category)

                if main_duty and sub_duty:
                    # 중복 확인
                    existing = db.select_where("duty_assignments", "duty_date", duty_date)
                    if not existing:
                        assignment_service.create_assignment({
                            "duty_date": duty_date,
                            "day_of_week": day_name,
                            "duty_type": "야간",
                            "day_category": day_category,
                            "main_duty_id": main_duty["id"],
                            "sub_duty_id": sub_duty["id"],
                            "status": "예정",
                        })
                        created_count += 1

        st.success(f"✅ {created_count}건 발령이 생성되었습니다!")
        st.cache_data.clear()
        st.rerun()

with col_b:
    st.info("💡 LAST 사번 기반으로 순번을 자동 배정하여 한 달치 발령을 생성합니다.")

st.markdown("---")

# ── 수동 발령 추가 ──
with st.expander("➕ 수동 발령 추가"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        new_date = st.date_input("당직일자", value=datetime(selected_year, selected_month, 1))

    with col2:
        new_day_category = st.selectbox("구분", ["평일", "휴무일"])

    with col3:
        # 총당직 선택
        main_employees = assignment_service.get_eligible_employees("총당직", new_day_category)
        main_options = {f"{e['name']} ({e['employee_no']})": e["id"] for e in main_employees}
        selected_main = st.selectbox("총당직", options=list(main_options.keys()))

    with col4:
        # 부당직 선택
        sub_employees = assignment_service.get_eligible_employees("부당직", new_day_category)
        sub_options = {f"{e['name']} ({e['employee_no']})": e["id"] for e in sub_employees}
        selected_sub = st.selectbox("부당직", options=list(sub_options.keys()))

    if st.button("✅ 발령 추가", use_container_width=True):
        weekday = new_date.weekday()
        day_name = ["월", "화", "수", "목", "금", "토", "일"][weekday]

        assignment_service.create_assignment({
            "duty_date": str(new_date),
            "day_of_week": day_name,
            "duty_type": "야간",
            "day_category": new_day_category,
            "main_duty_id": main_options[selected_main],
            "sub_duty_id": sub_options[selected_sub],
            "status": "예정",
        })

        st.success("발령이 추가되었습니다!")
        st.cache_data.clear()
        st.rerun()

# ── 도움말 ──
show_duty_rules()

page_footer()
