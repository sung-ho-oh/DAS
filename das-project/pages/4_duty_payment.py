"""
당직비 지급 LIST
- 월별 당직비 명세 조회
- 사업부별 소계/합계, 창원1/2 구분 집계
- Excel 다운로드
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.common_ui import page_header, page_footer
from services import payment_service

page_header("당직비 지급", "💰")

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

st.markdown("---")

# ── 당직비 계산 ──
st.subheader("⚡ 당직비 자동 계산")

col_calc, col_info = st.columns([3, 7])

with col_calc:
    if st.button("📊 당직비 계산하기", type="primary", use_container_width=True):
        with st.spinner("계산 중..."):
            try:
                payment_service.calculate_monthly_payments(selected_year, selected_month)
                st.success("✅ 당직비가 계산되었습니다!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"계산 실패: {e}")

with col_info:
    st.info("💡 해당 월의 당직 발령을 기준으로 직원별 당직비를 자동 계산합니다.")

st.markdown("---")

# ── 당직비 명세 조회 ──
st.subheader(f"💰 {selected_year}년 {selected_month}월 당직비 지급 명세")

payments = payment_service.get_payments_by_month(selected_year, selected_month)

if not payments:
    st.info(f"{selected_year}년 {selected_month}월 당직비 데이터가 없습니다.")
    st.info("💡 위의 '당직비 계산하기' 버튼을 클릭하여 계산하세요.")
else:
    # 데이터프레임 생성
    df_data = []
    for payment in payments:
        employee = payment["employee"]

        df_data.append({
            "사번": employee["employee_no"],
            "성명": employee["name"],
            "부서": employee["department"],
            "직위": employee["position"],
            "공장": employee["factory"],
            "사업부": employee["business_unit"],
            "당직횟수": payment["duty_count"],
            "금액": payment["amount"],
            "지급상태": payment["payment_status"],
        })

    df = pd.DataFrame(df_data)

    # 공장별 색상 구분
    def highlight_factory(row):
        if row["공장"] == "창원1공장":
            return ["background-color: #E3F2FD"] * len(row)
        elif row["공장"] == "창원2공장":
            return ["background-color: #F3E5F5"] * len(row)
        return [""] * len(row)

    styled_df = df.style.apply(highlight_factory, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 합계
    total_count = df["당직횟수"].sum()
    total_amount = df["금액"].sum()

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("대상 인원", f"{len(payments):,} 명")
    with col_stat2:
        st.metric("총 당직 횟수", f"{total_count:,} 회")
    with col_stat3:
        st.metric("총 지급액", f"{total_amount:,} 원")

    st.markdown("---")

    # ── 사업부별 집계 ──
    st.subheader("📊 사업부별 집계")

    summary = payment_service.get_summary_by_business_unit(selected_year, selected_month)

    if summary:
        summary_data = []
        for bu, data in summary.items():
            summary_data.append({
                "사업부": bu,
                "인원": data["count"],
                "당직횟수": data["total_duty_count"],
                "금액": data["total_amount"],
            })

        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.sort_values("사업부")

        st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── CSV 다운로드 ──
    st.subheader("📥 데이터 다운로드")

    csv = df.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=f"당직비_{selected_year}년{selected_month}월.csv",
        mime="text/csv",
        use_container_width=True,
    )

page_footer()
