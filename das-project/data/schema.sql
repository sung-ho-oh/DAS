-- ============================================================
-- DAS (Duty Assignment System) - Database Schema
-- Supabase SQL Editor에서 실행
-- ============================================================

-- 1. 직원 마스터
CREATE TABLE IF NOT EXISTS employees (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_no VARCHAR(20) UNIQUE NOT NULL,       -- 사번
    name VARCHAR(50) NOT NULL,                     -- 성명
    department VARCHAR(100) NOT NULL,              -- 소속부서
    position VARCHAR(20) NOT NULL,                 -- 직위 (수석,부장,차장,과장,대리,사원)
    grade INTEGER NOT NULL CHECK (grade BETWEEN 1 AND 4),  -- 급호 (1~4급)
    factory VARCHAR(20) NOT NULL,                  -- 공장 (창원1공장/창원2공장)
    business_unit VARCHAR(50) NOT NULL,            -- 사업부
    phone_home VARCHAR(20),                        -- 자택전화
    phone_mobile VARCHAR(20),                      -- 핸드폰
    bank_account VARCHAR(50),                      -- 계좌번호
    is_active BOOLEAN DEFAULT true,                -- 재직여부
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 당직 발령
CREATE TABLE IF NOT EXISTS duty_assignments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    duty_date DATE NOT NULL,                       -- 당직일자
    day_of_week VARCHAR(10) NOT NULL,              -- 요일
    duty_type VARCHAR(10) NOT NULL,                -- 주간/야간
    day_category VARCHAR(10) NOT NULL,             -- 휴무일/평일
    main_duty_id UUID REFERENCES employees(id),    -- 총당직자 FK
    sub_duty_id UUID REFERENCES employees(id),     -- 부당직자 FK
    status VARCHAR(10) DEFAULT '예정'              -- 예정/확정/변경/완료
        CHECK (status IN ('예정', '확정', '변경', '완료')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(duty_date, duty_type)
);

-- 3. 당직 변경
CREATE TABLE IF NOT EXISTS duty_changes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    assignment_id UUID NOT NULL REFERENCES duty_assignments(id) ON DELETE CASCADE,
    original_employee_id UUID NOT NULL REFERENCES employees(id),  -- 변경 전
    new_employee_id UUID NOT NULL REFERENCES employees(id),       -- 변경 후
    duty_role VARCHAR(10) NOT NULL,                -- 총당직/부당직
    change_reason VARCHAR(100) NOT NULL,           -- 변경사유
    change_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. 당직근무일지
CREATE TABLE IF NOT EXISTS duty_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    log_date DATE NOT NULL,                        -- 일자
    factory VARCHAR(20) NOT NULL,                  -- 공장구분
    duty_type VARCHAR(10) NOT NULL,                -- 주간/야간
    main_duty_id UUID REFERENCES employees(id),    -- 총당직자
    sub_duty_id UUID REFERENCES employees(id),     -- 부당직자
    workforce_status JSONB DEFAULT '{}',           -- 근무인원현황 (부서별 특근/야근)
    construction_status JSONB DEFAULT '{}',        -- 공사현황 (업체수/인원/화기)
    issues TEXT,                                   -- 문제점/조치사항
    special_notes TEXT,                            -- 특이사항
    approval_status VARCHAR(10) DEFAULT '작성중'
        CHECK (approval_status IN ('작성중', '승인요청', '승인', '부결')),
    rejection_reason TEXT,                         -- 부결 사유
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(log_date, factory, duty_type)
);

-- 5. 당직비 지급
CREATE TABLE IF NOT EXISTS duty_payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    payment_month VARCHAR(7) NOT NULL,             -- YYYY-MM
    employee_id UUID NOT NULL REFERENCES employees(id),
    duty_count INTEGER DEFAULT 0,                  -- 당직 횟수
    amount INTEGER DEFAULT 0,                      -- 금액 (원)
    payment_status VARCHAR(10) DEFAULT '미지급'
        CHECK (payment_status IN ('미지급', '지급완료')),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(payment_month, employee_id)
);

-- 6. 비상연락망
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_id UUID NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    phone_home VARCHAR(20),                        -- 자택전화
    phone_mobile VARCHAR(20),                      -- 핸드폰
    note TEXT,                                     -- 비고
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(employee_id)
);

-- 7. 발령기준/근무시간 (고정값)
CREATE TABLE IF NOT EXISTS duty_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    rule_type VARCHAR(20) NOT NULL,                -- 총당직/부당직
    day_category VARCHAR(10) NOT NULL,             -- 평일/휴무일
    target_grades TEXT NOT NULL,                   -- 대상직급 (JSON array)
    work_start TIME NOT NULL,                      -- 근무시작
    work_end TIME NOT NULL,                        -- 근무종료
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ── 인덱스 ──
CREATE INDEX IF NOT EXISTS idx_employees_no ON employees(employee_no);
CREATE INDEX IF NOT EXISTS idx_employees_factory ON employees(factory);
CREATE INDEX IF NOT EXISTS idx_employees_grade ON employees(grade);
CREATE INDEX IF NOT EXISTS idx_assignments_date ON duty_assignments(duty_date);
CREATE INDEX IF NOT EXISTS idx_assignments_status ON duty_assignments(status);
CREATE INDEX IF NOT EXISTS idx_logs_date ON duty_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_logs_approval ON duty_logs(approval_status);
CREATE INDEX IF NOT EXISTS idx_payments_month ON duty_payments(payment_month);

-- ── RLS (Row Level Security) ──
-- 테스트 환경에서는 기본적으로 anon key로 접근 가능하도록 설정
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_changes ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE duty_rules ENABLE ROW LEVEL SECURITY;

-- 테스트용: 모든 접근 허용 (운영 시 세분화 필요)
CREATE POLICY "Allow all for anon" ON employees FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON duty_assignments FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON duty_changes FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON duty_logs FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON duty_payments FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON emergency_contacts FOR ALL USING (true);
CREATE POLICY "Allow all for anon" ON duty_rules FOR ALL USING (true);
