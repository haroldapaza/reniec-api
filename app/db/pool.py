from psycopg_pool import ConnectionPool
from app.core.config import get_settings

settings = get_settings()

pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=settings.db_min_pool,
    max_size=settings.db_max_pool,
    open=False,
    kwargs={"autocommit": True},
)


def open_pool() -> None:
    pool.open(wait=True)


def close_pool() -> None:
    pool.close()
