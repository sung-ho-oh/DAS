"""
당직근무일지 서비스
- 일지 CRUD
- 승인 프로세스 (저장 → 승인요청 → 승인/부결)
"""
from services import db
from config import APPROVAL_STATUS
from datetime import datetime
import calendar


def get_logs_by_month(year: int, month: int, factory: str = None) -> list:
    """월별 일지 조회 (공장 필터 옵션)"""
    last_day = calendar.monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    # 일지 조회 (직원 정보 JOIN)
    client = db.get_client()
    query = (
        client.table("duty_logs")
        .select("*, main_duty:main_duty_id(*), sub_duty:sub_duty_id(*)")
        .gte("log_date", start_date)
        .lte("log_date", end_date)
        .order("log_date", desc=True)
    )

    if factory:
        query = query.eq("factory", factory)

    result = query.execute()
    return result.data if result.data else []


def get_log_by_date(log_date: str, factory: str, duty_type: str) -> dict | None:
    """날짜+공장+주야로 일지 조회"""
    client = db.get_client()
    result = (
        client.table("duty_logs")
        .select("*, main_duty:main_duty_id(*), sub_duty:sub_duty_id(*)")
        .eq("log_date", log_date)
        .eq("factory", factory)
        .eq("duty_type", duty_type)
        .execute()
    )

    return result.data[0] if result.data else None


def save_log(data: dict) -> dict:
    """일지 저장 (신규 또는 수정)"""
    # 기존 일지 확인
    existing = get_log_by_date(
        data["log_date"], data["factory"], data["duty_type"]
    )

    if existing:
        # 기존 일지 수정
        log_id = existing["id"]
        # 승인된 일지는 수정 불가
        if existing["approval_status"] == "승인":
            raise ValueError("승인된 일지는 수정할 수 없습니다.")

        return db.update("duty_logs", log_id, data)
    else:
        # 새 일지 생성
        data["approval_status"] = "작성중"
        return db.insert("duty_logs", data)


def request_approval(log_id: str) -> dict:
    """승인 요청 (작성중 → 승인요청)"""
    log = db.select_by_id("duty_logs", log_id)

    if not log:
        raise ValueError("일지를 찾을 수 없습니다.")

    if log["approval_status"] != "작성중":
        raise ValueError("작성중 상태의 일지만 승인 요청할 수 있습니다.")

    return db.update("duty_logs", log_id, {"approval_status": "승인요청"})


def approve_log(log_id: str) -> dict:
    """승인 (승인요청 → 승인)"""
    log = db.select_by_id("duty_logs", log_id)

    if not log:
        raise ValueError("일지를 찾을 수 없습니다.")

    if log["approval_status"] != "승인요청":
        raise ValueError("승인요청 상태의 일지만 승인할 수 있습니다.")

    return db.update("duty_logs", log_id, {
        "approval_status": "승인",
        "approved_at": datetime.now().isoformat(),
    })


def reject_log(log_id: str, reason: str) -> dict:
    """부결 (승인요청 → 부결)"""
    log = db.select_by_id("duty_logs", log_id)

    if not log:
        raise ValueError("일지를 찾을 수 없습니다.")

    if log["approval_status"] != "승인요청":
        raise ValueError("승인요청 상태의 일지만 부결할 수 있습니다.")

    return db.update("duty_logs", log_id, {
        "approval_status": "부결",
        "rejection_reason": reason,
    })
