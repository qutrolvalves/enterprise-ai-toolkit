"""
数据库模块（惰性初始化 + 优雅降级）。

- 连接成功时：自动建表、保存请求记录
- 连接失败时：API 仍可正常工作（仅日志记录错误）
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .config import DATABASE_URL

logger = logging.getLogger(__name__)

_db_available = False
_engine = None
_SessionLocal = None


def _create_engine():
    """创建数据库引擎并测试连接（惰性初始化）。"""
    global _engine, _SessionLocal, _db_available
    if _engine is not None:
        return

    try:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _SessionLocal = sessionmaker(bind=_engine)
        _db_available = True
        logger.info("数据库连接成功: %s", DATABASE_URL)
    except Exception as e:
        logger.warning("数据库不可用，将以无持久化模式运行: %s", e)
        _db_available = False


def get_db_available() -> bool:
    """返回数据库是否可用。"""
    return _db_available


def init_db():
    """初始化数据库：测试连接 + 创建表结构。"""
    global _db_available
    from .models import Base

    _create_engine()
    if not _db_available:
        return

    try:
        Base.metadata.create_all(bind=_engine)
        logger.info("数据库表结构已就绪")
    except SQLAlchemyError as e:
        logger.warning("数据库表创建失败，将以无持久化模式运行: %s", e)
        _db_available = False


def save_request(message: str, result: dict) -> int | None:
    """
    保存客户请求及处理结果到数据库。

    Returns:
        记录 ID，如果数据库不可用则返回 None。
    """
    if not _db_available or _SessionLocal is None:
        return None

    from .models import CustomerRequest

    try:
        session = _SessionLocal()
        record = CustomerRequest(
            message=message,
            result=result,
            status="completed",
        )
        session.add(record)
        session.commit()
        record_id = record.id
        session.close()
        logger.info("请求已持久化 (id=%d)", record_id)
        return record_id
    except SQLAlchemyError as e:
        logger.warning("请求持久化失败（不影响 API 响应）: %s", e)
        return None
