"""
初始化資料庫並填入種子資料
"""
import asyncio
import json

from sqlalchemy import select
from database import async_session_maker, init_db
from models import Anime, AnimeEpisode

SEED_ANIME = [
    {
        "id": "1",
        "title": "Demon Slayer: Kimetsu no Yaiba",
        "title_cn": "鬼滅之刃",
        "cover": "https://cdn.myanimelist.net/images/anime/1286/99889.jpg",
        "description": "Tanjiro sets out on a journey to become a demon slayer and save his sister Nezuko.",
        "genres": ["Action", "Supernatural", "Shounen"],
        "year": "2019",
        "status": "Completed",
        "sources": ["Source A", "Source B"],
    },
    {
        "id": "2",
        "title": "Jujutsu Kaisen",
        "title_cn": "咒術迴戰",
        "cover": "https://cdn.myanimelist.net/images/anime/1171/109222.jpg",
        "description": "Yuji Itadori swallows a cursed finger and becomes a Jujutsu sorcerer.",
        "genres": ["Action", "Supernatural", "Shounen"],
        "year": "2020",
        "status": "Ongoing",
        "sources": ["Source A", "Source C"],
    },
    {
        "id": "3",
        "title": "Spy x Family",
        "title_cn": "間諜家家酒",
        "cover": "https://cdn.myanimelist.net/images/anime/1441/122795.jpg",
        "description": "A spy creates a fake family for a mission, unaware they all have secrets.",
        "genres": ["Action", "Comedy", "Slice of Life"],
        "year": "2022",
        "status": "Ongoing",
        "sources": ["Source A", "Source B", "Source C"],
    },
    {
        "id": "4",
        "title": "Attack on Titan",
        "title_cn": "進擊的巨人",
        "cover": "https://cdn.myanimelist.net/images/anime/10/47347.jpg",
        "description": "Humanity fights against giant humanoid creatures called Titans.",
        "genres": ["Action", "Drama", "Fantasy", "Shounen"],
        "year": "2013",
        "status": "Completed",
        "sources": ["Source A"],
    },
    {
        "id": "5",
        "title": "My Hero Academia",
        "title_cn": "我的英雄學院",
        "cover": "https://cdn.myanimelist.net/images/anime/10/78745.jpg",
        "description": "A boy born without superpowers in a super-powered world dreams of becoming a hero.",
        "genres": ["Action", "Comedy", "Super Power", "Shounen"],
        "year": "2016",
        "status": "Ongoing",
        "sources": ["Source B", "Source C"],
    },
    {
        "id": "6",
        "title": "One Piece",
        "title_cn": "航海王",
        "cover": "https://cdn.myanimelist.net/images/anime/6/73245.jpg",
        "description": "Monkey D. Luffy and his crew sail the Grand Line in search of the ultimate treasure.",
        "genres": ["Action", "Adventure", "Fantasy", "Shounen"],
        "year": "1999",
        "status": "Ongoing",
        "sources": ["Source A", "Source B", "Source C"],
    },
    {
        "id": "7",
        "title": "Chainsaw Man",
        "title_cn": "鏈鋸人",
        "cover": "https://cdn.myanimelist.net/images/anime/1806/126216.jpg",
        "description": "Denji becomes a devil hunter with his pet devil Pochita who can transform into chainsaws.",
        "genres": ["Action", "Supernatural", "Shounen"],
        "year": "2022",
        "status": "Completed",
        "sources": ["Source A", "Source B"],
    },
    {
        "id": "8",
        "title": "Solo Leveling",
        "title_cn": "我獨自升級",
        "cover": "https://cdn.myanimelist.net/images/anime/1704/131238.jpg",
        "description": "The weakest hunter Sung Jinwoo gains a unique system that allows him to level up.",
        "genres": ["Action", "Adventure", "Fantasy"],
        "year": "2024",
        "status": "Ongoing",
        "sources": ["Source A", "Source B", "Source C"],
    },
]


async def seed():
    await init_db()
    async with async_session_maker() as session:
        result = await session.execute(select(Anime).limit(1))
        if result.scalar_one_or_none():
            print("資料庫已有資料，跳過種子匯入")
            return

        for item in SEED_ANIME:
            anime = Anime(
                id=item["id"],
                title=item["title"],
                title_cn=item.get("title_cn"),
                cover=item["cover"],
                description=item["description"],
                genres=json.dumps(item["genres"]),
                year=item.get("year"),
                status=item["status"],
                sources=json.dumps(item["sources"]),
            )
            session.add(anime)
            for i in range(1, 13):
                ep = AnimeEpisode(
                    anime_id=item["id"],
                    episode_num=i,
                    title=f"第 {i} 集",
                    url=f"/watch/{item['id']}/{i}",
                    source="Source A",
                )
                session.add(ep)
        await session.commit()
        print("種子資料匯入完成")


if __name__ == "__main__":
    asyncio.run(seed())
