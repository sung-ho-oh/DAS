"""
공통 UI 컴포넌트
- 페이지 헤더, 푸터, 스타일링
"""
import streamlit as st
from config import APP_TITLE, APP_VERSION


def page_header(title: str, icon: str = "📋"):
    """공통 페이지 헤더"""
    st.title(f"{icon} {title}")
    st.markdown("---")


def page_footer():
    """공통 페이지 푸터"""
    st.markdown("---")
    st.caption(f"{APP_TITLE} v{APP_VERSION} | 독립형 테스트 환경")


def show_success(message: str):
    """성공 메시지"""
    st.success(f"✅ {message}")


def show_error(message: str):
    """에러 메시지"""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """경고 메시지"""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """정보 메시지"""
    st.info(f"ℹ️ {message}")


def holiday_row_style(row):
    """휴무일 행 배경색 스타일 (pandas styling용)"""
    if row.get("day_category") == "휴무일":
        return ["background-color: #FFF3E0"] * len(row)
    return [""] * len(row)
