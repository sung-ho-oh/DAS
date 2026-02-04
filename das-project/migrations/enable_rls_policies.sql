-- ============================================
-- RLS 정책 설정 스크립트
-- DAS (Duty Assignment System)
-- ============================================
--
-- 이 스크립트를 Supabase SQL Editor에서 실행하여
-- anon 키로 모든 테이블에 접근할 수 있도록 설정합니다.
--
-- 실행 방법:
-- 1. Supabase Dashboard 접속
-- 2. SQL Editor 메뉴 클릭
-- 3. 이 스크립트 전체를 복사하여 붙여넣기
-- 4. "Run" 버튼 클릭
-- ============================================

-- 1. employees 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON employees;
CREATE POLICY "Allow all for anon" ON employees
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 2. duty_assignments 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_assignments;
CREATE POLICY "Allow all for anon" ON duty_assignments
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 3. duty_changes 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_changes;
CREATE POLICY "Allow all for anon" ON duty_changes
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 4. duty_logs 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_logs;
CREATE POLICY "Allow all for anon" ON duty_logs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 5. duty_payments 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_payments;
CREATE POLICY "Allow all for anon" ON duty_payments
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 6. emergency_contacts 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON emergency_contacts;
CREATE POLICY "Allow all for anon" ON emergency_contacts
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 7. duty_rules 테이블 (존재하는 경우)
DROP POLICY IF EXISTS "Allow all for anon" ON duty_rules;
CREATE POLICY "Allow all for anon" ON duty_rules
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================
-- 완료 메시지
-- ============================================
SELECT 'RLS 정책이 성공적으로 설정되었습니다!' as message;
