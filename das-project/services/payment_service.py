"""
당직비 지급 서비스
- 당직비 계산/집계
- 사업부별 소계/합계
- Excel 다운로드 데이터 생성
"""
from services import db
from config import DUTY_PAYMENT_RATES


def calculate_monthly_payments(year: int, month: int) -> list:
    """월별 당직비 계산"""
    from services import assignment_service

    # 해당 월의 모든 발령 조회
    assignments = assignment_service.get_assignments_by_month(year, month)

    # 직원별 당직 횟수 및 금액 계산
    employee_payments = {}

    for asmt in assignments:
        if asmt["status"] not in ["확정", "완료"]:
            continue  # 예정/변경 상태는 제외

        # 당직비 기준 결정
        key = f"{asmt['day_category'].replace('무일', '')}_{asmt['duty_type'].replace('간', '')}"
        # "휴무일_주" 또는 "평일_야"
        if asmt['day_category'] == "휴무일" and asmt['duty_type'] == "주간":
            rate = DUTY_PAYMENT_RATES.get("holiday_day", 50000)
        elif asmt['day_category'] == "휴무일" and asmt['duty_type'] == "야간":
            rate = DUTY_PAYMENT_RATES.get("holiday_night", 60000)
        elif asmt['day_category'] == "평일" and asmt['duty_type'] == "야간":
            rate = DUTY_PAYMENT_RATES.get("weekday_night", 40000)
        else:
            rate = 40000  # 기본값

        # 총당직자 카운트
        main_id = asmt.get("main_duty_id")
        if main_id:
            if main_id not in employee_payments:
                employee_payments[main_id] = {"count": 0, "amount": 0, "employee": asmt.get("main_duty")}
            employee_payments[main_id]["count"] += 1
            employee_payments[main_id]["amount"] += rate

        # 부당직자 카운트
        sub_id = asmt.get("sub_duty_id")
        if sub_id:
            if sub_id not in employee_payments:
                employee_payments[sub_id] = {"count": 0, "amount": 0, "employee": asmt.get("sub_duty")}
            employee_payments[sub_id]["count"] += 1
            employee_payments[sub_id]["amount"] += rate

    # 리스트로 변환
    result = []
    for emp_id, data in employee_payments.items():
        result.append({
            "employee_id": emp_id,
            "employee": data["employee"],
            "duty_count": data["count"],
            "amount": data["amount"],
        })

    return result


def get_payments_by_month(year: int, month: int) -> list:
    """월별 당직비 조회"""
    payment_month = f"{year}-{month:02d}"
    return db.select_where("duty_payments", "payment_month", payment_month, order_by="employee_id")


def get_summary_by_business_unit(year: int, month: int) -> dict:
    """사업부별 집계"""
    payments = calculate_monthly_payments(year, month)

    summary = {}
    total = {"count": 0, "amount": 0, "employees": 0}

    for payment in payments:
        emp = payment.get("employee", {})
        if not emp:
            continue

        bu = emp.get("business_unit", "미분류")

        if bu not in summary:
            summary[bu] = {"count": 0, "amount": 0, "employees": 0}

        summary[bu]["count"] += payment["duty_count"]
        summary[bu]["amount"] += payment["amount"]
        summary[bu]["employees"] += 1

        total["count"] += payment["duty_count"]
        total["amount"] += payment["amount"]
        total["employees"] += 1

    summary["전체"] = total
    return summary


def generate_excel_data(year: int, month: int) -> bytes:
    """Excel 다운로드용 데이터 생성"""
    import pandas as pd
    from io import BytesIO

    payments = calculate_monthly_payments(year, month)

    # DataFrame 생성
    data = []
    for payment in payments:
        emp = payment.get("employee", {})
        data.append({
            "사번": emp.get("employee_no", "-"),
            "성명": emp.get("name", "-"),
            "소속": emp.get("department", "-"),
            "직위": emp.get("position", "-"),
            "사업부": emp.get("business_unit", "-"),
            "공장": emp.get("factory", "-"),
            "당직 횟수": payment["duty_count"],
            "당직비": payment["amount"],
            "계좌번호": emp.get("bank_account", "-"),
        })

    df = pd.DataFrame(data)

    # Excel로 변환
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=f"{year}-{month:02d} 당직비", index=False)

    output.seek(0)
    return output.getvalue()
