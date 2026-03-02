"""
資料庫連線與 Session 管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL

# 建立非同步引擎
# MySQL 使用 pool_pre_ping 保持連線有效
_engine_opts = {"echo": False}
if "mysql" in DATABASE_URL:
    _engine_opts["pool_pre_ping"] = True
    _engine_opts["pool_recycle"] = 3600

engine = create_async_engine(DATABASE_URL, **_engine_opts)

# Session 工廠
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """依賴注入用：取得 DB Session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """建立所有資料表"""
    import models  # 確保模型已註冊到 Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
