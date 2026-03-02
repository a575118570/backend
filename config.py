"""
從 .env 載入資料庫連線設定
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 載入 .env 檔案（優先從 backend 目錄）
# 若 .env 不存在，會使用系統環境變數或預設值
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()  # 嘗試載入專案根目錄的 .env

# 資料庫連線
# 優先使用 DATABASE_URL，否則依 DB_* 組 MySQL，最後用 SQLite
_db_dir = Path(__file__).parent.resolve()
_default_sqlite = f"sqlite+aiosqlite:///{(_db_dir / 'anime.db').as_posix()}"

_db_url = os.getenv("DATABASE_URL")
if not _db_url and all(os.getenv(k) for k in ("DB_HOST", "DB_USER", "DB_NAME")):
    _host = os.getenv("DB_HOST", "localhost")
    _port = os.getenv("DB_PORT", "3306")
    _user = os.getenv("DB_USER", "root")
    _pass = os.getenv("DB_PASSWORD", "")
    _name = os.getenv("DB_NAME", "anime_db")
    _pass_part = f":{_pass}" if _pass else ""
    _db_url = f"mysql+aiomysql://{_user}{_pass_part}@{_host}:{_port}/{_name}"

DATABASE_URL = _db_url or _default_sqlite

# 其他設定
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
