"""
動漫聚合搜尋平台 - 後端 API
類似 mkanime.ai 的多源聚合搜尋服務
使用 .env 連接資料庫
"""
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from config import DATABASE_URL
from database import get_db, init_db
from models import Anime, AnimeEpisode

app = FastAPI(
    title="Anime Search API",
    description="多源動漫聚合搜尋 API",
    version="1.0.0"
)

# CORS 設定 - 允許前端跨域請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 資料模型 ============
class AnimeEpisodeSchema(BaseModel):
    episode_num: int
    title: str
    url: str
    source: str


class AnimeDetailSchema(BaseModel):
    id: str
    title: str
    title_cn: Optional[str] = None
    cover: str
    description: str
    genres: List[str]
    year: Optional[str] = None
    status: str
    episodes: List[AnimeEpisodeSchema]
    sources: List[str]


class AnimeItemSchema(BaseModel):
    id: str
    title: str
    title_cn: Optional[str] = None
    cover: str
    description: str
    genres: List[str]
    year: Optional[str] = None
    status: str
    sources: List[str]


# ============ 啟動時初始化資料庫 ============
@app.on_event("startup")
async def startup_event():
    """啟動時連接資料庫、建立資料表、匯入種子資料"""
    try:
        await init_db()
        from seed_data import seed
        await seed()
        # Windows console may be GBK and can't print some unicode symbols reliably.
        print(f"[OK] DB connected: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'SQLite (anime.db)'}")
    except Exception as e:
        print(f"[FAIL] DB init/connect failed: {e}")
        raise


# ============ API 路由 ============
@app.get("/")
async def root():
    return {
        "message": "動漫聚合搜尋 API",
        "version": "1.0.0",
        "database": "configured"
    }


@app.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    健康檢查：測試資料庫連線
    """
    try:
        result = await db.execute(select(Anime).limit(1))
        result.scalar_one_or_none()
        return {
            "status": "ok",
            "database": "connected",
            # Avoid mojibake on some Windows terminals; keep ASCII here.
            "message": "database connection OK"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "message": str(e)
        }


@app.get("/api/anime", response_model=List[AnimeItemSchema])
async def get_anime_list(
    q: Optional[str] = Query(None, description="搜尋關鍵字"),
    genre: Optional[str] = Query(None, description="類型篩選"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    取得動漫列表，支援搜尋和篩選
    """
    query = select(Anime)

    # 搜尋篩選
    if q:
        q_pattern = f"%{q}%"
        query = query.where(
            or_(
                Anime.title.ilike(q_pattern),
                Anime.title_cn.ilike(q_pattern),
                Anime.genres.ilike(q_pattern),
            )
        )

    # 類型篩選（genres 為 JSON 陣列字串）
    if genre:
        query = query.where(Anime.genres.contains(f'"{genre}"'))

    # 分頁
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    anime_list = result.scalars().all()

    return [
        AnimeItemSchema(
            id=a.id,
            title=a.title,
            title_cn=a.title_cn,
            cover=a.cover,
            description=a.description,
            genres=a.genres_list(),
            year=a.year,
            status=a.status,
            sources=a.sources_list(),
        )
        for a in anime_list
    ]


@app.get("/api/anime/{anime_id}", response_model=AnimeDetailSchema)
async def get_anime_detail(
    anime_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    取得單一動漫詳情
    """
    result = await db.execute(select(Anime).where(Anime.id == anime_id))
    anime = result.scalar_one_or_none()

    if not anime:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="動漫不存在")

    # 取得集數
    ep_result = await db.execute(
        select(AnimeEpisode)
        .where(AnimeEpisode.anime_id == anime_id)
        .order_by(AnimeEpisode.episode_num)
    )
    episodes = ep_result.scalars().all()

    return AnimeDetailSchema(
        id=anime.id,
        title=anime.title,
        title_cn=anime.title_cn,
        cover=anime.cover,
        description=anime.description,
        genres=anime.genres_list(),
        year=anime.year,
        status=anime.status,
        episodes=[
            AnimeEpisodeSchema(
                episode_num=ep.episode_num,
                title=ep.title,
                url=ep.url,
                source=ep.source,
            )
            for ep in episodes
        ],
        sources=anime.sources_list(),
    )


@app.get("/api/genres")
async def get_genres(db: AsyncSession = Depends(get_db)):
    """
    取得所有類型列表
    """
    result = await db.execute(select(Anime.genres))
    rows = result.scalars().all()
    genres = set()
    import json
    for row in rows:
        try:
            genres.update(json.loads(row))
        except (json.JSONDecodeError, TypeError):
            pass
    return sorted(list(genres))


@app.get("/api/sources")
async def get_sources(db: AsyncSession = Depends(get_db)):
    """
    取得所有來源列表
    """
    result = await db.execute(select(Anime.sources))
    rows = result.scalars().all()
    sources = set()
    import json
    for row in rows:
        try:
            sources.update(json.loads(row))
        except (json.JSONDecodeError, TypeError):
            pass
    return sorted(list(sources))


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
