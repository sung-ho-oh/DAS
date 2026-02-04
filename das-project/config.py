"""
DAS 시스템 설정
- 환경변수 로드
- 공통 상수 정의
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Supabase ──
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ── App ──
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
APP_TITLE = "DAS - 당직 업무 자동화 시스템"
APP_VERSION = "2.0.0"

# ── n8n ──
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")

# ── 조직 구조 (테스트용 고정값) ──
FACTORIES = ["창원1공장", "창원2공장"]

FACTORY1_DEPARTMENTS = [
    "세탁기", "에어컨", "청소기", "에어컨컴프", "전자관2", "경영지원담당1"
]
FACTORY2_DEPARTMENTS = [
    "연구소", "냉장고", "조리기기", "냉장고COMP", "경영지원담당2"
]

BUSINESS_UNITS = [
    "Digital A.", "경영지원담당1", "냉장고컴프레서",
    "조리기기", "냉장고", "경영지원담당2",
    "에어컨", "에어컨컴프", "청소기", "세탁기", "전자관2", "연구소"
]

# ── 직급 체계 ──
GRADES = {
    1: {"name": "1급", "positions": ["수석", "부장"]},
    2: {"name": "2급", "positions": ["차장", "과장"]},
    3: {"name": "3급", "positions": ["대리"]},
    4: {"name": "4급", "positions": ["사원"]},
}

# ── 당직 발령 기준 ──
DUTY_RULES = {
    "holiday_main": {"grades": [1, 2], "positions": ["수석", "부장", "차장"], "label": "휴무일 총당직"},
    "holiday_sub":  {"grades": [3, 4], "positions": ["대리", "사원"], "label": "휴무일 부당직"},
    "weekday_main": {"grades": [2],    "positions": ["과장"], "label": "평일 총당직"},
    "weekday_sub":  {"grades": [3, 4], "positions": ["대리", "사원"], "label": "평일 부당직"},
}

# ── 근무 시간 ──
WORK_HOURS = {
    "holiday_day":   {"start": "08:00", "end": "20:00", "label": "휴무일 주간"},
    "holiday_night": {"start": "20:00", "end": "08:00", "label": "휴무일 야간"},
    "weekday_night": {"start": "19:30", "end": "08:00", "label": "평일 야간"},
    "sat_2_4":       {"start": "17:00", "end": "08:00", "label": "2,4주 토요일"},
    "sat_5_day":     {"start": "12:00", "end": "22:00", "label": "5주 토요일 주간"},
    "sat_5_night":   {"start": "22:00", "end": "08:00", "label": "5주 토요일 야간"},
}

# ── 당직 변경 사유 ──
CHANGE_REASONS = ["출장", "파견", "교육", "경조사", "병가", "기타"]

# ── 승인 상태 ──
APPROVAL_STATUS = ["작성중", "승인요청", "승인", "부결"]

# ── 당직비 기준 (원) ──
DUTY_PAYMENT_RATES = {
    "holiday_day": 50000,
    "holiday_night": 60000,
    "weekday_night": 40000,
}
