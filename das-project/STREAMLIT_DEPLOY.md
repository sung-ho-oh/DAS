# Streamlit Cloud 배포 가이드

DAS (Duty Assignment System)을 Streamlit Cloud에 배포하는 방법을 안내합니다.

---

## 📋 준비사항

- [x] GitHub 계정
- [x] Supabase 프로젝트 (이미 설정됨)
- [ ] GitHub Public/Private Repository
- [ ] Streamlit Cloud 계정

---

## 🚀 배포 단계

### 1단계: GitHub Repository 준비

#### 옵션 A: 새 Repository 생성

1. **GitHub 접속**: https://github.com/new
2. **Repository 생성**:
   - Repository name: `DAS` 또는 원하는 이름
   - Description: `Duty Assignment System - 당직 업무 자동화`
   - Visibility: **Public** (무료 Streamlit Cloud) 또는 **Private** (팀 플랜)
   - ✅ Add a README file 체크 해제
   - Create repository 클릭

3. **로컬 Repository와 연결** (Windows PowerShell):
   ```powershell
   cd C:\Users\USER\Downloads\das-project\das-project
   git remote remove origin  # 기존 remote 제거
   git remote add origin https://github.com/[사용자명]/DAS.git
   git branch -M main
   git push -u origin main
   ```

#### 옵션 B: 기존 Repository 사용

이미 GitHub에 repository가 있다면:
```powershell
cd C:\Users\USER\Downloads\das-project\das-project
git push origin claude/review-progress-VUITS
```

---

### 2단계: Supabase RLS 정책 설정 (필수)

배포하기 전에 **반드시** Supabase RLS 정책을 설정해야 합니다.

1. **Supabase Dashboard** 접속: https://supabase.com/dashboard/project/dluufyjfxevumhgqnpzy
2. **SQL Editor** 열기
3. **`migrations/enable_rls_policies.sql`** 파일 내용 복사 및 실행
   ```powershell
   notepad C:\Users\USER\Downloads\das-project\das-project\migrations\enable_rls_policies.sql
   ```
4. SQL 전체를 복사하여 Supabase SQL Editor에 붙여넣고 **Run** 클릭

---

### 3단계: Streamlit Cloud 배포

#### ① Streamlit Cloud 접속

1. **Streamlit Cloud** 접속: https://share.streamlit.io/
2. **GitHub로 로그인** 또는 새 계정 생성

#### ② 새 앱 배포

1. **"New app"** 버튼 클릭
2. **Repository 선택**:
   - Repository: `[사용자명]/DAS`
   - Branch: `main` 또는 `claude/review-progress-VUITS`
   - Main file path: `das-project/app.py`

3. **Advanced settings** 클릭 (선택사항):
   - Python version: `3.11`

4. **Deploy!** 버튼 클릭

---

### 4단계: Secrets 설정 (중요!)

앱 배포 중 또는 배포 후 Secrets를 설정합니다.

#### Streamlit Cloud Dashboard에서:

1. 배포된 앱 선택
2. **Settings** (⚙️) 메뉴 클릭
3. **Secrets** 탭 선택
4. 다음 내용 입력:

```toml
SUPABASE_URL = "https://dluufyjfxevumhgqnpzy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsdXVmeWpmeGV2dW1oZ3FucHp5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzAxNjYyODMsImV4cCI6MjA4NTc0MjI4M30.Iy0HKZkkPVkrg7s1mMvUTgs_fRdp6SNYy56PW2UELNQ"
APP_ENV = "production"
APP_DEBUG = "false"
```

⚠️ **주의**: 실제 SUPABASE_KEY를 사용하세요 (.env 파일 참조)

5. **Save** 클릭
6. 앱이 자동으로 재시작됩니다

---

### 5단계: 배포 확인

#### ✅ 체크리스트

- [ ] 앱이 정상적으로 로드되나요?
- [ ] 메인 페이지가 표시되나요?
- [ ] 데이터베이스 연결이 작동하나요? (직원 목록이 보이나요?)
- [ ] 6개 페이지 모두 접근 가능한가요?
  - 1️⃣ 당직 예정자 LIST
  - 2️⃣ 당직일정 변경
  - 3️⃣ 비상연락망
  - 4️⃣ 당직비 지급
  - 5️⃣ 당직근무일지
  - 6️⃣ 관리자

---

## 🔧 문제 해결

### 문제 1: "ModuleNotFoundError"

**원인**: `requirements.txt`에 필요한 패키지가 누락되었습니다.

**해결**:
1. Streamlit Cloud 로그 확인
2. 누락된 패키지를 `requirements.txt`에 추가
3. Git commit & push
4. 자동으로 재배포됨

### 문제 2: "403 Forbidden" 또는 데이터가 안 보임

**원인**: Supabase RLS 정책이 설정되지 않았습니다.

**해결**:
1. `migrations/enable_rls_policies.sql` 실행 (2단계 참조)
2. Streamlit Cloud에서 앱 재시작

### 문제 3: Secrets가 인식되지 않음

**원인**: Secrets 형식이 잘못되었거나 앱이 재시작되지 않았습니다.

**해결**:
1. Secrets 탭에서 TOML 형식 확인 (따옴표 사용)
2. Save 후 앱 재시작 버튼 클릭
3. 로그에서 환경 변수 로드 확인

### 문제 4: "File not found: das-project/app.py"

**원인**: Main file path가 잘못되었습니다.

**해결**:
1. Repository 구조 확인
2. Main file path를 다음 중 하나로 변경:
   - `app.py` (repository 루트에 app.py가 있는 경우)
   - `das-project/app.py` (das-project 폴더 안에 있는 경우)

### 문제 5: 앱 로딩이 너무 느림

**해결**:
- Streamlit Cloud 무료 티어는 리소스가 제한됩니다
- 필요시 프로 플랜 고려
- 데이터 캐싱 최적화 (`@st.cache_data` 사용)

---

## 📱 배포 후 관리

### 앱 업데이트

코드를 수정한 후:
```powershell
cd C:\Users\USER\Downloads\das-project\das-project
git add .
git commit -m "Update features"
git push origin main
```

Streamlit Cloud가 자동으로 감지하고 재배포합니다.

### 로그 확인

1. Streamlit Cloud Dashboard
2. 앱 선택
3. **Manage app** > **Logs** 탭

### 앱 재시작

1. Streamlit Cloud Dashboard
2. 앱 선택
3. **⋮** 메뉴 > **Reboot app**

### 앱 삭제

1. Streamlit Cloud Dashboard
2. 앱 선택
3. **Settings** > **Delete app**

---

## 🔒 보안 권장사항

### Production 환경에서는:

1. **RLS 정책 강화**:
   - 현재: 모든 anon 사용자가 모든 데이터에 접근 가능
   - 권장: 사용자 인증 추가 및 세밀한 권한 설정

2. **Supabase Row Level Security**:
   ```sql
   -- 예시: 사용자별 접근 제어
   CREATE POLICY "Users can only see their department data"
   ON duty_assignments
   FOR SELECT
   USING (auth.uid() IS NOT NULL);
   ```

3. **환경 변수 분리**:
   - 개발: `.env` 파일
   - 프로덕션: Streamlit Cloud Secrets

4. **API Key 보호**:
   - anon key 대신 service_role key 사용 고려 (서버 환경)
   - 또는 Supabase Auth 통합

---

## 📚 참고 자료

- **Streamlit Cloud 문서**: https://docs.streamlit.io/streamlit-community-cloud
- **Supabase 문서**: https://supabase.com/docs
- **RLS 가이드**: https://supabase.com/docs/guides/auth/row-level-security

---

## ✅ 배포 완료 후

배포 URL (예시):
```
https://[앱이름]-[해시].streamlit.app
```

이 URL을 팀원들과 공유하세요! 🎉

---

**문의**: 배포 중 문제가 발생하면:
1. `SETUP_STATUS.md` - 전체 프로젝트 상태
2. `WINDOWS_SETUP.md` - Windows 로컬 설정
3. `migrations/README.md` - RLS 정책 설정

로그를 확인하여 문제를 해결하세요.
