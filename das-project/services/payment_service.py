"""
당직비 지급 서비스
- 당직비 계산/집계
- 사업부별 소계/합계
- Excel 다운로드 데이터 생성
"""
from services import db, assignment_service
from config import DUTY_PAYMENT_RATES
import calendar
from collections import defaultdict


def calculate_monthly_payments(year: int, month: int) -> list:
    """
    월별 당직비 계산
    - 해당 월의 당직 발령 조회
    - 직원별 당직 횟수 집계 (휴무일/평일 구분)
    - 당직비 계산 및 duty_payments 테이블에 저장/업데이트
    """
    payment_month = f"{year}-{month:02d}"

    # 해당 월의 발령 조회 (JOIN으로 직원 정보 포함)
    assignments = assignment_service.get_assignments_by_month(year, month)

    # 직원별 당직 집계
    employee_duty_count = defaultdict(lambda: {
        "employee_id": None,
        "holiday_count": 0,  # 휴무일 당직
        "weekday_count": 0,  # 평일 당직
        "total_count": 0,
        "amount": 0,
    })

    for asmt in assignments:
        # 총당직자
        main_duty = asmt.get("main_duty")
        if main_duty:
            emp_id = main_duty["id"]
            employee_duty_count[emp_id]["employee_id"] = emp_id

            if asmt["day_category"] == "휴무일":
                employee_duty_count[emp_id]["holiday_count"] += 1
                employee_duty_count[emp_id]["amount"] += DUTY_PAYMENT_RATES.get("holiday_night", 60000)
            else:
                employee_duty_count[emp_id]["weekday_count"] += 1
                employee_duty_count[emp_id]["amount"] += DUTY_PAYMENT_RATES.get("weekday_night", 40000)

            employee_duty_count[emp_id]["total_count"] += 1

        # 부당직자
        sub_duty = asmt.get("sub_duty")
        if sub_duty:
            emp_id = sub_duty["id"]
            employee_duty_count[emp_id]["employee_id"] = emp_id

            if asmt["day_category"] == "휴무일":
                employee_duty_count[emp_id]["holiday_count"] += 1
                employee_duty_count[emp_id]["amount"] += DUTY_PAYMENT_RATES.get("holiday_night", 60000)
            else:
                employee_duty_count[emp_id]["weekday_count"] += 1
                employee_duty_count[emp_id]["amount"] += DUTY_PAYMENT_RATES.get("weekday_night", 40000)

            employee_duty_count[emp_id]["total_count"] += 1

    # duty_payments 테이블에 저장/업데이트
    payment_records = []
    for emp_id, data in employee_duty_count.items():
        if data["employee_id"]:
            # 기존 레코드 확인
            existing = db.select_where("duty_payments", "payment_month", payment_month)
            existing_for_emp = [p for p in existing if p["employee_id"] == emp_id]

            payment_data = {
                "payment_month": payment_month,
                "employee_id": data["employee_id"],
                "duty_count": data["total_count"],
                "amount": data["amount"],
                "payment_status": "미지급",
            }

            if existing_for_emp:
                # 업데이트
                db.update("duty_payments", existing_for_emp[0]["id"], payment_data)
            else:
                # 신규 삽입
                db.insert("duty_payments", payment_data)

            payment_records.append(payment_data)

    return payment_records


def get_payments_by_month(year: int, month: int) -> list:
    """
    월별 당직비 조회 (직원 정보 JOIN)
    """
    payment_month = f"{year}-{month:02d}"

    # 당직비 조회
    payments = db.select_where("duty_payments", "payment_month", payment_month)

    # 직원 정보 조인
    enriched_payments = []
    for payment in payments:
        employee = db.select_by_id("employees", payment["employee_id"])
        if employee:
            enriched_payments.append({
                **payment,
                "employee": employee,
            })

    # 사번 순 정렬
    enriched_payments.sort(key=lambda x: x["employee"]["employee_no"])

    return enriched_payments


def get_summary_by_business_unit(year: int, month: int) -> dict:
    """
    사업부별 집계
    - 사업부별 인원/당직횟수/금액 합계
    """
    payments = get_payments_by_month(year, month)

    # 사업부별 집계
    summary = defaultdict(lambda: {
        "count": 0,
        "total_duty_count": 0,
        "total_amount": 0,
    })

    for payment in payments:
        business_unit = payment["employee"]["business_unit"]
        summary[business_unit]["count"] += 1
        summary[business_unit]["total_duty_count"] += payment["duty_count"]
        summary[business_unit]["total_amount"] += payment["amount"]

    return dict(summary)
