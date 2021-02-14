from typing import List

from pydantic import BaseModel, Field


class _KeywordBase(BaseModel):
    name: str


class KeywordRead(_KeywordBase):
    class Config:
        orm_mode = True


class Keyword(_KeywordBase):
    id: str
    contents: List["ContentRead"] = []

    class Config:
        orm_mode = True


class _ContentBase(BaseModel):
    filename: str = Field(..., example="02lag7ns7KtMWhCqcBdbjp.jpeg")
    keywords: List["str"] = Field([], example=["cat", "computer"])


# Content patch doesn't inherit from _ContentBase because we wont update the file
class ContentPatch(BaseModel):
    keywords: List["str"] = Field([], example=["cat", "computer"])


class ContentCreate(_ContentBase):
    filepath: str


class ContentRead(_ContentBase):
    keywords: List[KeywordRead] = []

    class Config:
        orm_mode = True


class Content(_ContentBase):
    id: int
    filepath: str
    keywords: List[Keyword] = []
    count: int = Field(
        0, example=154, description="Number of times this content has been accessed"
    )

    class Config:
        orm_mode = True
