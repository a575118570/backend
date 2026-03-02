"""
測試資料庫連線
執行: python db_connect.py
"""
import asyncio
import sys

from config import DATABASE_URL
from database import engine, init_db
from sqlalchemy import text


async def test_connection():
    print("=" * 50)
    print("Database Connection Test")
    print("=" * 50)
    print(f"URL: {DATABASE_URL[:50]}..." if len(DATABASE_URL) > 50 else f"URL: {DATABASE_URL}")

    try:
        # 測試連線
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("[OK] Connection successful")

        # 建立資料表
        await init_db()
        print("[OK] Tables created/exist")

        # 測試查詢
        from database import async_session_maker
        from models import Anime

        async with async_session_maker() as session:
            from sqlalchemy import select
            result = await session.execute(select(Anime).limit(1))
            anime = result.scalar_one_or_none()
            if anime:
                print(f"[OK] Query success, example: {anime.title}")
            else:
                print("[OK] Database empty (run python main.py to seed)")

        print("=" * 50)
        print("Database connection OK!")
        # Explicitly dispose engine to avoid aiomysql __del__ warnings on Windows.
        try:
            await engine.dispose()
        except Exception:
            pass
        return True

    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        print("\nPlease check:")
        print("  1. Create .env and set DATABASE_URL")
        print("  2. Copy env.example to .env: copy env.example .env")
        print("  3. For PostgreSQL/MySQL: pip install asyncpg or aiomysql")
        try:
            await engine.dispose()
        except Exception:
            pass
        return False


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
