from typing import List

from pydantic import BaseModel, Field


class _KeywordBase(BaseModel):
    name: str


class Keyword(_KeywordBase):
    id: str
    contents: List["Content"] = []

    class Config:
        orm_mode = True


class _ContentBase(BaseModel):
    filename: str = Field(..., example="02lag7ns7KtMWhCqcBdbjp.jpeg")
    keywords: List[str] = Field([], example=["cat", "computer"])
    count: int = Field(
        0, example=154, description="Number of times this content has been accessed"
    )


class ContentRead(_ContentBase):
    pass


class ContentCreate(_ContentBase):
    filepath: str


class Content(_ContentBase):
    id: int
    filepath: str
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True
