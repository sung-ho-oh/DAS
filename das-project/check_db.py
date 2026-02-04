"""
Supabase 연결 확인 스크립트
- .env 파일 설정 확인
- Supabase 연결 테스트
- 테이블 존재 여부 확인

사용법:
    python check_db.py
"""
import sys
from services.db import get_client
from config import SUPABASE_URL, SUPABASE_KEY


def check_env():
    """환경변수 확인"""
    print("🔍 환경변수 확인 중...")

    if not SUPABASE_URL or SUPABASE_URL == "https://your-project.supabase.co":
        print("  ❌ SUPABASE_URL이 설정되지 않았습니다.")
        print("     .env 파일에서 SUPABASE_URL을 설정하세요.")
        return False

    if not SUPABASE_KEY or SUPABASE_KEY == "your-anon-key-here":
        print("  ❌ SUPABASE_KEY가 설정되지 않았습니다.")
        print("     .env 파일에서 SUPABASE_KEY를 설정하세요.")
        return False

    print(f"  ✅ SUPABASE_URL: {SUPABASE_URL[:40]}...")
    print(f"  ✅ SUPABASE_KEY: {SUPABASE_KEY[:20]}...")
    return True


def check_connection():
    """Supabase 연결 확인"""
    print("\n🔌 Supabase 연결 확인 중...")

    try:
        client = get_client()
        print("  ✅ Supabase 클라이언트 생성 성공")
        return client
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}")
        return None


def check_tables(client):
    """테이블 존재 여부 확인"""
    print("\n📋 테이블 확인 중...")

    tables = [
        "employees",
        "duty_assignments",
        "duty_changes",
        "duty_logs",
        "duty_payments",
        "emergency_contacts",
        "duty_rules",
    ]

    all_exist = True
    for table in tables:
        try:
            # 빈 조회를 시도해서 테이블 존재 확인
            response = client.table(table).select("*").limit(1).execute()
            count = len(response.data)
            print(f"  ✅ {table}: {count}건 (테이블 존재)")
        except Exception as e:
            print(f"  ❌ {table}: 테이블 없음 또는 접근 불가")
            print(f"     오류: {e}")
            all_exist = False

    return all_exist


def main():
    """메인 실행"""
    print("=" * 60)
    print("DAS - Supabase 연결 확인")
    print("=" * 60)

    # 1. 환경변수 확인
    if not check_env():
        print("\n❌ 환경변수 설정 후 다시 시도하세요.")
        sys.exit(1)

    # 2. 연결 확인
    client = check_connection()
    if not client:
        print("\n❌ Supabase 연결에 실패했습니다.")
        sys.exit(1)

    # 3. 테이블 확인
    tables_ok = check_tables(client)

    print("\n" + "=" * 60)
    if tables_ok:
        print("✨ 모든 확인 완료! Supabase가 정상적으로 연결되었습니다.")
        print("\n다음 단계:")
        print("  1. python data/seed_data.py          # 테스트 데이터 삽입")
        print("  2. streamlit run app.py              # 앱 실행")
    else:
        print("⚠️  일부 테이블이 없습니다.")
        print("\n다음 단계:")
        print("  1. Supabase SQL Editor에서 data/schema.sql 실행")
        print("  2. python check_db.py                # 다시 확인")
        print("  3. python data/seed_data.py          # 테스트 데이터 삽입")
    print("=" * 60)


if __name__ == "__main__":
    main()
