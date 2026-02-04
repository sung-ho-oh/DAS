"""
당직 변경 서비스
- 변경 등록/조회
- 원본 발령 상태 업데이트
"""
from services import db
import calendar


def get_changes_by_month(year: int, month: int) -> list:
    """월별 변경 이력 조회"""
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    changes = db.select_between("duty_changes", "change_date", start_date, end_date, order_by="change_date")

    # 변경 이력에 직원 정보와 발령 정보 조인
    enriched_changes = []
    for change in changes:
        # 원본 직원 정보
        original_emp = db.select_by_id("employees", change["original_employee_id"])
        # 변경 후 직원 정보
        new_emp = db.select_by_id("employees", change["new_employee_id"])
        # 발령 정보
        assignment = db.select_by_id("duty_assignments", change["assignment_id"])

        enriched_changes.append({
            **change,
            "original_employee": original_emp,
            "new_employee": new_emp,
            "assignment": assignment,
        })

    return enriched_changes


def create_change(data: dict) -> dict:
    """변경 등록 + 원본 발령 상태 업데이트"""
    # 변경 이력 삽입
    change = db.insert("duty_changes", data)

    # 원본 발령 상태를 '변경'으로 업데이트
    assignment_id = data["assignment_id"]
    duty_role = data["duty_role"]  # '총당직' or '부당직'

    # 발령의 해당 당직자 변경
    assignment = db.select_by_id("duty_assignments", assignment_id)
    if assignment:
        update_data = {"status": "변경"}

        # 총당직/부당직 구분하여 업데이트
        if duty_role == "총당직":
            update_data["main_duty_id"] = data["new_employee_id"]
        else:
            update_data["sub_duty_id"] = data["new_employee_id"]

        db.update("duty_assignments", assignment_id, update_data)

    return change


def get_changes_by_assignment(assignment_id: str) -> list:
    """특정 발령의 변경 이력"""
    return db.select_where("duty_changes", "assignment_id", assignment_id)
