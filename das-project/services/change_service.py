"""
당직 변경 서비스
- 변경 등록/조회
- 원본 발령 상태 업데이트
"""
from services import db


def get_changes_by_month(year: int, month: int) -> list:
    """월별 변경 이력 조회"""
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"

    client = db.get_client()
    query = (
        client.table("duty_changes")
        .select("*, assignment:duty_assignments(*), original:employees!duty_changes_original_employee_id_fkey(*), new:employees!duty_changes_new_employee_id_fkey(*)")
        .gte("change_date", start_date)
        .lt("change_date", end_date)
        .order("change_date", desc=True)
    )

    response = query.execute()
    return response.data


def create_change(data: dict) -> dict:
    """변경 등록 + 원본 발령 상태 업데이트"""
    # 1. 변경 등록
    inserted_change = db.insert("duty_changes", data)

    # 2. 원본 발령 상태를 '변경'으로 업데이트
    assignment_id = data.get("assignment_id")
    if assignment_id:
        db.update("duty_assignments", assignment_id, {"status": "변경"})

    return inserted_change


def get_changes_by_assignment(assignment_id: str) -> list:
    """특정 발령의 변경 이력"""
    return db.select_where("duty_changes", "assignment_id", assignment_id)
