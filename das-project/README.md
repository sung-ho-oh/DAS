# DAS - Duty Assignment System (당직 업무 자동화 시스템)

## 개요
기존 3개 부서 5명이 수작업으로 처리하던 당직 업무를 1개 부서 1명이 처리할 수 있는 통합 시스템입니다.

**개발 방법론**: Vibe Coding (노코드 기반 AI 협업 개발)

## 기술 스택
| 구분 | 기술 | 역할 |
|------|------|------|
| Frontend | Streamlit 1.40+ | 웹 UI |
| Backend/DB | Supabase (PostgreSQL 15) | 데이터베이스, 인증, RLS |
| Automation | n8n 1.70+ | 메일 자동발송, 스케줄, Webhook |
| Testing | pytest 8.0+ | 자동 테스트 (단위/통합/E2E) |
| Test Data | Faker + Python | 임의 테스트 데이터 생성기 |

## 핵심 설계 원칙
- **완전 독립형**: LGE 인사시스템, DAS 통합시스템과 연동하지 않음
- **모듈화 구조**: 기능별 별도 파일로 분리 (pages/services/components)
- **자동 테스트**: pytest 기반 단위/통합/E2E 테스트
- **충분한 테스트 데이터**: Faker 기반 200명 직원 + 6개월치 당직 데이터

## 프로젝트 구조
```
das-project/
├── app.py                      # Streamlit 메인 엔트리포인트
├── config.py                   # 환경변수, 상수 정의
├── requirements.txt            # 패키지 목록
├── .env.example                # 환경변수 템플릿
├── .gitignore                  # Git 제외 파일
│
├── pages/                      # 화면 모듈 (6개 페이지)
│   ├── 1_duty_assignment.py    # 당직 예정자 LIST / 발령 관리
│   ├── 2_duty_change.py        # 당직일정 변경 / 변경자 LIST
│   ├── 3_emergency_contact.py  # 비상연락망 관리
│   ├── 4_duty_payment.py       # 당직비 지급 LIST
│   ├── 5_duty_log.py           # 당직근무일지 (1공장/2공장)
│   └── 6_admin.py              # 관리자 (발령기준, 데이터 초기화)
│
├── components/                 # 공통 UI 컴포넌트
│   ├── duty_rules_help.py      # 발령기준/근무시간 도움말
│   ├── employee_selector.py    # 직원 선택 컴포넌트
│   └── common_ui.py            # 공통 헤더, 푸터, 스타일링
│
├── services/                   # 비즈니스 로직 계층
│   ├── db.py                   # Supabase 연결 및 공통 CRUD
│   ├── assignment_service.py   # 발령 생성/조회/LAST사번 로직
│   ├── change_service.py       # 변경 등록/조회 로직
│   ├── log_service.py          # 일지 CRUD/승인 로직
│   ├── payment_service.py      # 당직비 계산/집계 로직
│   └── notification_service.py # 메일 발송 로직 (테스트: 로그만 기록)
│
├── data/                       # 테스트 데이터
│   ├── seed_data.py            # Faker 기반 테스트 데이터 생성기
│   └── schema.sql              # Supabase 테이블 생성 SQL
│
└── tests/                      # 자동 테스트
    ├── conftest.py             # pytest 공통 fixture
    ├── test_assignment.py      # 발령 기능 테스트
    ├── test_change.py          # 변경 기능 테스트
    ├── test_log.py             # 일지 기능 테스트
    ├── test_payment.py         # 당직비 계산 테스트
    └── test_data_generator.py  # 데이터 생성기 테스트
```

## 3계층 아키텍처
```
Layer 1: pages/          →  UI 표시 계층       → components, services 참조
Layer 2: services/       →  비즈니스 로직       → db.py(config) 참조
Layer 3: services/db.py  →  데이터 접근         → Supabase(config.py)
```
**핵심 규칙**: pages/ 파일은 직접 DB를 호출하지 않고, 반드시 services/를 통해 데이터에 접근합니다.

## 시작하기

### 1. 사전 준비
- Python 3.10+
- Supabase 프로젝트 생성 (supabase.com)
- Supabase URL + API Key 확보

### 2. 설치
```bash
git clone https://github.com/YOUR_USERNAME/das-project.git
cd das-project
pip install -r requirements.txt
```

### 3. 환경 설정
```bash
cp .env.example .env
# .env 파일에 Supabase URL과 Key 입력
```

### 4. DB 초기화
Supabase SQL Editor에서 `data/schema.sql` 실행

### 5. 테스트 데이터 생성
```bash
python data/seed_data.py
```

### 6. 실행
```bash
streamlit run app.py
```

### 7. 테스트
```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/test_assignment.py

# 통합 테스트
pytest --integration

# E2E 테스트
pytest --e2e
```

## 개발 로드맵 (10주)
| Phase | 기간 | 주요 작업 |
|-------|------|----------|
| 1 | 1주 | DB 스키마 + 테스트 데이터 생성기 |
| 2 | 2~3주 | 발령 관리 UI + 서비스 |
| 3 | 4주 | 변경등록 + 비상연락망 |
| 4 | 5~6주 | 당직근무일지 + 승인 플로우 |
| 5 | 7주 | 당직비 지급 + Excel 다운로드 |
| 6 | 8주 | n8n 메일 자동화 + 관리자 |
| 7 | 9~10주 | E2E 테스트 + UAT + 버그 수정 |

## Vibe Coding 개발 사이클
```
요구사항 확인(PRD) → AI 코드 생성 → 모듈 배치 → pytest 자동 테스트 → 버그 수정 → UI 확인 → 반복
```

## 라이선스
Private - 비공개 프로젝트
