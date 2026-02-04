"""
당직비 지급 LIST
- 월별 당직비 명세 조회
- 사업부별 소계/합계, 창원1/2 구분 집계
- Excel 다운로드
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from components.common_ui import page_header, page_footer, show_success, show_error, show_info
from services import payment_service

page_header("당직비 지급", "💰")

# ── 월 선택 ──
col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
with col1:
    year = st.selectbox("연도", range(2024, 2027), index=1, key="payment_year")
with col2:
    month = st.selectbox("월", range(1, 13), index=datetime.now().month - 1, key="payment_month")
with col3:
    if st.button("📊 계산", type="primary"):
        st.session_state["calculate_payment"] = True
with col4:
    if st.button("📥 Excel 다운로드"):
        try:
            excel_data = payment_service.generate_excel_data(year, month)
            st.download_button(
                label="다운로드",
                data=excel_data,
                file_name=f"당직비_{year}{month:02d}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            show_error(f"Excel 생성 실패: {e}")

# ── 당직비 계산 및 조회 ──
if st.session_state.get("calculate_payment"):
    try:
        payments = payment_service.calculate_monthly_payments(year, month)

        if payments:
            # 사업부별 집계
            summary = payment_service.get_summary_by_business_unit(year, month)

            # 집계 표시
            st.subheader("📊 사업부별 집계")
            summary_data = []
            for bu, data in summary.items():
                summary_data.append({
                    "사업부": bu,
                    "인원": data["employees"],
                    "당직 횟수": data["count"],
                    "총액": f"{data['amount']:,}원",
                })

            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

            # 상세 내역
            st.markdown("---")
            st.subheader("📋 상세 내역")

            display_data = []
            for payment in payments:
                emp = payment.get("employee", {})
                display_data.append({
                    "사번": emp.get("employee_no", "-"),
                    "성명": emp.get("name", "-"),
                    "소속": emp.get("department", "-"),
                    "직위": emp.get("position", "-"),
                    "사업부": emp.get("business_unit", "-"),
                    "공장": emp.get("factory", "-"),
                    "횟수": payment["duty_count"],
                    "당직비": f"{payment['amount']:,}원",
                    "계좌": emp.get("bank_account", "-"),
                })

            display_df = pd.DataFrame(display_data)
            st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)
            st.caption(f"총 {len(payments)}명 / {summary.get('전체', {}).get('amount', 0):,}원")

        else:
            show_info(f"{year}년 {month}월 당직비 데이터가 없습니다.")

    except Exception as e:
        show_error(f"데이터 조회 실패: {e}")
else:
    st.info("월을 선택하고 '📊 계산' 버튼을 눌러주세요.")

page_footer()
