from typing import Optional
from pydantic import BaseModel


class MangaPreview(BaseModel):
    id: int
    english_name: Optional[str]
    romaji_name: Optional[str]
    native_name: Optional[str]
    title_format: str
    url: str
    banner_image_url: Optional[str]
    description: Optional[str]
    genres: list[str]


class MangaRelation(BaseModel):
    id: int
    english_name: Optional[str]
    romaji_name: Optional[str]
    native_name: Optional[str]
    title_format: str
    url: str
    banner_image_url: Optional[str]
    description: Optional[str]
    genres: list[str]
    relation_type: str
