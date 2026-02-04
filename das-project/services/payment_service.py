"""
당직비 지급 서비스
- 당직비 계산/집계
- 사업부별 소계/합계
- Excel 다운로드 데이터 생성
"""
from services import db
from config import DUTY_PAYMENT_RATES


def calculate_monthly_payments(year: int, month: int) -> list:
    """월별 당직비 계산"""
    # TODO: Phase 5에서 구현
    pass


def get_payments_by_month(year: int, month: int) -> list:
    """월별 당직비 조회"""
    # TODO: Phase 5에서 구현
    pass


def get_summary_by_business_unit(year: int, month: int) -> dict:
    """사업부별 집계"""
    # TODO: Phase 5에서 구현
    pass


def generate_excel_data(year: int, month: int) -> bytes:
    """Excel 다운로드용 데이터 생성"""
    # TODO: Phase 5에서 구현
    pass
