"""
pytest 공통 fixture
- 테스트 DB 세팅, 공통 데이터 준비
"""
import pytest
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def pytest_addoption(parser):
    """커스텀 옵션 추가"""
    parser.addoption("--integration", action="store_true", default=False, help="통합 테스트 실행")
    parser.addoption("--e2e", action="store_true", default=False, help="E2E 테스트 실행")


def pytest_configure(config):
    """마커 등록"""
    config.addinivalue_line("markers", "integration: 통합 테스트")
    config.addinivalue_line("markers", "e2e: E2E 테스트")


def pytest_collection_modifyitems(config, items):
    """마커에 따라 테스트 필터링"""
    if not config.getoption("--integration"):
        skip_integration = pytest.mark.skip(reason="--integration 옵션 필요")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    if not config.getoption("--e2e"):
        skip_e2e = pytest.mark.skip(reason="--e2e 옵션 필요")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


@pytest.fixture
def sample_employee():
    """테스트용 직원 데이터"""
    return {
        "employee_no": "E9999",
        "name": "테스트직원",
        "department": "세탁기",
        "position": "과장",
        "grade": 2,
        "factory": "창원1공장",
        "business_unit": "Digital A.",
        "phone_home": "055-123-4567",
        "phone_mobile": "010-1234-5678",
        "bank_account": "국민-123456789",
        "is_active": True,
    }


@pytest.fixture
def sample_assignment():
    """테스트용 발령 데이터"""
    return {
        "duty_date": "2025-03-15",
        "day_of_week": "토",
        "duty_type": "주간",
        "day_category": "휴무일",
        "status": "예정",
    }
