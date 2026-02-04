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
    # TODO: Phase 2에서 구현
    # 가장 최근 완료/확정된 발령에서 해당 유형의 당직자 조회
    pass


def get_eligible_employees(duty_type: str, day_category: str) -> list:
    """
    발령 대상 직원 목록 조회 (직급 기준 필터링)
    - DUTY_RULES에서 해당 유형의 대상 직급/직위 확인
    - employees 테이블에서 해당 조건의 활동 직원 조회
    """
    # TODO: Phase 2에서 구현
    pass


def auto_assign_next(duty_type: str, day_category: str) -> dict | None:
    """
    LAST 사번 기반 다음 순번 자동 배정
    1. get_last_duty_person으로 최근 당직자 조회
    2. get_eligible_employees로 대상자 목록 조회
    3. 최근 당직자 다음 순번 반환 (순환)
    """
    # TODO: Phase 2에서 구현
    pass
