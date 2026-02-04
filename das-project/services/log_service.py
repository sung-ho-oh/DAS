"""
당직근무일지 서비스
- 일지 CRUD
- 승인 프로세스 (저장 → 승인요청 → 승인/부결)
"""
from services import db
from config import APPROVAL_STATUS


def get_log_by_date(duty_date: str, factory: str) -> dict | None:
    """날짜+공장으로 일지 조회"""
    # TODO: Phase 4에서 구현
    pass


def save_log(data: dict) -> dict:
    """일지 저장 (작성중 상태)"""
    # TODO: Phase 4에서 구현
    pass


def request_approval(log_id: str) -> dict:
    """승인 요청 (작성중 → 승인요청)"""
    # TODO: Phase 4에서 구현
    pass


def approve_log(log_id: str) -> dict:
    """승인 (승인요청 → 승인)"""
    # TODO: Phase 4에서 구현
    pass


def reject_log(log_id: str, reason: str) -> dict:
    """부결 (승인요청 → 부결)"""
    # TODO: Phase 4에서 구현
    pass
