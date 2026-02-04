"""
당직 변경 서비스
- 변경 등록/조회
- 원본 발령 상태 업데이트
"""
from services import db


def get_changes_by_month(year: int, month: int) -> list:
    """월별 변경 이력 조회"""
    # TODO: Phase 3에서 구현
    pass


def create_change(data: dict) -> dict:
    """변경 등록 + 원본 발령 상태 업데이트"""
    # TODO: Phase 3에서 구현
    pass


def get_changes_by_assignment(assignment_id: str) -> list:
    """특정 발령의 변경 이력"""
    return db.select_where("duty_changes", "assignment_id", assignment_id)
