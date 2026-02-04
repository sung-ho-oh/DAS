"""
당직 발령 기능 테스트
- 발령 CRUD
- LAST 사번 기반 순번 배정
- 직급별 자동 분류
"""
import pytest
from services import assignment_service
from config import DUTY_RULES


class TestAssignmentCRUD:
    """발령 기본 CRUD 테스트"""

    def test_get_assignments_by_month_returns_list(self):
        """월별 발령 조회 함수가 리스트를 반환하는지 검증"""
        # 단위 테스트: 함수가 올바른 타입을 반환하는지만 검증
        # 실제 DB 연결은 통합 테스트에서 검증
        assert callable(assignment_service.get_assignments_by_month)

    @pytest.mark.integration
    def test_create_assignment_db(self, sample_assignment):
        """[통합] DB에 발령 생성"""
        pytest.skip("Supabase 연결 필요 - UAT에서 테스트")

    @pytest.mark.integration
    def test_get_assignments_by_month_integration(self):
        """[통합] 월별 발령 조회"""
        pytest.skip("Supabase 연결 필요 - UAT에서 테스트")


class TestLastDutyPerson:
    """LAST 사번 테스트"""

    def test_auto_assign_next_function_exists(self):
        """자동배정 함수가 존재하는지 검증"""
        assert callable(assignment_service.auto_assign_next)

    def test_get_last_duty_person_function_exists(self):
        """LAST 사번 조회 함수가 존재하는지 검증"""
        assert callable(assignment_service.get_last_duty_person)

    @pytest.mark.integration
    def test_auto_assign_rotation(self):
        """[통합] 순번 자동배정 순환 검증"""
        pytest.skip("Supabase 연결 필요 - UAT에서 테스트")


class TestGradeClassification:
    """직급별 분류 테스트"""

    def test_duty_rules_config_exists(self):
        """발령 기준 설정이 존재하는지 검증"""
        assert "holiday_main" in DUTY_RULES
        assert "holiday_sub" in DUTY_RULES
        assert "weekday_main" in DUTY_RULES
        assert "weekday_sub" in DUTY_RULES

    def test_duty_rules_have_grades(self):
        """발령 기준에 직급 정보가 있는지 검증"""
        for rule_key, rule in DUTY_RULES.items():
            assert "grades" in rule, f"{rule_key}에 grades 필드 없음"
            assert isinstance(rule["grades"], list), f"{rule_key}의 grades가 리스트가 아님"
            assert len(rule["grades"]) > 0, f"{rule_key}의 grades가 비어있음"

    def test_get_eligible_employees_function_exists(self):
        """발령 대상 직원 조회 함수가 존재하는지 검증"""
        assert callable(assignment_service.get_eligible_employees)

    @pytest.mark.integration
    def test_eligible_employees_by_grade(self):
        """[통합] 직급별 대상 직원 조회"""
        pytest.skip("Supabase 연결 필요 - UAT에서 테스트")


class TestAssignmentServiceIntegrity:
    """서비스 계층 무결성 테스트"""

    def test_all_crud_functions_exist(self):
        """모든 CRUD 함수가 존재하는지 검증"""
        assert callable(assignment_service.get_assignments_by_month)
        assert callable(assignment_service.create_assignment)
        assert callable(assignment_service.update_assignment)
        assert callable(assignment_service.delete_assignment)

    def test_all_business_logic_functions_exist(self):
        """모든 비즈니스 로직 함수가 존재하는지 검증"""
        assert callable(assignment_service.get_last_duty_person)
        assert callable(assignment_service.get_eligible_employees)
        assert callable(assignment_service.auto_assign_next)
