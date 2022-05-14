from typing import Optional
from pydantic import BaseModel


class MangaPreview(BaseModel):
    id: int
    english_name: Optional[str]
    romaji_name: Optional[str]
    native_name: Optional[str]
    title_format: str
    url: str
    description: Optional[str]
    genres: list[str]


class MangaRelation(BaseModel):
    id: int
    english_name: Optional[str]
    romaji_name: Optional[str]
    native_name: Optional[str]
    title_format: str
    url: str
    relation_type: str


class MangaRelations(BaseModel):
    relations: list[MangaRelation]
    url: str
