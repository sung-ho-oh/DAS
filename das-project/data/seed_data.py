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


def insert_to_supabase(data: dict) -> dict:
    """
    생성된 데이터를 Supabase에 삽입
    반환: employee_no -> UUID 매핑
    """
    try:
        from services import db
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        print("   .env 파일에 SUPABASE_URL과 SUPABASE_KEY를 설정했는지 확인하세요.")
        return {}

    print("\n📤 Supabase에 데이터 삽입 중...")

    # 1. 직원 삽입 (employee_no -> UUID 매핑 생성)
    print("  → 직원 마스터 삽입 중...")
    emp_map = {}  # employee_no -> UUID
    try:
        inserted_emps = db.insert_many("employees", data["employees"])
        for emp in inserted_emps:
            emp_map[emp["employee_no"]] = emp["id"]
        print(f"    ✅ {len(inserted_emps)}명 삽입 완료")
    except Exception as e:
        print(f"    ❌ 직원 삽입 실패: {e}")
        return emp_map

    # 2. 당직 발령 삽입 (employee_no -> UUID 변환)
    print("  → 당직 발령 삽입 중...")
    assignments_with_ids = []
    for asmt in data["assignments"]:
        asmt_copy = asmt.copy()
        # employee_no를 UUID로 변환
        main_no = asmt_copy.pop("main_duty_employee_no")
        sub_no = asmt_copy.pop("sub_duty_employee_no")
        asmt_copy["main_duty_id"] = emp_map.get(main_no)
        asmt_copy["sub_duty_id"] = emp_map.get(sub_no)
        assignments_with_ids.append(asmt_copy)

    try:
        inserted_asmts = db.insert_many("duty_assignments", assignments_with_ids)
        print(f"    ✅ {len(inserted_asmts)}건 삽입 완료")
        # duty_date + duty_type -> assignment UUID 매핑 생성
        asmt_map = {(a["duty_date"], a["duty_type"]): a["id"] for a in inserted_asmts}
    except Exception as e:
        print(f"    ❌ 당직 발령 삽입 실패: {e}")
        asmt_map = {}

    # 3. 당직 변경 삽입 (employee_no -> UUID, duty_date -> assignment_id 변환)
    print("  → 당직 변경 삽입 중...")
    changes_with_ids = []
    for change in data["changes"]:
        change_copy = change.copy()
        # duty_date -> assignment_id 변환 (첫 번째 매칭되는 것 사용)
        duty_date = change_copy.pop("assignment_duty_date")
        assignment_id = None
        for (date_key, type_key), aid in asmt_map.items():
            if date_key == duty_date:
                assignment_id = aid
                break

        if not assignment_id:
            continue  # 해당 발령이 없으면 스킵

        # employee_no -> UUID 변환
        orig_no = change_copy.pop("original_employee_no")
        new_no = change_copy.pop("new_employee_no")
        change_copy["assignment_id"] = assignment_id
        change_copy["original_employee_id"] = emp_map.get(orig_no)
        change_copy["new_employee_id"] = emp_map.get(new_no)

        if change_copy["original_employee_id"] and change_copy["new_employee_id"]:
            changes_with_ids.append(change_copy)

    try:
        if changes_with_ids:
            inserted_changes = db.insert_many("duty_changes", changes_with_ids)
            print(f"    ✅ {len(inserted_changes)}건 삽입 완료")
        else:
            print(f"    ⚠️  삽입할 변경 데이터 없음")
    except Exception as e:
        print(f"    ❌ 당직 변경 삽입 실패: {e}")

    # 4. 비상연락망 삽입 (employee_no -> UUID 변환)
    print("  → 비상연락망 삽입 중...")
    contacts_with_ids = []
    for contact in data["contacts"]:
        contact_copy = contact.copy()
        emp_no = contact_copy.pop("employee_no")
        contact_copy["employee_id"] = emp_map.get(emp_no)
        if contact_copy["employee_id"]:
            contacts_with_ids.append(contact_copy)

    try:
        inserted_contacts = db.insert_many("emergency_contacts", contacts_with_ids)
        print(f"    ✅ {len(inserted_contacts)}건 삽입 완료")
    except Exception as e:
        print(f"    ❌ 비상연락망 삽입 실패: {e}")

    # 5. 당직근무일지 삽입 (main_duty_id, sub_duty_id는 None으로)
    print("  → 당직근무일지 삽입 중...")
    try:
        inserted_logs = db.insert_many("duty_logs", data["logs"])
        print(f"    ✅ {len(inserted_logs)}건 삽입 완료")
    except Exception as e:
        print(f"    ❌ 당직근무일지 삽입 실패: {e}")

    print("\n✅ Supabase 삽입 완료!")
    return emp_map


if __name__ == "__main__":
    data = generate_all()

    if "--dry-run" in sys.argv:
        print("\n📋 [Dry Run] 데이터 미리보기:")
        for key, items in data.items():
            print(f"  {key}: {len(items)}건")
            if items:
                print(f"    예시: {json.dumps(items[0], ensure_ascii=False, indent=2)[:200]}...")
    else:
        # Supabase에 삽입
        emp_map = insert_to_supabase(data)
        if emp_map:
            print(f"\n📊 삽입 완료 통계:")
            for key, items in data.items():
                print(f"  {key}: {len(items)}건")
