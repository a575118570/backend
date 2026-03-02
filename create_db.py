"""
建立小皮 MySQL 資料庫（若不存在）
執行: python create_db.py
"""
import asyncio
import aiomysql


async def create_database():
    # 從 .env 讀取，預設小皮常用設定
    import os
    from dotenv import load_dotenv
    from pathlib import Path

    load_dotenv(Path(__file__).parent / ".env")
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "root")
    db_name = os.getenv("DB_NAME", "anime_db")

    # 從 DATABASE_URL 解析
    url = os.getenv("DATABASE_URL", "")
    if "mysql" in url:
        # mysql+aiomysql://user:pass@host:port/dbname
        import re
        m = re.search(r"mysql\+aiomysql://([^:]+):([^@]*)@([^:]+):(\d+)/([^?]+)", url)
        if m:
            user, password, host, port, db_name = m.groups()
            port = int(port)

    print(f"Connecting to MySQL at {host}:{port} as {user}...")
    try:
        conn = await aiomysql.connect(
            host=host,
            port=port,
            user=user,
            password=password or None,
        )
        async with conn.cursor() as cur:
            await cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"[OK] Database '{db_name}' created or already exists")
        conn.close()
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        print("\nPlease ensure:")
        print("  1. Xiaopi MySQL service is running")
        print("  2. Check .env: DB_USER, DB_PASSWORD, DB_NAME")
        return False


if __name__ == "__main__":
    asyncio.run(create_database())
