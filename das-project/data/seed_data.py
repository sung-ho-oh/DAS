"""
테스트 데이터 생성기
- Faker 기반 200명 직원 + 6개월치 당직 데이터 생성
- Supabase에 직접 삽입하거나 CSV/JSON으로 내보내기 가능

사용법:
    python data/seed_data.py              # Supabase에 삽입
    python data/seed_data.py --dry-run    # 데이터만 생성 (삽입 안 함)
"""
import sys
import os
import json
import random
from datetime import date, timedelta
from typing import Optional

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from config import (
    FACTORIES, FACTORY1_DEPARTMENTS, FACTORY2_DEPARTMENTS,
    BUSINESS_UNITS, GRADES, CHANGE_REASONS,
)

fake = Faker("ko_KR")
Faker.seed(42)  # 재현 가능한 데이터
random.seed(42)


# ── 직원 마스터 생성 (200명) ──
def generate_employees(count: int = 200) -> list:
    """직원 마스터 데이터 생성"""
    employees = []
    emp_no_counter = 1001

    # 공장별 50:50 배분
    factory_split = count // 2

    for i in range(count):
        factory = FACTORIES[0] if i < factory_split else FACTORIES[1]
        departments = FACTORY1_DEPARTMENTS if factory == FACTORIES[0] else FACTORY2_DEPARTMENTS
        department = random.choice(departments)
        grade = random.choice([1, 2, 3, 4])
        position = random.choice(GRADES[grade]["positions"])
        business_unit = random.choice(BUSINESS_UNITS)

        employees.append({
            "employee_no": f"E{emp_no_counter}",
            "name": fake.name(),
            "department": department,
            "position": position,
            "grade": grade,
            "factory": factory,
            "business_unit": business_unit,
            "phone_home": fake.phone_number(),
            "phone_mobile": f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
            "bank_account": f"{random.choice(['국민','신한','우리','하나'])}-{fake.bban()}",
            "is_active": True,
        })
        emp_no_counter += 1

    return employees


# ── 당직 발령 생성 (6개월분) ──
def generate_assignments(employees: list, months: int = 6) -> list:
    """월별 당직 발령 데이터 생성"""
    assignments = []
    start_date = date(2025, 1, 1)

    # 직급별 직원 분류
    main_candidates = [e for e in employees if e["grade"] in [1, 2]]
    sub_candidates = [e for e in employees if e["grade"] in [3, 4]]

    main_idx = 0
    sub_idx = 0

    for day_offset in range(months * 30):
        current_date = start_date + timedelta(days=day_offset)
        if current_date > date(2025, 6, 30):
            break

        weekday = current_date.weekday()
        day_names = ["월", "화", "수", "목", "금", "토", "일"]
        is_holiday = weekday >= 5  # 토,일

        if is_holiday:
            # 휴무일: 주간 + 야간
            for duty_type in ["주간", "야간"]:
                main_emp = main_candidates[main_idx % len(main_candidates)]
                sub_emp = sub_candidates[sub_idx % len(sub_candidates)]
                assignments.append({
                    "duty_date": current_date.isoformat(),
                    "day_of_week": day_names[weekday],
                    "duty_type": duty_type,
                    "day_category": "휴무일",
                    "main_duty_employee_no": main_emp["employee_no"],
                    "sub_duty_employee_no": sub_emp["employee_no"],
                    "status": random.choice(["예정", "확정", "완료"]),
                })
                main_idx += 1
                sub_idx += 1
        else:
            # 평일: 야간만
            main_emp = main_candidates[main_idx % len(main_candidates)]
            sub_emp = sub_candidates[sub_idx % len(sub_candidates)]
            assignments.append({
                "duty_date": current_date.isoformat(),
                "day_of_week": day_names[weekday],
                "duty_type": "야간",
                "day_category": "평일",
                "main_duty_employee_no": main_emp["employee_no"],
                "sub_duty_employee_no": sub_emp["employee_no"],
                "status": random.choice(["예정", "확정", "완료"]),
            })
            main_idx += 1
            sub_idx += 1

    return assignments


# ── 당직 변경 생성 ──
def generate_changes(assignments: list, rate: float = 0.12) -> list:
    """발령 대비 10~15% 변경 데이터 생성"""
    changes = []
    sample_count = int(len(assignments) * rate)
    sampled = random.sample(assignments, min(sample_count, len(assignments)))

    for asmt in sampled:
        changes.append({
            "assignment_duty_date": asmt["duty_date"],
            "original_employee_no": asmt["main_duty_employee_no"],
            "new_employee_no": f"E{random.randint(1001, 1200)}",
            "duty_role": "총당직",
            "change_reason": random.choice(CHANGE_REASONS),
            "change_date": asmt["duty_date"],
        })

    return changes


# ── 비상연락망 생성 ──
def generate_emergency_contacts(employees: list) -> list:
    """전 직원 비상연락처"""
    return [{
        "employee_no": emp["employee_no"],
        "phone_home": emp["phone_home"],
        "phone_mobile": emp["phone_mobile"],
        "note": "",
    } for emp in employees]


# ── 당직근무일지 생성 ──
def generate_duty_logs(assignments: list, months: int = 3) -> list:
    """최근 3개월분 일지"""
    logs = []
    cutoff = date(2025, 3, 31)

    for asmt in assignments:
        if date.fromisoformat(asmt["duty_date"]) <= cutoff:
            for factory in FACTORIES:
                logs.append({
                    "log_date": asmt["duty_date"],
                    "factory": factory,
                    "duty_type": asmt["duty_type"],
                    "workforce_status": json.dumps({
                        "departments": {dept: {"특근": random.randint(0, 5), "야근": random.randint(0, 3)}
                                       for dept in (FACTORY1_DEPARTMENTS if factory == FACTORIES[0]
                                                    else FACTORY2_DEPARTMENTS)}
                    }),
                    "construction_status": json.dumps({
                        "주간": {"업체수": random.randint(0, 5), "인원": random.randint(0, 20), "화기작업": random.choice([True, False])},
                        "야간": {"업체수": random.randint(0, 3), "인원": random.randint(0, 10), "화기작업": random.choice([True, False])},
                    }),
                    "issues": fake.sentence() if random.random() > 0.7 else "",
                    "special_notes": fake.sentence() if random.random() > 0.8 else "",
                    "approval_status": random.choice(["승인", "승인", "승인", "부결"]),
                })

    return logs


# ── 메인 ──
def generate_all() -> dict:
    """모든 테스트 데이터 생성"""
    print("🔧 테스트 데이터 생성 중...")

    employees = generate_employees(200)
    print(f"  ✅ 직원 마스터: {len(employees)}명")

    assignments = generate_assignments(employees, 6)
    print(f"  ✅ 당직 발령: {len(assignments)}건")

    changes = generate_changes(assignments)
    print(f"  ✅ 당직 변경: {len(changes)}건")

    contacts = generate_emergency_contacts(employees)
    print(f"  ✅ 비상연락망: {len(contacts)}건")

    logs = generate_duty_logs(assignments, 3)
    print(f"  ✅ 당직근무일지: {len(logs)}건")

    return {
        "employees": employees,
        "assignments": assignments,
        "changes": changes,
        "contacts": contacts,
        "logs": logs,
    }


if __name__ == "__main__":
    data = generate_all()

    if "--dry-run" in sys.argv:
        print("\n📋 [Dry Run] 데이터 미리보기:")
        for key, items in data.items():
            print(f"  {key}: {len(items)}건")
            if items:
                print(f"    예시: {json.dumps(items[0], ensure_ascii=False, indent=2)[:200]}...")
    else:
        print("\n⚠️  Supabase 삽입은 Phase 1 개발 시 구현됩니다.")
        print("    현재는 --dry-run으로 데이터 생성만 확인해주세요.")
        print(f"\n📊 총 생성 데이터:")
        for key, items in data.items():
            print(f"  {key}: {len(items)}건")
