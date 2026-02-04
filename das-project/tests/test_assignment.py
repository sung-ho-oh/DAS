"""
당직 발령 기능 테스트
- 발령 CRUD
- LAST 사번 기반 순번 배정
- 직급별 자동 분류
"""
import pytest


class TestAssignmentCRUD:
    """발령 기본 CRUD 테스트"""

    def test_placeholder(self):
        """Phase 2에서 구현"""
        assert True

    @pytest.mark.integration
    def test_create_assignment_db(self, sample_assignment):
        """[통합] DB에 발령 생성"""
        pytest.skip("Phase 2에서 구현")

    @pytest.mark.integration
    def test_get_assignments_by_month(self):
        """[통합] 월별 발령 조회"""
        pytest.skip("Phase 2에서 구현")


class TestLastDutyPerson:
    """LAST 사번 테스트"""

    def test_placeholder(self):
        """Phase 2에서 구현"""
        assert True

    @pytest.mark.integration
    def test_auto_assign_rotation(self):
        """[통합] 순번 자동배정 순환 검증"""
        pytest.skip("Phase 2에서 구현")


class TestGradeClassification:
    """직급별 분류 테스트"""

    def test_placeholder(self):
        """Phase 2에서 구현"""
        assert True
