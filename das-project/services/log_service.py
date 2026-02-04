"""
당직근무일지 서비스
- 일지 CRUD
- 승인 프로세스 (저장 → 승인요청 → 승인/부결)
"""
from services import db
from config import APPROVAL_STATUS


def get_log_by_date(duty_date: str, factory: str, duty_type: str = None) -> dict | None:
    """날짜+공장으로 일지 조회"""
    client = db.get_client()
    query = (
        client.table("duty_logs")
        .select("*")
        .eq("log_date", duty_date)
        .eq("factory", factory)
    )

    if duty_type:
        query = query.eq("duty_type", duty_type)

    response = query.execute()
    if response.data:
        return response.data[0]
    return None


def save_log(data: dict) -> dict:
    """일지 저장 (작성중 상태)"""
    # 기존 일지 확인
    existing_log = get_log_by_date(data["log_date"], data["factory"], data.get("duty_type"))

    if existing_log:
        # 수정
        log_id = existing_log["id"]
        return db.update("duty_logs", log_id, data)
    else:
        # 신규 저장
        data["approval_status"] = "작성중"
        return db.insert("duty_logs", data)


def request_approval(log_id: str) -> dict:
    """승인 요청 (작성중 → 승인요청)"""
    return db.update("duty_logs", log_id, {"approval_status": "승인요청"})


def approve_log(log_id: str) -> dict:
    """승인 (승인요청 → 승인)"""
    from datetime import datetime
    return db.update("duty_logs", log_id, {
        "approval_status": "승인",
        "approved_at": datetime.now().isoformat(),
    })


def reject_log(log_id: str, reason: str) -> dict:
    """부결 (승인요청 → 부결)"""
    return db.update("duty_logs", log_id, {
        "approval_status": "부결",
        "rejection_reason": reason,
    })
