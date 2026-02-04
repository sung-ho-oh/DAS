"""
당직 발령 서비스
- Layer 2: 비즈니스 로직
- 발령 생성/조회/수정/삭제
- LAST 사번 기반 순번 자동배정
"""
from services import db
from config import DUTY_RULES


def get_assignments_by_month(year: int, month: int) -> list:
    """월별 당직 발령 조회"""
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    return db.select_between("duty_assignments", "duty_date", start_date, end_date, order_by="duty_date")


def create_assignment(data: dict) -> dict:
    """당직 발령 생성"""
    return db.insert("duty_assignments", data)


def update_assignment(assignment_id: str, data: dict) -> dict:
    """당직 발령 수정"""
    return db.update("duty_assignments", assignment_id, data)


def delete_assignment(assignment_id: str):
    """당직 발령 삭제"""
    return db.delete("duty_assignments", assignment_id)


def get_last_duty_person(duty_type: str, day_category: str) -> dict | None:
    """
    LAST 사번 조회: 해당 유형의 가장 최근 당직자 반환
    - duty_type: '총당직' | '부당직'
    - day_category: '휴무일' | '평일'
    """
    # 가장 최근 완료/확정된 발령 조회
    client = db.get_client()
    query = (
        client.table("duty_assignments")
        .select("*, main_duty:employees!duty_assignments_main_duty_id_fkey(*), sub_duty:employees!duty_assignments_sub_duty_id_fkey(*)")
        .eq("day_category", day_category)
        .in_("status", ["완료", "확정"])
        .order("duty_date", desc=True)
        .limit(1)
    )

    response = query.execute()
    if not response.data:
        return None

    assignment = response.data[0]

    # duty_type에 따라 총당직/부당직 반환
    if duty_type == "총당직":
        return assignment.get("main_duty")
    elif duty_type == "부당직":
        return assignment.get("sub_duty")

    return None


def get_eligible_employees(duty_type: str, day_category: str) -> list:
    """
    발령 대상 직원 목록 조회 (직급 기준 필터링)
    - DUTY_RULES에서 해당 유형의 대상 직급/직위 확인
    - employees 테이블에서 해당 조건의 활동 직원 조회
    """
    # DUTY_RULES에서 규칙 찾기
    rule_key = f"{day_category.replace('무일', '')}_{'main' if duty_type == '총당직' else 'sub'}"
    # 예: "휴무일" + "총당직" -> "휴_main" (X) -> "holiday_main"
    # 변환 로직
    if day_category == "휴무일":
        prefix = "holiday"
    elif day_category == "평일":
        prefix = "weekday"
    else:
        return []

    suffix = "main" if duty_type == "총당직" else "sub"
    rule_key = f"{prefix}_{suffix}"

    rule = DUTY_RULES.get(rule_key)
    if not rule:
        return []

    # 해당 직급의 활동 직원 조회
    target_grades = rule["grades"]
    client = db.get_client()
    query = (
        client.table("employees")
        .select("*")
        .eq("is_active", True)
        .in_("grade", target_grades)
        .order("employee_no")
    )

    response = query.execute()
    return response.data


def auto_assign_next(duty_type: str, day_category: str) -> dict | None:
    """
    LAST 사번 기반 다음 순번 자동 배정
    1. get_last_duty_person으로 최근 당직자 조회
    2. get_eligible_employees로 대상자 목록 조회
    3. 최근 당직자 다음 순번 반환 (순환)
    """
    last_person = get_last_duty_person(duty_type, day_category)
    eligible_list = get_eligible_employees(duty_type, day_category)

    if not eligible_list:
        return None

    # 최근 당직자가 없으면 첫 번째 직원 반환
    if not last_person:
        return eligible_list[0]

    # 최근 당직자 다음 순번 찾기
    last_emp_no = last_person.get("employee_no")
    for i, emp in enumerate(eligible_list):
        if emp["employee_no"] == last_emp_no:
            # 다음 순번 (순환)
            next_idx = (i + 1) % len(eligible_list)
            return eligible_list[next_idx]

    # 못 찾으면 첫 번째 반환
    return eligible_list[0]
