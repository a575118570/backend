"""
資料庫模型
"""
import json
from typing import List

from sqlalchemy import String, Text, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_cn: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cover: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    genres: Mapped[str] = mapped_column(Text, nullable=False)  # JSON 陣列
    year: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sources: Mapped[str] = mapped_column(Text, nullable=False)  # JSON 陣列

    episodes: Mapped[List["AnimeEpisode"]] = relationship(
        "AnimeEpisode", back_populates="anime", cascade="all, delete-orphan"
    )

    def genres_list(self) -> List[str]:
        return json.loads(self.genres) if self.genres else []

    def sources_list(self) -> List[str]:
        return json.loads(self.sources) if self.sources else []


class AnimeEpisode(Base):
    __tablename__ = "anime_episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    anime_id: Mapped[str] = mapped_column(String(50), ForeignKey("anime.id"), nullable=False)
    episode_num: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)

    anime: Mapped["Anime"] = relationship("Anime", back_populates="episodes")
