"""
알림(메일) 서비스
- 테스트 환경: 실제 메일 발송 없이 로그만 기록
- 운영 환경: n8n Webhook 호출로 메일 발송
"""
import logging
from datetime import datetime
from config import APP_ENV, N8N_WEBHOOK_URL

logger = logging.getLogger(__name__)


def send_notification(recipients: list, subject: str, body: str) -> dict:
    """
    알림 발송 (테스트에서는 로그만 기록)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "recipients": recipients,
        "subject": subject,
        "body_preview": body[:100],
        "status": "logged",
        "env": APP_ENV,
    }

    if APP_ENV == "production":
        # TODO: Phase 6에서 n8n Webhook 호출 구현
        # requests.post(N8N_WEBHOOK_URL, json=log_entry)
        log_entry["status"] = "sent"
    else:
        logger.info(f"[알림 로그] To: {recipients}, Subject: {subject}")
        log_entry["status"] = "test_logged"

    return log_entry


def send_assignment_notification(month: str, notification_type: str) -> dict:
    """
    당직 발령 메일 발송
    - notification_type: '예정자' (20일) | '확정자' (25일) | '리마인더' (D-5)
    """
    # TODO: Phase 6에서 구현
    return send_notification(
        recipients=["test@example.com"],
        subject=f"{month} 당직발령 {notification_type} 안내",
        body=f"{month} 당직발령 {notification_type} 안내 메일입니다.",
    )


def send_log_approval_notification(log_id: str, approved: bool) -> dict:
    """당직일지 승인/부결 알림"""
    # TODO: Phase 6에서 구현
    status = "승인" if approved else "부결"
    return send_notification(
        recipients=["test@example.com"],
        subject=f"당직근무일지 {status} 알림",
        body=f"당직근무일지(ID: {log_id})가 {status}되었습니다.",
    )
