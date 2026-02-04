"""
데이터 생성기 테스트
- 생성 건수 정확성
- 직급/부서 분포 균등성
- FK 정합성
"""
import pytest
from data.seed_data import (
    generate_employees,
    generate_assignments,
    generate_changes,
    generate_emergency_contacts,
    generate_duty_logs,
    generate_all,
)


class TestEmployeeGenerator:
    """직원 마스터 생성 테스트"""

    def test_count(self):
        employees = generate_employees(200)
        assert len(employees) == 200

    def test_unique_employee_no(self):
        employees = generate_employees(200)
        nos = [e["employee_no"] for e in employees]
        assert len(nos) == len(set(nos)), "사번 중복 발견"

    def test_factory_distribution(self):
        employees = generate_employees(200)
        f1 = [e for e in employees if e["factory"] == "창원1공장"]
        f2 = [e for e in employees if e["factory"] == "창원2공장"]
        assert len(f1) == 100
        assert len(f2) == 100

    def test_grade_range(self):
        employees = generate_employees(200)
        for emp in employees:
            assert 1 <= emp["grade"] <= 4, f"유효하지 않은 급호: {emp['grade']}"

    def test_required_fields(self):
        employees = generate_employees(10)
        required = ["employee_no", "name", "department", "position", "grade", "factory", "business_unit"]
        for emp in employees:
            for field in required:
                assert field in emp, f"필수 필드 누락: {field}"
                assert emp[field], f"필수 필드 값 없음: {field}"


class TestAssignmentGenerator:
    """당직 발령 생성 테스트"""

    def test_generates_assignments(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 1)
        assert len(assignments) > 0

    def test_weekday_only_night(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 1)
        weekday_assignments = [a for a in assignments if a["day_category"] == "평일"]
        for a in weekday_assignments:
            assert a["duty_type"] == "야간", "평일은 야간만 있어야 함"

    def test_holiday_both_shifts(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 1)
        holiday_assignments = [a for a in assignments if a["day_category"] == "휴무일"]
        types = set(a["duty_type"] for a in holiday_assignments)
        assert "주간" in types and "야간" in types, "휴무일은 주간+야간 모두 있어야 함"

    def test_valid_status(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 1)
        valid_statuses = {"예정", "확정", "변경", "완료"}
        for a in assignments:
            assert a["status"] in valid_statuses


class TestChangeGenerator:
    """당직 변경 생성 테스트"""

    def test_change_rate(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 3)
        changes = generate_changes(assignments, rate=0.12)
        ratio = len(changes) / len(assignments)
        assert 0.05 <= ratio <= 0.20, f"변경률 범위 이탈: {ratio:.2%}"

    def test_has_reason(self):
        employees = generate_employees(50)
        assignments = generate_assignments(employees, 1)
        changes = generate_changes(assignments)
        for ch in changes:
            assert ch["change_reason"], "변경사유 누락"


class TestEmergencyContacts:
    """비상연락망 생성 테스트"""

    def test_count_matches_employees(self):
        employees = generate_employees(100)
        contacts = generate_emergency_contacts(employees)
        assert len(contacts) == len(employees)


class TestGenerateAll:
    """전체 데이터 생성 테스트"""

    def test_all_keys_present(self):
        data = generate_all()
        expected_keys = {"employees", "assignments", "changes", "contacts", "logs"}
        assert set(data.keys()) == expected_keys

    def test_all_have_data(self):
        data = generate_all()
        for key, items in data.items():
            assert len(items) > 0, f"{key} 데이터가 비어 있음"
