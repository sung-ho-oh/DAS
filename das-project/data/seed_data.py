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
            "duty_type": asmt["duty_type"],  # assignment_id 매핑을 위해 추가
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


def insert_to_supabase(data: dict):
    """Supabase에 테스트 데이터 삽입"""
    from services import db

    print("\n🚀 Supabase에 데이터 삽입 중...")

    try:
        # 1. 직원 마스터 삽입
        print("  📥 직원 마스터 삽입 중...")
        inserted_employees = db.insert_many("employees", data["employees"])
        print(f"    ✅ {len(inserted_employees)}명 삽입 완료")

        # employee_no -> UUID 매핑 생성
        emp_no_to_id = {emp["employee_no"]: emp["id"] for emp in inserted_employees}

        # 2. 당직 발령 삽입 (employee_no -> UUID 변환)
        print("  📥 당직 발령 삽입 중...")
        assignments_with_ids = []
        for asmt in data["assignments"]:
            assignments_with_ids.append({
                "duty_date": asmt["duty_date"],
                "day_of_week": asmt["day_of_week"],
                "duty_type": asmt["duty_type"],
                "day_category": asmt["day_category"],
                "main_duty_id": emp_no_to_id.get(asmt["main_duty_employee_no"]),
                "sub_duty_id": emp_no_to_id.get(asmt["sub_duty_employee_no"]),
                "status": asmt["status"],
            })
        inserted_assignments = db.insert_many("duty_assignments", assignments_with_ids)
        print(f"    ✅ {len(inserted_assignments)}건 삽입 완료")

        # duty_date -> assignment_id 매핑 생성
        duty_date_to_id = {f"{a['duty_date']}_{a['duty_type']}": a["id"] for a in inserted_assignments}

        # 3. 당직 변경 삽입
        print("  📥 당직 변경 삽입 중...")
        changes_with_ids = []
        for change in data["changes"]:
            assignment_key = f"{change['assignment_duty_date']}_{change.get('duty_type', '야간')}"
            assignment_id = duty_date_to_id.get(assignment_key)
            if assignment_id and change["original_employee_no"] in emp_no_to_id and change["new_employee_no"] in emp_no_to_id:
                changes_with_ids.append({
                    "assignment_id": assignment_id,
                    "original_employee_id": emp_no_to_id[change["original_employee_no"]],
                    "new_employee_id": emp_no_to_id[change["new_employee_no"]],
                    "duty_role": change["duty_role"],
                    "change_reason": change["change_reason"],
                    "change_date": change["change_date"],
                })
        if changes_with_ids:
            inserted_changes = db.insert_many("duty_changes", changes_with_ids)
            print(f"    ✅ {len(inserted_changes)}건 삽입 완료")
        else:
            print(f"    ⚠️  삽입할 변경 데이터 없음")

        # 4. 비상연락망 삽입
        print("  📥 비상연락망 삽입 중...")
        contacts_with_ids = []
        for contact in data["contacts"]:
            if contact["employee_no"] in emp_no_to_id:
                contacts_with_ids.append({
                    "employee_id": emp_no_to_id[contact["employee_no"]],
                    "phone_home": contact["phone_home"],
                    "phone_mobile": contact["phone_mobile"],
                    "note": contact.get("note", ""),
                })
        inserted_contacts = db.insert_many("emergency_contacts", contacts_with_ids)
        print(f"    ✅ {len(inserted_contacts)}건 삽입 완료")

        # 5. 당직근무일지 삽입 (당직자 정보는 임시로 첫 번째 직원 사용)
        print("  📥 당직근무일지 삽입 중...")
        logs_with_ids = []
        first_emp_id = inserted_employees[0]["id"] if inserted_employees else None
        for log in data["logs"]:
            logs_with_ids.append({
                "log_date": log["log_date"],
                "factory": log["factory"],
                "duty_type": log["duty_type"],
                "main_duty_id": first_emp_id,  # 임시
                "sub_duty_id": first_emp_id,   # 임시
                "workforce_status": log["workforce_status"],
                "construction_status": log["construction_status"],
                "issues": log.get("issues", ""),
                "special_notes": log.get("special_notes", ""),
                "approval_status": log["approval_status"],
            })
        inserted_logs = db.insert_many("duty_logs", logs_with_ids)
        print(f"    ✅ {len(inserted_logs)}건 삽입 완료")

        print("\n✨ 모든 데이터 삽입 완료!")
        print(f"  - 직원: {len(inserted_employees)}명")
        print(f"  - 발령: {len(inserted_assignments)}건")
        print(f"  - 변경: {len(changes_with_ids)}건")
        print(f"  - 연락망: {len(inserted_contacts)}건")
        print(f"  - 일지: {len(inserted_logs)}건")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("  Supabase 연결 정보를 확인하세요 (.env 파일)")
        raise


if __name__ == "__main__":
    data = generate_all()

    if "--dry-run" in sys.argv:
        print("\n📋 [Dry Run] 데이터 미리보기:")
        for key, items in data.items():
            print(f"  {key}: {len(items)}건")
            if items:
                print(f"    예시: {json.dumps(items[0], ensure_ascii=False, indent=2)[:200]}...")
    else:
        insert_to_supabase(data)
