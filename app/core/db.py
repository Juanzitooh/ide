from contextlib import contextmanager
from typing import Iterator, Optional

import pymysql
from sqlalchemy import create_engine
from urllib.parse import quote_plus

from flask import current_app

_ENGINE = None


def _get_engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    config = current_app.config
    host = config.get("MYSQL_HOST")
    user = config.get("MYSQL_USER")
    password = config.get("MYSQL_PASSWORD")
    database = config.get("MYSQL_DB")
    if not all([host, user, database]):
        return None

    password_encoded = quote_plus(password or "")
    url = (
        f"mysql+pymysql://{user}:{password_encoded}@{host}:"
        f"{int(config.get('MYSQL_PORT', 3306))}/{database}"
    )
    _ENGINE = create_engine(
        url,
        pool_size=5,
        max_overflow=5,
        pool_recycle=280,
        pool_pre_ping=True,
        connect_args={"cursorclass": pymysql.cursors.DictCursor},
    )
    return _ENGINE


@contextmanager
def get_connection() -> Iterator[Optional[pymysql.connections.Connection]]:
    engine = _get_engine()
    if engine is None:
        yield None
        return
    connection = engine.raw_connection()
    try:
        yield connection
    finally:
        connection.close()
