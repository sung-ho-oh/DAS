"""
Supabase 연결 및 공통 CRUD 함수
- Layer 3: 데이터 접근 계층
- 다른 services 모듈에서 이 파일을 통해 DB에 접근
"""
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY


def get_client() -> Client:
    """Supabase 클라이언트 반환 (싱글톤 패턴)"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL과 SUPABASE_KEY가 .env 파일에 설정되어야 합니다. "
            ".env.example을 참고하세요."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ── 공통 CRUD ──

def select_all(table: str, order_by: str = "id", ascending: bool = True):
    """테이블 전체 조회"""
    client = get_client()
    query = client.table(table).select("*").order(order_by, desc=not ascending)
    response = query.execute()
    return response.data


def select_by_id(table: str, record_id: str):
    """ID로 단건 조회"""
    client = get_client()
    response = client.table(table).select("*").eq("id", record_id).single().execute()
    return response.data


def select_where(table: str, column: str, value, order_by: str = "id"):
    """조건 조회"""
    client = get_client()
    response = (
        client.table(table)
        .select("*")
        .eq(column, value)
        .order(order_by)
        .execute()
    )
    return response.data


def select_between(table: str, column: str, start, end, order_by: str = "id"):
    """범위 조회 (날짜 등)"""
    client = get_client()
    response = (
        client.table(table)
        .select("*")
        .gte(column, start)
        .lte(column, end)
        .order(order_by)
        .execute()
    )
    return response.data


def insert(table: str, data: dict):
    """단건 삽입"""
    client = get_client()
    response = client.table(table).insert(data).execute()
    return response.data


def insert_many(table: str, data_list: list):
    """다건 삽입"""
    client = get_client()
    response = client.table(table).insert(data_list).execute()
    return response.data


def update(table: str, record_id: str, data: dict):
    """단건 업데이트"""
    client = get_client()
    response = client.table(table).update(data).eq("id", record_id).execute()
    return response.data


def delete(table: str, record_id: str):
    """단건 삭제"""
    client = get_client()
    response = client.table(table).delete().eq("id", record_id).execute()
    return response.data


def delete_where(table: str, column: str, value):
    """조건 삭제"""
    client = get_client()
    response = client.table(table).delete().eq(column, value).execute()
    return response.data


def count(table: str, column: str = None, value=None) -> int:
    """건수 조회"""
    client = get_client()
    query = client.table(table).select("*", count="exact")
    if column and value is not None:
        query = query.eq(column, value)
    response = query.execute()
    return response.count or 0
