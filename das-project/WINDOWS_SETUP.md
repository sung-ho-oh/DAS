# DAS 프로젝트 - Windows 설정 가이드

**로컬 환경**: Windows
**로컬 경로**: `C:\Users\USER\Downloads\das-project\das-project`
**서버 환경**: Linux (Streamlit 앱 실행 중)

---

## 📥 1. Git에서 최신 코드 가져오기 (Windows)

Windows PowerShell 또는 CMD에서 실행:

```powershell
cd C:\Users\USER\Downloads\das-project\das-project
git fetch origin
git pull origin claude/review-progress-VUITS
```

최신 파일이 포함됩니다:
- `migrations/enable_rls_policies.sql` (RLS 정책 SQL)
- `migrations/README.md`
- `SETUP_STATUS.md`

---

## 🔧 2. Supabase RLS 정책 설정 (필수)

### 단계별 가이드

#### ① Supabase Dashboard 접속
브라우저에서 다음 URL 열기:
```
https://supabase.com/dashboard/project/dluufyjfxevumhgqnpzy
```

#### ② SQL Editor 열기
- 왼쪽 메뉴에서 **"SQL Editor"** 클릭

#### ③ SQL 스크립트 복사
Windows에서 파일 열기:
```powershell
cd C:\Users\USER\Downloads\das-project\das-project
notepad migrations\enable_rls_policies.sql
```

또는 아래 SQL을 직접 복사:

```sql
-- employees 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON employees;
CREATE POLICY "Allow all for anon" ON employees
    FOR ALL USING (true) WITH CHECK (true);

-- duty_assignments 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_assignments;
CREATE POLICY "Allow all for anon" ON duty_assignments
    FOR ALL USING (true) WITH CHECK (true);

-- duty_changes 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_changes;
CREATE POLICY "Allow all for anon" ON duty_changes
    FOR ALL USING (true) WITH CHECK (true);

-- duty_logs 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_logs;
CREATE POLICY "Allow all for anon" ON duty_logs
    FOR ALL USING (true) WITH CHECK (true);

-- duty_payments 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_payments;
CREATE POLICY "Allow all for anon" ON duty_payments
    FOR ALL USING (true) WITH CHECK (true);

-- emergency_contacts 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON emergency_contacts;
CREATE POLICY "Allow all for anon" ON emergency_contacts
    FOR ALL USING (true) WITH CHECK (true);

-- duty_rules 테이블
DROP POLICY IF EXISTS "Allow all for anon" ON duty_rules;
CREATE POLICY "Allow all for anon" ON duty_rules
    FOR ALL USING (true) WITH CHECK (true);

SELECT 'RLS 정책이 성공적으로 설정되었습니다!' as message;
```

#### ④ SQL Editor에 붙여넣고 실행
1. Supabase SQL Editor에 위 스크립트 붙여넣기
2. **"Run"** 버튼 클릭
3. 성공 메시지 확인: `"RLS 정책이 성공적으로 설정되었습니다!"`

---

## 🖥️ 3. Windows에서 로컬 실행 (선택사항)

서버에서 이미 실행 중이므로 선택사항입니다.

### Python 가상환경 설정

```powershell
cd C:\Users\USER\Downloads\das-project\das-project

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### .env 파일 확인

Windows에서 `.env` 파일 내용 확인:
```powershell
type .env
```

내용이 다음과 같아야 합니다:
```
SUPABASE_URL=https://dluufyjfxevumhgqnpzy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
APP_ENV=development
APP_DEBUG=true
```

### Streamlit 실행

```powershell
cd C:\Users\USER\Downloads\das-project\das-project
streamlit run app.py --server.port 8501
```

브라우저에서 자동으로 열립니다: http://localhost:8501

---

## 🧪 4. 데이터베이스 연결 테스트 (Windows)

RLS 정책 설정 후 Windows에서 테스트:

```powershell
cd C:\Users\USER\Downloads\das-project\das-project

# Python으로 직접 테스트
python -c "from services import db; print('직원:', db.count('employees'), '건'); print('당직 발령:', db.count('duty_assignments'), '건')"
```

성공 시 출력 예시:
```
직원: 50 건
당직 발령: 120 건
```

---

## 📊 5. 현재 실행 중인 서버 접속

Linux 서버에서 이미 Streamlit이 실행 중입니다.

### 서버 접속 URL
서버 IP가 공개되어 있다면:
```
http://[서버IP]:8501
```

또는 로컬호스트 (서버에서 직접 접속):
```
http://0.0.0.0:8501
http://localhost:8501
```

---

## 🔍 6. 문제 해결 (Windows)

### Git Pull 충돌 시
```powershell
cd C:\Users\USER\Downloads\das-project\das-project
git stash
git pull origin claude/review-progress-VUITS
git stash pop
```

### Python 모듈을 찾을 수 없는 경우
```powershell
# 현재 디렉토리를 PYTHONPATH에 추가
$env:PYTHONPATH="C:\Users\USER\Downloads\das-project\das-project"
```

### .env 파일이 로드되지 않는 경우
```powershell
# .env 파일 존재 확인
dir .env

# 없으면 .env.example 복사
copy .env.example .env

# notepad으로 편집
notepad .env
```

### Streamlit 포트가 이미 사용 중인 경우
```powershell
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

---

## 📁 7. 주요 파일 위치 (Windows 경로)

```
C:\Users\USER\Downloads\das-project\das-project\
├── .env                                    # 환경 변수
├── app.py                                  # Streamlit 앱
├── requirements.txt                        # Python 패키지 목록
├── migrations\
│   ├── enable_rls_policies.sql            # ⭐ RLS 설정 SQL
│   └── README.md                          # 마이그레이션 가이드
├── pages\                                 # UI 페이지 (6개)
├── services\                              # 비즈니스 로직
├── components\                            # 공통 UI
└── data\
    └── seed_data.py                       # 테스트 데이터 생성
```

---

## ✅ 체크리스트

- [ ] Git에서 최신 코드 pull
- [ ] Supabase Dashboard에서 RLS 정책 SQL 실행
- [ ] 데이터베이스 연결 테스트 (403 Forbidden 에러 해결 확인)
- [ ] 서버 또는 로컬에서 Streamlit 앱 접속
- [ ] 6개 페이지 모두 정상 작동 확인

---

## 🎯 핵심 요약

**Windows 환경에서 해야 할 가장 중요한 작업:**

1. **Git Pull** (최신 코드 받기)
   ```powershell
   cd C:\Users\USER\Downloads\das-project\das-project
   git pull origin claude/review-progress-VUITS
   ```

2. **Supabase RLS 정책 설정** (웹 브라우저에서)
   - https://supabase.com/dashboard 접속
   - SQL Editor에서 `migrations\enable_rls_policies.sql` 실행

이 두 단계만 완료하면 앱이 정상 작동합니다! 🚀

---

**문의사항**: 문제가 발생하면 `SETUP_STATUS.md` 파일을 참조하세요.
