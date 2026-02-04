# Database Migrations

## RLS 정책 설정 (필수)

Supabase에서 앱이 정상 작동하려면 RLS (Row Level Security) 정책을 설정해야 합니다.

### 설정 방법

1. **Supabase Dashboard 접속**
   - URL: https://supabase.com/dashboard/project/dluufyjfxevumhgqnpzy

2. **SQL Editor 열기**
   - 왼쪽 메뉴에서 "SQL Editor" 클릭

3. **스크립트 실행**
   - `enable_rls_policies.sql` 파일의 내용을 복사
   - SQL Editor에 붙여넣기
   - "Run" 버튼 클릭

4. **확인**
   - 성공 메시지가 표시되면 완료
   - 앱을 새로고침하여 데이터가 표시되는지 확인

### 문제 해결

**403 Forbidden 에러가 발생하는 경우:**
- RLS 정책이 올바르게 설정되지 않았을 수 있습니다
- 위 스크립트를 다시 실행해주세요

**테이블이 존재하지 않는다는 에러:**
- `data/seed_data.py`를 먼저 실행하여 테이블과 데이터를 생성해주세요
- `python data/seed_data.py`

### 설정되는 정책

- `employees`: 직원 정보
- `duty_assignments`: 당직 발령
- `duty_changes`: 당직 변경
- `duty_logs`: 당직근무일지
- `duty_payments`: 당직비 지급
- `emergency_contacts`: 비상연락망
- `duty_rules`: 발령 기준 (선택)

모든 테이블에 대해 anon 키로 모든 작업(SELECT, INSERT, UPDATE, DELETE)이 가능하도록 설정됩니다.

⚠️ **주의**: 프로덕션 환경에서는 더 엄격한 보안 정책을 사용해야 합니다.
